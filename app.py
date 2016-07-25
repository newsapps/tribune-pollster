import uuid

import boto3
from chalice import Chalice

# Data API

# TODO: Is there a way to break this out into a separate module?
# This would be ideal to swap between a SimpleDB backend and an
# eventual Postgres-based backend.
#
# Unfortunately, It seems like Lambda can't import from a module in the same
# directory

def transform_answer_item(item):
    data = {
        'poll_id': None,
        'question_id': None,
        'user_id': None,
        'answer_id': None,
        'value': None,
    }
    canonical_attrs = set(('poll_id', 'question_id', 'user_id', 'value'))

    data['answer_id'] = item['Name']

    for attr in item['Attributes']:
        name = attr['Name']
        if name in canonical_attrs:
            data[name] = attr['Value']

    return data

def get_responses(poll_id, question_id):
    client = boto3.client('sdb')
    select = "select * from `pollster-responses` where poll_id = '{}' intersection question_id = '{}'".format(poll_id, question_id)

    response = client.select(
        SelectExpression=select,
    )

    return [transform_answer_item(item) for item in response['Items']]

def create_response(poll_id, question_id, user_id, value):
    client = boto3.client('sdb')

    name = str(uuid.uuid4())

    response = client.batch_put_attributes(
        DomainName='pollster-responses',
        Items=[
            {
                'Name': name,
                'Attributes': [
                    {
                        'Name': 'value',
                        'Value': value,
                    },
                    {
                        'Name': 'user_id',
                        'Value': user_id,
                    },
                    {
                        'Name': 'poll_id',
                        'Value': poll_id
                    },
                    {
                        'Name': 'question_id',
                        'Value': question_id
                    },
                ]
            },
        ]
    )

    return {
        'answer_id': name,
        'poll_id': poll_id,
        'question_id': question_id,
        'user_id': user_id,
        'value': value,
    }

# AWS SimpleDB doesn't have any built-in aggregation functionality.
# We'll handle this ourselves using the MapReduce pattern
# (https://en.wikipedia.org/wiki/MapReduce)

def map_answer(item):
    return item['value'], 1

def group_by_answer(items):
    groups = {}
    for k, v in items:
        group = groups.setdefault(k, [])
        group.append(v)

    return [(k, values) for k, values in groups.items()]

def reduce_answer(answer, partial_counts):
    total_count = 0
    for partial_count in partial_counts:
        total_count += partial_count

    return answer, total_count

def get_response_summary(poll_id, question_id):
    answers = get_responses(poll_id, question_id)

    total = 0
    num_answers = {}

    by_answer = group_by_answer([map_answer(a) for a in answers])
    for answer, responses in by_answer:
        answer, answer_total_count = reduce_answer(answer, responses)
        num_answers[answer] = answer_total_count
        total += answer_total_count

    num_answers['__total__'] = total

    return num_answers


# Public endpoints

app = Chalice(app_name='tribune-pollster')

@app.route('/polls/{poll_id}/questions/{question_id}/responses',
        methods=['POST', 'GET'])
def poll_responses(poll_id, question_id):
    request = app.current_request

    if request.method == 'POST':
        body = request.json_body
        user_id = body['user_id']
        value = body['value']
        return {
            'responses': [
                create_response(poll_id, question_id, user_id, value)
            ]
        }

    elif request.method == 'GET':
        answers = get_responses(poll_id, question_id)
        return {
            'responses': answers,
        }


@app.route('/polls/{poll_id}/questions/{question_id}/summary',
        methods=['GET'])
def poll_summary(poll_id, question_id):
    return {
        'poll_id': poll_id ,
        'question_id': question_id,
        'summary': get_response_summary(poll_id, question_id),
    }
