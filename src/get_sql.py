from db.sql import *
from misc import SRC_DIR

import os.path

dst = os.path.join(SRC_DIR, "output.sql")

with open(dst, "w") as f:
    f.write(create_table_sql)
    f.write(create_view_sql)
    f.write(create_index_sql)
    f.write(create_trigger_sql)
    f.write(finalized_sql)
