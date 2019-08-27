# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from typing import Any

import requests

from api.datatypes import CreatePersonRequest, Person, CreatePersonResponse
from app import OPERATION_CREATE_PERSON, SERVICE_PORT


def test_get_dubbing_job_status_local():
    response = _send_request(secure=False,
                             host='localhost',
                             service_port=SERVICE_PORT,
                             operation=OPERATION_CREATE_PERSON,
                             request=CreatePersonRequest(Person(name='Jane Doe', age='40')))

    response_obj = CreatePersonResponse.from_json(response)

    assert response_obj.person_id is not None


def test_get_dubbing_job_status_API():
    response = _send_request(secure=True,
                             host='<<yourapi>>..execute-api.us-east-1.amazonaws.com',
                             service_port=80,
                             path='sample-generated-api',
                             operation=OPERATION_CREATE_PERSON,
                             request=CreatePersonRequest(Person(name='Jane Doe', age='40')),
                             api_key='<<yourapikey>>')

    response_obj = CreatePersonResponse.from_json(response)

    assert response_obj.person_id is not None


def _send_request(secure: bool, host: str, service_port, path: str, operation: str, request:Any, api_key=None) -> str:
    base_url = f'{"https" if secure else "http"}://{host}:{service_port}/{path}'

    response = requests.post(f'{base_url}/{operation}', headers={'x-api-key': api_key}, json=request.to_json())
    print("Response is: {}".format(response.text))
    return response.text

