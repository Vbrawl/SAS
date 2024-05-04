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
from .templates import PersonTemplateArguments
import sqlite3
import os


class Database:
    def __init__(self, dbName:str):
        initDB = not os.path.exists(dbName)
        self.conn = sqlite3.connect(dbName)
        if initDB:
            self.init_db()
    

    def init_db(self):
        ################################################
        # Create `People` table                        #
        # This table holds information about people    #
        # People should be used as `TemplateArguments` #
        ################################################
        self.conn.execute('''CREATE TABLE IF NOT EXISTS `People` (
                          `id` INTEGER NOT NULL UNIQUE,
                          `first_name` TEXT,
                          `last_name` TEXT,
                          `telephone` TEXT NOT NULL,
                          `address` TEXT,
                          PRIMARY KEY(`id`));''')
        
        ########################################################
        # Create `Templates` table                             #
        # This table holds information about message templates #
        # And the "message" column holds the Template(message) #
        ########################################################
        self.conn.execute('''CREATE TABLE IF NOT EXISTS `Templates` (
                          `id` INTEGER NOT NULL UNIQUE,
                          `label` TEXT,
                          `message` TEXT NOT NULL,
                          PRIMARY KEY(`id`));''')
        
        ########################################################
        # Create `TimeDeltas` table                            #
        # This table holds information about timedelta objects #
        ########################################################
        self.conn.execute('''CREATE TABLE IF NOT EXISTS `TimeDeltas` (
                          `id` INTEGER NOT NULL UNIQUE,
                          `days` INTEGER NOT NULL,
                          `seconds` INTEGER NOT NULL,
                          `microseconds` INTEGER NOT NULL,
                          PRIMARY KEY(`id`));''')

        ##############################################################
        # Create `SendMessageRule` table                             #
        # This table holds information about SendMessageRule objects #
        # It basically has rules about sending messages and such     #
        ##############################################################
        self.conn.execute('''CREATE TABLE IF NOT EXISTS `SendMessageRule` (
                          `id` INTEGER NOT NULL UNIQUE,
                          `templateID` INTEGER NOT NULL,
                          `start_date` DATETIME NOT NULL,
                          `end_date` DATETIME,
                          `intervalID` INTEGER,
                          `last_executed` DATETIME,
                          PRIMARY KEY(`id`),
                          CONSTRAINT FK_templateID FOREIGN KEY (`templateID`) REFERENCES `Templates`(`id`),
                          CONSTRAINT FK_intervalID FOREIGN KEY (`intervalID`) REFERENCES `TimeDeltas`(`id`));''')

        self.conn.commit()
    

    def get_person(self, id:int) -> PersonTemplateArguments|None:
        cur = self.conn.execute('SELECT `first_name`, `last_name`, `telephone`, `address` FROM `People` WHERE `id`=?', (id,))
        row:tuple[str|None, str|None, str, str|None]|None = cur.fetchone()
        if row:
            return PersonTemplateArguments(id=id, first_name=row[0], last_name=row[1], telephone=row[2], address=row[3])

    def get_people(self, limit:int|None = None, offset:int|None = None) -> list[PersonTemplateArguments]:
        query:str = 'SELECT `id`, `first_name`, `last_name`, `telephone`, `address` FROM `People`'
        params:tuple = tuple()
        if limit is not None:
            query += ' LIMIT ?'
            params = (limit,)
            if offset is not None:
                query += ' OFFSET ?'
                params = (limit, offset)
        cur = self.conn.execute(query, params)

        res:list[tuple[int, str, str, str, str]] = cur.fetchall()
        return list(map(lambda x: PersonTemplateArguments(
            id=x[0],
            first_name=x[1],
            last_name=x[2],
            telephone=x[3],
            address=x[4]
            ), res))
    
    def add_person(self, person:PersonTemplateArguments):
        telephone:str = person.telephone
        first_name:str|None = getattr(person, "first_name", None)
        last_name:str|None = getattr(person, "last_name", None)
        address:str|None = getattr(person, "address", None)

        self.conn.execute("INSERT INTO `People` (first_name, last_name, telephone, address) VALUES (?, ?, ?, ?);", (first_name, last_name, telephone, address))
        self.conn.commit()
    
    def alter_person(self, person:PersonTemplateArguments, id:int|None = None):
        if id is None:
            id = getattr(person, "id", None)
        if id is None:
            raise ValueError("You must provide an ID either through the parameters or person(id)")
        telephone:str = person.telephone
        first_name:str|None = getattr(person, "first_name", None)
        last_name:str|None = getattr(person, "last_name", None)
        address:str|None = getattr(person, "address", None)

        self.conn.execute("UPDATE `People` SET `first_name`=?, `last_name`=?, `telephone`=?, `address`=? WHERE `id`=?", (first_name, last_name, telephone, address, id))
        self.conn.commit()