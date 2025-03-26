import pyodbc

class DatabaseManager:
    def __init__(self, server, database, username, password):
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.conn = self.connect_to_sql_server()
        self.cursor = self.conn.cursor()

    def connect_to_sql_server(self):
        conn = pyodbc.connect(f'DRIVER={{SQL Server}};SERVER={self.server};DATABASE={self.database};UID={self.username};PWD={self.password}')
        return conn

    def create_tables(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS SlackMessages (
            id VARCHAR(50),
            text VARCHAR(MAX),
            user VARCHAR(50),
            ts VARCHAR(50)
        );
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS SlackThreadMessages (
            id VARCHAR(50),
            text VARCHAR(MAX),
            user VARCHAR(50),
            ts VARCHAR(50),
            thread_ts VARCHAR(50)
        );
        """)

    def insert_channel_messages(self, messages):
        for message in messages:
            self.cursor.execute("INSERT INTO SlackMessages (id, text, user, ts) VALUES (?, ?, ?, ?)",
                        message.get("client_msg_id"), message.get("text"), message.get("user"), message.get("ts"))

    def insert_thread_messages(self, thread_messages, thread_ts):
        for message in thread_messages:
            self.cursor.execute("INSERT INTO SlackThreadMessages (id, text, user, ts, thread_ts) VALUES (?, ?, ?, ?, ?)",
                        message.get("client_msg_id"), message.get("text"), message.get("user"), message.get("ts"), thread_ts)

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()