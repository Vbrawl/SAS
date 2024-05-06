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
from .templates import PersonTemplateArguments, TemplateArguments, Template
from .rules import SendMessageRule
from datetime import datetime, timedelta
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
                          `message` TEXT NOT NULL,
                          PRIMARY KEY(`id`));''')
        
        ############################################
        # Create `PeopleInRule` table              #
        # This table links people to message rules #
        ############################################
        self.conn.execute('''CREATE TABLE IF NOT EXISTS `PeopleInRule` (
                          `personID` INTEGER NOT NULL,
                          `ruleID` INTEGER NOT NULL,
                          PRIMARY KEY (`personID`, `ruleID`),
                          CONSTRAINT FK_personID FOREIGN KEY (`personID`) REFERENCES `People`(`id`),
                          CONSTRAINT FK_ruleID FOREIGN KEY (`ruleID`) REFERENCES `SendMessageRule`(`id`));''')

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
                          `interval_weeks` INTEGER,
                          `interval_days` INTEGER,
                          `interval_hours` INTEGER,
                          `interval_minutes` INTEGER,
                          `interval_seconds` INTEGER,
                          `last_executed` DATETIME,
                          PRIMARY KEY(`id`),
                          CONSTRAINT FK_templateID FOREIGN KEY (`templateID`) REFERENCES `Templates`(`id`));''')

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
    
    def get_template(self, id:int) -> Template|None:
        cur = self.conn.execute("SELECT `message` FROM `Templates` WHERE `id`=?;", (id,))
        res:tuple[str]|None = cur.fetchone()
        if res:
            return Template(id=id, message=res[0])
    
    def get_templates(self, limit:int|None = None, offset:int|None = None) -> list[Template]:
        query:str = 'SELECT `id`, `message` FROM `Templates`'
        params:tuple = tuple()
        if limit is not None:
            query += " LIMIT ?"
            params = (limit,)
            if offset is not None:
                query += " OFFSET ?"
                params = (limit, offset)
        cur = self.conn.execute(query, params)
        res:list[tuple[int, str]] = cur.fetchall()
        return list(map(lambda x: Template(id=x[0], message=x[1]), res))
    
    def add_template(self, template:Template):
        message = template._message
        self.conn.execute("INSERT INTO `Templates` (`message`) VALUES (?)", (message,))
        self.conn.commit()
    
    def alter_template(self, template:Template, id:int|None = None):
        if id is None:
            id = template.id
        if id is None:
            raise ValueError("You must provide an ID either through the parameters or template(id)")
        
        message = template._message
        self.conn.execute("UPDATE `Templates` SET `message`=? WHERE `id`=?;", (message,id))
        self.conn.commit()
    
    def get_rule(self, id:int) -> SendMessageRule|None:
        def asInt(x:int|None) -> int:
            return x if x is not None else 0

        cur = self.conn.execute("SELECT T.`id`, T.`message`, SMR.`start_date`, SMR.`end_date`, SMR.`interval_weeks`, SMR.`interval_days`, SMR.`interval_hours`, SMR.`interval_minutes`, SMR.`interval_seconds`, SMR.`last_executed` FROM `SendMessageRule` AS SMR JOIN `Templates` AS T ON SMR.templateID = T.id WHERE SMR.id=?;", (id,))
        res:tuple[int, str, datetime, datetime|None, int|None, int|None, int|None, int|None, int|None, datetime|None]|None = cur.fetchone()
        if res:
            cur = cur.execute("SELECT `P`.`id`, `P`.`first_name`, `P`.`last_name`, `P`.`telephone`, `P`.`address` FROM `PeopleInRule` as `PIR` JOIN `People` AS `P` ON `PIR`.`personID` = `P`.`id` WHERE `PIR`.`ruleID`=?;", (id,))
            recipients:list[tuple[int, str, str, str, str]] = cur.fetchall()

            return SendMessageRule(
                list(map(lambda x: PersonTemplateArguments(id=x[0], first_name=x[1], last_name=x[2], telephone=x[3], address=x[4]), recipients)),
                Template(id=res[0], message=res[1]),
                res[2],
                res[3],
                timedelta(weeks=asInt(res[4]), days=asInt(res[5]), hours=asInt(res[6]), minutes=asInt(res[7]), seconds=asInt(res[8])),
                res[9],
                id=id
            )
    
    def get_rules(self, limit:int|None = None, offset:int|None = None) -> list[SendMessageRule]:
        def fetchRecipients(id:int) -> list[PersonTemplateArguments]:
            cur = self.conn.execute("SELECT `P`.`id`, `P`.`first_name`, `P`.`last_name`, `P`.`telephone`, `P`.`address` FROM `PeopleInRule` as `PIR` JOIN `People` AS `P` ON `PIR`.`personID` = `P`.`id` WHERE `PIR`.`ruleID`=?;", (id,))
            res:list[tuple[int, str|None, str|None, str, str|None]] = cur.fetchall()
            if res:
                return list(map(lambda x: PersonTemplateArguments(id=x[0], first_name=x[1], last_name=x[2], telephone=x[3], address=x[4]), res))
            return []
        def asInt(x:int|None) -> int:
            return x if x is not None else 0
        query:str = "SELECT SMR.`id`, T.`id`, T.`message`, SMR.`start_date`, SMR.`end_date`, SMR.`interval_weeks`, SMR.`interval_days`, SMR.`interval_hours`, SMR.`interval_minutes`, SMR.`interval_seconds`, SMR.`last_executed` FROM `SendMessageRule` AS SMR JOIN `Templates` AS T ON SMR.templateID = T.id"
        params:tuple = tuple()

        if limit is not None:
            query += " LIMIT ?"
            params = (limit,)
            if offset is not None:
                query += " OFFSET ?"
                params = (limit, offset)

        cur = self.conn.execute(query, params)
        res:list[tuple[int, int, str, datetime, datetime|None, int|None, int|None, int|None, int|None, int|None, datetime|None]] = cur.fetchall()
        if res:
            return list(map(lambda x:
                            SendMessageRule(
                                id=x[0],
                                recipients=fetchRecipients(x[0]), # type: ignore
                                template=Template(id=x[1], message=x[2]),
                                start_date=x[3],
                                end_date=x[4],
                                interval=timedelta(weeks=asInt(x[5]), days=asInt(x[6]), hours=asInt(x[7]), minutes=asInt(x[8]), seconds=asInt(x[9])),
                                last_executed=x[10]
                            ), res))
        return []