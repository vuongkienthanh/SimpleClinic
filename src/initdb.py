import db
from misc import MY_DATABASE_PATH

if __name__ == "__main__":
    connection = db.Connection(MY_DATABASE_PATH)
    connection.make_db()
    connection.sqlcon.close()
