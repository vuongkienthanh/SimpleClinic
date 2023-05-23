CREATE TABLE IF NOT EXISTS singleton (
    id INTEGER PRIMARY KEY,
    last_open_date DATE
);
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    gender GENDER NOT NULL,
    birthdate DATE NOT NULL,
    address TEXT,
    phone TEXT,
    past_history TEXT
);
CREATE TABLE IF NOT EXISTS visits (
    id INTEGER PRIMARY KEY,
    exam_datetime TIMESTAMP DEFAULT (datetime('now', 'localtime')),
    diagnosis TEXT NOT NULL,
    weight DECIMAL NOT NULL,
    days INTEGER NOT NULL,
    recheck INTEGER NOT NULL,
    patient_id INTEGER NOT NULL,
    vnote TEXT,
    follow TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CHECK (recheck >=0 AND days >= 0 AND weight >=0 )
);
CREATE TABLE IF NOT EXISTS queue (
    id INTEGER PRIMARY KEY,
    patient_id INTEGER UNIQUE NOT NULL,
    added_datetime TIMESTAMP DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (patient_id) REFERENCES patients (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
CREATE TABLE IF NOT EXISTS seen_today (
    id INTEGER PRIMARY KEY,
    patient_id INTEGER UNIQUE NOT NULL,
    visit_id INTEGER UNIQUE NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (visit_id) REFERENCES visits (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY,
    patient_id INTEGER UNIQUE NOT NULL,
    appointed_date DATE NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
CREATE TABLE IF NOT EXISTS warehouse (
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
CREATE TABLE IF NOT EXISTS linedrugs (
    id INTEGER PRIMARY KEY,
    drug_id INTEGER NOT NULL,
    times INTEGER NOT NULL,
    dose TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    visit_id INTEGER NOT NULL,
    note TEXT,
    FOREIGN KEY (visit_id) REFERENCES visits (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (drug_id) REFERENCES warehouse (id)
        ON DELETE RESTRICT
        ON UPDATE NO ACTION,
    CHECK ( quantity > 0 AND times > 0 AND dose != '')
);
CREATE TABLE IF NOT EXISTS sampleprescription (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS linesampleprescription (
    id INTEGER PRIMARY KEY,
    drug_id INTEGER NOT NULL,
    sample_id INTEGER NOT NULL,
    times INTEGER NOT NULL,
    dose TEXT NOT NULL,
    FOREIGN KEY (drug_id) REFERENCES warehouse (id)
        ON DELETE RESTRICT
        ON UPDATE NO ACTION,
    FOREIGN KEY (sample_id) REFERENCES sampleprescription (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CHECK (times > 0 AND dose != ''),
    UNIQUE (drug_id, sample_id)
);
CREATE TABLE IF NOT EXISTS procedures (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    price INTEGER NOT NULL,
    CHECK (price >= 0)
);
CREATE TABLE IF NOT EXISTS lineprocedure (
    id INTEGER PRIMARY KEY,
    procedure_id INTEGER NOT NULL,
    visit_id INTEGER NOT NULL,
    FOREIGN KEY (visit_id) REFERENCES visits (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (procedure_id) REFERENCES procedures (id)
        ON DELETE RESTRICT
        ON UPDATE NO ACTION
);


CREATE INDEX IF NOT EXISTS patient_name ON patients (name);
CREATE INDEX IF NOT EXISTS procedure_name ON procedures (name);
CREATE INDEX IF NOT EXISTS drug_name ON warehouse (name);
CREATE INDEX IF NOT EXISTS drug_element ON warehouse (element);


CREATE VIEW IF NOT EXISTS queue_view AS
    SELECT
        p.id AS pid,
        p.name,
        p.gender,
        p.birthdate,
        q.added_datetime
    FROM queue AS q
    JOIN patients AS p
    ON q.patient_id = p.id
    ORDER BY q.added_datetime ASC
;
CREATE VIEW IF NOT EXISTS seen_today_view AS
    SELECT
        p.id AS pid,
        p.name,
        p.gender,
        p.birthdate,
        v.id as vid,
        v.exam_datetime
    FROM seen_today AS st
    JOIN patients AS p
    ON st.patient_id = p.id
    JOIN visits as v
    ON st.visit_id = v.id
    ORDER BY v.exam_datetime DESC
;
CREATE VIEW IF NOT EXISTS appointments_view AS
    SELECT
        p.id AS pid,
        p.name,
        p.gender,
        p.birthdate
    FROM appointments AS a
    JOIN patients AS p
    ON a.patient_id = p.id
    WHERE DATE(a.appointed_date, 'localtime') = DATE('now', 'localtime')
;

CREATE TRIGGER IF NOT EXISTS last_open_date_update
AFTER UPDATE OF last_open_date ON singleton 
WHEN DATE(OLD.last_open_date, 'localtime') < DATE(NEW.last_open_date, 'localtime')
BEGIN
DELETE FROM seen_today; 
DELETE FROM appointments 
    WHERE DATE(appointments.appointed_date, 'localtime') < DATE('now','localtime');
END;

CREATE TRIGGER IF NOT EXISTS linedrug_insert 
BEFORE INSERT ON linedrugs
BEGIN
UPDATE warehouse SET quantity = quantity - NEW.quantity
    WHERE id = NEW.drug_id;
END;

CREATE TRIGGER IF NOT EXISTS linedrug_delete
BEFORE DELETE ON linedrugs
BEGIN
UPDATE warehouse SET quantity = quantity + OLD.quantity
    WHERE id = OLD.drug_id;
END;

CREATE TRIGGER IF NOT EXISTS linedrug_update
BEFORE UPDATE ON linedrugs
WHEN NEW.drug_id = OLD.drug_id
BEGIN
UPDATE warehouse SET quantity = quantity + OLD.quantity - NEW.quantity
    WHERE id = OLD.drug_id;
END;

CREATE TRIGGER IF NOT EXISTS visit_insert
BEFORE INSERT ON visits
BEGIN
DELETE FROM queue
    WHERE patient_id = NEW.patient_id;
END;

INSERT OR IGNORE INTO singleton (id, last_open_date) VALUES ( 1, DATE('now', 'localtime'));

