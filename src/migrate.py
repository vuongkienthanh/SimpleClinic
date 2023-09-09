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
    VALUES (:id, :exam_datetime, {Visit.named_style_placeholders()})""",
    (
        {col: v[col] for col in v.keys()} | {"price": 0}
        for v in old_con.execute("SELECT * FROM visits").fetchall()
    ),
)
new_con.executemany(
    f"""
    INSERT INTO {Queue.__tablename__} 
    (id, added_datetime, {Queue.commna_joined_field_names()}) 
    VALUES (:id, :added_datetime, {Queue.qmark_style_placeholders()})""",
    old_con.execute(f"SELECT * FROM queuelist").fetchall(),
)
new_con.executescript(
    f"""
    INSERT INTO {SeenToday.__tablename__} 
    (patient_id, visit_id) 
    SELECT patient_id, id FROM visits 
    WHERE DATE(exam_datetime) = DATE('now','localtime')"""
)
new_con.executemany(
    f"""
    INSERT INTO {Warehouse.__tablename__} 
    (id, {Warehouse.commna_joined_field_names()}) 
    VALUES (:id,{Warehouse.named_style_placeholders()})""",
    (
        {col: wh[col] for col in wh.keys()} | {"drug_note": wh["note"]}
        for wh in old_con.execute("SELECT * FROM warehouse").fetchall()
    ),
)
new_con.executescript(
    f"""
    INSERT INTO {Appointment.__tablename__} (patient_id, appointed_date) 
    SELECT patient_id, DATE(exam_datetime, '+'||CAST(recheck AS text)||' days') FROM visits WHERE true
    ON CONFLICT (patient_id) DO UPDATE SET appointed_date=excluded.appointed_date
    """
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
    INSERT INTO {Procedure.__tablename__}
    (id, {Procedure.commna_joined_field_names()})
    VALUES (?,{Procedure.qmark_style_placeholders()})""",
    old_con.execute("SELECT * FROM procedures").fetchall(),
)
new_con.executemany(
    f"""
    INSERT INTO {LineProcedure.__tablename__}
    (id, {LineProcedure.commna_joined_field_names()})
    VALUES (?,{LineProcedure.qmark_style_placeholders()})""",
    old_con.execute("SELECT * FROM lineprocedure").fetchall(),
)
new_con.executemany(
    f"""
    INSERT INTO {LineSamplePrescription.__tablename__}
    (id, {LineSamplePrescription.commna_joined_field_names()})
    VALUES (:id,{LineSamplePrescription.named_style_placeholders()})""",
    (
        {col: ls[col] for col in ls.keys()} | {"warehouse_id": ls["drug_id"]}
        for ls in old_con.execute("SELECT * FROM linesampleprescription").fetchall()
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
        SELECT id, drug_id, times, dose, quantity, visit_id, note
        FROM {LineDrug.__tablename__}
        """
    ),
)

new_con.executescript(create_view_sql)
new_con.executescript(create_index_sql)
new_con.executescript(create_trigger_sql)
new_con.executescript(finalized_sql)
new_con.commit()


for i in range(5, 0, -1):
    print("close in ", i)
    time.sleep(0.5)
