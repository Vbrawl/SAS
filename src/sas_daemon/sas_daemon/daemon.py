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
from .database import Database
from .rules import SendMessageRule
from .datetimezone import datetimezone
from .security import Security, User
import pytz
from . import Constants
from .wsAPI.server import WSAPI
from .api import TelnyxAPI
import asyncio



class Daemon:
    def __init__(self):
        self.collect_rules_interval = Constants.COLLECT_RULES_INTERVAL

        self.db = Database(Constants.DATABASE_FILE)
        self.security = Security(self.db, Constants.PASSWORD_TIME_COST, Constants.PASSWORD_MEMORY_COST, Constants.PASSWORD_PARALLELISM)
        self.sms_gateway:TelnyxAPI|None = None
        self.operations:dict[int, asyncio.Task] = {}
        self.op_lock = asyncio.Lock()

        self.wsapi = WSAPI(self.db, self.security, Constants.API_ADDRESS, Constants.API_PORT)
        # Update when a rule is updated, their attributes are automatically updated before sending.
        self.wsapi.OPTIONS["rule"]["add"] = self.rule_add_and_register # type: ignore
        self.wsapi.OPTIONS["rule"]["alter"] = self.rule_alter_and_register # type: ignore
        self.wsapi.OPTIONS["rule"]["remove"] = self.rule_deregister_and_remove # type: ignore
        self.wsapi.OPTIONS["timezone"]["alter"] = self.update_timezone # type: ignore



    async def update_timezone(self, wsapi:WSAPI, current_user:User, **kwargs):
        try:
            datetimezone.set_tz(pytz.timezone(kwargs["timezone"]))
            self.db.set_setting("timezone", kwargs["timezone"])
            async with self.op_lock:
                all_ids = set(self.operations.keys())
                for id in all_ids:
                    self.operations[id].cancel()
                    rule = self.db.get_rule(id)
                    if rule is None:
                        del self.operations[id]
                    else:
                        self.operations[id] = asyncio.create_task(rule.infschedule(self.send_sms, self.update_rule_last_executed))
            return {"status": "success"}
        except Exception:
            return {}

    async def rule_add_and_register(self, wsapi:WSAPI, current_user:User, **kwargs):
        res = await wsapi.rule_add(current_user, **kwargs)
        if "added_id" in res:
            id:int = res["added_id"]
            rule:SendMessageRule = self.db.get_rule(id) # type: ignore
            async with self.op_lock:
                self.operations[id] = asyncio.create_task(rule.infschedule(self.send_sms, self.update_rule_last_executed))
        return res

    async def rule_alter_and_register(self, wsapi:WSAPI, current_user:User, **kwargs):
        res = await wsapi.rule_alter(current_user, **kwargs)
        if "status" in res and res["status"] == "success":
            id:int = kwargs["id"]
            rule:SendMessageRule = self.db.get_rule(id) # type: ignore

            async with self.op_lock:
                if id in self.operations.keys():
                    self.operations[id].cancel()
                if rule is None:
                    del self.operations[id]
                else:
                    self.operations[id] = asyncio.create_task(rule.infschedule(self.send_sms, self.update_rule_last_executed))
        return res
    
    async def rule_deregister_and_remove(self, wsapi:WSAPI, current_user:User, **kwargs):
        id = kwargs.get("id", None)
        if isinstance(id, int):
            async with self.op_lock:
                if id in self.operations.keys():
                    self.operations[id].cancel()
                    del self.operations[id]
        return await wsapi.rule_remove(current_user, **kwargs)

    async def send_sms(self, pta:SendMessageRule): # callback
        template = pta.template
        if pta.template.id is not None:
            temp = self.db.get_template(pta.template.id)
            if temp is not None:
                template = temp

        for recipient in pta.recipients:
            if recipient.id is not None:
                temp = self.db.get_person(recipient.id)
                if temp is not None:
                    recipient = temp
            msg = template.compileFor(recipient)
            if self.sms_gateway:
                self.sms_gateway.sendSMS(recipient.telephone.replace(' ', ''), msg)
    
    async def update_rule_last_executed(self, rule:SendMessageRule):
        self.db.alter_rule(rule)
    
    async def collect_rules_indefinitely(self):
        while True:
            async with self.op_lock:
                keys_to_remove = []
                for k,v in self.operations.items():
                    if v.done():
                        keys_to_remove.append(k)
                
                for k in keys_to_remove:
                    del self.operations[k]
            await asyncio.sleep(self.collect_rules_interval)

    async def start(self):
        api_key = self.db.get_setting(Constants.DATABASE_APIKEY_SETTING)
        telephone = self.db.get_setting(Constants.DATABASE_TELEPHONE_SETTING)
        if api_key is not None and telephone is not None:
            self.sms_gateway = TelnyxAPI(api_key, telephone)

        timezone = self.db.get_setting(Constants.DATABASE_TELEPHONE_SETTING)
        if timezone:
            datetimezone.set_tz(pytz.timezone(timezone))
        for rule in self.db.get_rules():
            if rule.id is not None:
                self.operations[rule.id] = asyncio.create_task(rule.infschedule(self.send_sms, self.update_rule_last_executed))

        await self.wsapi.start_server()
        await self.collect_rules_indefinitely()