# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=line-too-long
from io import TextIOWrapper
from re import Match, sub, match
from sys import argv
from enum import Enum
from typing import Union
from isa import Opcode, DataCell, Mapping

single_opcode = [Opcode.PRT, Opcode.RD, Opcode.HLT]


class Token(Enum):
    COMMAND: str = r"^(" + "|".join(op.name.lower() for op in Opcode.__iter__() if op not in single_opcode) + \
                   r")\s+(\@?|#?)(0|[1-9]\d*)|(" + "|".join(op.name.lower() for op in single_opcode) + ")$"
    LABEL: str = r"^(\.[a-zA-Z]\w*)\:$"
    POINTER: str = r"^(\w+)\s+(0|[1-9]\d*|(?:\'.+\'))$"


class SysLabel(Enum):
    DATA = ".data"
    PROGRAMM = ".text"


def trim_line(line: str) -> str:
    return sub(r"//.*", "", sub(r"^\s+", "", sub(r"\s+$", "", sub(r"\s+", " ", line))))


class Translator:
    def __init__(self) -> None:
        self.program_section: int = -1
        self.labels = []
        self.pointers = []
        self.pvalues = {}
        self.lvalues = {}
        self.program: list[DataCell] = []

    def __insert_mapping(self, line: str) -> str:
        line = line.split()
        if len(line) == 2:
            for nlabel, _ in enumerate(self.labels):
                if line[1] == self.labels[nlabel]:
                    line[1] = "#" + str(nlabel)
            for npointer, _ in enumerate(self.pointers):
                if line[1] == self.pointers[npointer]:
                    line[1] = "@" + str(npointer)
        return " ".join(line)

    def parse_line(self, line: str) -> dict[str, Union[Token, Match]]:
        line = self.__insert_mapping(line)
        for token in Token.__iter__():
            matched: Match = match(token.value, line)
            if matched:
                return {"token": token, "match": matched}
        return None

    def __file_analize(self, file: list[str]) -> None:
        line_counter: int = 0
        current_section: SysLabel = None
        for line in file:
            line_counter += 1
            line = trim_line(line)
            if not line:
                continue
            line = self.parse_line(line)
            if not line:
                continue

            if line["token"] == Token.LABEL:
                if not current_section and line["match"].groups()[0] == SysLabel.DATA.value:
                    current_section = SysLabel.DATA
                    continue
                if current_section != SysLabel.PROGRAMM and line["match"].groups()[0] == SysLabel.PROGRAMM.value:
                    current_section = SysLabel.PROGRAMM
                    self.program_section = line_counter
                    continue

            if current_section == SysLabel.DATA:
                if line["match"].groups()[0] not in self.pointers:
                    self.pointers.append(line["match"].groups()[0])
                    val = line["match"].groups()[1]
                    self.pvalues[str(len(self.pointers) - 1)] = int(val) if val[0] != "'" else val
                else:
                    raise SyntaxError(f"Not unique pointer at line: {str(line_counter)}")

            if line["token"] == Token.LABEL:
                self.labels.append(line["match"].groups()[0])

    def parse_file(self, file: TextIOWrapper) -> None:
        lines = file.readlines()
        self.__file_analize(lines)
        if self.program_section < 0:
            raise SyntaxError("Can't find start of programm")
        line_counter: int = self.program_section
        instruction_counter: int = 0
        for line in lines[self.program_section:]:
            line_counter += 1
            line = trim_line(line)
            if not line:
                continue
            line = self.parse_line(line)

            if not line or line["token"] == Token.POINTER:
                raise SyntaxError(f"Syntax Error at line: {str(line_counter)}")

            if line["token"] == Token.LABEL:
                self.lvalues[str(self.labels.index(line["match"].groups()[0]))] = instruction_counter

            if line["token"] == Token.COMMAND:
                command: DataCell = DataCell()
                type_of_programm = line["match"].groups()[0]
                command.operation = line["match"].groups()[0 if type_of_programm else 3]
                if type_of_programm:
                    command.type = (Mapping.LABEL if line["match"].groups()[1] == '#' else Mapping.POINTER) if len(
                        line["match"].groups()[1]) else Mapping.DATA
                    command.operand = line["match"].groups()[2]
                self.program.append(command)
                instruction_counter += 1
        if 'hlt' not in [p.operation for p in self.program]:
            raise SyntaxError("Can't find end of programm")

    def __str__(self) -> str:
        labels: str = str(self.lvalues).replace("'", '"')
        pointers = "{" + ", ".join('"' + p_key + '"' + ": " + str(p_value).replace("'", '"') for p_key, p_value in self.pvalues.items()) + "}"
        program: str = f'[{", ".join(["{" + f"{str(p)}" + "}" for p in self.program])}]'
        return "{" + f'"labels":{labels},"pointers":{pointers},"program":{program}' + "}"


def main(arg):
    trans = Translator()
    if len(arg) == 3:
        with open(arg[1], "r", encoding='utf-8') as output_file:
            trans.parse_file(output_file)
        with open(arg[2], "w", encoding='utf-8') as output_file:
            output_file.write(str(trans))
    else:
        raise AttributeError("Need 2 files to read and to write.")


if __name__ == "__main__":
    main(argv)
