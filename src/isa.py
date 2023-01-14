from json import loads, dumps
from enum import Enum
from typing import Optional
from random import randint


_MAX_NUMBER = 2 ** 63 - 1
_NUMBER_MASK = 2 ** 64 - 1


class Opcode(Enum):
    hlt: int = 0
    ld: int = 1
    sv: int = 2
    prt: int = 3
    rd: int = 4
    add: int = 5
    sub: int = 6
    mul: int = 7
    div: int = 8
    cmp: int = 9
    jmp: int = 10
    je: int = 11
    jne: int = 12
    jg: int = 13
    jl: int = 14
    jc: int = 15
    pprt: int = 16


class Mapping(Enum):
    data: int = 0
    pointer: int = 1
    label: int = 2


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
            self.type = Mapping.data
        if not self.operation:
            return '"value":"{}"'.format(self.value)
        return '"operation":"{}","operand":"{}","type":"{}"'.format(self.operation, self.operand, self.type.name)


def parse_data_from_raw(raw) -> Optional[list[DataCell]]:
    if type(raw) is int:
        return [DataCell(raw)]
    elif type(raw) is str:
        return [DataCell(ord(char)) for char in raw] + [DataCell(0)]
    else:
        return None


def parse_command_from_raw(raw: dict) -> DataCell:
    command = DataCell()
    command.operand = raw['operand'] if raw['operand'] != 'None' else None
    for operation in Opcode.__iter__():
        if operation.name == raw['operation']:
            command.operation = operation
    for mapping in Mapping.__iter__():
        if mapping.name == raw['type']:
            command.type = mapping
    return command


def write_program_file(filename, program):
    with open(filename, "w") as file:
        file.write(dumps(program, indent=4))


def read_program_file(filename):
    with open(filename, "r") as file:
        program = loads(file.read())
        return program


def read_input_file(filename):
    with open(filename, "r") as file:
        input_file = loads(file.read())
        return input_file
