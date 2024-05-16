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
from typing import Any
from ..templates import Template, PersonTemplateArguments
from ..rules import SendMessageRule
from ..database import Database




def parse_as_template(kwargs:dict[str, Any], id_required:bool = False) -> Template:
    id = kwargs.get("id", None)
    if id_required and id is None:
        raise TypeError("ID Required for object creation but is not present in the data")
    
    return Template.fromJSON(kwargs)
    
def parse_as_person(kwargs:dict[str, Any], id_required:bool = False) -> PersonTemplateArguments:
    id = kwargs.get("id", None)
    if id_required and id is None:
        raise TypeError("ID Required for object creation but is not present in the data")
    
    return PersonTemplateArguments.fromJSON(kwargs)

def parse_as_rule(db:Database, kwargs:dict[str, Any], id_required:bool = False) -> SendMessageRule:
    id:int|None = kwargs.get("id", None)
    if id_required and id is None:
        raise TypeError("ID Required for object creation but is not present in the data")
        
    return SendMessageRule.fromJSON(kwargs, db)