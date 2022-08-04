from db.db_func import Connection
from db.db_class import *
from paths import SAMPLE_DIR, MY_DATABASE_PATH

import os
import csv
import datetime as dt
import decimal


class CSVReader(csv.DictReader):
    def __init__(self, t: type[BASE], csvfilepath: str):
        self.t = t
        self.csvfile = open(csvfilepath, 'r', encoding='utf-8')
        self.fields = self.csvfile.readline().strip().split(',')
        self.csvfile.seek(0)
        super().__init__(self.csvfile)

    def get_type(self):
        return self.t

    def parse(self, row):
        for n, t in self.t.__annotations__.items():
            if t == int:
                row[n] = int(row[n])
            elif t == Gender:
                row[n] = Gender(int(row[n]))
            elif t == dt.date:
                row[n] = dt.date.fromisoformat(row[n])
            elif t == dt.datetime:
                row[n] = dt.datetime.fromisoformat(row[n])
            elif t == Decimal:
                row[n] = Decimal(row[n])
            elif t == str | None:
                if row[n] == '':
                    row[n] = None
        return self.t(**row)

    def __iter__(self):
        return super().__iter__()

    def __next__(self):
        res = self.parse(super().__next__())
        if res is not None:
            return res
        else:
            raise StopIteration

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.csvfile.close()

    def close(self):
        self.csvfile.close()


def make_sample():
    def f(s): return os.path.join(SAMPLE_DIR, s)

    con = Connection(MY_DATABASE_PATH)
    for reader in [
        CSVReader(Warehouse, f('warehouse.csv')),
        CSVReader(Procedure, f('procedures.csv')),
        CSVReader(Patient, f('patients.csv')),
        CSVReader(Visit, f('visits.csv')),
        CSVReader(LineDrug, f('linedrugs.csv')),
        CSVReader(LineProcedure, f('lineprocedure.csv')),
        CSVReader(QueueList, f('queuelist.csv')),
        CSVReader(SamplePrescription, f('sampleprescription.csv')),
        CSVReader(LineSamplePrescription, f('linesampleprescription.csv')),
    ]:
        with con.sqlcon as sqlcon:
            sqlcon.executemany(f"""
                INSERT INTO {reader.t.table_name} ({','.join(reader.fields)})
                VALUES ({','.join(['?']* len(reader.fields))})
            """, (
                tuple(getattr(row, attr)
                      for attr in reader.fields)
                for row in reader
            ))
        reader.close()
    con.insert(Visit, {
        "diagnosis": "Viêm ruột thừa",
        "weight": decimal.Decimal(10),
        "days": 2,
        "recheck": 2,
        "patient_id": 6,
        "follow": "follow",
        "vnote": "dynamic created"
    })
    con.close()
    print('Sample populized')


if __name__ == '__main__':
    make_sample()
