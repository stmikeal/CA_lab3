from enum import Enum
from typing import Union
from isa import Opcode, Command, Mapping
from io import TextIOWrapper
from re import Match, sub, match
from sys import argv

single_opcode = [Opcode.prt, Opcode.rd, Opcode.hlt]

class Token(Enum):
    command     = r"^(" + "|".join(op.name for op in Opcode.__iter__() if op not in single_opcode) + \
            r")\s+(\@?|#?)(0|[1-9]\d*)|(" + "|".join(op.name for op in single_opcode) +  ")$"
    label       = r"^(\.[a-zA-Z]\w*)\:$"
    pointer     = r"^(\w+)\s+(0|[1-9]\d*)$"

class SysLabel(Enum):
    data        = ".data"
    programm    = ".text"

class Translator:
    def __init__(self) -> None:
        self.program_section : int = None
        self.labels     = []
        self.pointers   = []
        self.pvalues    = dict()
        self.lvalues    = dict()
        self.program : list[Command]   = []

    def __insert_mapping(self, line : str) -> str:
        line = line.split()
        if len(line) == 2:
            for nlabel in range(len(self.labels)):
                if line[1] == self.labels[nlabel]:
                    line[1] = "#" + str(nlabel)
            for npointer in range(len(self.pointers)):
                if line[1] == self.pointers[npointer]:
                    line[1] = "@" + str(npointer)
        return " ".join(line)
    
    def parse_line(self, line : str) -> dict[str, Union[Token, Match]]:
        line = self.__insert_mapping(line)
        for token in Token.__iter__():
            matched : Match = match(token.value, line)
            if matched:
                return {"token" : token, "match" : matched}
        return None

    def _trim_line(self, line : str) -> str:
        return sub(r"^\s+", "", sub(r"\s+$", "", sub(r"\s+", " ", line)))

    def __file_analize(self, file : list[str]) -> None:
        line_counter        : int= 0
        current_section     : SysLabel= None
        for line in file:
            line_counter += 1
            line = self._trim_line(line)
            if not line or not len(line):
                continue
            line = self.parse_line(line)
            if not line:
                continue

            if line["token"] == Token.label:
                if not current_section and line["match"].groups()[0] == SysLabel.data.value:
                    current_section = SysLabel.data
                    continue
                elif current_section == SysLabel.data and line["match"].groups()[0] == SysLabel.programm.value:
                    current_section = SysLabel.programm
                    self.program_section = line_counter
                    continue

            if current_section == SysLabel.data:
                if line["match"].groups()[0] not in self.pointers:
                    self.pointers.append(line["match"].groups()[0])
                    self.pvalues[line["match"].groups()[0]] = int(line["match"].groups()[1])
                else:
                    raise SyntaxError("Not unique pointer at line: {}".format(str(line_counter)))

            if line["token"] == Token.label:
                self.labels.append(line["match"].groups()[0])

    def parse_file(self, file : TextIOWrapper) -> None:
        lines = file.readlines()
        self.__file_analize(lines)
        if not self.program_section:
            raise SyntaxError("Can't find start of programm")
        line_counter        : int= self.program_section
        instruction_counter : int= 0
        for line in lines[self.program_section:]:
            line_counter += 1
            line = self._trim_line(line)
            if not line or not len(line):
                continue
            line = self.parse_line(line)

            if not line or line["token"] == Token.pointer:
                raise SyntaxError("Syntax Error at line: {}".format(str(line_counter)))
            
            if line["token"] == Token.label:
                self.lvalues[line["match"].groups()[0]] = instruction_counter
            
            if line["token"] == Token.command:
                command : Command = Command()
                type = line["match"].groups()[0]
                command.operation = line["match"].groups()[0 if type else 3]
                if type:
                    command.type = (Mapping.label if line["match"].groups()[1]=='#' else Mapping.pointer) if len(line["match"].groups()[1]) else Mapping.data
                    command.operand = line["match"].groups()[2]
                self.program.append(command)
                instruction_counter += 1
        if 'hlt' not in [p.operation for p in self.program]:
            raise SyntaxError("Can't find end of programm")

    def __str__(self) -> str:
        labels      : str = str(self.lvalues).replace("'", '"')
        pointers    : str = str(self.pvalues).replace("'", '"')
        program     : str = "[{}]".format(", ".join(["{" + "{}".format(str(p)) + "}" for p in self.program]))
        return "{" + '"labels":{},"pointers":{},"program":{}'.format(labels, pointers, program) + "}"

            
            
if __name__ == "__main__":
    t = Translator()
    if len(argv) == 3:
        with open(argv[1], "r") as f:
            t.parse_file(f)
        with open(argv[2], "w") as f:
            f.write(str(t))
    else:
        raise AttributeError("Need 2 files to read and to write.")
