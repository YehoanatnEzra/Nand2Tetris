"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""


import typing


class SymbolTable:
    """A symbol table that associates names with information needed for Jack
    compilation: type, kind, and running index. The symbol table has two nested
    scopes (class/subroutine).
    """

    def __init__(self) -> None:
        """Creates a new empty symbol table."""
        self.types_counter = {
            "var": 0,
            "argument": 0,
            "field": 0,
            "static": 0
        }
        self.class_symbol_table = {}
        self.subroutine_symbol_table = {}

    def start_subroutine(self) -> None:
        """Starts a new subroutine scope (i.e., resets the subroutine's
        symbol table)."""
        self.subroutine_symbol_table.clear()
        self.types_counter["var"] = 0
        self.types_counter["argument"] = 0

    def define(self, name: str, type: str, kind: str) -> None:
        """Defines a new identifier with a given name, type, and kind,
        and assigns it a running index. "STATIC" and "FIELD" identifiers
        have a class scope, while "ARG" and "VAR" identifiers have a
        subroutine scope.

        Args:
            name (str): The name of the new identifier.
            type (str): The type of the new identifier.
            kind (str): The kind of the new identifier, can be:
                        "STATIC", "FIELD", "ARG", "VAR".
        """
        index = self.types_counter[kind]
        if kind in {"field", "static"}:
            self.class_symbol_table[name] = [type, kind, index]
        else:
            self.subroutine_symbol_table[name] = [type, kind, index]
        self.types_counter[kind] += 1

    def var_count(self, kind: str) -> int:
        """Returns the number of variables of the given kind already defined
        in the current scope.

        Args:
            kind (str): The kind of variable ("STATIC", "FIELD", "ARG", "VAR").

        Returns:
            int: The number of variables of the given kind.
        """
        return self.types_counter[kind]

    def kind_of(self, name: str) -> typing.Optional[str]:
        """Returns the kind of the named identifier in the current scope.

        Args:
            name (str): Name of an identifier.

        Returns:
            str: The kind of the identifier, or None if unknown.
        """
        return self.get_value_from_symbol_table(name, 0)

    def type_of(self, name: str) -> typing.Optional[str]:
        """Returns the type of the named identifier in the current scope.

        Args:
            name (str): Name of an identifier.

        Returns:
            str: The type of the identifier, or None if unknown.
        """
        return self.get_value_from_symbol_table(name, 1)

    def index_of(self, name: str) -> typing.Optional[int]:
        """Returns the index assigned to the named identifier.

        Args:
            name (str): Name of an identifier.

        Returns:
            int: The index of the identifier, or None if unknown.
        """
        return self.get_value_from_symbol_table(name, 2)

    def get_value_from_symbol_table(self, name: str, index_in_symbol: int) -> typing.Optional[typing.Any]:
        """Retrieves a specific value from the symbol table.

        Args:
            name (str): Name of an identifier.
            index_in_symbol (int): The index of the required value.

        Returns:
            Any: The requested value, or None if the identifier is unknown.
        """
        if name in self.subroutine_symbol_table:
            return self.subroutine_symbol_table[name][index_in_symbol]
        elif name in self.class_symbol_table:
            return self.class_symbol_table[name][index_in_symbol]
        return None

    def check_kind_existence(self, kind: str) -> bool:
        """Checks if a given kind exists in either symbol table.

        Args:
            kind (str): The kind to check for existence.

        Returns:
            bool: True if the kind exists, False otherwise.
        """
        for symbol_info in self.subroutine_symbol_table.values():
            if symbol_info[1] == kind:
                return True
        for symbol_info in self.class_symbol_table.values():
            if symbol_info[1] == kind:
                return True
        return False
