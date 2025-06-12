#! /usr/bin/python3
# python calculator.py

from enum import Enum
from typing import Tuple


class Number:
    def __init__(self, value: float):
        self.value = value


class Operand(Enum):
    PLUS = 1
    MINUS = 2
    TIMES = 3
    DIVIEDES = 4


class MonoFunc(Enum):
    ABS = 1
    ROUND = 2
    INT = 3


type Token = Number | Operand | MonoFunc


class InvalidSyntaxError(Exception):
    pass


# Recognize numbers and store them in tokens.
# Also recognize decimal points to enable calculations with decimals.
def read_number(
    line: str, index: int
) -> Tuple[Token, int]:  # 拡張機能が古い？ typing.Listを試す
    number = 0
    while index < len(line) and line[index].isdigit():
        number = number * 10 + int(line[index])
        index += 1
    if index < len(line) and line[index] == ".":
        index += 1
        decimal = 0.1
        while index < len(line) and line[index].isdigit():
            number += int(line[index]) * decimal
            decimal /= 10
            index += 1
    token = Number(number)
    return token, index


# Read symbols and return tokens and index


# Store the "+" token and increment the index by 1
def read_plus(index: int) -> Tuple[Token, int]:
    token = Operand.PLUS
    return token, index + 1


# Store the "-" token and increment the index by 1
def read_minus(index: int) -> Tuple[Token, int]:
    token = Operand.MINUS
    return token, index + 1


# Store the "*" token and increment the index by 1
def read_times(index: int) -> Tuple[Token, int]:
    token = Operand.TIMES
    return token, index + 1


# Store the "/" token and increment the index by 1
def read_divide(index: int) -> Tuple[Token, int]:
    token = Operand.DIVIEDES
    return token, index + 1


# Store the "(" token and increment the index by 1
def read_PAREN_left(index: int) -> Tuple[Token, int]:
    token = {"type": "PAREN_LEFT"}
    return token, index + 1


# Store the ")" token and increment the index by 1
def read_PAREN_right(index: int) -> Tuple[dict, int]:
    token = {"type": "PAREN_RIGHT"}
    return token, index + 1


# Store the "abs" token and increment the index by 3 (length of "abs")
def read_abs(index: int) -> Tuple[dict, int]:
    token = MonoFunc.ABS
    return token, index + 3


# Store the "round" token and increment the index by 5 (length of "round")
def read_round(index: int) -> Tuple[Token, int]:
    token = MonoFunc.ROUND
    return token, index + 5


# Store the "int" token and increment the index by 3 (length of "int")
def read_int(index: int) -> Tuple[Token, int]:
    token = MonoFunc.INT
    return token, index + 3


# Create a list of tokens
def tokenize(line: str) -> list:
    tokens = []
    index = 0
    while index < len(line):
        if line[index].isdigit():
            (token, index) = read_number(line, index)
        elif line[index] == "+":
            (token, index) = read_plus(index)
        elif line[index] == "-":
            (token, index) = read_minus(index)
        elif line[index] == "*":
            (token, index) = read_times(index)
        elif line[index] == "/":
            (token, index) = read_divide(index)
        elif line[index] == "(":
            (token, index) = read_PAREN_left(index)
        elif line[index] == ")":
            (token, index) = read_PAREN_right(index)
        elif line[index : index + 3] == "abs":
            (token, index) = read_abs(index)
        elif line[index : index + 5] == "round":
            (token, index) = read_round(index)
        elif line[index : index + 3] == "int":  # 負の値だった時は０に近づく
            (token, index) = read_int(index)
        elif (
            line[index] == " "
        ):  # If it's a space, skip processing without appending a token
            index += 1
            continue
        else:
            raise InvalidSyntaxError(f"Invalid character found: {line[index]}")
        tokens.append(token)
    return tokens


# Perform calculations for abs, round, and int.
# If the next value after abs is a number, calculate abs(number) and insert it into the token list.
# If it's not a number, handle it as invalid input and raise an error.
# Perform similar processing for int and round.


def evaluate_options(tokens: list) -> list:
    index = 0
    while index < len(tokens):
        if tokens[index] == MonoFunc.ABS:
            if isinstance(tokens[index + 1], Number):
                number = abs(tokens[index + 1].value)
                tokens = tokens[:index] + [Number(number)] + tokens[index + 2 :]
            else:
                raise InvalidSyntaxError("Invalid syntax for ABS function")

        elif tokens[index] == MonoFunc.ROUND:
            if isinstance(tokens[index + 1], Number):
                number = round(tokens[index + 1].value)
                tokens = tokens[:index] + [Number(number)] + tokens[index + 2 :]
            else:
                raise InvalidSyntaxError("Invalid syntax for ROUND function")

        elif tokens[index] == MonoFunc.INT:
            if isinstance(tokens[index + 1], Number):
                number = int(tokens[index + 1].value)
                tokens = tokens[:index] + [Number(number)] + tokens[index + 2 :]
            else:
                raise InvalidSyntaxError("Invalid syntax for INT function")

        else:
            index += 1
    return tokens


# Process Parentheses.
# If ")" is found, decrement the index to find the first "(".
# Calculate the part enclosed by Parentheses by calling the evaluate function.
# Insert the calculation result into tokens.
# Continue processing until all Parentheses are removed.
def evaluate_PAREN(tokens: list) -> list:
    index = 0
    while index < len(tokens):
        if isinstance(tokens[index], dict) and tokens[index]["type"] == "PAREN_RIGHT":
            left_index = index - 1
            while left_index >= 0:
                if (
                    isinstance(tokens[left_index], dict)
                    and tokens[left_index]["type"] == "PAREN_LEFT"
                ):
                    break
                else:
                    left_index -= 1
            if left_index < 0:
                raise InvalidSyntaxError("Mismatched Parentheses")
            part_of_tokens = tokens[left_index + 1 : index]
            if not part_of_tokens:
                raise InvalidSyntaxError("Empty Parentheses")
            calculated_number = evaluate(part_of_tokens)
            tokens = (
                tokens[:left_index] + [Number(calculated_number)] + tokens[index + 1 :]
            )
            index = left_index
        else:
            index += 1
    return tokens


# Process multiplication and division.
# If the token is a number and the previous index is "*", multiply it with the number two indices before.
# If the token two indices before "*" is not a number, handle it as invalid input and raise an error.
# Insert the calculation result into the token list and decrement the index by 2 for the reduced tokens.
# Perform similar processing for division.
# If the token at the index is neither a number, PLUS, nor MINUS, handle it as invalid input and raise an error.
def evaluate_times_divide(tokens: list) -> list:
    index = 1
    while index < len(tokens):
        if isinstance(tokens[index], Number):
            if index - 2 >= 0 and tokens[index - 1] == Operand.TIMES:
                if isinstance(tokens[index - 2], Number):
                    answer = tokens[index - 2].value * tokens[index].value
                    tokens = (
                        tokens[: index - 2] + [Number(answer)] + tokens[index + 1 :]
                    )
                    index -= 2
                else:
                    raise InvalidSyntaxError("Invalid syntax for TIMES calculation")

            elif index - 2 >= 0 and tokens[index - 1] == Operand.DIVIEDES:
                if isinstance(tokens[index - 2], Number):
                    answer = tokens[index - 2].value / tokens[index].value
                    tokens = (
                        tokens[: index - 2] + [Number(answer)] + tokens[index + 1 :]
                    )
                    index -= 2
                else:
                    raise InvalidSyntaxError("Invalid syntax for  DIVIDES calculation")

            elif (
                tokens[index - 1] != Operand.PLUS and tokens[index - 1] != Operand.MINUS
            ):
                raise InvalidSyntaxError("Invalid syntax for TIMES_DIVIDES calculation")
        index += 1
    if (Operand.TIMES in tokens) or (Operand.DIVIEDES in tokens):
        raise InvalidSyntaxError("Invalid syntax for the unnecessary sign")
    return tokens


# Perform actual calculations.
# First, calculate PARENtheses, abs, and other symbols, as well as multiplication and division.
# Finally, calculate the remaining plus and minus operations.


def evaluate(tokens: list) -> float:
    tokens = evaluate_PAREN(tokens)
    tokens = evaluate_options(tokens)
    tokens = evaluate_times_divide(tokens)

    answer = 0
    tokens.insert(0, Operand.PLUS)  # Insert a dummy '+' token
    index = 1
    while index < len(tokens):
        if isinstance(tokens[index], Number):
            if tokens[index - 1] == Operand.PLUS:
                answer += tokens[index].value
            elif tokens[index - 1] == Operand.MINUS:
                answer -= tokens[index].value
            else:
                raise InvalidSyntaxError("Error for plus_minus calculation")
        index += 1
    return answer


if __name__ == "__main__":
    while True:
        print("> ", end="")
        line = input()
        tokens = tokenize(line)
        answer = evaluate(tokens)
        print("answer = %f\n" % answer)
