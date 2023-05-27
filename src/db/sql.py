from .classes import *


create_table_sql = f"""\
CREATE TABLE IF NOT EXISTS singleton (
    id INTEGER PRIMARY KEY,
    last_open_date DATE
);
CREATE TABLE IF NOT EXISTS {Patient.__tablename__} (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    gender GENDER NOT NULL,
    birthdate DATE NOT NULL,
    address TEXT,
    phone TEXT,
    past_history TEXT
);
CREATE TABLE IF NOT EXISTS {Visit.__tablename__} (
    id INTEGER PRIMARY KEY,
    exam_datetime TIMESTAMP DEFAULT (datetime('now', 'localtime')),
    diagnosis TEXT NOT NULL,
    weight DECIMAL NOT NULL,
    days INTEGER NOT NULL,
    recheck INTEGER NOT NULL,
    price INTEGER NOT NULL,
    patient_id INTEGER NOT NULL,
    vnote TEXT,
    follow TEXT,
    FOREIGN KEY (patient_id) REFERENCES {Patient.__tablename__} (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT recheck_BE_0 CHECK (recheck >=0),
    CONSTRAINT days_BE_0 CHECK (days >= 0),
    CONSTRAINT weight_BT_0 CHECK (weight > 0) 
);
CREATE TABLE IF NOT EXISTS {Queue.__tablename__} (
    id INTEGER PRIMARY KEY,
    patient_id INTEGER UNIQUE NOT NULL,
    added_datetime TIMESTAMP DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (patient_id) REFERENCES {Patient.__tablename__} (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
CREATE TABLE IF NOT EXISTS {SeenToday.__tablename__} (
    id INTEGER PRIMARY KEY,
    patient_id INTEGER UNIQUE NOT NULL,
    visit_id INTEGER UNIQUE NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES {Patient.__tablename__} (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (visit_id) REFERENCES {Visit.__tablename__} (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
CREATE TABLE IF NOT EXISTS {Appointment.__tablename__} (
    id INTEGER PRIMARY KEY,
    patient_id INTEGER UNIQUE NOT NULL,
    appointed_date DATE NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES {Patient.__tablename__} (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
CREATE TABLE IF NOT EXISTS {Warehouse.__tablename__} (
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
CREATE TABLE IF NOT EXISTS {LineDrug.__tablename__} (
    id INTEGER PRIMARY KEY,
    warehouse_id INTEGER NOT NULL,
    times INTEGER NOT NULL,
    dose TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    visit_id INTEGER NOT NULL,
    usage_note TEXT,
    FOREIGN KEY (visit_id) REFERENCES {Visit.__tablename__} (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (warehouse_id) REFERENCES {Warehouse.__tablename__} (id)
        ON DELETE RESTRICT
        ON UPDATE NO ACTION,
    CONSTRAINT qt_ti_do_check CHECK (
        quantity > 0 AND 
        times > 0 AND 
        dose != ''
        )
);
CREATE TABLE IF NOT EXISTS {SamplePrescription.__tablename__} (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS {LineSamplePrescription.__tablename__} (
    id INTEGER PRIMARY KEY,
    warehouse_id INTEGER NOT NULL,
    sample_id INTEGER NOT NULL,
    times INTEGER NOT NULL,
    dose TEXT NOT NULL,
    FOREIGN KEY (warehouse_id) REFERENCES {Warehouse.__tablename__} (id)
        ON DELETE RESTRICT
        ON UPDATE NO ACTION,
    FOREIGN KEY (sample_id) REFERENCES {SamplePrescription.__tablename__} (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT ti_do_check CHECK (times > 0 AND dose != ''),
    CONSTRAINT unique_wh_sp UNIQUE (warehouse_id, sample_id)
);
CREATE TABLE IF NOT EXISTS {Procedure.__tablename__} (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    price INTEGER NOT NULL,
    CONSTRAINT price_BE_0 CHECK (price >= 0)
);
CREATE TABLE IF NOT EXISTS {LineProcedure.__tablename__} (
    id INTEGER PRIMARY KEY,
    procedure_id INTEGER NOT NULL,
    visit_id INTEGER NOT NULL,
    FOREIGN KEY (visit_id) REFERENCES {Visit.__tablename__} (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (procedure_id) REFERENCES {Procedure.__tablename__} (id)
        ON DELETE RESTRICT
        ON UPDATE NO ACTION
);
"""

create_index_sql = f"""
CREATE INDEX IF NOT EXISTS patient_name ON {Patient.__tablename__} (name);
CREATE INDEX IF NOT EXISTS procedure_name ON {Procedure.__tablename__} (name);
CREATE INDEX IF NOT EXISTS drug_name ON {Warehouse.__tablename__} (name);
CREATE INDEX IF NOT EXISTS drug_element ON {Warehouse.__tablename__} (element);
"""

create_view_sql = f"""
CREATE VIEW IF NOT EXISTS {Queue.__tablename__}_view AS
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
CREATE VIEW IF NOT EXISTS {SeenToday.__tablename__}_view AS
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
CREATE VIEW IF NOT EXISTS {Appointment.__tablename__}_view AS
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
CREATE TRIGGER IF NOT EXISTS last_open_date_update
AFTER UPDATE OF last_open_date ON singleton 
WHEN DATE(OLD.last_open_date, 'localtime') < DATE(NEW.last_open_date, 'localtime')
BEGIN
DELETE FROM {Queue.__tablename__};
DELETE FROM {SeenToday.__tablename__}; 
DELETE FROM {Appointment.__tablename__} 
    WHERE DATE({Appointment.__tablename__}.appointed_date, 'localtime') < DATE('now','localtime');
END;

CREATE TRIGGER IF NOT EXISTS linedrug_insert 
BEFORE INSERT ON {LineDrug.__tablename__}
BEGIN
UPDATE {Warehouse.__tablename__} SET quantity = quantity - NEW.quantity
    WHERE id = NEW.warehouse_id;
END;

CREATE TRIGGER IF NOT EXISTS linedrug_delete
BEFORE DELETE ON {LineDrug.__tablename__}
BEGIN
UPDATE {Warehouse.__tablename__} SET quantity = quantity + OLD.quantity
    WHERE id = OLD.warehouse_id;
END;

CREATE TRIGGER IF NOT EXISTS linedrug_update
BEFORE UPDATE ON {LineDrug.__tablename__}
WHEN NEW.warehouse_id = OLD.warehouse_id
BEGIN
UPDATE {Warehouse.__tablename__} SET quantity = quantity + OLD.quantity - NEW.quantity
    WHERE id = OLD.warehouse_id;
END;

CREATE TRIGGER IF NOT EXISTS visit_insert_before
BEFORE INSERT ON {Visit.__tablename__}
BEGIN
DELETE FROM {Queue.__tablename__}
    WHERE patient_id = NEW.patient_id;
END;

CREATE TRIGGER IF NOT EXISTS visit_insert_after
AFTER INSERT ON {Visit.__tablename__}
BEGIN
INSERT INTO {SeenToday.__tablename__} ({SeenToday.commna_joined_field_names()})
VALUES (NEW.patient_id, NEW.id);
END;
"""

finalized_sql = f"""
INSERT OR IGNORE INTO singleton (id, last_open_date) VALUES ( 1, DATE('now', 'localtime'));
"""
