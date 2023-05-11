from db.sql import create_table_sql
from misc import SRC_DIR

import os.path

dst = os.path.join(SRC_DIR, "output.sql")

with open(dst, "w") as f:
    f.write(create_table_sql)
