"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        self.__output_stream = output_stream
        self.label_count = 0
        self.input_filename = None

    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is 
        started.

        Args:
            filename (str): The name of the VM file.
        """
        self.input_filename = filename

    def write_arithmetic(self, command: str) -> None:
        """Writes assembly code that is the translation of the given 
        arithmetic command. For the commands eq, lt, gt, you should correctly
        compare between all numbers our computer supports, and we define the
        value "true" to be -1, and "false" to be 0.

        Args:
            command (str): an arithmetic command.
        """
        if command == "add":
            self.if_add()
        elif command == "sub":
            self.if_sub()
        elif command == "neg":
            self.if_neg()
        elif command == "eq":
            self.if_eq_lt_gt("eq")
        elif command == "lt":
            self.if_eq_lt_gt("lt")
        elif command == "gt":
            self.if_eq_lt_gt("gt")
        elif command == "and":
            self.if_and_or("and")
        elif command == "or":
            self.if_and_or("or")
        elif command == "not":
            self.if_not()
        elif command == "shiftRight":
            self.if_shift_right()
        elif command == "shiftLeft":
            self.if_shift_left()

    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes assembly code that is the translation of the given 
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        if command == "C_POP":
            self.if_pop(segment, index)
        else:
            self.if_push(segment, index)

    def close(self) -> None:
        """
        Closes the output stream to finalize writing to the file.
        """
        self.__output_stream.close()

    def sp_down_or_up(self, instruction: str) -> None:
        """
        Adjusts the stack pointer (SP) up or down.

        Args:
            instruction (str): "up" to increment SP, "down" to decrement SP.
        """
        if instruction == "up":
            self.__output_stream.write("@SP\n")
            self.__output_stream.write("M=M+1\n")
        else:
            self.__output_stream.write("@SP\n")
            self.__output_stream.write("M=M-1\n")

    def if_add(self):
        self.__output_stream.write("//add\n")
        self.__output_stream.write("@SP\n")
        self.__output_stream.write("A=M-1\n")
        self.__output_stream.write("D=M\n")
        self.__output_stream.write("A=A-1\n")
        self.__output_stream.write("D=D+M\n")
        self.__output_stream.write("M=D\n")
        self.sp_down_or_up("down")

    def if_sub(self) -> None:
        """
        Performs subtraction (SP[-2] = SP[-2] - SP[-1]) and decrements SP.
        """
        self.__output_stream.write("// sub\n")
        self.__output_stream.write("@SP\n")
        self.__output_stream.write("A=M-1\n")
        self.__output_stream.write("D=M\n")
        self.__output_stream.write("A=A-1\n")
        self.__output_stream.write("M=M-D\n")
        self.sp_down_or_up("down")

    def if_neg(self) -> None:
        """
        Negates the topmost value in the stack (SP[-1] = -SP[-1]).
        """
        self.__output_stream.write("// neg\n")
        self.__output_stream.write("@SP\n")
        self.__output_stream.write("A=M-1\n")
        self.__output_stream.write("M=-M\n")

    def if_not(self) -> None:
        """
        Applies bitwise NOT to the topmost value in the stack (SP[-1] = !SP[-1]).
        """
        self.__output_stream.write("@SP\n")
        self.__output_stream.write("A=M-1\n")
        self.__output_stream.write("M=!M\n")

    def if_shift_right(self) -> None:
        """
        Shifts the topmost value in the stack right (SP[-1] >>= 1).
        """
        self.__output_stream.write("@SP\n")
        self.__output_stream.write("A=M-1\n")
        self.__output_stream.write("M=>>M\n")

    def if_shift_left(self) -> None:
        """
        Shifts the topmost value in the stack left (SP[-1] <<= 1).
        """
        self.__output_stream.write("@SP\n")
        self.__output_stream.write("A=M-1\n")
        self.__output_stream.write("M=<<M\n")

    def if_and_or(self, sel: str) -> None:
        """
        Performs bitwise AND or OR operation on the top two stack values.

        Args:
            sel (str): "and" for bitwise AND, "or" for bitwise OR.
        """
        self.sp_down_or_up("down")
        self.__output_stream.write("A=M\n")
        self.__output_stream.write("D=M\n")
        self.__output_stream.write("A=A-1\n")

        if sel == "and":
            self.__output_stream.write("D=D&M\n")
        else:
            self.__output_stream.write("D=D|M\n")

        self.__output_stream.write("M=D\n")

    def make_add(self, segmant: str, index: int) -> None:
        """
        Computes the address of the given segment and stores it in a temporary register.

        Args:
            segmant (str): The memory segment ("local", "argument", "this", "that", "temp", "static").
            index (int): The index within the segment.
        """
        if segmant in ["local", "argument", "this", "that"]:
            segmant_map = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT"}
            segmant = segmant_map[segmant]

            self.__output_stream.write("@" + str(index) + "\n")
            self.__output_stream.write("D=A\n")
            self.__output_stream.write("@" + segmant + "\n")
            self.__output_stream.write("D=D+M\n")
            self.__output_stream.write("@addr\n")
            self.__output_stream.write("M=D\n")

        elif segmant == "temp":
            index = str(int(index) + 5)
            if int(index) > 12:
                raise ValueError("Problem detected: index out of bounds for temp segment")
            self.__output_stream.write("@" + index + "\n")
            self.__output_stream.write("D=A\n")
            self.__output_stream.write("@addr\n")
            self.__output_stream.write("M=D\n")

        elif segmant == "static":
            ind = str(int(index))
            if int(ind) > 240:
                raise ValueError("Problem detected: index out of bounds for static segment")
            self.__output_stream.write("@" + self.input_filename + "." + ind + "\n")
            self.__output_stream.write("D=A\n")
            self.__output_stream.write("@addr\n")
            self.__output_stream.write("M=D\n")

    def if_pop(self, segmant: str, index: int) -> None:
        """
        Handles the POP command, storing the value from the stack into the specified memory segment.

        Args:
            segmant (str): The memory segment to store the value.
            index (int): The index within the memory segment.
        """
        self.__output_stream.write("// pop " + segmant + " " + str(index) + "\n")
        self.sp_down_or_up("down\n")

        if segmant == "pointer":
            self.__output_stream.write("A=M\n")
            self.__output_stream.write("D=M\n")
            self.__output_stream.write("@THIS\n" if int(index) == 0 else "@THAT\n")
            self.__output_stream.write("M=D\n")
        else:
            self.make_add(segmant, index)
            self.__output_stream.write("@SP\n")
            self.__output_stream.write("A=M\n")
            self.__output_stream.write("D=M\n")  # D = value to pop
            self.__output_stream.write("@addr\n")
            self.__output_stream.write("A=M\n")
            self.__output_stream.write("M=D\n")

    def if_push(self, segmant: str, index: int) -> None:
        """
        Handles the PUSH command, pushing a value from a memory segment onto the stack.

        Args:
            segmant (str): The memory segment to retrieve the value from.
            index (int): The index within the memory segment.
        """
        self.__output_stream.write("// push " + segmant + " " + str(index) + "\n")

        if segmant == "constant":
            self.push_constant(index)
        elif segmant == "pointer":  # this=3, that=4
            self.__output_stream.write("@THIS\n" if int(index) == 0 else "@THAT\n")
            self.__output_stream.write("D=M\n")
            self.__output_stream.write("@SP\n")
            self.__output_stream.write("A=M\n")
            self.__output_stream.write("M=D\n")
            self.sp_down_or_up("up")
        else:
            self.make_add(segmant, index)
            self.__output_stream.write("@addr\n")
            self.__output_stream.write("A=M\n")
            self.__output_stream.write("D=M\n")
            self.__output_stream.write("@SP\n")
            self.__output_stream.write("A=M\n")
            self.__output_stream.write("M=D\n")
            self.sp_down_or_up("up")

    def push_constant(self, index: int) -> None:
        """
        Pushes a constant value onto the stack.

        Args:
            index (int): The constant value to push.
        """
        self.__output_stream.write("@" + str(index) + "\n")
        self.__output_stream.write("D=A\n")
        self.__output_stream.write("@SP\n")
        self.__output_stream.write("A=M\n")
        self.__output_stream.write("M=D\n")
        self.sp_down_or_up("up")

    def if_eq_lt_gt(self, cond: str) -> None:
        """
        Handles the comparison operations (eq, lt, gt) and updates the stack accordingly.

        Args:
            cond (str): The comparison operation ("eq", "lt", or "gt").
        """
        # Decrement SP
        self.sp_down_or_up("down")

        # Load top stack value into D
        self.__output_stream.write("A=M\n")
        self.__output_stream.write("D=M\n")

        # Check conditions and jump accordingly
        self.__output_stream.write("@Ypos" + str(self.label_count) + "\n")
        self.__output_stream.write("D;JGE\n")

        # Decrement SP again
        self.sp_down_or_up("down")

        # Load next stack value into D
        self.__output_stream.write("A=M\n")
        self.__output_stream.write("D=M\n")

        # Check if X is positive and Y is negative
        self.__output_stream.write("@XposYneg" + str(self.label_count) + "\n")
        self.__output_stream.write("D;JGE\n")

        # Perform subtraction
        self.__output_stream.write("A=A+1\n")
        self.__output_stream.write("D=M-D\n")

        # Jump to end temp label
        self.__output_stream.write("@END_TEMP" + str(self.label_count) + "\n")
        self.__output_stream.write("0;JMP\n")

        # Handle X positive and Y negative case
        self.__output_stream.write("(XposYneg" + str(self.label_count) + ")\n")
        self.__output_stream.write("D=-1\n")
        self.__output_stream.write("@END_TEMP" + str(self.label_count) + "\n")
        self.__output_stream.write("0;JMP\n")

        # Handle Y positive case
        self.__output_stream.write("(Ypos" + str(self.label_count) + ")\n")
        self.sp_down_or_up("down")
        self.__output_stream.write("A=M\n")
        self.__output_stream.write("D=M\n")
        self.__output_stream.write("@YposXpos" + str(self.label_count) + "\n")
        self.__output_stream.write("D;JGE\n")
        self.__output_stream.write("D=1\n")
        self.__output_stream.write("@END_TEMP" + str(self.label_count) + "\n")
        self.__output_stream.write("0;JMP\n")

        # Handle Y positive and X positive case
        self.__output_stream.write("(YposXpos" + str(self.label_count) + ")\n")
        self.__output_stream.write("@SP\n")
        self.__output_stream.write("A=M+1\n")
        self.__output_stream.write("D=M-D\n")
        self.__output_stream.write("@END_TEMP" + str(self.label_count) + "\n")
        self.__output_stream.write("0;JMP\n")

        # Handle end temp label
        self.__output_stream.write("(END_TEMP" + str(self.label_count) + ")\n")

        # Set result based on comparison
        self.__output_stream.write("@TRUELABEL" + str(self.label_count) + "\n")
        if cond == "eq":
            self.__output_stream.write("D;JEQ\n")
        elif cond == "lt":
            self.__output_stream.write("D;JGT\n")
        else:
            self.__output_stream.write("D;JLT\n")

        self.__output_stream.write("D=0\n")
        self.__output_stream.write("@END" + str(self.label_count) + "\n")
        self.__output_stream.write("0;JMP\n")

        # Handle true case
        self.__output_stream.write("(TRUELABEL" + str(self.label_count) + ")\n")
        self.__output_stream.write("D=-1\n")

        # Handle end case
        self.__output_stream.write("(END" + str(self.label_count) + ")\n")
        self.__output_stream.write("@SP\n")
        self.__output_stream.write("A=M\n")
        self.__output_stream.write("M=D\n")
        self.sp_down_or_up("up")
        self.label_count += 1

