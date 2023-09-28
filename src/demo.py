import csv
import datetime as dt
import os

from db import *
from main import App, platform_settings
from misc import SAMPLE_DIR


class CSVReader(csv.DictReader):
    def __init__(self, t: type[BASE], csvfilepath: str):
        self.t = t
        self.csvfile = open(csvfilepath, "r", encoding="utf-8")
        self.fields = self.csvfile.readline().strip().split(",")
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
            elif t == str | None:
                if row[n] == "":
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


def sample_con():
    con = Connection(":memory:")
    con.make_db()

    def f(s):
        return os.path.join(SAMPLE_DIR, s)

    for reader in [
        CSVReader(Warehouse, f("warehouse.csv")),
        CSVReader(Procedure, f("procedures.csv")),
        CSVReader(Patient, f("patients.csv")),
        CSVReader(Visit, f("visits.csv")),
        CSVReader(LineDrug, f("linedrugs.csv")),
        CSVReader(LineProcedure, f("lineprocedures.csv")),
        CSVReader(Queue, f("queue.csv")),
        CSVReader(SamplePrescription, f("sampleprescription.csv")),
        CSVReader(LineSamplePrescription, f("linesampleprescription.csv")),
    ]:
        with con:
            con.executemany(
                f"""
                INSERT INTO {reader.t.__tablename__} ({','.join(reader.fields)})
                VALUES ({','.join(['?']* len(reader.fields))})
            """,
                (tuple(getattr(row, attr) for attr in reader.fields) for row in reader),
            )
        reader.close()
    con.insert(
        Visit,
        {
            "diagnosis": "Viêm ruột thừa",
            "weight": 10,
            "days": 2,
            "recheck": 2,
            "price": 1000000,
            "patient_id": 6,
            "follow": "follow",
            "vnote": "fake",
            "temperature": 375,
            "height": 100,
        },
    )
    print("Fake data generated")
    return con


if __name__ == "__main__":
    connection = sample_con()
    platform_settings()
    App(connection)
