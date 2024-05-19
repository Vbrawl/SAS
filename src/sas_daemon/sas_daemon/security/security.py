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
        return self.ph.verify(user.password, password)
    
    def needs_rehash(self, user:User):
        return self.ph.check_needs_rehash(user.password)
    
    def rehash_password(self, user:User):
        user.password = self.ph.hash(user.password)
    
    def login(self, username:str, password:str) -> User|None:
        user = self.db.get_user(username)

        # Return None if user doesn't exist or password doesn't match
        if user is None: return
        if not self.check_password(user, password): return

        # Rehash if needed
        if self.needs_rehash(user):
            self.rehash_password(user)
            self.db.alter_user(user)
        
        # Return the logged in user
        return user
