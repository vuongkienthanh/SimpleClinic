from db.classes import *


create_table_sql = f"""\
CREATE TABLE IF NOT EXISTS singleton (
    id INTEGER PRIMARY KEY,
    last_open_date DATE
);
CREATE TABLE IF NOT EXISTS {Patient.table_name} (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    gender GENDER NOT NULL,
    birthdate DATE NOT NULL,
    address TEXT,
    phone TEXT,
    past_history TEXT
);
CREATE TABLE IF NOT EXISTS {Visit.table_name} (
    id INTEGER PRIMARY KEY,
    exam_datetime TIMESTAMP DEFAULT (datetime('now', 'localtime')),
    diagnosis TEXT NOT NULL,
    weight DECIMAL NOT NULL,
    days INTEGER NOT NULL,
    recheck INTEGER NOT NULL,
    patient_id INTEGER NOT NULL,
    vnote TEXT,
    follow TEXT,
    FOREIGN KEY (patient_id) REFERENCES {Patient.table_name} (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CHECK (recheck >=0 AND days >= 0 AND weight >=0 )
);
CREATE TABLE IF NOT EXISTS {Queue.table_name} (
    id INTEGER PRIMARY KEY,
    patient_id INTEGER UNIQUE NOT NULL,
    added_datetime TIMESTAMP DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (patient_id) REFERENCES {Patient.table_name} (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
CREATE TABLE IF NOT EXISTS {SeenToday.table_name} (
    id INTEGER PRIMARY KEY,
    patient_id INTEGER UNIQUE NOT NULL,
    visit_id INTEGER UNIQUE NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES {Patient.table_name} (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (visit_id) REFERENCES {Visit.table_name} (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
CREATE TABLE IF NOT EXISTS {Appointment.table_name} (
    id INTEGER PRIMARY KEY,
    patient_id INTEGER UNIQUE NOT NULL,
    appointed_date DATE NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES {Patient.table_name} (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
CREATE TABLE IF NOT EXISTS {Warehouse.table_name} (
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
    note TEXT,
    CHECK (quantity >= 0),
    CHECK ((sale_price >= purchase_price) AND (purchase_price >= 0))
);
CREATE TABLE IF NOT EXISTS {LineDrug.table_name} (
    id INTEGER PRIMARY KEY,
    drug_id INTEGER NOT NULL,
    times INTEGER NOT NULL,
    dose TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    visit_id INTEGER NOT NULL,
    note TEXT,
    FOREIGN KEY (visit_id) REFERENCES {Visit.table_name} (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (drug_id) REFERENCES {Warehouse.table_name} (id)
        ON DELETE RESTRICT
        ON UPDATE NO ACTION,
    CHECK ( quantity > 0 AND times > 0 AND dose != '')
);
CREATE TABLE IF NOT EXISTS {SamplePrescription.table_name} (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS {LineSamplePrescription.table_name} (
    id INTEGER PRIMARY KEY,
    drug_id INTEGER NOT NULL,
    sample_id INTEGER NOT NULL,
    times INTEGER NOT NULL,
    dose TEXT NOT NULL,
    FOREIGN KEY (drug_id) REFERENCES {Warehouse.table_name} (id)
        ON DELETE RESTRICT
        ON UPDATE NO ACTION,
    FOREIGN KEY (sample_id) REFERENCES {SamplePrescription.table_name} (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CHECK (times > 0 AND dose != ''),
    UNIQUE (drug_id, sample_id)
);
CREATE TABLE IF NOT EXISTS {Procedure.table_name} (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    price INTEGER NOT NULL,
    CHECK (price >= 0)
);
CREATE TABLE IF NOT EXISTS {LineProcedure.table_name} (
    id INTEGER PRIMARY KEY,
    procedure_id INTEGER NOT NULL,
    visit_id INTEGER NOT NULL,
    FOREIGN KEY (visit_id) REFERENCES {Visit.table_name} (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (procedure_id) REFERENCES {Procedure.table_name} (id)
        ON DELETE RESTRICT
        ON UPDATE NO ACTION
);


CREATE INDEX IF NOT EXISTS patient_name ON {Patient.table_name} (name);
CREATE INDEX IF NOT EXISTS procedure_name ON {Procedure.table_name} (name);
CREATE INDEX IF NOT EXISTS drug_name ON {Warehouse.table_name} (name);
CREATE INDEX IF NOT EXISTS drug_element ON {Warehouse.table_name} (element);


CREATE VIEW IF NOT EXISTS {Queue.table_name}_view AS
    SELECT
        p.id AS pid,
        p.name,
        p.gender,
        p.birthdate,
        q.added_datetime
    FROM {Queue.table_name} AS q
    JOIN {Patient.table_name} AS p
    ON q.patient_id = p.id
    ORDER BY q.added_datetime ASC
;
CREATE VIEW IF NOT EXISTS {SeenToday.table_name}_view AS
    SELECT
        p.id AS pid,
        p.name,
        p.gender,
        p.birthdate,
        v.id as vid,
        v.exam_datetime
    FROM {SeenToday.table_name} AS st
    JOIN {Patient.table_name} AS p
    ON st.patient_id = p.id
    JOIN {Visit.table_name} as v
    ON st.visit_id = v.id
    ORDER BY v.exam_datetime DESC
;
CREATE VIEW IF NOT EXISTS {Appointment.table_name}_view AS
    SELECT
        p.id AS pid,
        p.name,
        p.gender,
        p.birthdate
    FROM {Appointment.table_name} AS a
    JOIN {Patient.table_name} AS p
    ON a.patient_id = p.id
    WHERE DATE(a.appointed_date, 'localtime') = DATE('now', 'localtime')
;

CREATE TRIGGER IF NOT EXISTS last_open_date_update
AFTER UPDATE OF last_open_date ON singleton 
WHEN DATE(OLD.last_open_date, 'localtime') < DATE(NEW.last_open_date, 'localtime')
BEGIN
DELETE FROM {SeenToday.table_name}; 
DELETE FROM {Appointment.table_name} 
    WHERE DATE({Appointment.table_name}.appointed_date, 'localtime') < DATE('now','localtime');
END;

CREATE TRIGGER IF NOT EXISTS linedrug_insert 
BEFORE INSERT ON {LineDrug.table_name}
BEGIN
UPDATE {Warehouse.table_name} SET quantity = quantity - NEW.quantity
    WHERE id = NEW.drug_id;
END;

CREATE TRIGGER IF NOT EXISTS linedrug_delete
BEFORE DELETE ON {LineDrug.table_name}
BEGIN
UPDATE {Warehouse.table_name} SET quantity = quantity + OLD.quantity
    WHERE id = OLD.drug_id;
END;

CREATE TRIGGER IF NOT EXISTS linedrug_update
BEFORE UPDATE ON {LineDrug.table_name}
WHEN NEW.drug_id = OLD.drug_id
BEGIN
UPDATE {Warehouse.table_name} SET quantity = quantity + OLD.quantity - NEW.quantity
    WHERE id = OLD.drug_id;
END;

CREATE TRIGGER IF NOT EXISTS visit_insert
BEFORE INSERT ON {Visit.table_name}
BEGIN
DELETE FROM {Queue.table_name}
    WHERE patient_id = NEW.patient_id;
END;

INSERT OR IGNORE INTO singleton (id, last_open_date) VALUES ( 1, DATE('now', 'localtime'));

"""
