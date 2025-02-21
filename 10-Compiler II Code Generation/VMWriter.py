"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class VMWriter:
    """
    Writes VM commands into a file. Encapsulates the VM command syntax.
    """

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Creates a new file and prepares it for writing VM commands."""
        self.output_stream = output_stream

    def write_push(self, segment: str, index: int) -> None:
        """Writes a VM push command.

        Args:
            segment (str): The segment to push to, can be "CONST", "ARG",
                           "LOCAL", "STATIC", "THIS", "THAT", "POINTER", "TEMP".
            index (int): The index to push to.
        """
        self.output_stream.write("push " + self.translate_segment(segment) + " " + str(index) + "\n")

    def write_pop(self, segment: str, index: int) -> None:
        """Writes a VM pop command.

        Args:
            segment (str): The segment to pop from, can be "CONST", "ARG",
                           "LOCAL", "STATIC", "THIS", "THAT", "POINTER", "TEMP".
            index (int): The index to pop from.
        """
        self.output_stream.write("pop " + self.translate_segment(segment) + " " + str(index) + "\n")

    def write_arithmetic(self, command: str) -> None:
        """Writes a VM arithmetic command.

        Args:
            command (str): The command to write, can be "ADD", "SUB", "NEG",
                           "EQ", "GT", "LT", "AND", "OR", "NOT", "SHIFTLEFT", "SHIFTRIGHT".
        """
        self.output_stream.write(self.translate_segment(command) + "\n")

    def write_label(self, label: str) -> None:
        """Writes a VM label command.

        Args:
            label (str): The label to write.
        """
        self.output_stream.write("label " + label + "\n")

    def write_goto(self, label: str) -> None:
        """Writes a VM goto command.

        Args:
            label (str): The label to go to.
        """
        self.output_stream.write("goto " + label + "\n")

    def write_if_go_to(self, label: str) -> None:
        """Writes a VM if-goto command.

        Args:
            label (str): The label to go to.
        """
        self.output_stream.write("if-goto " + label + "\n")

    def write_call(self, name: str, n_args: int) -> None:
        """Writes a VM call command.

        Args:
            name (str): The name of the function to call.
            n_args (int): The number of arguments the function receives.
        """
        self.output_stream.write("call " + name + " " + str(n_args) + "\n")

    def write_function(self, name: str, n_locals: int) -> None:
        """Writes a VM function command.

        Args:
            name (str): The name of the function.
            n_locals (int): The number of local variables the function uses.
        """
        self.output_stream.write("function " + name + " " + str(n_locals) + "\n")

    def write_return(self) -> None:
        """Writes a VM return command."""
        self.output_stream.write("return\n")

    def translate_segment(self, segment: str) -> str:
        """Translates a given segment abbreviation into its corresponding full term.

        Args:
            segment (str): The abbreviation of the segment to be translated.

        Returns:
            str: The full term corresponding to the provided segment abbreviation.
        """
        if segment is None:
            return "None"
        lower_case_segment = segment.lower()

        segment_translation = {
            "field": "this",
            "+": "add",
            "-": "sub",
            "=": "eq",
            "<": "lt",
            ">": "gt",
            "|": "or",
            "&": "and",
            "~": "not",
            "ARG": "argument",
            "var": "local"
        }

        return segment_translation.get(segment, lower_case_segment)

    arithmetics_vm = {
        '=': 'EQ', '-': 'SUB', '+': 'ADD', '~': 'NOT', '<': 'LT', '>': 'GT', '&': 'AND', '|': 'OR',
        '>>': "shiftright", '<<': 'shiftleft', '/': 'call Math.divide 2', '*': 'call Math.multiply 2'
    }
