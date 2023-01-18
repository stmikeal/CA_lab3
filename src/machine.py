# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=line-too-long
import logging
import sys
from enum import Enum
from isa import _NUMBER_MASK, DataCell, read_program_file, read_input_file, parse_command_from_raw, \
    parse_data_from_raw, Opcode, Mapping

OUTPUT_BUFFER_SIZE = 20
EXECUTE_LIMIT = 4000


class SigAccCode(Enum):
    ALU = 0
    MEM = 1
    RAW = 2
    INC = 3


class SigAddrCode(Enum):
    RAW = 0
    RD = 1
    PRT = 2
    REL = 3


class SigIpCode(Enum):
    INC = 0
    RAW = 1


class SigStepCode(Enum):
    INC = 0
    ZERO = 1


class SigArgCode(Enum):
    RAW = 0
    MEM = 1
    ZERO = 2


class Machine:
    def __init__(self, code):
        # Инициализация регистров
        self._tick = 0
        self._step_counter = 0
        self._addr = 0
        self._ip = 0
        self._acc = 0
        self._rd = 0
        self._wr = 0
        self._output_buffer_counter = 1
        self._ic = 0

        # Инициализация флагов
        self._zero = True
        self._carry = False
        self._positive = True

        # Инициализация памяти и 'линковка'
        self._labels = {}
        self._pointers = {}
        self._program = code
        # Сначала заполняем память командами
        self._memory: list[DataCell] = [parse_command_from_raw(command) for command in code]

        # Инициализация буфера вывода
        self._wr = len(self._memory) + 1
        self._memory += [DataCell(0)] * OUTPUT_BUFFER_SIZE

    def set_labels(self, labels=None):
        if labels is None:
            labels = []
        if not self._labels:
            self._labels = labels

    def set_input_buffer(self, input_string: list[DataCell] = None):
        if input_string is None:
            input_string = []
        self._rd = len(self._memory)
        self._memory += [DataCell(val) for val in input_string] + [DataCell(0)]

    def set_pointers(self, pointers: dict = None):
        if pointers is None:
            pointers = []
        if not self._pointers:
            for pointer in pointers:
                data = parse_data_from_raw(pointers[pointer])
                self._pointers[pointer] = len(self._memory)
                if len(data) > 1:
                    self._memory.append(DataCell(len(self._memory)))
                self._memory += data

    def tick(self):
        self._tick += 1

    def get_tick(self):
        return self._tick

    def get_ic(self):
        return self._ic

    def represent_output(self):
        res = []
        self._wr -= 1
        for p in range(self._output_buffer_counter):
            if not self._memory[self._wr - p].value:
                continue
            if 0 <= self._memory[self._wr].value <= 255:
                res = [chr(self._memory[self._wr - p].value)] + res
            else:
                res = [self._memory[self._wr - p].value] + res
        return res

    def __div__(self, arg, acc):
        self._carry = acc % arg != 0
        return acc // arg

    def alu_calculate(self, sig_arg, operation):
        alu_operations = {
            Opcode.add: lambda arg, acc: arg + acc,
            Opcode.sub: lambda arg, acc: acc - arg,
            Opcode.mul: lambda arg, acc: arg * acc,
            Opcode.div: lambda arg, acc: self.__div__(arg, acc)
        }
        operand = 0
        if sig_arg != SigArgCode.ZERO:
            operand = int(self._memory[self._ip].operand) if sig_arg == SigArgCode.RAW else self._memory[self._addr].value
            operand &= _NUMBER_MASK
        return alu_operations[operation](operand, self._acc)

    def set_flags(self, value, operation: Opcode = Opcode.add):
        if operation != Opcode.div:
            self._carry = value & _NUMBER_MASK != value
        self._zero = value & _NUMBER_MASK == 0
        self._positive = value >= 0

    def latch_acc(self, sig_acc: SigAccCode, sig_arg: SigArgCode = SigArgCode.RAW, operation: Opcode = Opcode.add):
        res = 0
        if sig_acc == SigAccCode.INC:
            res = self._acc + 1
        if sig_acc == SigAccCode.ALU:
            res = self.alu_calculate(sig_arg, operation)
        elif sig_acc == SigAccCode.MEM:
            res = self._memory[self._addr].value
        elif sig_acc == SigAccCode.RAW:
            res = int(self._memory[self._ip].operand)
        self._acc = res & _NUMBER_MASK
        if sig_acc == SigAccCode.ALU:
            self.set_flags(res, operation)

    def latch_addr(self, sig_addr=SigAddrCode.RAW):
        if sig_addr == SigAddrCode.RAW:
            self._addr = self._pointers[self._memory[self._ip].operand] & _NUMBER_MASK
        if sig_addr == SigAddrCode.RD:
            self._addr = self._rd
            self._rd += 1
        if sig_addr == SigAddrCode.PRT:
            self._addr = self._wr
            self._wr += 1
        if sig_addr == SigAddrCode.REL:
            self._addr = self._memory[self._addr].value

    def latch_step_counter(self, sig_step):
        self._step_counter = 0 if sig_step == SigStepCode.ZERO else self._step_counter + 1

    def latch_ip(self, sig_ip):
        self._ic += 1
        self._ip = self._labels[self._memory[self._ip].operand] if sig_ip == SigIpCode.RAW else self._ip + 1

    def latch_mem(self):
        self._memory[self._addr] = DataCell(self._acc)

    __op_transition = (Opcode.jc, Opcode.je, Opcode.jg, Opcode.jl, Opcode.jmp, Opcode.jne)
    __op_arithmetic = (Opcode.add, Opcode.sub, Opcode.mul, Opcode.div)

    def decode_and_execute(self):
        command = self._memory[self._ip]
        operation: Opcode = command.operation
        self.tick()

        if operation in self.__op_transition:
            transition = operation == Opcode.jc and self._carry
            transition |= operation == Opcode.je and self._zero
            transition |= operation == Opcode.jg and self._positive
            transition |= operation == Opcode.jl and not self._positive
            transition |= operation == Opcode.jmp
            transition |= operation == Opcode.jne and not self._zero
            self.latch_ip(SigIpCode.RAW if transition else SigIpCode.INC)

        if operation == Opcode.ld:
            if command.type == Mapping.pointer:
                if not self._step_counter:
                    self.latch_addr()
                    self.latch_step_counter(SigStepCode.INC)
                else:
                    self.latch_acc(SigAccCode.MEM)
                    self.latch_step_counter(SigStepCode.ZERO)
                    self.latch_ip(SigIpCode.INC)
            else:
                self.latch_acc(SigAccCode.RAW)
                self.latch_ip(SigIpCode.INC)

        if operation == Opcode.sv:
            if not self._step_counter:
                self.latch_addr()
                self.latch_step_counter(SigStepCode.INC)
            else:
                self.latch_mem()
                self.latch_step_counter(SigStepCode.ZERO)
                self.latch_ip(SigIpCode.INC)

        if operation == Opcode.cmp:
            if command.type == Mapping.pointer:
                if not self._step_counter:
                    self.latch_addr()
                    self.latch_step_counter(SigStepCode.INC)
                else:
                    res = self.alu_calculate(SigArgCode.MEM, Opcode.sub)
                    self.set_flags(res)
                    self.latch_step_counter(SigStepCode.ZERO)
                    self.latch_ip(SigIpCode.INC)
            else:
                res = self.alu_calculate(SigArgCode.RAW, Opcode.sub)
                self.set_flags(res)
                self.latch_ip(SigIpCode.INC)

        if operation in self.__op_arithmetic:
            if command.type == Mapping.pointer:
                if not self._step_counter:
                    self.latch_addr()
                    self.latch_step_counter(SigStepCode.INC)
                else:
                    self.latch_acc(SigAccCode.ALU, SigArgCode.MEM, operation)
                    self.latch_step_counter(SigStepCode.ZERO)
                    self.latch_ip(SigIpCode.INC)
            else:
                self.latch_acc(SigAccCode.ALU, SigArgCode.RAW, operation)
                self.latch_ip(SigIpCode.INC)

        if operation == Opcode.rd:
            if not self._step_counter:
                self.latch_addr(SigAddrCode.RD)
                self.latch_step_counter(SigStepCode.INC)
            else:
                self.latch_acc(SigAccCode.MEM)
                self.set_flags(self._acc)
                self.latch_step_counter(SigStepCode.ZERO)
                self.latch_ip(SigIpCode.INC)

        if operation == Opcode.prt:
            if not self._step_counter:
                self.latch_addr(SigAddrCode.PRT)
                self.latch_step_counter(SigStepCode.INC)
            else:
                self.latch_mem()
                self.latch_step_counter(SigStepCode.ZERO)
                self._output_buffer_counter += 1
                if self._output_buffer_counter > OUTPUT_BUFFER_SIZE:
                    raise OverflowError("Output buffer is crowded")
                self.latch_ip(SigIpCode.INC)

        if operation == Opcode.pprt:
            if self._step_counter == 0:
                self.latch_addr()
                self.latch_step_counter(SigStepCode.INC)
            elif self._step_counter == 1:
                self.latch_acc(SigAccCode.MEM)
                self.latch_step_counter(SigStepCode.INC)
            elif self._step_counter == 2:
                self.latch_acc(SigAccCode.INC)
                self.latch_step_counter(SigStepCode.INC)
            elif self._step_counter == 3:
                self.latch_mem()
                self.latch_step_counter(SigStepCode.INC)
            elif self._step_counter == 4:
                self.latch_addr(SigAddrCode.REL)
                self.latch_step_counter(SigStepCode.INC)
            elif self._step_counter == 5:
                self.latch_acc(SigAccCode.MEM)
                self.latch_step_counter(SigStepCode.INC)
            elif self._step_counter == 6:
                self.latch_acc(SigAccCode.ALU, SigArgCode.ZERO)
                self.latch_step_counter(SigStepCode.INC)
            elif self._step_counter == 7:
                self.latch_addr(SigAddrCode.PRT)
                self.latch_step_counter(SigStepCode.INC)
            elif self._step_counter == 8:
                self.latch_mem()
                self.latch_step_counter(SigStepCode.ZERO)
                self._output_buffer_counter += 1
                if self._output_buffer_counter > OUTPUT_BUFFER_SIZE:
                    raise OverflowError("Output buffer is crowded")
                self.latch_ip(SigIpCode.INC)

        if operation == Opcode.hlt:
            return False
        return True

    def __bool_to_char(self, flag: bool):
        return "1" if flag else "0"

    def __str__(self):
        return "TICK: {}, ADDR: {}, IP: {}, ACC: {}, ZCP: {}, SC: {}, WR: {}, RD: {}\nOP: {}, ARG: {}, T: {}, D: {}".format(
            self._tick,
            self._addr,
            self._ip,
            self._acc,
            self.__bool_to_char(self._zero) \
            + self.__bool_to_char(self._carry) \
            + self.__bool_to_char(self._positive),
            self._step_counter,
            self._wr,
            self._rd,
            self._memory[self._ip].operation.name,
            self._memory[self._ip].operand,
            self._memory[self._ip].type.name,
            self._memory[self._ip].value,
        )


def simulate(model: Machine) -> tuple:
    is_execute = True
    while is_execute:
        logging.debug(model)
        if model.get_ic() > EXECUTE_LIMIT:
            raise OverflowError("Instruction limit is crowded")
        is_execute = model.decode_and_execute()
    return model.represent_output(), model.get_ic(), model.get_tick()


def prepare_and_go(args) -> None:
    if 1 < len(args) < 4:
        logging.getLogger().setLevel(logging.DEBUG)
        program = read_program_file(args[1])
        input_buffer = read_input_file(args[2]) if len(args) > 2 else None
        machine = Machine(program['program'])
        machine.set_labels(program['labels'])
        machine.set_pointers(program['pointers'])
        machine.set_input_buffer(input_buffer)
        output_buffer, ip, ticks = simulate(machine)
        print("Output: {}\nInstruction Counter: {}\nTicks: {}".format(output_buffer, ip, ticks))
    else:
        print("Invalid program argument, should be: machine.py <code_filename> [<input_filename>]")


if __name__ == '__main__':
    prepare_and_go(sys.argv)
