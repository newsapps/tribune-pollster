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


Authors
-------

* Geoff Hing <geoffhing@gmail.com> for the Chicago Tribune DataViz team

