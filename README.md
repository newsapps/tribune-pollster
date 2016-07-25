tribune-pollster
================

A serverless API for storing user responses to poll questions.

Built with [Chalice](https://github.com/awslabs/chalice) to run on AWS Lambda and AWS API Gateway.

This should be considered alpha-quality software.  The API and implementation approach is not stable by any means.

Assumptions
-----------

* Amazon Web Services (AWS) account (AWS)
* AWS access keypair
* Python 2.7 (this is a requirement of Lambda)
* virtualenvwrapper

Installation
------------

Create a virtualenv:

    mkvirtualenv tribune-pollster

Clone the repository:

    git clone https://github.com/newsapps/tribune-pollster.git


Deployment
----------

Deployment is handled through the Chalice framework.

To reuse this outside of the Chicago Tribune, you'll likely have to create a Lambda function in the AWS console or through the AWS API and then edit `.chalice/config.json` to replace the `lambda_arn` value with the ARN of your function.

Then, deploy using the `chalice` command:

    chalice deploy

The current version uses AWS SimpleDB as the data store. This decision was made to avoid the complexity of deploying the `psycopg2` package on AWS Lambda.  In order to use SimpleDB, you'll need to create a SimpleDB "domain" named  `pollster-responses`.  You can do this with the `create_simpledb_domain.py` script:

    ./create_simpledb_domain.py


Public API
----------

### Create a response to a question

`POST /polls/<poll-id>/questions/<question-id>/responses` 

Required parameters:

* `poll_id`
* `question_id`
* `user_id`
* `value`

Example payload:

    {
        "user_id": "test",
        "value": "meh"
    }

Example request:

    curl -H "Content-Type: application/json" -X POST -d '{"user_id":"test","value":"lame"}' https://2dpij75av9.execute-api.us-east-1.amazonaws.com/dev/polls/lollapalooza-anniversary/questions/1991/responses

Example response:

    {"responses": [{"question_id": "1991", "user_id": "test", "value": "lame", "poll_id": "lollapalooza-anniversary", "answer_id": "499e628f-af11-4f5b-b0d5-b2b244bf7579"}]}


### Get all responses to a question

`GET /polls/<poll-id>/questions/<question-id>/responses` 

Required parameters:

* `poll_id`
* `question_id`

Example request:

    curl https://2dpij75av9.execute-api.us-east-1.amazonaws.com/dev/polls/lollapalooza-anniversary/questions/1991/responses

Example response:

    {"responses": [{"answer_id": "test-lollapalooza-anniversary-1991", "user_id": "test", "value": "lame", "poll_id": "lollapalooza-anniversary", "question_id": "1991"}, {"answer_id": "183b6640-e500-4c89-81b9-213d8ccaa4e4", "user_id": "test", "value": "lame", "poll_id": "lollapalooza-anniversary", "question_id": "1991"}, {"answer_id": "499e628f-af11-4f5b-b0d5-b2b244bf7579", "user_id": "test", "value": "lame", "poll_id": "lollapalooza-anniversary", "question_id": "1991"}]}

### Get a summary of responses to a question

`GET /polls/<poll-id>/questions/<question-id>/summary` 

Gets the number of responses, by response value. 

Required parameters:

* `poll_id`
* `question_id`

Example request:

    curl https://2dpus-east-1.amazonaws.com/dev/polls/lollapalooza-anniversary/questions/1991/summary

Example response:

    {"summary": {"__total__": 3, "lame": 3}, "poll_id": "lollapalooza-anniversary", "question_id": "1991"}


Authors
-------

* Geoff Hing <geoffhing@gmail.com> for the Chicago Tribune DataViz team

