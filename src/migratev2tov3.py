import os
from pathlib import Path
from db import Connection, create_table_sql
from db.classes import *


old_db_path = os.path.join(Path.home(), ".pmpktn", "my_database.db")
new_db_path = os.path.join(Path.home(), ".SimpleClinic", "my_database.db")

if os.path.exists(new_db_path):
    os.remove(new_db_path)

old_con = Connection(old_db_path)
new_con = Connection(new_db_path)
new_con.executescript(create_table_sql)

new_con.executemany(
    f"""
    INSERT INTO {Patient.__tablename__} 
    (id, {Patient.commna_joined_field_names()}) 
    VALUES (?,{Patient.qmark_style_placeholders()})""",
    old_con.execute("SELECT * FROM patients").fetchall(),
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
    old_con.execute("SELECT * FROM queuelist").fetchall(),
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
new_con.executemany(
    f"""
    INSERT INTO {LineDrug.__tablename__}
    (id, {LineDrug.commna_joined_field_names()})
    VALUES (:id,{LineDrug.named_style_placeholders()})""",
    (
        {col: ld[col] for col in ld.keys()}
        | {"usage_note": ld["note"], "warehouse_id": ld["drug_id"]}
        for ld in old_con.execute("SELECT * FROM linedrugs").fetchall()
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
    INSERT INTO {SamplePrescription.__tablename__}
    (id, {SamplePrescription.commna_joined_field_names()})
    VALUES (?,{SamplePrescription.qmark_style_placeholders()})""",
    old_con.execute("SELECT * FROM sampleprescription").fetchall(),
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
new_con.executescript(
    f"""
    INSERT INTO {Appointment.__tablename__} (patient_id, appointed_date) 
    SELECT patient_id, DATE(exam_datetime, 'localtime', '+'||CAST(recheck AS text)||' days') FROM visits WHERE true
    ON CONFLICT (patient_id) DO UPDATE SET appointed_date=excluded.appointed_date
    """
)
new_con.commit()
