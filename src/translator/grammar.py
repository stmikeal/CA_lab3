from enum import Enum
from typing import Callable
from re import compile, match

class Register(Enum):
    eax : int = 0
    ebx : int = 1
    ecx : int = 2
    edx : int = 3
    esi : int = 4
    edi : int = 5
    esp : int = 6
    eip : int = 7
    r8  : int = 8
    r9  : int = 9
    r10 : int = 10
    r11 : int = 11
    r12 : int = 12
    r13 : int = 13
    r14 : int = 14
    r15 : int = 15

class Operation0(Enum):
    ret : int = 0
    nop : int = 1

class Operation1_s(Enum):
    push    : int = 0
    mul     : int = 1
    div     : int = 2
    test    : int = 3

class Operation1_mem(Enum):
    pop     : int = 0
    inc     : int = 1
    dec     : int = 2
    neg     : int = 3
    not_op  : int = 4

class Operation2(Enum):
    mov     : int = 0
    add     : int = 1
    sub     : int = 2
    cmp     : int = 3
    xor     : int = 4
    and_op  : int = 5
    or_op   : int = 6

class Operation_jump(Enum):
    jmp     : int = 0
    je      : int = 1
    jne     : int = 2
    jg      : int = 3
    jl      : int = 4
    jng     : int = 5
    jnl     : int = 6
    loop    : int = 7
    call    : int = 8

class TokenInfo:
    def __init__(self, pattern : str) -> None:
        self.pattern = pattern
        self.regex   = compile('^(?:' + pattern + ')$')

class Token(Enum):
    number  : TokenInfo = TokenInfo(r'(?:[1-9]\d*|0)|0x(?:\d|[AaBbCcDdEeFf])+|0b[01]+')
    reg     : TokenInfo = TokenInfo(r'(eax)|(ebx)|(ecx)|(edx)|(esi)|(edi)|(esp)|(eip)|(r8)|(r9)|(r10)|(r11)|(r12)|(r13)|(r14)|(r15)')
    op0     : TokenInfo = TokenInfo(r"(ret)|(nop)")
    s_op1   : TokenInfo = TokenInfo(r"(push)|(mul)|(div)|(test)")
    mem_op1 : TokenInfo = TokenInfo(r"(pop)|(inc)|(dec)|(neg)|(not)")
    op2     : TokenInfo = TokenInfo(r"(mov)|(add)|(sub)|(cmp)|(xor)|(and)|(or)")
    jump_op : TokenInfo = TokenInfo(r"(jmp)|(je)|(jne)|(jg)|(jl)|(jng)|(jnl)|(loop)|(call)")
    string  : TokenInfo = TokenInfo(r"[a-zA-Z]\w*")

macro_regex = compile(r"^%define .+$")
pointer_regex = compile(r"^\w+\s+dd\s+[1-9]\d*$")

token_func : dict[Token : Enum] = {
    Token.reg       : Register,
    Token.op0       : Operation0,
    Token.s_op1     : Operation1_s,
    Token.mem_op1   : Operation1_mem,
    Token.op2       : Operation2,
    Token.jump_op   : Operation_jump
}

