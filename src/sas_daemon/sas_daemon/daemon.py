from sas_commons import Database, SendMessageRule, PersonTemplateArguments
from wsAPI.server import WSAPI
import asyncio
import math



class Daemon:
    def __init__(self):
        self.db = Database("temp.db")
        self.operations:dict[int, asyncio.Task] = {}
        self.op_lock = asyncio.Lock()

        self.wsapi = WSAPI(self.db)
        self.wsapi.OPTIONS["rule"]["add"] = self.rule_add_and_register # type: ignore
        self.wsapi.OPTIONS["rule"]["alter"] = self.rule_alter_and_register # type: ignore
        self.wsapi.OPTIONS["rule"]["remove"] = self.rule_deregister_and_remove # type: ignore

    async def rule_add_and_register(self, wsapi:WSAPI, **kwargs):
        res = await wsapi.rule_add(**kwargs)
        if "id" in res:
            id:int = res["id"]
            rule:SendMessageRule = self.db.get_rule(id) # type: ignore
            async with self.op_lock:
                self.operations[id] = asyncio.create_task(rule.infschedule(self.send_sms))
        return res

    async def rule_alter_and_register(self, wsapi:WSAPI, **kwargs):
        res = await wsapi.rule_alter(**kwargs)
        if "status" in res and res["status"] == "success":
            id:int = kwargs["id"]
            rule:SendMessageRule = self.db.get_rule(id) # type: ignore

            async with self.op_lock:
                if id in self.operations.keys():
                    self.operations[id].cancel()
                if rule is None:
                    del self.operations[id]
                else:
                    self.operations[id] = asyncio.create_task(rule.infschedule(self.send_sms))
        return res
    
    async def rule_deregister_and_remove(self, wsapi:WSAPI, **kwargs):
        id = kwargs.get("id", None)
        if isinstance(id, int):
            async with self.op_lock:
                if id in self.operations.keys():
                    self.operations[id].cancel()
                    del self.operations[id]
        return await wsapi.rule_remove(**kwargs)

    async def send_sms(self, pta:PersonTemplateArguments, message:str): # callback
        print(message)

    async def start(self):
        for rule in self.db.get_rules():
            if rule.id is not None:
                self.operations[rule.id] = asyncio.create_task(rule.infschedule(self.send_sms))
        await self.wsapi.start_server()
        await asyncio.sleep(math.inf)