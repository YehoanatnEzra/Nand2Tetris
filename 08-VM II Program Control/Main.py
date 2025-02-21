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
from Parser import Parser
from CodeWriter import CodeWriter


def translate_file(input_file: typing.TextIO, output_file: typing.TextIO, bootstrap: bool) -> None:
    """
    Translates a single file from VM code to Hack assembly.

    Args:
        input_file (typing.TextIO): The input VM file to translate.
        output_file (typing.TextIO): The output file where translated assembly code is written.
        bootstrap (bool): If True, writes bootstrap code at the beginning.
    """

    code_writer = CodeWriter(output_file)
    parser = Parser(input_file)
    input_filename = os.path.splitext(os.path.basename(input_file.name))[0]
    code_writer.set_file_name(input_filename)
    cur_function = "Sys.init"

    if bootstrap:
        code_writer.bootstrap_write()

    while parser.has_more_commands():
        type = parser.command_type()  # Get the command type
        suplement = cur_function

        if type == "C_ARITHMETIC":
            sub_type = parser.arg1()
            str_to_send = suplement + "$"
            code_writer.write_arithmetic(sub_type, str_to_send)
        elif type == "C_PUSH":
            arg1 = parser.arg1()
            arg2 = parser.arg2()
            code_writer.write_push_pop("C_PUSH", arg1, arg2)
        elif type == "C_POP":
            arg1 = parser.arg1()
            arg2 = parser.arg2()
            code_writer.write_push_pop("C_POP", arg1, arg2)
        elif type == "C_GOTO":
            arg1 = suplement + "$" + parser.arg1()
            code_writer.write_goto(arg1)
        elif type == "C_IF":
            arg1 = suplement + "$" + parser.arg1()
            code_writer.write_if(arg1)
        elif type == "C_LABEL":
            arg1 = suplement + "$" + parser.arg1()
            code_writer.write_label(arg1)
        elif type == "C_CALL":
            arg1 = parser.arg1()
            arg2 = parser.arg2()
            code_writer.write_call(arg1, arg2)
        elif type == "C_FUNCTION":
            arg1 = parser.arg1()
            cur_function = arg1
            arg2 = parser.arg2()
            code_writer.write_function(arg1, arg2)
        elif type == "C_RETURN":
            code_writer.write_return()

        parser.advance()


if "__main__" == __name__:
    # Parses the input path and calls translate_file on each input file.
    # This opens both the input and the output files!
    # Both are closed automatically when the code finishes running.
    # If the output file does not exist, it is created automatically in the
    # correct path, using the correct filename.
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: VMtranslator <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_translate = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
        output_path = os.path.join(argument_path, os.path.basename(argument_path))

    else:
        files_to_translate = [argument_path]
        output_path, extension = os.path.splitext(argument_path)
    output_path += ".asm"
    bootstrap = True
    with open(output_path, 'w') as output_file:
        for input_path in files_to_translate:
            filename, extension = os.path.splitext(input_path)
            if extension.lower() != ".vm":
                continue
            with open(input_path, 'r') as input_file:
                translate_file(input_file, output_file, bootstrap)
            bootstrap = False
