"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""


class CompilationEngine:
    check = 0
    """Gets input from a self.input and emits its parsed structure into an
    output stream.
    """

    def __init__(self, input_stream: "JackTokenizer", output_stream) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        self.output_stream = output_stream
        self.input = input_stream
        self.unary_op = ['+', '-', '*', '/', '&amp;', '|', '&lt;', '&gt;', '=']

    def compile_class(self) -> None:
        """
        Compiles a complete class, including class variable declarations and subroutine declarations.
        This method starts by writing the opening XML tag for a class, processes all class-level variables,
        then compiles the subroutines within the class, and finally closes the class definition.
        """

        is_it_var = True
        is_it_sub = True

        self.write_opening_tag("class")
        self.write_wrap()  # class keyword
        self.input.advance()
        self.write_wrap()  # class name
        self.input.advance()
        self.write_wrap()  # opening brace '{'
        self.input.advance()

        # Compile class variable declarations
        if self.input.token_type() == "KEYWORD":
            while is_it_var:
                if self.input.keyword().lower() in ["static", "field"]:
                    self.compile_class_var_dec()
                else:
                    is_it_var = False

        # Compile subroutines
        if self.input.token_type() == "KEYWORD":
            while is_it_sub:
                if self.input.keyword().lower() in ["constructor", "function", "method"]:
                    self.compile_subroutine()
                else:
                    is_it_sub = False

        self.write_wrap()  # closing brace '}'
        self.input.advance()
        self.write_closing_tag("class")

    def compile_class_var_dec(self) -> None:
        """
        Compiles a static declaration or a field declaration.
        This includes processing multiple variable declarations separated by commas
        and ending the declaration with a semicolon.
        """
        self.write_opening_tag("classVarDec")
        more_var = True

        self.write_wrap()  # static/field keyword
        self.input.advance()
        self.write_wrap()  # type
        self.input.advance()
        self.write_wrap()  # variable name
        self.input.advance()

        while more_var:
            if self.input.symbol() == ",":
                self.write_wrap()  # comma ','
                self.input.advance()
                self.write_wrap()  # next variable name
                self.input.advance()
            elif self.input.symbol() == ";":
                self.write_wrap()  # semicolon ';'
                self.input.advance()
                more_var = False

        self.write_closing_tag("classVarDec")

    def write_opening_tag(self, val: str):
        """
        Writes an opening XML tag to the output stream.
        :param val: The tag name to be opened.
        """
        self.output_stream.write("<" + val + ">\n")

    def write_closing_tag(self, val: str):
        """
        Writes a closing XML tag to the output stream.
        :param val: The tag name to be closed.
        """
        self.output_stream.write("</" + val + ">\n")

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        self.write_opening_tag("subroutineDec")
        self.write_wrap()  # (constructor|method|function)
        self.input.advance()
        self.write_wrap()   # (void|type)
        self.input.advance()
        self.write_wrap()   # (subroutine name)
        self.input.advance()
        self.write_wrap()  # (
        self.input.advance()
        self.compile_parameter_list()
        self.write_wrap()  # )
        self.input.advance()
        self.compile_subroutine_body()
        self.write_closing_tag("subroutineDec")

    def compile_subroutine_body(self):
        """
        Compiles a subroutine's body, including variable declarations and statements.
        This method writes the opening tag for the subroutine body, processes variable
        declarations if present, then compiles statements until the closing brace '}' is reached.
        """

        self.write_opening_tag("subroutineBody")
        self.write_wrap()  # open {
        self.input.advance()

        # Process variable declarations and statements
        while self.input.symbol() != "}":
            flag = self.compile_var_dec()
            if not flag:
                self.compile_statements()

        self.write_wrap()  # close }
        self.input.advance()
        self.write_closing_tag("subroutineBody")

    def compile_parameter_list(self) -> None:
        """
        Compiles a (possibly empty) parameter list, not including the enclosing "()".
        This method processes function parameters, handling types and variable names,
        and managing multiple parameters separated by commas.
        """

        self.write_opening_tag("parameterList")

        # If the parameter list is empty, close the tag and return
        if self.input.token_type() == "SYMBOL":
            self.write_closing_tag("parameterList")
            return

        # Process the first parameter (type and name)
        self.write_wrap()
        self.input.advance()
        self.write_wrap()
        self.input.advance()

        # Process additional parameters if they exist
        while self.input.symbol() == ',':
            self.write_wrap()  # comma ','
            self.input.advance()
            self.write_wrap()  # type
            self.input.advance()
            self.write_wrap()  # variable name
            self.input.advance()

        self.write_closing_tag("parameterList")

    def compile_var_dec(self) -> bool:
        """
        Compiles a variable declaration statement.
        This method processes 'var' declarations, ensuring that all variables
        and their types are parsed correctly and enclosed properly in the XML output.
        Returns False if the token is a keyword indicating the start of a statement,
        meaning there are no more variable declarations to process.
        """

        if self.input.token_type() == "KEYWORD":
            if self.input.keyword().lower() in ['let', 'do', 'if', 'while', 'return']:
                return False

        self.write_opening_tag("varDec")

        # Process variable declaration until ';' is reached
        while self.input.symbol() != ";":
            self.write_wrap()
            self.input.advance()

        self.write_wrap()  # semicolon ';'
        self.input.advance()
        self.write_closing_tag("varDec")

        return True

# TODO - here
    def compile_statements(self) -> None:
        """
        Compiles a sequence of statements, not including the enclosing "{}".
        This method processes multiple statements inside a block, calling the appropriate
        compilation method based on the type of statement encountered.
        """

        self.write_opening_tag("statements")

        # Process each statement until the closing '}' symbol is reached
        while self.input.token_type() != "SYMBOL":  # until "}"

            letter = self.input.keyword().lower()

            if letter == "let":
                self.compile_let()
            elif letter == "if":
                self.compile_if()
            elif letter == "while":
                self.compile_while()
            elif letter == "do":
                self.compile_do()
            elif letter == "return":
                self.compile_return()

        self.write_closing_tag("statements")

    def compile_subroutine_call(self):
        """
        Compiles a subroutine call, which can be either:
        - A direct function call with parentheses (e.g., `foo()`)
        - A method call on an object (e.g., `obj.foo()`)
        This method processes the function name, optional object/class name,
        and the list of expressions passed as arguments.
        """

        if self.input.symbol() == '(':
            self.write_wrap()  # '('
            self.input.advance()
            self.compile_expression_list()
            self.write_wrap()  # ')'
            self.input.advance()

        elif self.input.symbol() == '.':
            self.write_wrap()  # '.'
            self.input.advance()
            self.write_wrap()  # subroutine name
            self.input.advance()
            self.write_wrap()  # '('
            self.input.advance()
            self.compile_expression_list()
            self.write_wrap()  # ')'
            self.input.advance()

    def compile_do(self) -> None:
        """
        Compiles a 'do' statement.
        A 'do' statement consists of the 'do' keyword followed by a subroutine call
        and ending with a semicolon (';'). This method processes the entire 'do' statement
        and ensures correct XML formatting.
        """

        self.write_opening_tag("doStatement")

        self.write_wrap()  # 'do' keyword
        self.input.advance()
        self.write_wrap()  # subroutine name or object
        self.input.advance()

        self.compile_subroutine_call()

        self.write_wrap()  # ';' (end of statement)
        self.input.advance()

        self.write_closing_tag("doStatement")

    def compile_let(self) -> None:
        """
        Compiles a 'let' statement.

        A 'let' statement assigns a value to a variable. It follows this structure:
        - 'let' keyword
        - Variable name
        - Optional array indexing (if assigning to an array element)
        - '=' symbol
        - Expression to be assigned
        - ';' to close the statement

        This method processes the entire statement and ensures correct XML formatting.
        """

        self.write_opening_tag("letStatement")

        self.write_wrap()  # 'let' keyword
        self.input.advance()
        self.write_wrap()  # variable name
        self.input.advance()

        # Handle array indexing if present
        if self.input.token_type() == "SYMBOL" and self.input.symbol() == "[":
            self.write_wrap()  # '['
            self.input.advance()
            self.compile_expression()
            self.write_wrap()  # ']'
            self.input.advance()

        self.write_wrap()  # '='
        self.input.advance()
        self.compile_expression()

        self.write_wrap()  # ';' (end of statement)
        self.input.advance()

        self.write_closing_tag("letStatement")

    def compile_while(self) -> None:
        """
        Compiles a 'while' statement.

        A 'while' statement follows this structure:
        - 'while' keyword
        - Opening parenthesis '('
        - Boolean expression (condition for looping)
        - Closing parenthesis ')'
        - Opening brace '{'
        - Body of the loop (statements inside the while loop)
        - Closing brace '}'

        This method processes the entire statement and ensures correct XML formatting.
        """

        self.write_opening_tag("whileStatement")

        self.write_wrap()  # 'while' keyword
        self.input.advance()
        self.write_wrap()  # '('
        self.input.advance()

        self.compile_expression()  # Condition expression

        self.write_wrap()  # ')'
        self.input.advance()
        self.write_wrap()  # '{'
        self.input.advance()

        self.compile_statements()  # Statements inside the loop

        self.write_wrap()  # '}'
        self.input.advance()

        self.write_closing_tag("whileStatement")

    def compile_return(self) -> None:
        """
        Compiles a 'return' statement.

        A 'return' statement can take one of two forms:
        - 'return;' (returning nothing)
        - 'return <expression>;' (returning a value)

        This method processes the 'return' keyword, checks whether an expression
        follows it, and ensures correct XML formatting.
        """

        self.write_opening_tag("returnStatement")

        self.write_wrap()  # 'return' keyword
        self.input.advance()

        # Check if the return statement contains an expression
        if self.input.symbol() == ";":
            self.write_wrap()  # ';'
            self.input.advance()
        else:
            self.compile_expression()
            self.write_wrap()  # ';'
            self.input.advance()

        self.write_closing_tag("returnStatement")

    def compile_if(self) -> None:
        """
        Compiles an 'if' statement, possibly with a trailing 'else' clause.

        An 'if' statement follows this structure:
        - 'if' keyword
        - Opening parenthesis '(' for the condition
        - Boolean expression (condition for the 'if' block)
        - Closing parenthesis ')'
        - Opening brace '{' for the statement block
        - Statements inside the 'if' block
        - Closing brace '}'
        - (Optional) 'else' keyword followed by another statement block

        This method processes both the 'if' and the optional 'else' part and ensures correct XML formatting.
        """

        self.write_opening_tag("ifStatement")

        self.write_wrap()  # 'if' keyword
        self.input.advance()
        self.write_wrap()  # '('
        self.input.advance()

        self.compile_expression()  # Condition expression

        self.write_wrap()  # ')'
        self.input.advance()
        self.write_wrap()  # '{'
        self.input.advance()

        self.compile_statements()  # Statements inside the 'if' block

        self.write_wrap()  # '}'
        self.input.advance()

        # Check for optional 'else' clause
        if self.input.token_type() == "KEYWORD" and self.input.keyword().lower() == "else":
            self.write_wrap()  # 'else' keyword
            self.input.advance()
            self.write_wrap()  # '{'
            self.input.advance()
            self.compile_statements()
            self.write_wrap()  # '}'
            self.input.advance()

        self.write_closing_tag("ifStatement")

    def compile_expression(self) -> None:
        """
        Compiles an expression.

        An expression consists of one or more terms connected by operators.
        This method processes a single term first, then checks for additional
        terms connected by binary operators. If present, it processes them
        accordingly and ensures correct XML formatting.
        """

        self.write_opening_tag("expression")

        self.compile_term()  # Compile the first term

        # Process additional terms connected by operators
        while self.input.token_type() == "SYMBOL" and self.input.symbol() in self.unary_op:
            if self.input.symbol() in self.unary_op:
                self.write_wrap()
                self.input.advance()
                self.compile_term()

        self.write_closing_tag("expression")

    def compile_term(self) -> None:
        """Compiles a term.
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        self.write_opening_tag("term")
        if self.input.token_type() == "INT_CONST" or self.input.token_type() == "STRING_CONST":
            self.write_wrap()
            self.input.advance()
        elif self.input.token_type() == "KEYWORD":
            if self.input.keyword().lower() == 'true' or 'false' or 'null' or 'this':
                self.write_wrap()
                self.input.advance()
        elif self.input.token_type() == "SYMBOL":
            if self.input.symbol() == '(':
                self.write_wrap()
                self.input.advance()
                self.compile_expression()
                self.write_wrap()
                self.input.advance()
            elif self.input.symbol() == '-' or '~':
                self.write_wrap()
                self.input.advance()
                self.compile_term()

        elif self.input.token_type() == "IDENTIFIER":

            self.write_wrap()
            self.input.advance()
            if self.input.token_type() != "SYMBOL":
                pass
            else:
                if self.input.symbol() == '(' or self.input.symbol() == '.':
                    self.compile_subroutine_call()

                elif self.input.symbol() == '[':  # array
                    self.write_wrap()
                    self.input.advance()
                    self.compile_expression()
                    self.write_wrap()
                    self.input.advance()
        self.write_closing_tag("term")

    def compile_expression_list(self) -> None:
        """
        Compiles a (possibly empty) comma-separated list of expressions.

        An expression list appears in function calls and array initializations.
        It consists of zero or more expressions separated by commas.

        This method processes the list of expressions, ensuring correct XML formatting.
        """

        self.write_opening_tag("expressionList")

        # Check if the list is empty
        if self.input.symbol() != ")":
            self.compile_expression()

            # Process additional expressions separated by commas
            while self.input.symbol() == ",":
                self.write_wrap()  # ','
                self.input.advance()
                self.compile_expression()

        self.write_closing_tag("expressionList")

    def write(self, string1: str) -> None:
        """
        Writes a given string to the output stream.

        :param string1: The string to be written to the output stream.
        """
        self.output_stream.write(string1)

    def write_wrap(self) -> None:
        """
        Writes the current token wrapped in XML tags to the output stream.

        This method identifies the type of the current token, processes it accordingly,
        and formats it into an XML-compliant string before writing it to the output.
        """

        type1 = self.input.token_type()

        if type1 == "KEYWORD":
            word = self.input.keyword().lower()
            type1 = type1.lower()
        elif type1 == "SYMBOL":
            word = self.input.symbol()
            type1 = type1.lower()
        elif type1 == "INT_CONST":
            word = str(self.input.int_val())
            type1 = "integerConstant"
        elif type1 == "STRING_CONST":
            word = self.input.string_val()[1:-1]  # Remove surrounding quotes
            type1 = "stringConstant"
        elif type1 == "IDENTIFIER":
            word = self.input.identifier()
            type1 = type1.lower()

        self.write(f"<{type1}> {word} </{type1}>\n")
