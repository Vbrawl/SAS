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

This file (Constants.py) contains some constant-values and built-in settings
for the "Daemon" component of the project (SAS).
'''
import argon2

COLLECT_RULES_INTERVAL = 60
DATABASE_FILE = "temp.db"
API_ADDRESS = "0.0.0.0"
API_PORT = 8585
DEFAULT_TIMEZONE = "UTC"

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"

PASSWORD_TIME_COST = argon2.DEFAULT_TIME_COST # 3
PASSWORD_MEMORY_COST = argon2.DEFAULT_MEMORY_COST # 65536
PASSWORD_PARALLELISM = argon2.DEFAULT_PARALLELISM # 4

DATABASE_TIMEZONE_SETTING = "timezone"
DATABASE_APIKEY_SETTING = "api-key"
DATABASE_TELEPHONE_SETTING = ""