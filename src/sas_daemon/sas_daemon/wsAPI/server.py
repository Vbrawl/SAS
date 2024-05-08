from typing import Callable, Coroutine, Any
from sas_commons import Database, Template, PersonTemplateArguments, SendMessageRule
from datetime import datetime, timedelta
import json
import asyncio
import websockets
import math



class WSAPI:
    def __init__(self, db:Database, host:str = "0.0.0.0", port:int = 8585):
        """WebSocket API

        To use this WS API send a JSON object:
        {
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
        self.host = host
        self.port = port
    
    async def start_server(self):
        await websockets.serve(ws_handler=self.handle, host=self.host, port=self.port)
    
    def navigate_options(self, message_parts:list[str], kwargs:dict[str, Any]) -> Coroutine[Any, Any, dict]|None:
        OPTIONS:dict[str, dict|Callable] = {
            "template": {
                "get": self.template_get,
                "add": self.template_add,
                "alter": self.template_alter,
                "remove": self.template_remove
            },
            "people": {
                "get": self.people_get,
                "add": self.people_add,
                "alter": self.people_alter,
                "remove": self.people_remove
            },
            "rule": {
                "get": self.rule_get,
                "add": self.rule_add,
                "alter": self.rule_alter,
                "remove": self.rule_remove
            },
            "people_in_rule": {
                "link": self.people_in_rule_link,
                "unlink": self.people_in_rule_unlink
            }
        }

        # Navigate to the correct endpoint
        nav:dict[str, dict|Callable]|Callable[[Any], Coroutine[Any, Any, dict]] = OPTIONS
        try:
            for part in message_parts:
                nav = nav[part] # type: ignore
            return nav(**kwargs) # type: ignore
        except Exception:
            return None

    async def handle(self, ws:websockets.WebSocketServerProtocol):
        message:str
        async for message in ws: # type: ignore
            try:
                packet = json.loads(message)
                print(packet)
                task = self.navigate_options(packet["action"], packet["parameters"])
                res = json.dumps(await task) # type: ignore
                print(res)
                await ws.send(res)
            except Exception as err:
                print(err)
                continue
    

    def parse_as_template(self, kwargs:dict[str, Any], id_required:bool = False) -> Template:
        id = kwargs.get("id", None)
        if id_required and id is None:
            raise TypeError("ID Required for object creation but is not present in the data")
        elif not isinstance(id, (int, type(None))):
            raise TypeError("Invalid ID parameter")
        message = kwargs["message"]
        if not isinstance(message, str):
            raise TypeError("Invalid MESSAGE parameter")
        return Template(id=id, message=message)
    
    def parse_as_person(self, kwargs:dict[str, Any], id_required:bool = False) -> PersonTemplateArguments:
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
    
    def parse_as_rule(self, kwargs:dict[str, Any], id_required:bool = False) -> SendMessageRule:
        id:int|None = kwargs.get("id", None)
        if id_required and id is None:
            raise TypeError("ID Required for object creation but is not present in the data")
        elif not isinstance(id, (int, type(None))):
            raise TypeError("Invalid ID parameter")
        
        recipientIds:list[int] = kwargs.get("recipients", [])
        if not isinstance(recipientIds, list): raise TypeError("Invalid RECIPIENTS parameter")
        recipients:list[PersonTemplateArguments] = list(map(lambda x: self.db.get_person(x), recipientIds)) # type: ignore
        if any(map(lambda x: x is None, recipients)): raise TypeError("Invalid RECIPIENTS parameter values")

        templateId:int = kwargs["template"]
        if not isinstance(templateId, int): raise TypeError("Invalid TEMPLATE parameter")
        template = self.db.get_template(templateId)
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

    
    async def template_get(self, **kwargs) -> dict:
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
                    lambda x: {
                        "id": x.id,
                        "message": x._message
                    },
                    results))
            }
        except Exception:
            return {}
    
    async def template_add(self, **kwargs) -> dict:
        try:
            template = self.parse_as_template(kwargs)
            id = self.db.add_template(template)

            if id is None:
                raise RuntimeError("Unknown error, Template could not be added to the database")

            return {"id": id}
        except Exception:
            return {}
    
    async def template_alter(self, **kwargs) -> dict:
        try:
            template = self.parse_as_template(kwargs, True)
            self.db.alter_template(template)

            return {"status": "success"}
        except Exception:
            return {}
    
    async def template_remove(self, **kwargs) -> dict:
        try:
            id:int = kwargs["id"]
            if not isinstance(id, int): raise TypeError("Invalid ID parameter")

            self.db.delete_template(id)
            return {"status": "success"}
        except Exception:
            return {}
    

    async def people_get(self, **kwargs) -> dict:
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
                "status": list(map(
                    lambda x: {
                        "id": getattr(x, "id", None),
                        "first_name": getattr(x, "first_name", None),
                        "last_name": getattr(x, "last_name", None),
                        "telephone": x.telephone,
                        "address": getattr(x, "address", None)
                    },
                    results))
            }
        except Exception:
            return {}

    async def people_add(self, **kwargs) -> dict:
        try:
            person = self.parse_as_person(kwargs)
            id = self.db.add_person(person)

            return {"id": id}
        except Exception:
            return {}

    async def people_alter(self, **kwargs) -> dict:
        try:
            person = self.parse_as_person(kwargs, True)
            self.db.alter_person(person=person)
            
            return {"status": "success"}
        except Exception:
            return {}

    async def people_remove(self, **kwargs) -> dict:
        try:
            id:int = kwargs["id"]
            if not isinstance(id, int): raise TypeError("Invalid ID parameter")

            self.db.delete_person(id)
            return {"status": "success"}
        except Exception:
            return {}
        


    async def rule_get(self, **kwargs) -> dict:
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
                    lambda x: {
                        "id": x.id,
                        "recipients": x.recipients,
                        "template": x.template,
                        "start_date": x._start_date,
                        "end_date": x._end_date,
                        "interval": x._interval,
                        "last_executed": x._last_executed
                    },
                    results))
            }
        except Exception:
            return {}
    
    async def rule_add(self, **kwargs) -> dict:
        try:
            rule = self.parse_as_rule(kwargs)
            id = self.db.add_rule(rule)

            return {"id": id}
        except Exception:
            return {}
    
    async def rule_alter(self, **kwargs) -> dict:
        try:
            rule = self.parse_as_rule(kwargs, True)
            self.db.alter_rule(rule)
            
            return {"status": "success"}
        except Exception:
            return {}

    async def rule_remove(self, **kwargs) -> dict:
        try:
            id:int = kwargs["id"]
            if not isinstance(id, int): raise TypeError("Invalid ID parameter")

            self.db.delete_rule(id)
            return {"status": "success"}
        except Exception:
            return {}

    async def people_in_rule_link(self, **kwargs) -> dict:
        try:
            # get PersonID
            personId:int|None = kwargs["personId"]
            if not isinstance(personId, int): raise TypeError("Invalid PERSONID parameter")
            
            # get RuleID
            ruleId:int = kwargs["ruleId"]
            if not isinstance(ruleId, int): raise TypeError("Invalid RULEID parameter")

            # Link
            self.db.link_recipient(personId, ruleId)
            return {"status": "success"}
        except Exception:
            return {}
    
    async def people_in_rule_unlink(self, **kwargs) -> dict:
        try:
            # get PersonID
            personId:int|None = kwargs.get("personId", None)
            if not isinstance(personId, (int, type(None))): raise TypeError("Invalid PERSONID parameter")
            
            # get RuleID
            ruleId:int = kwargs["ruleId"]
            if not isinstance(ruleId, int): raise TypeError("Invalid RULEID parameter")

            # Link
            if personId is None:
                self.db.unlink_all_recipients_from_rule(ruleId)
            else:
                self.db.unlink_recipient(personId, ruleId)
            return {"status": "success"}
        except Exception:
            return {}






if __name__ == "__main__":
    async def main():
        wsapi = WSAPI(Database("../temp.db"))
        await wsapi.start_server()
        await asyncio.sleep(math.inf)
    asyncio.run(main())