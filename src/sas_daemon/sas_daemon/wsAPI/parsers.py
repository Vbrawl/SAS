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
from datetime import datetime, timedelta




def parse_as_template(kwargs:dict[str, Any], id_required:bool = False) -> Template:
    id = kwargs.get("id", None)
    if id_required and id is None:
        raise TypeError("ID Required for object creation but is not present in the data")
    elif not isinstance(id, (int, type(None))):
        raise TypeError("Invalid ID parameter")
    message = kwargs["message"]
    if not isinstance(message, str):
        raise TypeError("Invalid MESSAGE parameter")
    return Template(id=id, message=message)
    
def parse_as_person(kwargs:dict[str, Any], id_required:bool = False) -> PersonTemplateArguments:
    id = kwargs.get("id", None)
    if id_required and id is None:
        raise TypeError("ID Required for object creation but is not present in the data")
    elif not isinstance(id, (int, type(None))):
        raise TypeError("Invalid ID parameter")

    first_name:str|None = kwargs.get("first_name", None)
    if not isinstance(first_name, (str, type(None))): raise TypeError("Invalid FIRST_NAME parameter")

    last_name:str|None = kwargs.get("last_name", None)
    if not isinstance(last_name, (str, type(None))): raise TypeError("Invalid LAST_NAME parameter")

    telephone:str = kwargs["telephone"]
    if not isinstance(telephone, str): raise TypeError("Invalid TELEPHONE parameter")

    address:str|None = kwargs.get("address", None)
    if not isinstance(address, (str, type(None))): raise TypeError("Invalid ADDRESS parameter")

    return PersonTemplateArguments(
        id=id,
        first_name=first_name,
        last_name=last_name,
        telephone=telephone,
        address=address
    )

def parse_as_rule(db:Database, kwargs:dict[str, Any], id_required:bool = False) -> SendMessageRule:
    id:int|None = kwargs.get("id", None)
    if id_required and id is None:
        raise TypeError("ID Required for object creation but is not present in the data")
    elif not isinstance(id, (int, type(None))):
        raise TypeError("Invalid ID parameter")
        
    recipientIds:list[int] = kwargs.get("recipients", [])
    if not isinstance(recipientIds, list): raise TypeError("Invalid RECIPIENTS parameter")
    recipients:list[PersonTemplateArguments] = list(map(lambda x: db.get_person(x), recipientIds)) # type: ignore
    if any(map(lambda x: x is None, recipients)): raise TypeError("Invalid RECIPIENTS parameter values")

    templateId:int = kwargs["template"]
    if not isinstance(templateId, int): raise TypeError("Invalid TEMPLATE parameter")
    template = db.get_template(templateId)
    if template is None: raise TypeError("Invalid TEMPLATE parameter value")

    start_date = datetime.strptime(kwargs["start_date"], "%Y-%m-%d %H:%M:%S.%f")
    end_date_p = kwargs.get("end_date", None)
    if not isinstance(end_date_p, (str, type(None))): raise TypeError("Invalid END_DATE parameter")
    elif end_date_p is not None: end_date = datetime.strptime(end_date_p, "%Y-%m-%d %H:%M:%S.%f")
    else: end_date = None

    interval_days = kwargs.get("interval_days", 0)
    interval_seconds = kwargs.get("interval_seconds", 0)
    if not isinstance(interval_days, int): raise TypeError("Invalid INTERVAL_DAYS parameter")
    if not isinstance(interval_seconds, int): raise TypeError("Invalid INTERVAL_SECONDS parameter")
    interval = timedelta(days=interval_days, seconds=interval_seconds)

    last_executed_p = kwargs.get("last_executed", None)
    if not isinstance(last_executed_p, (str, type(None))): raise TypeError("Invalid LAST_EXECUTED parameter")
    if last_executed_p is not None: last_executed = datetime.strptime(last_executed_p, "%Y-%m-%d %H:%M:%S.%f")
    else: last_executed = None


    return SendMessageRule(
        recipients = recipients,
        template = template,
        start_date = start_date,
        end_date = end_date,
        interval = interval,
        last_executed = last_executed,
        id = id
    )