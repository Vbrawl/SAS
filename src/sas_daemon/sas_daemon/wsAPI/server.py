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
from typing import Callable, Coroutine, Any
from ..database import Database
from ..security import Security, User
from ..templates import Template, PersonTemplateArguments
from ..rules import SendMessageRule
from .. import Constants
from . import parsers
import json
import websockets
import logging

logger = logging.getLogger("sas.daemon.wsapi")


class WSAPI:
    def __init__(self, db:Database, security:Security, host:str = "0.0.0.0", port:int = 8585):
        """WebSocket API

        To use this WS API send a JSON object:
        {
            "id": "whatever value you want",
            "username": "Username",
            "password": "Password",
            "action": [...],
            "parameters": {...}
        }

        Where "action" is a list with identifiers (found in OPTIONS), it's basically a path to the endpoint.
        "parameters" is a dictionary with parameter-value pairs.

        Args:
            db (Database): The database object to use.
            host (str, optional): The address to use to serve the server. Defaults to "0.0.0.0".
            port (int, optional): The port number to use for the server. Defaults to 8585.
        """
        self.db = db
        self.security = security
        self.host = host
        self.port = port
        self.OPTIONS:dict[str, dict|Callable] = {
        "template": {
            "get": WSAPI.template_get,
            "add": WSAPI.template_add,
            "alter": WSAPI.template_alter,
            "remove": WSAPI.template_remove
        },
        "people": {
            "get": WSAPI.people_get,
            "add": WSAPI.people_add,
            "alter": WSAPI.people_alter,
            "remove": WSAPI.people_remove
        },
        "rule": {
            "get": WSAPI.rule_get,
            "add": WSAPI.rule_add,
            "alter": WSAPI.rule_alter,
            "remove": WSAPI.rule_remove
        },
        "users": {
            "login": WSAPI.report_login,
            "alter": WSAPI.user_alter
        },
        "timezone": {
            "get": WSAPI.timezone_get,
            "alter": WSAPI.ignore, # needs "timezone" parameter
        },
        "sms-api-key": {
            "get": WSAPI.sms_api_key_get,
            "alter": WSAPI.ignore # needs "api-key" parameter
        },
        "telephone": {
            "get": WSAPI.telephone_get,
            "alter": WSAPI.ignore # needs "telephone" parameter
        }
    }
    
    async def start_server(self):
        await websockets.serve(ws_handler=self.handle, host=self.host, port=self.port)
        logger.info("Websocket API initialized: ws://%s:%s", self.host, self.port)
    
    def navigate_options(self, current_user:User, message_parts:list[str], kwargs:dict[str, Any]) -> Coroutine[Any, Any, dict]|None:
        # Navigate to the correct endpoint
        nav:dict[str, dict|Callable]|Callable[[Any], Coroutine[Any, Any, dict]] = self.OPTIONS
        try:
            for part in message_parts:
                nav = nav[part] # type: ignore
            return nav(self, current_user, **kwargs) # type: ignore
        except Exception:
            return None

    async def handle(self, ws:websockets.WebSocketServerProtocol):
        message:str

        try:
            remote_host = ws.remote_address[0]
        except Exception:
            remote_host = 'UnknownIP'

        async for message in ws: # type: ignore
            try:
                packet = json.loads(message)
                user = self.security.login(packet["username"], packet["password"], remote_host)
                if user is not None:
                    task = self.navigate_options(user, packet["action"], packet["parameters"])
                    res = await task # type: ignore
                else:
                    res = {}
                res["id"] = packet["id"]
                res = json.dumps(res)
                await ws.send(res)
            except Exception:
                logger.error("%s - %s", remote_host, json.dumps(packet), exc_info=True)
                continue

    
    async def template_get(self, current_user:User, **kwargs) -> dict:
        try:
            # get ID
            id:int|None = kwargs.get("id", None)
            if not isinstance(id, (int, type(None))): raise TypeError("Invalid ID parameter")

            # get LIMIT
            limit:int|None = kwargs.get("limit", None)
            if not isinstance(limit, (int, type(None))): raise TypeError("Invalid LIMIT parameter")

            # get OFFSET
            offset:int|None = kwargs.get("offset", None)
            if not isinstance(offset, (int, type(None))): raise TypeError("Invalid OFFSET parameter")

            # Fetch a single template or multiple templates
            results:list[Template] = []
            if id is not None:
                res = self.db.get_template(id)
                if res is not None:
                    results.append(res)
            else:
                results = self.db.get_templates(limit, offset)

            return {
                "results": list(map(
                    lambda x: x.toJSON(),
                    results))
            }
        except Exception:
            return {}
    
    async def template_add(self, current_user:User, **kwargs) -> dict:
        try:
            template = parsers.parse_as_template(kwargs)
            id = self.db.add_template(template)

            if id is None:
                raise RuntimeError("Unknown error, Template could not be added to the database")

            return {"added_id": id}
        except Exception:
            return {}
    
    async def template_alter(self, current_user:User, **kwargs) -> dict:
        try:
            template = parsers.parse_as_template(kwargs, True)
            self.db.alter_template(template)

            return {"status": "success"}
        except Exception:
            return {}
    
    async def template_remove(self, current_user:User, **kwargs) -> dict:
        try:
            id:int = kwargs["id"]
            if not isinstance(id, int): raise TypeError("Invalid ID parameter")

            self.db.delete_template(id)
            return {"status": "success"}
        except Exception:
            return {}
    

    async def people_get(self, current_user:User, **kwargs) -> dict:
        try:
            # get ID
            id:int|None = kwargs.get("id", None)
            if not isinstance(id, (int, type(None))): raise TypeError("Invalid ID parameter")

            # get LIMIT
            limit:int|None = kwargs.get("limit", None)
            if not isinstance(limit, (int, type(None))): raise TypeError("Invalid LIMIT parameter")

            # get OFFSET
            offset:int|None = kwargs.get("offset", None)
            if not isinstance(offset, (int, type(None))): raise TypeError("Invalid OFFSET parameter")

            # Fetch a single template or multiple templates
            results:list[PersonTemplateArguments] = []
            if id is not None:
                res = self.db.get_person(id)
                if res is not None:
                    results.append(res)
            else:
                results = self.db.get_people(limit, offset)
            
            return {
                "results": list(map(
                    lambda x: x.toJSON(),
                    results))
            }
        except Exception:
            return {}

    async def people_add(self, current_user:User, **kwargs) -> dict:
        try:
            person = parsers.parse_as_person(kwargs)
            id = self.db.add_person(person)

            return {"added_id": id}
        except Exception:
            return {}

    async def people_alter(self, current_user:User, **kwargs) -> dict:
        try:
            person = parsers.parse_as_person(kwargs, True)
            self.db.alter_person(person=person)
            
            return {"status": "success"}
        except Exception:
            return {}

    async def people_remove(self, current_user:User, **kwargs) -> dict:
        try:
            id:int = kwargs["id"]
            if not isinstance(id, int): raise TypeError("Invalid ID parameter")

            self.db.delete_person(id)
            return {"status": "success"}
        except Exception:
            return {}
        


    async def rule_get(self, current_user:User, **kwargs) -> dict:
        try:
            # get ID
            id:int|None = kwargs.get("id", None)
            if not isinstance(id, (int, type(None))): raise TypeError("Invalid ID parameter")

            # get LIMIT
            limit:int|None = kwargs.get("limit", None)
            if not isinstance(limit, (int, type(None))): raise TypeError("Invalid LIMIT parameter")

            # get OFFSET
            offset:int|None = kwargs.get("offset", None)
            if not isinstance(offset, (int, type(None))): raise TypeError("Invalid OFFSET parameter")

            # Fetch a single template or multiple templates
            results:list[SendMessageRule] = []
            if id is not None:
                res = self.db.get_rule(id)
                if res is not None:
                    results.append(res)
            else:
                results = self.db.get_rules(limit, offset)

            return {
                "results": list(map(
                    lambda x: x.toJSON(),
                    results))
            }
        except Exception:
            return {}
    
    async def rule_add(self, current_user:User, **kwargs) -> dict:
        try:
            rule = parsers.parse_as_rule(self.db, kwargs)
            id = self.db.add_rule(rule)

            return {"added_id": id}
        except Exception:
            return {}
    
    async def rule_alter(self, current_user:User, **kwargs) -> dict:
        try:
            rule = parsers.parse_as_rule(self.db, kwargs, True)
            self.db.alter_rule(rule)
            
            return {"status": "success"}
        except Exception:
            return {}

    async def rule_remove(self, current_user:User, **kwargs) -> dict:
        try:
            id:int = kwargs["id"]
            if not isinstance(id, int): raise TypeError("Invalid ID parameter")

            self.db.delete_rule(id)
            return {"status": "success"}
        except Exception:
            return {}

    async def report_login(self, current_user:User, **kwargs) -> dict:
        try:
            return {"status": "success"}
        except Exception:
            return {}
    
    async def user_alter(self, current_user:User, **kwargs) -> dict:
        try:
            new_username = kwargs["new_username"]
            new_password = kwargs["new_password"]
            
            current_user.username = new_username
            self.security.set_password(current_user, new_password)

            self.db.alter_user(current_user)
            return {"status": "success"}
        except Exception:
            return {}
    
    async def timezone_get(self, current_user:User, **kwargs):
        try:
            tz = self.db.get_setting(Constants.DATABASE_TIMEZONE_SETTING)
            if tz:
                return {"timezone": tz}
            else:
                return {}
        except Exception:
            return {}
    
    async def sms_api_key_get(self, current_user:User, **kwargs):
        try:
            apikey = self.db.get_setting(Constants.DATABASE_APIKEY_SETTING)
            return {"api-key": apikey}
        except Exception:
            return {}
    
    async def telephone_get(self, current_user:User, **kwargs):
        try:
            telephone = self.db.get_setting(Constants.DATABASE_TELEPHONE_SETTING)
            return {"telephone": telephone}
        except Exception:
            return {}
    
    async def ignore(self, current_user:User, **kwargs) -> dict:
        return {}