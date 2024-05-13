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
from .templates import PersonTemplateArguments, Template
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
                          `interval_days` INTEGER,
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
    
    def get_recipients(self, ruleId:int) -> list[PersonTemplateArguments]:
        cur = self.conn.execute("SELECT `P`.`id`, `P`.`first_name`, `P`.`last_name`, `P`.`telephone`, `P`.`address` FROM `PeopleInRule` as `PIR` JOIN `People` AS `P` ON `PIR`.`personID` = `P`.`id` WHERE `PIR`.`ruleID`=?;", (ruleId,))
        res:list[tuple[int, str|None, str|None, str, str|None]] = cur.fetchall()
        if res:
            return list(map(lambda x: PersonTemplateArguments(id=x[0], first_name=x[1], last_name=x[2], telephone=x[3], address=x[4]), res))
        return []
    
    def link_recipient(self, personId:int, ruleId:int):
        self.conn.execute("INSERT INTO `PeopleInRule` (`personID`, `ruleID`) VALUES (?, ?);", (personId, ruleId))
        self.conn.commit()
    
    def unlink_recipient(self, personId:int, ruleId:int):
        self.conn.execute("DELETE FROM `PeopleInRule` WHERE `personID`=? AND `ruleID`=?;", (personId, ruleId))
        self.conn.commit()
    
    def unlink_recipient_from_all_rules(self, personId:int):
        self.conn.execute("DELETE FROM `PeopleInRule` WHERE `personID`=?;", (personId,))
        self.conn.commit()
    
    def unlink_all_recipients_from_rule(self, ruleId:int):
        self.conn.execute("DELETE FROM `PeopleInRule` WHERE `ruleID`=?;", (ruleId,))
        self.conn.commit()
    
    def add_person(self, person:PersonTemplateArguments) -> int|None:
        telephone:str = person.telephone
        first_name:str|None = getattr(person, "first_name", None)
        last_name:str|None = getattr(person, "last_name", None)
        address:str|None = getattr(person, "address", None)

        self.conn.execute("INSERT INTO `People` (first_name, last_name, telephone, address) VALUES (?, ?, ?, ?);", (first_name, last_name, telephone, address))
        cur = self.conn.execute("SELECT last_insert_rowid();")
        res = cur.fetchone()
        self.conn.commit()

        if res is not None:
            return res[0]
    
    def ensure_person(self, person:PersonTemplateArguments) -> int|None:
        exists = True
        id = getattr(person, "id", None)

        if id is None:
            exists = False
        elif self.get_person(id) is None:
            exists = False
        
        if not exists:
            return self.add_person(person)
        return id
    
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
    
    def delete_person(self, id:int):
        self.unlink_recipient_from_all_rules(id)
        self.conn.execute("DELETE FROM `People` WHERE `id`=?;", (id,))
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
    
    def add_template(self, template:Template) -> int|None:
        message = template._message
        self.conn.execute("INSERT INTO `Templates` (`message`) VALUES (?)", (message,))
        cur = self.conn.execute("SELECT last_insert_rowid();")
        res = cur.fetchone()
        self.conn.commit()

        if res is not None:
            return res[0]
        
    def ensure_template(self, template:Template) -> int|None:
        exists = True
        id = template.id

        if id is None:
            exists = False
        elif self.get_template(id) is None:
            exists = False
        
        if not exists:
            return self.add_template(template)
        return id
    
    def alter_template(self, template:Template, id:int|None = None):
        if id is None:
            id = template.id
        if id is None:
            raise ValueError("You must provide an ID either through the parameters or template(id)")
        
        message = template._message
        self.conn.execute("UPDATE `Templates` SET `message`=? WHERE `id`=?;", (message,id))
        self.conn.commit()
    
    def delete_template(self, id:int):
        self.conn.execute("DELETE FROM `Templates` WHERE `id`=?;", (id,))
        self.conn.commit()
    
    def get_rule(self, id:int) -> SendMessageRule|None:
        cur = self.conn.execute("SELECT T.`id`, T.`message`, SMR.`start_date`, SMR.`end_date`, SMR.`interval_days`, SMR.`interval_seconds`, SMR.`last_executed` FROM `SendMessageRule` AS SMR JOIN `Templates` AS T ON SMR.templateID = T.id WHERE SMR.id=?;", (id,))
        res:tuple[int, str, str, str|None, int|None, int|None, str|None]|None = cur.fetchone()
        if res:
            return SendMessageRule(
                self.get_recipients(id),
                Template(id=res[0], message=res[1]),
                datetime.strptime(res[2], "%Y-%m-%d %H:%M:%S.%f"),
                datetime.strptime(res[3], "%Y-%m-%d %H:%M:%S.%f") if res[3] else None,
                timedelta(
                    days=res[4] if res[4] else 0,
                    seconds=res[5] if res[5] else 0),
                datetime.strptime(res[6], "%Y-%m-%d %H:%M:%S.%f") if res[6] else None,
                id=id
            )
    
    def get_rules(self, limit:int|None = None, offset:int|None = None) -> list[SendMessageRule]:
        query:str = "SELECT SMR.`id`, T.`id`, T.`message`, SMR.`start_date`, SMR.`end_date`, SMR.`interval_days`, SMR.`interval_seconds`, SMR.`last_executed` FROM `SendMessageRule` AS SMR JOIN `Templates` AS T ON SMR.templateID = T.id"
        params:tuple = tuple()

        if limit is not None:
            query += " LIMIT ?"
            params = (limit,)
            if offset is not None:
                query += " OFFSET ?"
                params = (limit, offset)

        cur = self.conn.execute(query, params)
        res:list[tuple[int, int, str, str, str|None, int|None, int|None, str|None]] = cur.fetchall()
        if res:
            return list(map(lambda x:
                            SendMessageRule(
                                id=x[0],
                                recipients=self.get_recipients(x[0]),
                                template=Template(id=x[1], message=x[2]),
                                start_date=datetime.strptime(x[3], "%Y-%m-%d %H:%M:%S.%f"),
                                end_date=datetime.strptime(x[4], "%Y-%m-%d %H:%M:%S.%f") if x[4] else None,
                                interval=timedelta(
                                    days=x[5] if x[5] else 0,
                                    seconds=x[6] if x[6] else 0),
                                last_executed=datetime.strptime(x[7], "%Y-%m-%d %H:%M:%S.%f") if x[7] else None
                            ), res))
        return []
    
    def add_rule(self, rule:SendMessageRule) -> int|None:
        recipients = rule.recipients
        template = rule.template
        start_date = rule._start_date
        end_date = rule._end_date
        interval = rule._interval
        last_executed = rule._last_executed


        # If the template doesn't exist add it to the database
        template.id = self.ensure_template(template)
        if template.id is None:
            raise sqlite3.Error("Template existence could not be verified.")

        # Insert all info to the database
        self.conn.execute('INSERT INTO `SendMessageRule` (`templateID`, `start_date`, `end_date`, `interval_days`, `interval_seconds`, `last_executed`) VALUES (?, ?, ?, ?, ?, ?)',
                          (template.id, start_date.strftime("%Y-%m-%d %H:%M:%S.%f"), end_date.strftime("%Y-%m-%d %H:%M:%S.%f") if end_date else None, interval.days, interval.seconds, last_executed.strftime("%Y-%m-%d %H:%M:%S.%f") if last_executed else None))
        cur = self.conn.execute("SELECT last_insert_rowid();")
        res = cur.fetchone()
        if res is None:
            raise sqlite3.Error("Rule existence could not be verified.")
        rule.id:int = res[0] # type: ignore

        # Add all people that don't exist to the database
        # Mark all people in the recipients list as recipients of the rule
        for recipient in recipients:
            rid = self.ensure_person(recipient)
            if rid:
                recipient.id = rid
                self.link_recipient(recipient.id, rule.id)

        self.conn.commit()
        return rule.id
    
    def alter_rule(self, rule:SendMessageRule, id:int|None = None):
        if id is None:
            id = rule.id
        if id is None:
            raise ValueError("You must provide an ID either through the parameters or SendMessageRule(id)")
        recipients = rule.recipients
        template = rule.template
        start_date = rule._start_date
        end_date = rule._end_date
        interval = rule._interval
        last_executed = rule._last_executed

        # ensure template exists
        template.id = self.ensure_template(template)

        # Clear recipients
        self.unlink_all_recipients_from_rule(id)

        # Update rule
        self.conn.execute("UPDATE `SendMessageRule` SET `templateID`=?, `start_date`=?, `end_date`=?, `interval_days`=?, `interval_seconds`=?, `last_executed`=? WHERE `id`=?;",
                          (template.id, start_date.strftime("%Y-%m-%d %H:%M:%S.%f"), end_date.strftime("%Y-%m-%d %H:%M:%S.%f") if end_date else None, interval.days, interval.seconds, last_executed.strftime("%Y-%m-%d %H:%M:%S.%f") if last_executed else None, id))

        # Link all new recipients
        for recipient in recipients:
            rid = self.ensure_person(recipient)
            if rid:
                recipient.id = rid
                self.link_recipient(recipient.id, id)
    
    def delete_rule(self, id:int):
        self.unlink_all_recipients_from_rule(id)
        self.conn.execute("DELETE FROM `SendMessageRule` WHERE `id`=?;", (id,))
        self.conn.commit()