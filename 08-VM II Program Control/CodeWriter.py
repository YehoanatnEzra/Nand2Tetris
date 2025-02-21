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
    label_count = 0
    call_counter = 0

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        self.__output_stream = output_stream
        self.input_filename = None
        self.__output_stream.write("")

    def bootstrap_write(self):
        """
               Writes the VM bootstrap code to initialize the stack and call Sys.init.

               This method sets the stack pointer to address 256 and invokes the Sys.init function.
               """
        self.__output_stream.write("@256\n")
        self.__output_stream.write("D=A\n")
        self.__output_stream.write("@SP\n")
        self.__output_stream.write("M=D\n")
        self.write_call("Sys.init", 0)

    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is
        started.

        Args:
            filename (str): The name of the VM file.
        """
        self.input_filename = filename

    def write_arithmetic(self, command: str, label1: str) -> None:
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
            self.if_eq_lt_gt("eq", label1)
        elif command == "lt":
            self.if_eq_lt_gt("lt", label1)
        elif command == "gt":
            self.if_eq_lt_gt("gt", label1)
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

    def close(self):
        """
               Closes the output stream.
               """
        self.__output_stream.close()

    def write_label(self, label: str) -> None:
        """Writes assembly code that affects the label command.
        Let "Xxx.foo" be a function within the file Xxx.vm. The handling of
        each "label bar" command within "Xxx.foo" generates and injects the symbol
        "Xxx.foo$bar" into the assembly code stream.
        When translating "goto bar" and "if-goto bar" commands within "foo",
        the label "Xxx.foo$bar" must be used instead of "bar".

        Args:
            label (str): the label to write.
        """
        self.__output_stream.write("//***************** + label  " + "\n")
        self.__output_stream.write("(" + label + ")" + "\n")

    def write_goto(self, label: str) -> None:
        """Writes assembly code that affects the goto command.

        Args:
            label (str): the label to go to.
        """
        self.__output_stream.write("//goto" + label + "\n")
        self.__output_stream.write("@" + label + "\n")
        self.__output_stream.write("0;JMP\n")

    def write_if(self, label: str) -> None:
        """Writes assembly code that affects the if-goto command.

        Args:
            label (str): the label to go to.
        """
        self.__output_stream.write("//if-goto " + label + "\n")
        self.__output_stream.write("@SP\n")
        self.__output_stream.write("M=M-1\n")
        self.__output_stream.write("A=M\n")
        self.__output_stream.write("D=M\n")
        self.__output_stream.write("@" + label + "\n")
        self.__output_stream.write("D;JNE\n")

    def write_function(self, function_name: str, n_vars: int) -> None:
        """
        Writes assembly code that defines a function in Hack assembly.

        Each "function Xxx.foo" command in the VM file generates a corresponding
        symbol "Xxx.foo" in the assembly code, marking the function's entry point.
        The assembler later translates this symbol into the physical address of
        the function's code.

        This method also initializes the local variables of the function by
        setting them to 0.

        Args:
            function_name (str): The name of the function.
            n_vars (int): The number of local variables in the function.
        """

        self.__output_stream.write("(" + function_name + ")" + "\n")
        for i in range(int(n_vars)):
            self.__output_stream.write("@SP\n")
            self.__output_stream.write("A=M\n")
            self.__output_stream.write("M=0\n")
            self.sp_down_or_up("up")

    def write_call(self, function_name: str, n_args: int) -> None:
        """
        Writes assembly code that implements a function call.

        Each "call" command generates a return label "Xxx.foo$ret.i" where "i"
        is a running integer. This label is used to store the return address
        within the caller's code. The assembler translates this label into the
        memory address of the command following the "call" instruction.

        Steps performed:
        - Pushes the return address label onto the stack.
        - Pushes LCL, ARG, THIS, and THAT onto the stack.
        - Repositions ARG and LCL.
        - Jumps to the called function.
        - Defines the return address label.

        Args:
            function_name (str): The name of the function to call.
            n_args (int): The number of arguments passed to the function.
        """

        ret_add = function_name + "$ret." + str(CodeWriter.call_counter)
        CodeWriter.call_counter += 1

        self.__output_stream.write("@" + ret_add + "\n")
        self.__output_stream.write("D=A\n")
        self.__output_stream.write("@SP\n")
        self.__output_stream.write("A=M\n")
        self.__output_stream.write("M=D\n")
        self.sp_down_or_up("up")

        # Push LCL, ARG, THIS, THAT
        self.push_val_in_sp("LCL")
        self.push_val_in_sp("ARG")
        self.push_val_in_sp("THIS")
        self.push_val_in_sp("THAT")

        # ARG = SP - 5 - n_args
        self.__output_stream.write("@SP\n")
        self.__output_stream.write("D=M\n")
        num_of_diss = 5 + int(n_args)
        self.__output_stream.write("@" + str(num_of_diss) + "\n")
        self.__output_stream.write("D=D-A\n")
        self.__output_stream.write("@ARG\n")
        self.__output_stream.write("M=D\n")

        # LCL = SP
        self.__output_stream.write("@SP\n")
        self.__output_stream.write("D=M\n")
        self.__output_stream.write("@LCL\n")
        self.__output_stream.write("M=D\n")

        # Goto function_name
        self.write_goto(function_name)

        # Define return label
        self.__output_stream.write("(" + ret_add + ")\n")

    def write_return(self) -> None:
        """
        Writes assembly code that implements the 'return' command.

        This method restores the caller's state and jumps back to the return address.

        Steps performed:
        - Stores the current LCL in R15 (endFrame).
        - Saves the return address from (frame-5) in R14.
        - Moves the return value from the stack to *ARG.
        - Repositions SP to ARG + 1.
        - Restores THAT, THIS, ARG, and LCL from the caller's frame.
        - Jumps to the return address.
        """

        # endFrame(R15) = LCL
        self.__output_stream.write("@LCL\n")
        self.__output_stream.write("D=M\n")
        self.__output_stream.write("@R15\n")
        self.__output_stream.write("M=D\n")

        # return_address (R14) = *(frame-5) (R15-5)
        self.__output_stream.write("@5\n")
        self.__output_stream.write("D=A\n")
        self.__output_stream.write("@R15\n")
        self.__output_stream.write("D=M-D\n")
        self.__output_stream.write("A=D\n")
        self.__output_stream.write("D=M\n")
        self.__output_stream.write("@R14\n")
        self.__output_stream.write("M=D\n")

        # *ARG = pop()
        self.__output_stream.write("@SP\n")
        self.__output_stream.write("A=M-1\n")
        self.__output_stream.write("D=M\n")  # D contains the last argument in the stack
        self.__output_stream.write("@ARG\n")
        self.__output_stream.write("A=M\n")
        self.__output_stream.write("M=D\n")  # last argument in the stack saved in *ARG

        # SP = ARG + 1
        self.__output_stream.write("@ARG\n")
        self.__output_stream.write("D=M+1\n")
        self.__output_stream.write("@SP\n")
        self.__output_stream.write("M=D\n")

        # Restore THAT, THIS, ARG, and LCL
        self.framing(1, "THAT")
        self.framing(2, "THIS")
        self.framing(3, "ARG")
        self.framing(4, "LCL")

        # goto return_address (R14)
        self.__output_stream.write("@R14\n")
        self.__output_stream.write("A=M\n")
        self.__output_stream.write("0;JMP\n")

    def framing(self, val: int, spot: str) -> None:
        """
        Restores a saved segment from the caller's frame.

        This method is used in function returns to restore values for THAT, THIS, ARG, and LCL.

        Args:
            val (int): The offset from the end frame where the value is stored.
            spot (str): The segment name to restore (e.g., "THAT", "THIS").
        """

        self.__output_stream.write("@" + str(val) + "\n")
        self.__output_stream.write("D=A\n")
        self.__output_stream.write("@R15\n")  # @endFrame
        self.__output_stream.write("D=M-D\n")  # endFrame - val
        self.__output_stream.write("A=D\n")
        self.__output_stream.write("D=M\n")
        self.__output_stream.write("@" + spot + "\n")
        self.__output_stream.write("M=D\n")  # Restore value to segment

    def sp_down_or_up(self, instruction: str) -> None:
        """
        Adjusts the stack pointer (SP) up or down.

        Args:
            instruction (str): "up" to increment SP, anything else to decrement SP.
        """

        if instruction == "up":
            self.__output_stream.write("@SP\n")
            self.__output_stream.write("M=M+1\n")
        else:
            self.__output_stream.write("@SP\n")
            self.__output_stream.write("M=M-1\n")

    def if_add(self) -> None:
        """
        Performs addition on the top two stack values and stores the result.
        """
        self.__output_stream.write("// add\n")
        self.__output_stream.write("@SP\n")
        self.__output_stream.write("A=M-1\n")
        self.__output_stream.write("D=M\n")
        self.__output_stream.write("A=A-1\n")
        self.__output_stream.write("D=D+M\n")
        self.__output_stream.write("M=D\n")
        self.sp_down_or_up("down")

    def if_sub(self) -> None:
        """
        Performs subtraction on the top two stack values and stores the result.
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
        Negates the top value of the stack.
        """
        self.__output_stream.write("// neg\n")
        self.__output_stream.write("@SP\n")
        self.__output_stream.write("A=M-1\n")
        self.__output_stream.write("M=-M\n")

    def if_not(self) -> None:
        """
        Applies logical NOT to the top value of the stack.
        """
        self.__output_stream.write("@SP\n")
        self.__output_stream.write("A=M-1\n")
        self.__output_stream.write("M=!M\n")

    def if_shift_right(self) -> None:
        """
        Performs a bitwise right shift on the top value of the stack.
        """
        self.__output_stream.write("@SP\n")
        self.__output_stream.write("A=M-1\n")
        self.__output_stream.write("M=M>>1\n")

    def if_shift_left(self) -> None:
        """
        Performs a bitwise left shift on the top value of the stack.
        """
        self.__output_stream.write("@SP\n")
        self.__output_stream.write("A=M-1\n")
        self.__output_stream.write("M=M<<1\n")

    def if_and_or(self, sel: str) -> None:
        """
        Performs a bitwise AND or OR operation on the top two values of the stack.

        Args:
            sel (str): "and" for bitwise AND, any other value for bitwise OR.
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

    def make_add(self, segment: str, index: str) -> None:
        """
        Computes the effective address for a given segment and index,
        storing the result in R13.

        Args:
            segment (str): The memory segment (e.g., "local", "argument", "this", "that", "temp", "static").
            index (str): The index within the segment.
        """

        if segment in ["local", "argument", "this", "that"]:
            segment_map = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT"}
            segment = segment_map[segment]

            self.__output_stream.write("@" + index + "\n")
            self.__output_stream.write("D=A\n")
            self.__output_stream.write("@" + segment + "\n")
            self.__output_stream.write("D=D+M\n")
            self.__output_stream.write("@R13\n")
            self.__output_stream.write("M=D\n")

        elif segment == "temp":
            index = str(int(index) + 5)
            if int(index) > 12:
                raise ValueError("problem detected")
            self.__output_stream.write("@" + index + "\n")
            self.__output_stream.write("D=A\n")
            self.__output_stream.write("@R13\n")
            self.__output_stream.write("M=D\n")

        elif segment == "static":
            ind = str(int(index))
            if int(ind) > 240:
                raise ValueError("problem detected")
            self.__output_stream.write("@" + self.input_filename + "." + ind + "\n")
            self.__output_stream.write("D=A\n")
            self.__output_stream.write("@R13\n")
            self.__output_stream.write("M=D\n")

    def if_pop(self, segment: str, index: str) -> None:
        """
        Handles the 'pop' command by storing the top stack value into the given memory segment.

        Args:
            segment (str): The memory segment (e.g., "local", "argument", "pointer").
            index (str): The index within the segment.
        """
        self.__output_stream.write("// pop " + segment + " " + index + "\n")
        self.sp_down_or_up("down\n")

        if segment == "pointer":
            self.__output_stream.write("A=M\n")
            self.__output_stream.write("D=M\n")
            if int(index) == 0:
                self.__output_stream.write("@THIS\n")
            else:
                self.__output_stream.write("@THAT\n")
            self.__output_stream.write("M=D\n")
        else:
            self.make_add(segment, index)
            self.__output_stream.write("@SP\n")
            self.__output_stream.write("A=M\n")
            self.__output_stream.write("D=M\n")  # D = the value to pop
            self.__output_stream.write("@R13\n")
            self.__output_stream.write("A=M\n")
            self.__output_stream.write("M=D\n")

    def if_push(self, segment: str, index: str) -> None:
        """
        Handles the 'push' command by retrieving the value from the given memory segment and pushing it onto the stack.

        Args:
            segment (str): The memory segment (e.g., "constant", "pointer").
            index (str): The index within the segment.
        """
        self.__output_stream.write("// push " + segment + " " + index + "\n")

        if segment == "constant":
            self.push_constant(index)
        elif segment == "pointer":  # this=3, that=4
            if int(index) == 0:
                self.__output_stream.write("@THIS\n")
            else:
                self.__output_stream.write("@THAT\n")
            self.__output_stream.write("D=M\n")
            self.__output_stream.write("@SP\n")
            self.__output_stream.write("A=M\n")
            self.__output_stream.write("M=D\n")
            self.sp_down_or_up("up")
        else:
            self.make_add(segment, index)
            self.__output_stream.write("@R13\n")
            self.__output_stream.write("A=M\n")
            self.__output_stream.write("D=M\n")
            self.__output_stream.write("@SP\n")
            self.__output_stream.write("A=M\n")
            self.__output_stream.write("M=D\n")
            self.sp_down_or_up("up")

    def push_constant(self, index: str) -> None:
        """
        Pushes a constant value onto the stack.

        Args:
            index (str): The constant value to push.
        """
        self.__output_stream.write("@" + index + "\n")
        self.__output_stream.write("D=A\n")
        self.__output_stream.write("@SP\n")
        self.__output_stream.write("A=M\n")
        self.__output_stream.write("M=D\n")
        self.sp_down_or_up("up")

    def if_eq_lt_gt(self, cond: str, label: str) -> None:
        """
        Handles equality and comparison operations (eq, lt, gt).

        Args:
            cond (str): The comparison condition ("eq", "lt", "gt").
            label (str): A unique label identifier.
        """

        CodeWriter.label_count += 1

        # SP down
        self.sp_down_or_up("down")
        self.__output_stream.write("A=M\n")
        self.__output_stream.write("D=M\n")

        # Check conditions and jump accordingly
        self.__output_stream.write("@" + label + "Ypos" + str(CodeWriter.label_count) + "\n")
        self.__output_stream.write("D;JGE\n")

        self.sp_down_or_up("down")
        self.__output_stream.write("A=M\n")
        self.__output_stream.write("D=M\n")

        self.__output_stream.write("@" + label + "XposYneg" + str(CodeWriter.label_count) + "\n")
        self.__output_stream.write("D;JGE\n")

        self.__output_stream.write("A=A+1\n")
        self.__output_stream.write("D=M-D\n")
        self.__output_stream.write("@" + label + "END_TEMP" + str(CodeWriter.label_count) + "\n")
        self.__output_stream.write("0;JMP\n")

        # Handle X positive, Y negative case
        self.__output_stream.write("(" + label + "XposYneg" + str(CodeWriter.label_count) + ")\n")
        self.__output_stream.write("D=-1\n")
        self.__output_stream.write("@" + label + "END_TEMP" + str(CodeWriter.label_count) + "\n")
        self.__output_stream.write("0;JMP\n")

        # Handle Y positive case
        self.__output_stream.write("(" + label + "Ypos" + str(CodeWriter.label_count) + ")\n")
        self.sp_down_or_up("down")
        self.__output_stream.write("A=M\n")
        self.__output_stream.write("D=M\n")
        self.__output_stream.write("@" + label + "YposXpos" + str(CodeWriter.label_count) + "\n")
        self.__output_stream.write("D;JGE\n")
        self.__output_stream.write("D=1\n")
        self.__output_stream.write("@" + label + "END_TEMP" + str(CodeWriter.label_count) + "\n")
        self.__output_stream.write("0;JMP\n")

        # Handle Y positive, X positive case
        self.__output_stream.write("(" + label + "YposXpos" + str(CodeWriter.label_count) + ")\n")
        self.__output_stream.write("@SP\n")
        self.__output_stream.write("A=M+1\n")
        self.__output_stream.write("D=M-D\n")
        self.__output_stream.write("@" + label + "END_TEMP" + str(CodeWriter.label_count) + "\n")
        self.__output_stream.write("0;JMP\n")

        # End temporary label
        self.__output_stream.write("(" + label + "END_TEMP" + str(CodeWriter.label_count) + ")\n")
        self.__output_stream.write("@" + label + "TRUELABEL" + str(CodeWriter.label_count) + "\n")

        if cond == "eq":
            self.__output_stream.write("D;JEQ\n")
        elif cond == "lt":
            self.__output_stream.write("D;JGT\n")
        else:
            self.__output_stream.write("D;JLT\n")

        self.__output_stream.write("D=0\n")
        self.__output_stream.write("@" + label + "END" + str(CodeWriter.label_count) + "\n")
        self.__output_stream.write("0;JMP\n")

        self.__output_stream.write("(" + label + "TRUELABEL" + str(CodeWriter.label_count) + ")\n")
        self.__output_stream.write("D=-1\n")
        self.__output_stream.write("(" + label + "END" + str(CodeWriter.label_count) + ")\n")
        self.__output_stream.write("@SP\n")
        self.__output_stream.write("A=M\n")
        self.__output_stream.write("M=D\n")
        self.sp_down_or_up("up")

    def push_val_in_sp(self, val: str) -> None:
        """
        Pushes the value stored in the given memory segment onto the stack.

        Args:
            val (str): The name of the memory segment whose value is to be pushed.
        """
        self.__output_stream.write("@" + val + "\n")
        self.__output_stream.write("D=M\n")
        self.__output_stream.write("@SP\n")
        self.__output_stream.write("A=M\n")
        self.__output_stream.write("M=D\n")
        self.sp_down_or_up("up")
