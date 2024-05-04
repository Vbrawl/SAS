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
                          `id` INTEGER NOT NULL UNIQUE AUTOINCREMENT,
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
                          `id` INTEGER NOT NULL UNIQUE AUTOINCREMENT,
                          `label` TEXT,
                          `message` TEXT NOT NULL,
                          PRIMARY KEY(`id`));''')
        
        ########################################################
        # Create `TimeDeltas` table                            #
        # This table holds information about timedelta objects #
        ########################################################
        self.conn.execute('''CREATE TABLE IF NOT EXISTS `TimeDeltas` (
                          `id` INTEGER NOT NULL UNIQUE AUTOINCREMENT,
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
                          `id` INTEGER NOT NULL UNIQUE AUTOINCREMENT,
                          `templateID` INTEGER NOT NULL,
                          `start_date` DATETIME NOT NULL,
                          `end_date` DATETIME,
                          `intervalID` INTEGER,
                          `last_executed` DATETIME,
                          PRIMARY KEY(`id`),
                          CONSTRAINT FK_templateID FOREIGN KEY (`templateID`) REFERENCES `Templates`(`id`),
                          CONSTRAINT FK_intervalID FOREIGN KEY (`intervalID`) REFERENCES `TimeDeltas`(`id`));''')

        self.conn.commit()