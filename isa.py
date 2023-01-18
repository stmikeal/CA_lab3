# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=line-too-long
# pylint: disable=too-few-public-methods)
from json import loads, dumps
from enum import Enum
from typing import Optional
from random import randint


_MAX_NUMBER = 2 ** 63 - 1
_NUMBER_MASK = 2 ** 64 - 1


class Opcode(Enum):
    HLT: int = 0
    LD: int = 1
    SV: int = 2
    PRT: int = 3
    RD: int = 4
    ADD: int = 5
    SUB: int = 6
    MUL: int = 7
    DIV: int = 8
    CMP: int = 9
    JMP: int = 10
    JE: int = 11
    JNE: int = 12
    JG: int = 13
    JL: int = 14
    JC: int = 15
    PPRT: int = 16


class Mapping(Enum):
    DATA: int = 0
    POINTER: int = 1
    LABEL: int = 2


class DataCell:
    def __init__(self, value=None) -> None:
        if value is None:
            self.value = randint(-_MAX_NUMBER, _MAX_NUMBER)
        else:
            self.value = value
        self.operand: Optional[str] = None
        self.operation: Optional[Opcode] = None
        self.type: Optional[Mapping] = None

    def __str__(self) -> str:
        if not self.type:
            self.type = Mapping.DATA
        if not self.operation:
            return f'"value":"{self.value}"'
        return f'"operation":"{self.operation}","operand":"{self.operand}","type":"{self.type.name}"'


def parse_data_from_raw(raw) -> Optional[list[DataCell]]:
    if isinstance(raw, int):
        return [DataCell(raw)]
    if isinstance(raw, str):
        return [DataCell(ord(char)) for char in raw] + [DataCell(0)]
    return None


def parse_command_from_raw(raw: dict) -> DataCell:
    command = DataCell()
    command.operand = raw['operand'] if raw['operand'] != 'None' else None
    for operation in Opcode.__iter__():
        if operation.name.lower() == raw['operation']:
            command.operation = operation
    for mapping in Mapping.__iter__():
        if mapping.name == raw['type']:
            command.type = mapping
    return command


def write_program_file(filename, program):
    with open(filename, "w", encoding='utf-8') as file:
        file.write(dumps(program, indent=4))


def read_program_file(filename):
    with open(filename, "r", encoding='utf-8') as file:
        program = loads(file.read())
        return program


def read_input_file(filename):
    with open(filename, "r", encoding='utf-8') as file:
        input_file = loads(file.read())
        return input_file
