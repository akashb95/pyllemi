from dataclasses import dataclass
from enum import unique, IntEnum

from common.logger.logger import setup_logger

LOGGER = setup_logger(__name__)


@unique
class Type(IntEnum):
    UNKNOWN = 0
    MODULE = 1
    PACKAGE = 2
    STUB = 3
    THIRD_PARTY_MODULE = 4
    PROTOBUF_GEN = 5


@dataclass
class Import:
    import_: str
    type_: Type

    def __eq__(self, other: "Import") -> bool:
        return self.import_ == other.import_ and self.type_ == other.type_

    @property
    def type(self):
        return self.type_
