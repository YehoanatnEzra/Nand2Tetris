"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Commons Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
from VMWriter import VMWriter
from SymbolTable import SymbolTable


class CompilationEngine:
    """Gets input from a self.input and emits its parsed structure into an
    output stream.
    """
    arithmetics_vm = {'=': 'EQ', '-': 'SUB', '+': 'ADD', '~': 'NOT', '<': 'LT', '>': 'GT', '&': 'AND', '|': 'OR',
                      '>>': "shiftright", '<<': 'shiftleft', '/': 'call Math.divide 2', '*': 'call Math.multiply 2'}
    method_type = ["var", "argument", "field", "static"]
    statements = ["if", "do", "while", "return", "let"]
    ops = ["+", "-", "*", "/", "&", "|", "<", ">", "="]
    unary_ops = ['-', '~']

    def __init__(self, input_stream: "JackTokenizer", output_stream) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        self.cur_func = ""
        self.object_caller = ""
        self.class_name = ""
        self.vm_writer = VMWriter(output_stream)
        self.symbolTable = SymbolTable()
        self.output_stream = output_stream
        self.input = input_stream
        self.l_counter = 0
        self.unary_op = ['+', '-', '*', '/', '&amp;', '|', '&lt;', '&gt;', '=']

    def compile_class(self) -> None:
        """
        Compiles a complete class.

        This method performs the following steps:
        - Saves the class name.
        - Skips the initial 'class ClassName {' tokens.
        - Processes class variable declarations (static and field variables).
        - Processes subroutine declarations (constructor, function, and method).
        """

        # Save the class name
        self.class_name = self.input.tokens[1]

        # Skip 'class ClassName {'
        self.input.advance(3)

        # Define class variables
        while self.input.cur_token.lower() in ["static", "field"]:
            self.compile_class_var_dec()

        # Define class subroutines
        while self.input.cur_token in ["constructor", "function", "method"]:
            self.compile_subroutine()

    def compile_class_var_dec(self) -> None:
        """
        Compiles a static or field variable declaration.

        This method processes class-level variables, following these steps:
        - Extracts the kind (static or field).
        - Extracts the type and name of the first variable.
        - Defines the variable in the symbol table.
        - Handles multiple variable declarations in the same statement.
        - Advances past the terminating semicolon.
        """

        kind = self.input.cur_token
        self.input.advance(1)
        type = self.input.cur_token
        self.input.advance(1)
        name = self.input.cur_token
        self.input.advance(1)
        self.symbolTable.define(name, type, kind)

        # Process additional variables in the same declaration
        while self.input.cur_token == ',':
            self.input.advance(1)
            name = self.input.cur_token
            self.input.advance(1)
            self.symbolTable.define(name, type, kind)

        # Advance past the terminating semicolon
        self.input.advance(1)

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        Assumes that classes with constructors have at least one field,
        which is necessary for project 11.
        """
        self.symbolTable.start_subroutine()
        kind_of_sub = self.input.cur_token
        self.input.advance(1)
        self.input.advance(1)
        name_sub = self.input.cur_token
        self.input.advance(2)

        self.compile_parameter_list()
        self.input.advance(2)  # Skip ')' and '{'

        self.cur_func = self.class_name + "." + name_sub
        self.compile_subroutine_body(kind_of_sub)

        self.input.advance(1)  # Skip '}'

    def compile_subroutine_body(self, kind_of_sub: str) -> None:
        """
        Compiles the body of a subroutine.

        This method processes the subroutine body, performing the following steps:
        - Iterates through the subroutine body until encountering a closing brace ('}').
        - Compiles variable declarations.
        - Determines the number of local variables and writes the VM function declaration.
        - Handles special cases for 'method' and 'constructor' subroutines:
          - Methods set up 'this' as an implicit first argument.
          - Constructors allocate memory for the new object.
        - Compiles the statements inside the subroutine body.

        Args:
            kind_of_sub (str): The type of subroutine ('method', 'function', or 'constructor').
        """

        while self.input.symbol() != "}":
            self.compile_var_dec()
            count_param = self.symbolTable.var_count("var")
            self.output_stream.write("function " + self.cur_func + " " + str(count_param) + "\n")

            if kind_of_sub == "method":
                self.symbolTable.define("this", self.class_name, "argument")
                self.vm_writer.write_push('argument', 0)
                self.vm_writer.write_pop('pointer', 0)

            if kind_of_sub == 'constructor':
                field_count = self.symbolTable.var_count("field")
                self.vm_writer.write_push('constant', field_count)
                self.vm_writer.write_call('Memory.alloc', 1)
                self.vm_writer.write_pop('pointer', 0)

            self.compile_statements()

        return

    def compile_parameter_list(self) -> None:
        """
        Compiles a (possibly empty) parameter list, excluding the enclosing parentheses.

        This method processes function parameters, ensuring they are properly defined
        in the symbol table as arguments.
        """

        while self.input.cur_token != ")":
            if self.input.cur_token == ',':
                self.input.advance(1)
            type_parameter = self.input.cur_token
            self.input.advance(1)
            name_parameter = self.input.cur_token
            self.input.advance(1)
            self.symbolTable.define(name_parameter, type_parameter, "argument")

    def compile_var_dec(self) -> None:
        """
        Compiles a local variable declaration.

        This method processes local variables within a subroutine, ensuring they
        are properly stored in the symbol table.
        """

        while self.input.cur_token in self.method_type:
            kind = self.input.cur_token
            self.input.advance(1)
            type = self.input.cur_token
            self.input.advance(1)
            name = self.input.cur_token
            self.input.advance(1)
            self.symbolTable.define(name, type, kind)

            # Process additional variables in the same declaration
            while self.input.cur_token != ';':
                self.input.advance(1)  # Skip ','
                name = self.input.cur_token
                self.input.advance(1)  # Skip name
                self.symbolTable.define(name, type, kind)

            self.input.advance(1)  # Skip ';'

    def compile_statements(self) -> None:
        """
        Compiles a sequence of statements, not including the enclosing "{}".

        This method iterates over statements and calls the corresponding compilation method
        based on the statement type.
        """

        while self.input.cur_token in self.statements:
            if self.input.cur_token == "let":
                self.compile_let()
            elif self.input.cur_token == "if":
                self.compile_if()
            elif self.input.cur_token == "while":
                self.compile_while()
            elif self.input.cur_token == "do":
                self.compile_do()
            elif self.input.cur_token == "return":
                self.compile_return()

            if self.input.cur_token == ';':
                self.input.advance(1)  # Skip ';'

    def compile_let(self) -> None:
        """
        Compiles a 'let' statement.

        A 'let' statement assigns a value to a variable, and its structure can include:
        - Simple variable assignment (e.g., `let x = expression;`)
        - Array assignment (e.g., `let arr[i] = expression;`)

        This method determines whether the target is an array or a simple variable,
        compiles the expression, and generates the appropriate VM commands for storage.
        """

        is_array = False
        self.input.advance(1)  # Skip 'let'

        obj_name = self.input.cur_token
        obj_type = self.symbolTable.type_of(obj_name)
        obj_index = self.symbolTable.index_of(obj_name)

        self.input.advance(1)  # Skip variable name

        if self.input.cur_token == "[":  # Handle array assignment
            is_array = True
            self.input.advance(1)  # Skip '['
            self.compile_expression()
            self.input.advance(1)  # Skip ']'
            self.vm_writer.write_push(obj_type, obj_index)
            self.vm_writer.write_arithmetic("ADD")

        self.input.advance(1)  # Skip '='
        self.compile_expression()

        if is_array:
            self.vm_writer.write_pop("TEMP", 0)
            self.vm_writer.write_pop("POINTER", 1)
            self.vm_writer.write_push("TEMP", 0)
            self.vm_writer.write_pop("THAT", 0)
        else:
            self.vm_writer.write_pop(obj_type, obj_index)

        if (self.cur_func.split(".")[0]) == (self.symbolTable.kind_of(obj_name)):
            self.vm_writer.write_push(obj_type, obj_index)

    def compile_while(self) -> None:
        """
        Compiles a 'while' statement.

        This method follows these steps:
        - Creates unique labels for the loop.
        - Writes the loop label and compiles the condition.
        - Uses 'NOT' to invert the condition and jumps to the end label if false.
        - Compiles the loop body and jumps back to the loop label.
        - Writes the end label after the loop.
        """

        # Initialize labels
        l_while = "WHILE_LABEL" + str(self.l_counter)
        l_end = "END_WHILE" + str(self.l_counter)
        self.l_counter += 1

        self.vm_writer.write_label(l_while)
        self.input.advance(2)  # Skip 'while' and '('

        self.compile_expression()

        self.input.advance(2)  # Skip ')' and '{'
        self.vm_writer.write_arithmetic("NOT")
        self.vm_writer.write_if_go_to(l_end)
        self.compile_statements()

        self.vm_writer.write_goto(l_while)
        self.vm_writer.write_label(l_end)
        self.input.advance(1)  # Skip '}'

    def compile_return(self) -> None:
        """
        Compiles a 'return' statement.

        This method handles:
        - Returning an expression value (e.g., `return x + 1;`)
        - Returning void (i.e., `return;` generates a return of constant 0).
        - Advances the input and writes the VM return command.
        """

        self.input.advance(1)  # Skip 'return'

        if self.input.cur_token != ";":
            self.compile_expression()
        else:
            self.vm_writer.write_push("constant", 0)

        self.input.advance(1)
        self.vm_writer.write_return()

    def compile_if(self) -> None:
        """
        Compiles an 'if' statement, possibly with a trailing 'else' clause.

        This method follows these steps:
        - Generates labels for false and end conditions.
        - Skips 'if' and '(' tokens.
        - Compiles the conditional expression.
        - Skips ')' and '{' tokens.
        - Writes a NOT operation and jumps to the false label if the condition is false.
        - Compiles the 'if' block statements and jumps to the end label.
        - If an 'else' clause is present, compiles its statements.
        - Writes the final label marking the end of the if statement.
        """

        l_false = 'IF_FALSE' + str(self.l_counter)
        l_end = 'END_IF' + str(self.l_counter)
        self.l_counter += 1

        self.input.advance(2)  # Skip 'if' and '('
        self.compile_expression()
        self.input.advance(2)  # Skip ')' and '{'
        self.vm_writer.write_arithmetic("NOT")
        self.vm_writer.write_if_go_to(l_false)

        self.compile_statements()
        self.vm_writer.write_goto(l_end)
        self.input.advance(1)  # Skip '}'

        self.vm_writer.write_label(l_false)

        if self.input.cur_token == "else":
            self.input.advance(1)  # Skip 'else'
            self.compile_statements()
            self.input.advance(1)

        self.vm_writer.write_label(l_end)  # End if

    def compile_expression(self) -> None:
        """
        Compiles an expression.

        This method processes:
        - A sequence of terms connected by operators.
        - Handles multiplication and division using function calls to `Math.multiply` and `Math.divide`.
        - Writes the appropriate arithmetic operations.
        """

        self.compile_term()

        while self.input.token_type() == "SYMBOL" and self.input.cur_token in self.ops:
            operator = self.input.cur_token
            self.input.advance(1)
            self.compile_term()

            if operator == "*":
                self.vm_writer.write_call("Math.multiply", 2)
            elif operator == "/":
                self.vm_writer.write_call("Math.divide", 2)
            else:
                self.vm_writer.write_arithmetic(operator)

    def compile_term(self) -> None:
        """
        Compiles a term.

        This method handles:
        - Integer and string constants.
        - Keyword constants (`true`, `false`, `null`, `this`).
        - Parenthesized expressions.
        - Unary operations (`-`, `~`).
        - Variable names, array accesses, and subroutine calls.
        """

        if self.input.token_type() == "INT_CONST":
            self.vm_writer.write_push("constant", self.input.cur_token)
            self.input.advance(1)
        elif self.input.token_type() == "STRING_CONST":
            self.get_string()
        elif self.input.token_type() == "KEYWORD":
            if self.input.cur_token in ['true', 'false', 'null']:
                self.vm_writer.write_push("constant", 0)
                if self.input.cur_token == "true":
                    self.vm_writer.write_push("constant", -1)
                self.input.advance(1)
            elif self.input.cur_token == "this":
                self.input.advance(1)
                self.vm_writer.write_push("pointer", 0)
        elif self.input.token_type() == "SYMBOL":
            if self.input.symbol() == '(':
                self.input.advance(1)
                self.compile_expression()
                self.input.advance(1)
            elif self.input.cur_token in ['-', '~']:
                symbol_token = self.input.cur_token
                self.input.advance(1)
                self.compile_expression()
                if symbol_token == '-':
                    self.vm_writer.write_arithmetic("NEG")
                elif symbol_token == '~':
                    self.vm_writer.write_arithmetic("NOT")
        elif self.input.token_type() == "IDENTIFIER":
            self.handle_identifier()

    def get_string(self) -> None:
        """
        Converts a string constant into VM commands for creating and storing the string.
        """

        string = self.input.cur_token
        self.input.advance(1)
        self.vm_writer.write_push("constant", len(string))
        self.vm_writer.write_call("String.new", 1)

        for char in string:
            self.vm_writer.write_push("constant", ord(char))
            self.vm_writer.write_call("String.appendChar", 2)

    def handle_identifier(self) -> None:
        """
        Handles variable names, array accesses, and subroutine calls.
        """

        name = self.input.cur_token
        type = self.symbolTable.type_of(name)
        kind = self.symbolTable.kind_of(name)
        index = self.symbolTable.index_of(name)
        self.input.advance(1)

        if self.input.symbol() in ['(', '.']:
            self.cur_func = name
            self.object_caller = name
            if kind:
                self.cur_func = kind
            while self.input.cur_token != '(':
                self.cur_func += self.input.cur_token
                self.input.advance(1)
            self.compile_do()
        elif self.input.symbol() == '[':  # Array access
            self.input.advance(1)  # Skip '['
            self.compile_expression()
            self.input.advance(1)  # Skip ']'
            self.vm_writer.write_push(type, index)
            self.vm_writer.write_arithmetic("ADD")
            self.vm_writer.write_pop("pointer", 1)
            self.vm_writer.write_push("that", 0)
        else:
            self.vm_writer.write_push(type, index)

    def compile_expression_list(self) -> int:
        """
        Compiles a (possibly empty) comma-separated list of expressions.
        Returns the number of expressions compiled.
        """

        arg_num = 0
        if self.input.symbol() != ")":
            self.compile_expression()
            arg_num += 1
            while self.input.cur_token == ",":
                self.input.advance(1)  # Skip ','
                self.compile_expression()
                arg_num += 1
        return arg_num

    def compile_do(self) -> None:
        """
        Compiles a 'do' statement.

        This method processes subroutine calls within a 'do' statement, following these steps:
        - Skips the 'do' keyword.
        - Identifies whether the subroutine is a method call (implying an implicit 'this' argument).
        - Constructs the function name.
        - Skips the opening parenthesis and compiles the argument list.
        - Generates the VM call instruction.
        - If the 'do' statement does not return a value, it discards the result.
        """

        is_do = False
        arg_num = 0

        if self.input.cur_token == 'do':
            is_do = True
            self.input.advance(1)  # Skip 'do'
            kind_of_this = self.symbolTable.kind_of(self.input.cur_token)
            self.cur_func = ""

            if kind_of_this:
                self.cur_func = kind_of_this
                self.object_caller = self.input.cur_token
                self.input.advance(1)

            while self.input.cur_token != '(':
                self.cur_func += self.input.cur_token
                self.input.advance(1)

        self.input.advance(1)  # Skip '('
        function_to_write = self.cur_func

        if self.symbolTable.kind_of(self.object_caller) is not None:  # Add 'this'
            arg_num += 1
            self.vm_writer.write_push("var", 0)

        arg_num += self.compile_expression_list()

        self.vm_writer.write_call(function_to_write, arg_num)
        self.object_caller = ""

        if is_do:
            self.vm_writer.write_pop('temp', 0)  # Discard return value

        self.cur_func = ""  # Reset cur_func
        self.input.advance(1)  # Skip ')'
