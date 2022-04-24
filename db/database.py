import psycopg2
import logging

logging.basicConfig(level=logging.INFO)

class DB:
    def __init__(self, db_name, db_user, db_password, db_host, db_port):
        try:
            self.conn = psycopg2.connect(dbname=db_name, user=db_user, password=db_password, host=db_host, port=db_port)
        except Exception as e:
            logging.error(e)
            raise e
        # Create Schema
        logging.info("connection to DB")
        self._create_schema()

    def _create_schema(self):
        with self.conn.cursor() as cur:
            cur.execute(
                """CREATE TABLE IF NOT EXISTS app_users(
                    username varchar(63) PRIMARY KEY NOT NULL,
                    password varchar(512) NOT NULL)""")
            cur.execute("""
            CREATE TABLE IF NOT EXISTS app_public_keys(
            username varchar(63) NOT NULL PRIMARY KEY,
            public_key varchar(2048) NOT NULL,
            FOREIGN KEY (username) REFERENCES app_users(username))
            """)
            cur.execute("""
            CREATE TABLE IF NOT EXISTS app_messages(
            id serial PRIMARY KEY NOT NULL,
            to_user varchar(63) NOT NULL,
            from_user varchar(63) NOT NULL,
            send_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
            message BYTEA NOT NULL,
            session_key varchar(2048) NOT NULL,
            file_type VARCHAR(31) NOT NULL,
            FOREIGN KEY (to_user) REFERENCES app_users(username),
            FOREIGN KEY (from_user) REFERENCES app_users(username))
            """)

    def add_user(self, username, password):
        with self.conn.cursor() as cur:
            cur.execute("INSERT INTO app_users(username, password) VALUES(%s, %s)", (username, password))
        self.conn.commit()

    def get_user_by_username(self, username):
        with self.conn.cursor() as cur:
            cur.execute("SELECT * FROM app_users WHERE username = '%s'", (username))
        self.conn.commit()
    
    def add_user_public_key(self, username, public_key):
        with self.conn.cursor() as cur:
            cur.execute("INSERT INTO app_public_keys(username, public_key) VALUES(%s, %s)", (username, public_key))
        self.conn.commit()
    
    def get_user_by_username(self, username):
        with self.conn.cursor() as cur:
            cur.execute("SELECT public_key FROM app_public_keys WHERE username = '%s'", (username))
        self.conn.commit()
    
    def send_user_message(self, from_user, message, file_type, to_user, session_key):
        with self.conn.cursor() as cur:
            cur.execute("INSERT INTO app_messages(from_user, message, file_type, to_user, session_key) VALUES(%s, %s, %s, %s, %s)", (from_user, message, file_type, to_user, session_key))
        self.conn.commit()
    
    def get_user_messages(self, username):
        with self.conn.cursor() as cur:
            cur.execute("SELECT message FROM app_messages WHERE username = '%s'", (username))
        self.conn.commit()
    
    def get_user_messages(self, username, message_id):
        with self.conn.cursor() as cur:
            cur.execute("SELECT message FROM app_messages WHERE username = '%s', id = %s", (username, message_id))
        self.conn.commit()

if __name__ == "__main__":
    db = DB("infosec", "infosec", "infosec", "localhost", "5435")
