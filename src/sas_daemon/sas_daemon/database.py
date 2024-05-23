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
# Avoid recursion problems by definine the Database class here
class Database: pass # type: ignore

from .templates import PersonTemplateArguments, Template
from .rules import SendMessageRule
from .datetimezone import datetimezone
from .security import User
from . import Constants
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
                          `label` TEXT,
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
                          `label` TEXT,
                          `templateID` INTEGER NOT NULL,
                          `start_date` DATETIME NOT NULL,
                          `end_date` DATETIME,
                          `interval` INTEGER,
                          `last_executed` DATETIME,
                          PRIMARY KEY(`id`),
                          CONSTRAINT FK_templateID FOREIGN KEY (`templateID`) REFERENCES `Templates`(`id`));''')

        ##################################################
        # Create `Users` table                           #
        # This table holds login information about users #
        # NOTE: All users are considered admins for now  #
        ##################################################
        self.conn.execute('''CREATE TABLE IF NOT EXISTS `Users` (
                          `id` INTEGER NOT NULL UNIQUE,
                          `username` TEXT NOT NULL UNIQUE,
                          `password` TEXT NOT NULL);''')
        
        ################################
        # Create `Settings` table      #
        # This table holds information #
        # about settings               #
        ################################
        self.conn.execute('''CREATE TABLE IF NOT EXISTS `Settings` (
                          `key` TEXT NOT NULL UNIQUE,
                          `value` TEXT);''')




        ############################
        # Add an admin user        #
        # Credentials: admin:admin #
        ############################
        self.conn.execute('INSERT INTO `Users` (`id`, `username`, `password`) VALUES (1, "admin", "$argon2id$v=19$m=32,t=3,p=4$N253UGNtdnc5TU44aVc2TA$rvmyGjoQKjCE/FxjxlUydQ")')

        #############################
        # Add some default settings #
        #############################
        self.conn.executemany('''INSERT INTO `Settings` (`key`, `value`) VALUES (?, ?);''', (
                                (Constants.DATABASE_TIMEZONE_SETTING, Constants.DEFAULT_TIMEZONE),
                                (Constants.DATABASE_APIKEY_SETTING, None),
                                (Constants.DATABASE_TELEPHONE_SETTING, None)))

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
        cur = self.conn.execute("SELECT `label`, `message` FROM `Templates` WHERE `id`=?;", (id,))
        res:tuple[str|None, str]|None = cur.fetchone()
        if res:
            return Template(id=id, label=res[0], message=res[1])
    
    def get_templates(self, limit:int|None = None, offset:int|None = None) -> list[Template]:
        query:str = 'SELECT `id`, `label`, `message` FROM `Templates`'
        params:tuple = tuple()
        if limit is not None:
            query += " LIMIT ?"
            params = (limit,)
            if offset is not None:
                query += " OFFSET ?"
                params = (limit, offset)
        cur = self.conn.execute(query, params)
        res:list[tuple[int|None, str|None, str]] = cur.fetchall()
        return list(map(lambda x: Template(id=x[0], label=x[1], message=x[2]), res))
    
    def add_template(self, template:Template) -> int|None:
        label = template.label
        message = template._message
        self.conn.execute("INSERT INTO `Templates` (`label`, `message`) VALUES (?, ?)", (label, message))
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

        label = template.label        
        message = template._message
        self.conn.execute("UPDATE `Templates` SET `label`=?, `message`=? WHERE `id`=?;", (label, message, id))
        self.conn.commit()
    
    def delete_template(self, id:int):
        self.conn.execute("DELETE FROM `Templates` WHERE `id`=?;", (id,))
        self.conn.commit()
    
    def get_rule(self, id:int) -> SendMessageRule|None:
        cur = self.conn.execute("SELECT T.`id`, T.`message`, SMR.`start_date`, SMR.`end_date`, SMR.`interval`, SMR.`last_executed`, SMR.`label` FROM `SendMessageRule` AS SMR JOIN `Templates` AS T ON SMR.templateID = T.id WHERE SMR.id=?;", (id,))
        res:tuple[int, str, str, str|None, int|None, str|None, str|None]|None = cur.fetchone()
        if res:
            return SendMessageRule(
                self.get_recipients(id),
                Template(id=res[0], message=res[1]),
                datetimezone(datetime.strptime(res[2], Constants.DATETIME_FORMAT)),
                datetimezone(datetime.strptime(res[3], Constants.DATETIME_FORMAT)) if res[3] else None,
                timedelta(seconds=res[4] if res[4] else 0),
                datetimezone(datetime.strptime(res[5], Constants.DATETIME_FORMAT)) if res[5] else None,
                id=id,
                label=res[6]
            )
    
    def get_rules(self, limit:int|None = None, offset:int|None = None) -> list[SendMessageRule]:
        query:str = "SELECT SMR.`id`, SMR.`label`, T.`id`, T.`message`, SMR.`start_date`, SMR.`end_date`, SMR.`interval`, SMR.`last_executed` FROM `SendMessageRule` AS SMR JOIN `Templates` AS T ON SMR.templateID = T.id"
        params:tuple = tuple()

        if limit is not None:
            query += " LIMIT ?"
            params = (limit,)
            if offset is not None:
                query += " OFFSET ?"
                params = (limit, offset)

        cur = self.conn.execute(query, params)
        res:list[tuple[int, str, int, str, str, str|None, int|None, str|None]] = cur.fetchall()
        if res:
            return list(map(lambda x:
                            SendMessageRule(
                                id=x[0],
                                label=x[1],
                                recipients=self.get_recipients(x[0]),
                                template=Template(id=x[2], message=x[3]),
                                start_date=datetimezone(datetime.strptime(x[4], Constants.DATETIME_FORMAT)),
                                end_date=datetimezone(datetime.strptime(x[5], Constants.DATETIME_FORMAT)) if x[5] else None,
                                interval=timedelta(seconds=x[6] if x[6] else 0),
                                last_executed=datetimezone(datetime.strptime(x[7], Constants.DATETIME_FORMAT)) if x[7] else None
                            ), res))
        return []
    
    def add_rule(self, rule:SendMessageRule) -> int|None:
        recipients = rule.recipients
        template = rule.template
        label = rule.label
        start_date = rule.str_start_date
        end_date = rule.str_end_date
        interval = rule._interval
        last_executed = rule.str_last_executed


        # If the template doesn't exist add it to the database
        template.id = self.ensure_template(template)
        if template.id is None:
            raise sqlite3.Error("Template existence could not be verified.")

        # Insert all info to the database
        self.conn.execute('INSERT INTO `SendMessageRule` (`templateID`, `label`, `start_date`, `end_date`, `interval`, `last_executed`) VALUES (?, ?, ?, ?, ?, ?)',
                          (template.id, label, start_date, end_date, interval.total_seconds(), last_executed))
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
        label = rule.label
        template = rule.template
        start_date = rule.str_start_date
        end_date = rule.str_end_date
        interval = rule._interval
        last_executed = rule.str_last_executed

        # ensure template exists
        template.id = self.ensure_template(template)

        # Clear recipients
        self.unlink_all_recipients_from_rule(id)

        # Update rule
        self.conn.execute("UPDATE `SendMessageRule` SET `templateID`=?, `label`=?, `start_date`=?, `end_date`=?, `interval`=?, `last_executed`=? WHERE `id`=?;",
                          (template.id, label, start_date, end_date, interval.total_seconds(), last_executed, id))

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
    
    def get_user(self, username:str) -> User|None:
        cur = self.conn.execute("SELECT `id`, `password` FROM `Users` WHERE `username`=?;", (username,))
        res:tuple[int, str]|None = cur.fetchone()
        if res:
            return User(
                res[0],
                username,
                res[1]
            )
    
    def alter_user(self, user:User):
        self.conn.execute("UPDATE `Users` SET `username`=?, `password`=? WHERE `id`=?", (user.username, user.password, user.id))
        self.conn.commit()
    
    def get_setting(self, key:str) -> str|None:
        cur = self.conn.execute("SELECT `value` FROM `Settings` WHERE `key`=?;", (key,))
        res:tuple[str]|None = cur.fetchone()
        if res: return res[0]
    
    def set_setting(self, key:str, value:str):
        self.conn.execute("UPDATE `Settings` SET `value`=? WHERE `key`=?;", (value, key))
        self.conn.commit()