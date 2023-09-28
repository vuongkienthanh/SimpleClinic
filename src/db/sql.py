from .models import *

create_table_sql = f"""\
CREATE TABLE singleton (
    id INTEGER PRIMARY KEY,
    last_open_date DATE
);
CREATE TABLE {Patient.__tablename__} (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    gender GENDER NOT NULL,
    birthdate DATE NOT NULL,
    address TEXT,
    phone TEXT,
    past_history TEXT
);
CREATE TABLE {Visit.__tablename__} (
    id INTEGER PRIMARY KEY,
    exam_datetime TIMESTAMP DEFAULT (datetime('now', 'localtime')),
    diagnosis TEXT NOT NULL,
    weight INTEGER NOT NULL, -- real weight *10
    days INTEGER NOT NULL,
    recheck INTEGER NOT NULL,
    price INTEGER NOT NULL,
    patient_id INTEGER NOT NULL,
    vnote TEXT,
    follow TEXT,
    temperature INTEGER,
    height INTEGER,
    CONSTRAINT ref_patient FOREIGN KEY (patient_id) REFERENCES {Patient.__tablename__} (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT recheck_BE_0 CHECK (recheck >=0),
    CONSTRAINT days_BE_0 CHECK (days >= 0),
    CONSTRAINT weight_BT_0 CHECK (weight > 0),
    CONSTRAINT temperature_BT_0 CHECK (temperature >= 0),
    CONSTRAINT height_BT_0 CHECK (height >= 0)
);
CREATE TABLE {Queue.__tablename__} (
    id INTEGER PRIMARY KEY,
    patient_id INTEGER UNIQUE NOT NULL,
    added_datetime TIMESTAMP DEFAULT (datetime('now', 'localtime')),
    CONSTRAINT ref_patient FOREIGN KEY (patient_id) REFERENCES {Patient.__tablename__} (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
CREATE TABLE {SeenToday.__tablename__} (
    id INTEGER PRIMARY KEY,
    patient_id INTEGER NOT NULL,
    visit_id INTEGER NOT NULL,
    CONSTRAINT patient_visit_unique_for_seentoday UNIQUE (patient_id, visit_id),
    CONSTRAINT ref_patient FOREIGN KEY (patient_id) REFERENCES {Patient.__tablename__} (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT ref_visit FOREIGN KEY (visit_id) REFERENCES {Visit.__tablename__} (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
CREATE TABLE {Appointment.__tablename__} (
    id INTEGER PRIMARY KEY,
    patient_id INTEGER UNIQUE NOT NULL,
    appointed_date DATE NOT NULL,
    CONSTRAINT ref_patient FOREIGN KEY (patient_id) REFERENCES {Patient.__tablename__} (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
CREATE TABLE {Warehouse.__tablename__} (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    element TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    usage_unit TEXT NOT NULL,
    usage TEXT NOT NULL,
    sale_unit TEXT,
    purchase_price INTEGER NOT NULL,
    sale_price INTEGER NOT NULL,
    expire_date DATE,
    made_by TEXT,
    drug_note TEXT,
    CONSTRAINT quantity_BE_0 CHECK (quantity >= 0),
    CONSTRAINT price_check CHECK (
        sale_price >= purchase_price AND 
        purchase_price >= 0
        )
);
CREATE TABLE {LineDrug.__tablename__} (
    id INTEGER PRIMARY KEY,
    warehouse_id INTEGER NOT NULL,
    times INTEGER NOT NULL,
    dose TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    visit_id INTEGER NOT NULL,
    usage_note TEXT,
    outclinic BOOLEAN DEFAULT FALSE,
    CONSTRAINT ref_visit FOREIGN KEY (visit_id) REFERENCES {Visit.__tablename__} (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT ref_warehouse FOREIGN KEY (warehouse_id) REFERENCES {Warehouse.__tablename__} (id)
        ON DELETE RESTRICT
        ON UPDATE NO ACTION,
    CONSTRAINT qt_ti_do_check CHECK (
        quantity > 0 AND 
        times > 0 AND 
        dose != ''
        )
);
CREATE TABLE {SamplePrescription.__tablename__} (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);
CREATE TABLE {LineSamplePrescription.__tablename__} (
    id INTEGER PRIMARY KEY,
    warehouse_id INTEGER NOT NULL,
    sample_id INTEGER NOT NULL,
    times INTEGER NOT NULL,
    dose TEXT NOT NULL,
    CONSTRAINT ref_warehouse FOREIGN KEY (warehouse_id) REFERENCES {Warehouse.__tablename__} (id)
        ON DELETE RESTRICT
        ON UPDATE NO ACTION,
    CONSTRAINT ref_sample FOREIGN KEY (sample_id) REFERENCES {SamplePrescription.__tablename__} (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT ti_do_check CHECK (times > 0 AND dose != ''),
    CONSTRAINT unique_wh_sp UNIQUE (warehouse_id, sample_id)
);
CREATE TABLE {Procedure.__tablename__} (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    price INTEGER NOT NULL,
    CONSTRAINT price_BE_0 CHECK (price >= 0)
);
CREATE TABLE {LineProcedure.__tablename__} (
    id INTEGER PRIMARY KEY,
    procedure_id INTEGER NOT NULL,
    visit_id INTEGER NOT NULL,
    CONSTRAINT ref_visit FOREIGN KEY (visit_id) REFERENCES {Visit.__tablename__} (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT ref_procedure FOREIGN KEY (procedure_id) REFERENCES {Procedure.__tablename__} (id)
        ON DELETE RESTRICT
        ON UPDATE NO ACTION
);
"""

create_index_sql = f"""
CREATE INDEX patient_name ON {Patient.__tablename__} (name);
CREATE INDEX procedure_name ON {Procedure.__tablename__} (name);
CREATE INDEX drug_name ON {Warehouse.__tablename__} (name);
CREATE INDEX drug_element ON {Warehouse.__tablename__} (element);
"""

create_view_sql = f"""
CREATE VIEW {Queue.__tablename__}_view AS
    SELECT
        p.id AS pid,
        p.name,
        p.gender,
        p.birthdate,
        q.added_datetime
    FROM {Queue.__tablename__} AS q
    JOIN {Patient.__tablename__} AS p
    ON q.patient_id = p.id
    ORDER BY q.added_datetime ASC
;
CREATE VIEW {SeenToday.__tablename__}_view AS
    SELECT
        p.id AS pid,
        p.name,
        p.gender,
        p.birthdate,
        v.id as vid,
        v.exam_datetime
    FROM {SeenToday.__tablename__} AS st
    JOIN {Patient.__tablename__} AS p
    ON st.patient_id = p.id
    JOIN {Visit.__tablename__} as v
    ON st.visit_id = v.id
    ORDER BY v.exam_datetime DESC
;
CREATE VIEW {Appointment.__tablename__}_view AS
    SELECT
        p.id AS pid,
        p.name,
        p.gender,
        p.birthdate
    FROM {Appointment.__tablename__} AS a
    JOIN {Patient.__tablename__} AS p
    ON a.patient_id = p.id
    WHERE DATE(a.appointed_date, 'localtime') = DATE('now', 'localtime')
;
"""

create_trigger_sql = f"""
CREATE TRIGGER last_open_date_insert
BEFORE INSERT ON singleton 
BEGIN
DELETE FROM {Queue.__tablename__};
DELETE FROM {SeenToday.__tablename__};
DELETE FROM {Appointment.__tablename__} 
    WHERE JULIANDAY(appointed_date) < JULIANDAY(NEW.last_open_date);
END;

CREATE TRIGGER last_open_date_update
BEFORE UPDATE OF last_open_date ON singleton 
WHEN JULIANDAY(OLD.last_open_date) < JULIANDAY(NEW.last_open_date)
BEGIN
DELETE FROM {Queue.__tablename__};
DELETE FROM {SeenToday.__tablename__};
DELETE FROM {Appointment.__tablename__} 
    WHERE JULIANDAY(appointed_date) < JULIANDAY(NEW.last_open_date);
END;

CREATE TRIGGER linedrug_insert 
BEFORE INSERT ON {LineDrug.__tablename__}
WHEN NEW.outclinic = FALSE
BEGIN
UPDATE {Warehouse.__tablename__} SET quantity = quantity - NEW.quantity
    WHERE id = NEW.warehouse_id;
END;

CREATE TRIGGER linedrug_delete
BEFORE DELETE ON {LineDrug.__tablename__}
WHEN OLD.outclinic = FALSE
BEGIN
UPDATE {Warehouse.__tablename__} SET quantity = quantity + OLD.quantity
    WHERE id = OLD.warehouse_id;
END;

CREATE TRIGGER linedrug_update
BEFORE UPDATE ON {LineDrug.__tablename__}
WHEN NEW.warehouse_id = OLD.warehouse_id AND
    NEW.outclinic = FALSE AND
    OLD.outclinic = FALSE
BEGIN
UPDATE {Warehouse.__tablename__} SET quantity = quantity + OLD.quantity - NEW.quantity
    WHERE id = OLD.warehouse_id;
END;

CREATE TRIGGER linedrug_update_from_no_outclinic_to_yes_outclinic
BEFORE UPDATE ON {LineDrug.__tablename__}
WHEN NEW.warehouse_id = OLD.warehouse_id AND
    NEW.outclinic = TRUE AND
    OLD.outclinic = FALSE
BEGIN
UPDATE {Warehouse.__tablename__} SET quantity = quantity - NEW.quantity
    WHERE id = OLD.warehouse_id;
END;

CREATE TRIGGER linedrug_update_from_yes_outclinic_to_no_outclinic
BEFORE UPDATE ON {LineDrug.__tablename__}
WHEN NEW.warehouse_id = OLD.warehouse_id AND
    NEW.outclinic = FALSE AND
    OLD.outclinic = TRUE
BEGIN
UPDATE {Warehouse.__tablename__} SET quantity = quantity + OLD.quantity
    WHERE id = OLD.warehouse_id;
END;

CREATE TRIGGER visit_insert_before
BEFORE INSERT ON {Visit.__tablename__}
BEGIN
DELETE FROM {Queue.__tablename__}
    WHERE patient_id = NEW.patient_id;
DELETE FROM {Appointment.__tablename__}
    WHERE patient_id = NEW.patient_id;
END;

CREATE TRIGGER visit_insert_after
AFTER INSERT ON {Visit.__tablename__}
BEGIN
INSERT INTO {SeenToday.__tablename__} ({SeenToday.commna_joined_fields()})
    VALUES (NEW.patient_id, NEW.id);
END;

CREATE TRIGGER visit_insert_after_recheck
AFTER INSERT ON {Visit.__tablename__}
WHEN NEW.recheck > 0
BEGIN
INSERT INTO {Appointment.__tablename__} ({Appointment.commna_joined_fields()})
VALUES (NEW.patient_id, DATE('now','localtime', '+'||CAST(NEW.recheck AS TEXT)||' days'))
ON CONFLICT (patient_id) DO UPDATE SET appointed_date=excluded.appointed_date;
END;

CREATE TRIGGER visit_update
BEFORE UPDATE OF recheck ON {Visit.__tablename__}
WHEN NEW.recheck > 0 AND OLD.recheck > 0 AND NEW.recheck != OLD.recheck
BEGIN
UPDATE {Appointment.__tablename__} SET appointed_date=DATE(NEW.exam_datetime, '+'||CAST(NEW.recheck AS TEXT)||' days')
    WHERE patient_id = OLD.patient_id;
END;

CREATE TRIGGER visit_update_before_recheck_BT_0
BEFORE UPDATE OF recheck ON {Visit.__tablename__}
WHEN NEW.recheck > 0 AND OLD.recheck = 0
BEGIN
INSERT INTO {Appointment.__tablename__} ({Appointment.commna_joined_fields()})
VALUES (NEW.patient_id, DATE('now','localtime', '+'||CAST(NEW.recheck AS TEXT)||' days'));
END;

CREATE TRIGGER visit_update_before_recheck_EQ_0
BEFORE UPDATE OF recheck ON {Visit.__tablename__}
WHEN NEW.recheck = 0 AND OLD.recheck > 0
BEGIN
DELETE FROM {Appointment.__tablename__} WHERE patient_id = OLD.patient_id;
END;
"""

finalized_sql = """
INSERT OR IGNORE INTO singleton (id, last_open_date) VALUES ( 1, DATE('now', 'localtime'));
"""
