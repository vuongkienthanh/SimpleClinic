import state
from db import Connection, Warehouse


class AllWarehouseState:
    def __get__(self, obj: "state.main_state.State", _) -> dict[int, Warehouse]:
        return obj._all_warehouse

    def __set__(self, obj: "state.main_state.State", _dict: dict[int, Warehouse]):
        obj._all_warehouse = _dict

    @staticmethod
    def fetch(connection: Connection):
        return connection.selectall(Warehouse)
