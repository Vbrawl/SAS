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

from sas_commons import SendMessageRule
from datetime import timedelta
import asyncio




class SMSSender:
    def __init__(self):
        self.rules:list[SendMessageRule] = []
        self.rules_lock = asyncio.Lock()
        self.idle_interval = 1

    async def __find_rule_index(self, ruleId:int, auto_lock:bool = True) -> int:
        if auto_lock:
            await self.rules_lock.acquire()
        index = -1
        for i, rule in enumerate(self.rules):
            if rule.id == ruleId:
                index = i
                break
        if auto_lock:
            self.rules_lock.release()
        return index

    async def set_rule(self, rule:SendMessageRule):
        if rule.id is None:
            raise RuntimeError("All rules must have an ID before entering the rule-list")
        if rule.template is None:
            raise RuntimeError("All rules must have a template before entering the rule-list")
        if not rule.recipients:
            raise RuntimeError("All rules must have at least 1 participant before entering the rule-list")

        async with self.rules_lock:
            index = await self.__find_rule_index(rule.id, auto_lock=False)

            if index == -1:
                self.rules.append(rule)
            else:
                self.rules[index] = rule
    
    async def remove_rule(self, rule:SendMessageRule|int):
        if not isinstance(rule, (SendMessageRule, int)):
            raise ValueError("remove_rule accepts either a SendMessageRule object or an int")
        
        if isinstance(rule, SendMessageRule):
            if rule.id is None:
                raise ValueError("remove_rule accepts SendMessageRule objects ONLY if they have an ID")
            ruleId = rule.id
        else:
            ruleId = rule
        
        async with self.rules_lock:
            index = await self.__find_rule_index(ruleId, auto_lock=False)

            if index != -1:
                self.rules.pop(index)

    
    async def _find_ready_rules(self, auto_lock:bool = True) -> list[SendMessageRule]:
        if auto_lock: await self.rules_lock.acquire()
        ready_rules = []

        timedelta_obj = timedelta() # Cache timedelta()
        for rule in self.rules:
            if rule.next_execution == timedelta_obj:
                ready_rules.append(rule)

        if auto_lock: self.rules_lock.release()
        return ready_rules
    
    async def _find_next_execution_interval(self, auto_lock:bool = True) -> timedelta|None:
        if auto_lock: await self.rules_lock.acquire()
        # next_execution_interval
        nei:timedelta|None = None

        for rule in self.rules:
            ne = rule.next_execution # Cache rule.next_execution
            if nei is None or ne < nei:
                nei = ne
        
        if auto_lock: self.rules_lock.release()
        return nei
    
    async def send_sms_loop(self):
        timedelta_obj = timedelta() # Cache timedelta()
        while True:
            ready_rules = await self._find_ready_rules()
            invalid_rules = []

            for rule in ready_rules:
                try:
                    await self.send_sms(rule)
                except RuntimeError:
                    invalid_rules.append(rule)
            
            # TODO: Make a separate function with proper exception handling
            async with self.rules_lock:
                while invalid_rules:
                    try:
                        rule = invalid_rules.pop()
                        self.rules.remove(rule)
                    except Exception:
                        pass

            next_execution = await self._find_next_execution_interval()

            if next_execution != timedelta_obj:
                # Don't have ready rules
                await asyncio.sleep(next_execution.total_seconds() if next_execution is not None else self.idle_interval)
            # else: We have ready rules, we simply loop back to send the messages.
    
    async def send_sms(self, rule:SendMessageRule):
        if rule.template is None:
            raise RuntimeError("A rule must have a template to be valid for sending an SMS")
        if not rule.recipients:
            raise RuntimeError("A rule must have at least 1 recipient to be valid for sending an SMS")

        for recipient in rule.recipients:
            msg = rule.template.compileFor(recipient)
            pass # TODO: Send SMS
            # TODO: Update rule last_executed.