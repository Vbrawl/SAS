'''
Copyright 2024 Jim Konstantos <konstantosjim@gmail.com>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
from __future__ import annotations
from typing import Any
from .TemplateArguments import TemplateArguments




class PersonTemplateArguments(TemplateArguments):
    def __init__(self, *, telephone:str, id:int|None = None, first_name:str|None = None, last_name:str|None = None, address:str|None = None, **kwargs):
        self.__dict__.update(kwargs)
        self.telephone = telephone
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.address = address
    
    @classmethod
    def fromJSON(cls:type[PersonTemplateArguments], data:dict[str, Any]) -> PersonTemplateArguments:
        return cls(
            id = data.get("id", None),
            first_name = data.get("first_name", None),
            last_name = data.get("last_name", None),
            telephone = data["telephone"],
            address = data.get("address", None)
        )