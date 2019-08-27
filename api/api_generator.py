# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import argparse
import json
import logging
import os

import boto3
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from api.datatypes import CreatePersonRequest, CreatePersonResponse
from app import OPERATION_CREATE_PERSON

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(os.path.basename(__file__))


def find_api_id(api_gateway_client, api_name):
    """
    :param api_gateway_client: the client to use
    :param api_name: the API to find
    :return: the API ID of a unique API name; raises an error if there none or too many APIs with that name
    """
    # Do use a paginator if you have a large number of APIs within the same region:
    #   https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/apigateway.html#APIGateway.Paginator.GetRestApis

    apis = api_gateway_client.get_rest_apis()

    if apis['ResponseMetadata']['HTTPStatusCode'] != 200:
        return None

    api_ids = list(filter(lambda api: api['name'] == api_name, apis['items']))

    if len(api_ids) > 1:
        raise RuntimeError(f'Too many APIs with the same name: {api_name}')
    elif len(api_ids) == 0:
        raise RuntimeError(f'No API with the name: {api_name}')

    return api_ids[0]['id']


def generate_open_api_definition(update: bool):
    api_name = "sample-generated-api"
    spec = APISpec(
        title=api_name,
        version="1.0.0",
        openapi_version="3.0.2",
        info=dict(description="Sample Generated API from Python code"),
        plugins=[MarshmallowPlugin()]
    )

    spec.components.security_scheme("api_key", {
        "type": "apiKey",
        "name": "x-api-key",
        "in": "header"
    })

    ################
    generate_operation(path=OPERATION_CREATE_PERSON,
                       request_schema=CreatePersonRequest.schema(),
                       request_schema_name=CreatePersonRequest.__name__,
                       response_schema=CreatePersonResponse.schema(),
                       response_schema_name=CreatePersonResponse.__name__,
                       spec=spec,
                       ecs_host='http://myecshost-1234567890.us-east-1.elb.amazonaws.com')

    spec_dict = spec.to_dict()

    api_definition = json.dumps(spec_dict, indent=2)

    logger.info(f'API definition:\n{api_definition}')

    api_gateway_client = boto3.client('apigateway')

    if not update:
        logger.info(f'Creating API: {api_name}')
        api_gateway_client.import_rest_api( body=api_definition )
    else:
        logger.info(f'Updating API: {api_name}')
        api_gateway_client.put_rest_api(body=api_definition, mode='merge', restApiId=find_api_id(api_gateway_client, api_name))


def generate_operation(path, request_schema, request_schema_name, response_schema, response_schema_name, spec, ecs_host):
    spec.components.schema(request_schema_name, schema=request_schema)
    spec.components.schema(response_schema_name, schema=response_schema)
    spec.path(
        path=f"/{path}",
        operations=dict(
            post={
                "x-amazon-apigateway-auth": {
                    "type": "NONE"
                },
                "requestBody": {"content": {"application/json": {"schema": request_schema}}},
                "responses": {"200": {"description": 'the response', "content": {"application/json": {"schema": response_schema}}}},
                "security": [{"api_key": []}],

                # Documented in https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-swagger-extensions-integration.html
                "x-amazon-apigateway-integration": {
                    "passthroughBehavior": "when_no_match",
                    "type": "http_proxy",
                    "httpMethod": "POST",
                    "uri": f"{ecs_host}/{path}"
                }
            }
        )
    )


if __name__ == '__main__':
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument('--update', default=False, action='store_true', help='validates the command line parameters and shows a summary of them')

    ARGS = PARSER.parse_args()
    generate_open_api_definition(update=ARGS.update)
