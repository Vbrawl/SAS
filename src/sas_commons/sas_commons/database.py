from .templates import TemplateArguments
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
    

    def get_person(self, id:int) -> TemplateArguments|None:
        cur = self.conn.execute('SELECT `first_name`, `last_name`, `telephone`, `address` FROM `People` WHERE `id`=?', (id,))
        row:tuple[str, ...]|None = cur.fetchone()
        if row:
            return TemplateArguments(id=id, first_name=row[0], last_name=row[1], telephone=row[2], address=row[3])

    def get_people(self, limit:int|None = None, offset:int|None = None) -> list[TemplateArguments]:
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
        return list(map(lambda x: TemplateArguments(
            id=x[0],
            first_name=x[1],
            last_name=x[2],
            telephone=x[3],
            address=x[4]
            ), res))