"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class Parser:
    """
    # Parser

    Handles the parsing of a single .vm file, and encapsulates access to the
    input code. It reads VM commands, parses them, and provides convenient
    access to their components.
    In addition, it removes all white space and comments.

    ## VM Language Specification

    A .vm file is a stream of characters. If the file represents a
    valid program, it can be translated into a stream of valid assembly
    commands. VM commands may be separated by an arbitrary number of whitespace
    characters and comments, which are ignored. Comments begin with "//" and
    last until the line’s end.
    The different parts of each VM command may also be separated by an arbitrary
    number of non-newline whitespace characters.

    - Arithmetic commands:
      - add, sub, and, or, eq, gt, lt
      - neg, not, shiftleft, shiftright
    - Memory segment manipulation:
      - push <segment> <number>
      - pop <segment that is not constant> <number>
      - <segment> can be any of: argument, local, static, constant, this, that,
                                 pointer, temp
    - Branching (only relevant for project 8):
      - label <label-name>
      - if-goto <label-name>
      - goto <label-name>
      - <label-name> can be any combination of non-whitespace characters.
    - Functions (only relevant for project 8):
      - call <function-name> <n-args>
      - function <function-name> <n-vars>
      - return
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """
        Initializes the parser and reads all lines from the input file.

        Args:
            input_file (typing.TextIO): The input file to parse.
        """
        self.__input_lines = input_file.read().splitlines()
        self.__counter = 0
        self.__num_of_lines = len(self.__input_lines)
        self.__cur_line = self.__input_lines[0] if self.__input_lines else ""

    def has_more_commands(self) -> bool:
        """
        Checks if there are more commands in the input.

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        return self.__counter < self.__num_of_lines

    def advance(self) -> None:
        """
        Reads the next command from the input and makes it the current command.
        Should be called only if has_more_commands() is True.
        """
        self.__counter += 1
        if self.has_more_commands():
            self.__cur_line = self.__input_lines[self.__counter]

    def command_type(self) -> str:
        """
        Determines the type of the current VM command.

        Returns:
            str: The type of the current VM command.
        """
        if not self.__cur_line or self.__cur_line.startswith("/"):
            return "null"

        self.__cur_line = self.__cur_line.lstrip()

        if self.__cur_line.startswith(
                ("add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not", "shiftLeft", "shiftRight")):
            return "C_ARITHMETIC"
        elif self.__cur_line.startswith("pop"):
            return "C_POP"
        elif self.__cur_line.startswith("push"):
            return "C_PUSH"
        return "null"

    def arg1(self) -> str:
        """
        Retrieves the first argument of the current command.

        Returns:
            str: The first argument of the command. If it's an arithmetic command,
            the command itself is returned.
        """
        if self.command_type() == "C_ARITHMETIC":
            return self.__cur_line.split()[0]
        return self.__cur_line.split()[1]

    def arg2(self) -> int:
        """
        Retrieves the second argument of the current command.

        Returns:
            int: The second argument of the command.
        """
        if self.command_type() in ["C_PUSH", "C_POP", "C_FUNCTION", "C_CALL"]:
            return int(self.__cur_line.split()[2])
        return 0
