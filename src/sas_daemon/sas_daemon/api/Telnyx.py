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
from .BasicAPI import BasicAPI
import telnyx

class TelnyxAPI(BasicAPI):
    def __init__(self, api_key:str, from_number:str):
        self.api_key = api_key
        self.from_number = from_number

    def sendSMS(self, telephone:str, message:str):
        telnyx.Message.create(
            api_key = self.api_key,
            from_   = self.from_number,
            to      = telephone,
            text    = message,
            type    = "SMS"
        )