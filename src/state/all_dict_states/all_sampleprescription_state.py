import state
from db import Connection, SamplePrescription


class AllSamplePrescriptionState:
    def __get__(
        self, obj: "state.main_state.State", _
    ) -> dict[int, SamplePrescription]:
        return obj._all_sampleprescription

    def __set__(
        self, obj: "state.main_state.State", _dict: dict[int, SamplePrescription]
    ):
        obj._all_sampleprescription = _dict

    @staticmethod
    def fetch(connection: Connection):
        return connection.selectall(SamplePrescription)
