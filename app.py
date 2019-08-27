# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import logging

from flask import request, Flask

from api.datatypes import CreatePersonRequest, CreatePersonResponse

SERVICE_PORT = 8888

app = Flask(__name__)


OPERATION_CREATE_PERSON: str = 'create-person'
@app.route(f'/{OPERATION_CREATE_PERSON}', methods=['POST'])
def create_person():
    payload = request.get_json()
    logging.info(f"Incoming payload for {OPERATION_CREATE_PERSON}: {payload}")

    person = CreatePersonRequest.from_json(payload)
    logging.info(f'Creating person {person}')

    response = CreatePersonResponse(person_id=1234)

    return response.to_json()


if __name__ == '__main__':
    app.run(debug=True, port=SERVICE_PORT, host='0.0.0.0')


