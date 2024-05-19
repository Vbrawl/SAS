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
from .user import User
from ..database import Database
import argon2

class Security:
    def __init__(self, db:Database,
                 time_cost:int = argon2.DEFAULT_TIME_COST,
                 memory_cost:int = argon2.DEFAULT_MEMORY_COST,
                 parallelism:int = argon2.DEFAULT_PARALLELISM):
        self.db = db
        self.ph = argon2.PasswordHasher(
            time_cost=time_cost,
            memory_cost=memory_cost,
            parallelism=parallelism
        )
    
    def check_password(self, user:User, password:str) -> bool:
        try:
            return self.ph.verify(user.password, password)
        except Exception:
            return False
    
    def needs_rehash(self, user:User):
        return self.ph.check_needs_rehash(user.password)
    
    def set_password(self, user:User, password:str):
        user.password = self.ph.hash(password)
    
    def login(self, username:str, password:str) -> User|None:
        user = self.db.get_user(username)

        # Return None if user doesn't exist or password doesn't match
        if user is None: return
        if not self.check_password(user, password): return

        # Rehash if needed
        if self.needs_rehash(user):
            self.set_password(user, password)
            self.db.alter_user(user)
        
        # Return the logged in user
        return user