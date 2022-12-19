from enum import Enum
import re

class Opcode(Enum):
    data    : int = 0
    ld      : int = 1
    sv      : int = 2
    prt     : int = 3
    rd      : int = 4
    add     : int = 5
    sub     : int = 6
    mul     : int = 7
    div     : int = 8
    cmp     : int = 9
    jmp     : int = 10
    je      : int = 11
    jne     : int = 12
    jg      : int = 13
    jl      : int = 14
    jc      : int = 15
    hlt     : int = 16

class Mapping(Enum):
    data    : int = 0
    pointer : int = 1
    label   : int = 2

class Command:
    def __init__(self) -> None:
        self.operand    : str       = None
        self.operation  : str       = None 
        self.type       : Mapping   = None
    def __str__(self) -> str:
        if not self.type:
            self.type = Mapping.data
        return '"operation":"{}","operand":"{}","type":"{}"'.format(self.operation, self.operand, self.type.name)