# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from dataclasses import dataclass

from dataclasses_json import dataclass_json


@dataclass
@dataclass_json
class Person:
  name: str
  age: int


@dataclass
@dataclass_json
class CreatePersonRequest:
  person: Person


@dataclass
@dataclass_json
class CreatePersonResponse:
  person_id: int

