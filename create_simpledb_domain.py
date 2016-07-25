#!/usr/bin/env python

import boto3

if __name__ == "__main__":
    client = boto3.client('sdb')
    client.create_domain(
        DomainName='pollster-responses'
    )
