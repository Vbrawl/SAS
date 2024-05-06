from typing import Callable, Coroutine, Any
from sas_commons import Database, Template
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
            db (Database): _description_
            host (str, optional): _description_. Defaults to "0.0.0.0".
            port (int, optional): _description_. Defaults to 8585.
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
                "get": ...,
                "add": ...,
                "alter": ...,
                "remove": ...
            },
            "rules": {
                "get": ...,
                "add": ...,
                "alter": ...,
                "remove": ...
            },
            "people_in_rule": {
                "get": ...,
                "link": ...,
                "unlink": ...
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
            message:str = kwargs["message"]
            if not isinstance(message, str): raise TypeError("Invalid MESSAGE parameter")


            template = Template(message)
            id = self.db.add_template(template)

            if id is None:
                raise RuntimeError("Unknown error, Template could not be added to the database")

            return {"id": id}
        except Exception:
            return {}
    
    async def template_alter(self, **kwargs) -> dict:
        try:
            id:int = kwargs["id"]
            if not isinstance(id, int): raise TypeError("Invalid ID parameter")

            message:str = kwargs["message"]
            if not isinstance(message, str): raise TypeError("Invalid MESSAGE parameter")

            template = Template(message)
            self.db.alter_template(template, id)

            return {"status": "success"}
        except Exception:
            return {}
    
    async def template_remove(self, **kwargs) -> dict:
        try:
            id:int = kwargs["id"]
            if not isinstance(id, int): raise TypeError("Invalid ID parameter")

            self.db.delete_template(id)
            return {"status": "success"}
        except Exception as err:
            print(err)
            return {}
        
        return {}





if __name__ == "__main__":
    async def main():
        wsapi = WSAPI(Database("../temp.db"))
        await wsapi.start_server()
        await asyncio.sleep(math.inf)
    asyncio.run(main())