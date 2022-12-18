from parsertools import Parser, Operation
from sys import argv

if __name__ == "__main__":
    parser : Parser = Parser()
    filename_read = r"C:\\Data\\Labs\\CA\\Lab3\\src\\asm\\prob5.asm"
    #filename_write = argv[2]
    with open(filename_read, "r") as file:
        line = file.readline()
        while line:
            parser.parse_macro(line)
            line = file.readline()
    with open(filename_read, "r") as file:
        line = file.readline()
        while line:
            op : Operation = parser.parse_operation(line)
            if op:
                print(op)
            line = file.readline()
