import typing

class JackTokenizer:
    """Tokenizer for the Jack programming language. 
    This class removes comments and splits input into tokens according to Jack grammar.
    """

    def __init__(self, input_stream: typing.TextIO) -> None:
        """Initializes the tokenizer by reading the input and preparing the token stream.

        Args:
            input_stream (typing.TextIO): The input stream containing the Jack source code.
        """
        self.keywords = ['class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'int', 'char', 
                         'boolean', 'void', 'true', 'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return']
        self.symbols = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~', '^', '#']
        self.arithmetics = ['-', '/', '+', '*']
        self.input_lines = input_stream.read()
        self.pre_tokens1 = self.delete_comments()
        self.pre_tokens1 = self.pre_tokens1.splitlines()
        self.pre_tokens = []
        self.tokens = []
        self.seperate_strings(self.pre_tokens1)
        self.seperate_tokens()
        self.tokens_counter = 0
        self.num_of_tokens = len(self.tokens) - 1
        self.cur_token = self.tokens[0]

    def check_expression_loop(self) -> bool:
        """Checks if the current token is an arithmetic operator.

        Returns:
            bool: True if the current token is an arithmetic operator, False otherwise.
        """
        if self.cur_token in self.arithmetics:
            return True
        return False

    def has_more_tokens(self) -> bool:
        """Checks if there are more tokens in the input.

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        if self.tokens_counter >= self.num_of_tokens:
            return False
        return True

    def advance(self, tokens_to_advance: int) -> None:
        """Advances the tokenizer by a given number of tokens.

        Args:
            tokens_to_advance (int): The number of tokens to advance.
        """
        for i in range(tokens_to_advance):
            self.tokens_counter += 1
            if self.has_more_tokens():
                self.cur_token = self.tokens[self.tokens_counter]

    def token_type(self) -> str:
        """Determines the type of the current token.

        Returns:
            str: One of "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST".
        """
        if self.cur_token in self.keywords:
            return "KEYWORD"
        elif self.cur_token in self.symbols:
            return "SYMBOL"
        elif self.cur_token[0].isdigit():
            return "INT_CONST"
        elif self.cur_token[0] == '"':
            return "STRING_CONST"
        else:
            return "IDENTIFIER"

    def keyword(self) -> str:
        """Returns the current token as an uppercase keyword.

        Returns:
            str: The keyword token in uppercase.
        """
        return self.cur_token.upper()

    def symbol(self) -> str:
        """Returns the current token as a symbol.

        Returns:
            str: The current symbol token.
        """
        return self.cur_token

    def identifier(self) -> str:
        """Returns the current token as an identifier.

        Returns:
            str: The identifier token.
        """
        return self.cur_token

    def int_val(self) -> int:
        """Returns the integer value of the current token.

        Returns:
            int: The integer constant token if in range [0, 32767].
        """
        if 0 <= int(self.cur_token) < 32768:
            return int(self.cur_token)

    def string_val(self) -> str:
        """Returns the string value of the current token without quotes.

        Returns:
            str: The string constant without enclosing quotes.
        """
        return self.cur_token.strip('"')

    def delete_comments(self) -> str:
        """Removes all comments from the input code.

        Returns:
            str: The input code with comments removed.
        """
        lines_input = self.input_lines
        text = ""
        i = 0
        in_string = False
        while i < len(lines_input):
            if not in_string and lines_input[i:i + 2] == "/*":
                end_comment_index = lines_input.find("*/", i + 2)
                if end_comment_index != -1:
                    i = end_comment_index + 2
            elif not in_string and lines_input[i:i + 2] == "//":
                end_line_index = lines_input.find("\n", i + 2)
                if end_line_index != -1:
                    i = end_line_index + 1
            elif lines_input[i] == '"':
                in_string = not in_string
                text += lines_input[i]
                i += 1
            else:
                text += lines_input[i]
                i += 1
        return text

    def seperate_strings(self, lines_):
        """Separates string literals from the rest of the tokens."""
        for line in lines_:
            self.pre_tokens.append(line)

    def seperate_tokens(self):
        """Tokenizes the preprocessed input."""
        for line in self.pre_tokens:
            tryit = line.split()
            if tryit == []:
                continue
            if line[0] == '"':
                self.tokens.append(line)
                continue
            words = line.split()
            for section in words:
                self.append_until_symbol(section)

    def append_until_symbol(self, section):
        """Splits a given section into tokens based on symbols."""
        counter = 0
        word = ""
        for letter in section:
            if letter in self.symbols:
                if word != "":
                    self.tokens.append(word)
                    self.tokens.append(letter)
                    word = ""
                else:
                    self.tokens.append(letter)
            else:
                word += letter
                counter += 1
        if word != "":
            self.tokens.append(word)
