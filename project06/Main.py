"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing
from SymbolTable import SymbolTable
from Parser import Parser
from Code import Code


def is_shift(input_string: str) -> bool:
    """Checks if a given binary computation pattern corresponds to a shift operation."""
    valid_patterns = {"1010100000", "1010110000", "1011100000", "1010000000", "1010010000", "1011000000"}
    return input_string in valid_patterns


def translate_to_binary(a) -> str:
    """Converts a given integer value to a 16-bit binary string."""
    a_temp = int(a)
    str_ = ""
    for i in range(15, -1, -1):
        b = pow(2, i)
        if b <= a_temp:
            str_ += "1"
            a_temp = a_temp - b
        else:
            str_ += "0"
    return str_


def assemble_file(input_file: typing.TextIO, output_file: typing.TextIO) -> None:
    """Assembles a single file.

    Args:
        input_file (typing.TextIO): the file to assemble.
        output_file (typing.TextIO): writes all output to this file.
    """
    parser_first = Parser(input_file)
    symboltable = SymbolTable()
    text = ""
    counter_code = 0

    while parser_first.has_more_commands():
        symb = parser_first.command_type()
        if symb == "L_COMMAND":
            l_command = parser_first.symbol()
            symboltable.add_entry(l_command, counter_code)
        elif symb == "C_COMMAND" or symb == "A_COMMAND":
            counter_code += 1
        parser_first.advance()
    rom = 16
    input_file.seek(0)
    parser_second = Parser(input_file)
    while parser_second.has_more_commands():
        symb = parser_second.command_type()
        if symb == "C_COMMAND":
            binary_dest = Code.dest(parser_second.dest())
            binary_comp = Code.comp(parser_second.comp())
            binary_jump = Code.jump(parser_second.jump())
            if is_shift(binary_comp):
                binary = str(binary_comp) + str(binary_dest) + str(binary_jump)
            else:
                binary = "111" + str(binary_comp) + str(binary_dest) + str(binary_jump)
        elif symb == "A_COMMAND":
            a_command = parser_second.symbol()
            if symboltable.contains(a_command):
                address = symboltable.get_address(a_command)
                binary = translate_to_binary(address)
            else:
                if a_command.isnumeric():
                    binary = translate_to_binary(a_command)
                else:
                    symboltable.add_entry(a_command, rom)
                    address = symboltable.get_address(a_command)
                    binary = translate_to_binary(address)
                    rom += 1
        else:
            parser_second.advance()
            continue
        text = text + str(binary) + "\n"
        parser_second.advance()

    output_file.write(text)


if "__main__" == __name__:
    # Parses the input path and calls assemble_file on each input file.
    # This opens both the input and the output files!
    # Both are closed automatically when the code finishes running.
    # If the output file does not exist, it is created automatically in the
    # correct path, using the correct filename.
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: Assembler <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_assemble = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
    else:
        files_to_assemble = [argument_path]
    for input_path in files_to_assemble:
        filename, extension = os.path.splitext(input_path)
        if extension.lower() != ".asm":
            continue
        output_path = filename + ".hack"
        with open(input_path, 'r') as input_file, \
                open(output_path, 'w') as output_file:
            assemble_file(input_file, output_file)
