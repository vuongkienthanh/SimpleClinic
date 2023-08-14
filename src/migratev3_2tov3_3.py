import os
import shutil
import time

from db import *
from misc import MY_DATABASE_PATH

ans = input("This will back up the database in .SimpleClinic, confirm migration[y/N]")
match ans:
    case "y" | "Y":
        pass
    case _:
        print("exit")
        exit()

bak = (
    os.path.realpath(MY_DATABASE_PATH)
    + dt.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    + ".bak"
)
shutil.copyfile(MY_DATABASE_PATH, bak)
os.remove(MY_DATABASE_PATH)

try:
    old_con = Connection(bak)
    new_con = Connection(MY_DATABASE_PATH)

    new_con.executescript(create_table_sql)

    new_con.executemany(
        f"""
        INSERT INTO {Patient.__tablename__} 
        (id, {Patient.commna_joined_field_names()}) 
        VALUES (?, {Patient.qmark_style_placeholders()})
        """,
        old_con.execute(f"SELECT * FROM {Patient.__tablename__}"),
    )
    new_con.executemany(
        f"""
        INSERT INTO {Visit.__tablename__} 
        (id, exam_datetime, {Visit.commna_joined_field_names()}) 
        VALUES (?,?, {Visit.qmark_style_placeholders()})""",
        old_con.execute(
            f""" SELECT 
                id,
                exam_datetime,
                {",".join(Visit.fields())}
            FROM {Visit.__tablename__}"""
        ).fetchall(),
    )
    new_con.executemany(
        f"""
        INSERT INTO {Queue.__tablename__} 
        (id, added_datetime, {Queue.commna_joined_field_names()}) 
        VALUES (:id, :added_datetime, {Queue.qmark_style_placeholders()})""",
        old_con.execute(f"SELECT * FROM {Queue.__tablename__}").fetchall(),
    )
    for c in [
        SeenToday,
        Appointment,
        Warehouse,
        Procedure,
        LineProcedure,
        LineSamplePrescription,
    ]:
        new_con.executemany(
            f"""
            INSERT INTO {c.__tablename__} 
            (id, {c.commna_joined_field_names()}) 
            VALUES (?, {c.qmark_style_placeholders()})
            """,
            old_con.execute(
                f"SELECT id, {','.join(c.fields())} FROM {c.__tablename__}"
            ),
        )
    new_con.executemany(
        f"""
        INSERT INTO {SamplePrescription.__tablename__} 
        (id, {SamplePrescription.commna_joined_field_names()}) 
        VALUES (?, {SamplePrescription.qmark_style_placeholders()})
        """,
        old_con.execute(
            f"SELECT id, {','.join(SamplePrescription.fields())} FROM sampleprescription"
        ),
    )
    new_con.executemany(
        f"""
        INSERT INTO {LineDrug.__tablename__} 
        (id, warehouse_id, times, dose, quantity, visit_id, usage_note)
        VALUES (?,?,?,?,?,?,?)
        """,
        old_con.execute(
            f"""
            SELECT id, warehouse_id, times, dose, quantity, visit_id, usage_note
            FROM {LineDrug.__tablename__}
            """
        ),
    )

    new_con.executescript(create_view_sql)
    new_con.executescript(create_index_sql)
    new_con.executescript(create_trigger_sql)
    new_con.executescript(finalized_sql)
    new_con.commit()
    old_con.sqlcon.close()
    new_con.sqlcon.close()
except Exception:
    os.remove(MY_DATABASE_PATH)
    shutil.copyfile(bak, MY_DATABASE_PATH)
    os.remove(bak)


for i in range(5, 0, -1):
    print("close in ", i)
    time.sleep(0.5)
