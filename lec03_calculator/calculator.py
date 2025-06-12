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
def read_PARENT_left(index: int) -> Tuple[Token, int]:
    token = {"type": "PARENT_LEFT"}
    return token, index + 1


# Store the ")" token and increment the index by 1
def read_PARENT_right(index: int) -> Tuple[dict, int]:
    token = {"type": "PARENT_RIGHT"}
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
            (token, index) = read_PARENT_left(index)
        elif line[index] == ")":
            (token, index) = read_PARENT_right(index)
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


# Process parentheses.
# If ")" is found, decrement the index to find the first "(".
# Calculate the part enclosed by parentheses by calling the evaluate function.
# Insert the calculation result into tokens.
# Continue processing until all parentheses are removed.
def evaluate_PARENT(tokens: list) -> list:
    index = 0
    while index < len(tokens):
        if isinstance(tokens[index], dict) and tokens[index]["type"] == "PARENT_RIGHT":
            left_index = index - 1
            while left_index >= 0:
                if (
                    isinstance(tokens[left_index], dict)
                    and tokens[left_index]["type"] == "PARENT_LEFT"
                ):
                    break
                else:
                    left_index -= 1
            if left_index < 0:
                raise InvalidSyntaxError("Mismatched parentheses")
            part_of_tokens = tokens[left_index + 1 : index]
            if not part_of_tokens:
                raise InvalidSyntaxError("Empty parentheses")
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
        raise InvalidSyntaxError("Invalid syntax for the removal sign")
    return tokens


# Perform actual calculations.
# First, calculate parentheses, abs, and other symbols, as well as multiplication and division.
# Finally, calculate the remaining plus and minus operations.


def evaluate(tokens: list) -> float:
    tokens = evaluate_PARENT(tokens)
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


# Test
# Compare the actual calculation result with the value from eval, and print PASS if correct.
def test(line: str) -> str:
    tokens = tokenize(line)
    actual_answer = evaluate(tokens)
    expected_answer = eval(line)
    if abs(actual_answer - expected_answer) < 1e-8:
        print("PASS! (%s = %f)" % (line, expected_answer))
    else:
        print(
            "FAIL! (%s should be %f but was %f)"
            % (line, expected_answer, actual_answer)
        )


# Add more tests to this function :)
def run_test():
    print("==== Test started! ====")
    test("1+2")
    test("1.0+2.1-3")
    test("1+2*3")  # Check if multiplication order is correct
    test("1+2/3")  # Check if division order is correct
    test("2+4.0*2.0/5")  # Check decimals, multiplication, and division
    test("2+4*5/2-1")
    test("(2+3)")  # Check if parentheses are calculated correctly
    test("2*(3+4)")
    test("3*(2+5)*(3+2)")  # Check if parentheses are calculated first
    test("((3+2)*2+1)")
    test("(3.0+4*(2-1))/5")
    test("2 + 3")  # Check if spaces are handled correctly
    test("(3+1) * 4")  # Check spaces
    test("abs(-2)")  # abs
    test("int(2.2)")  # int
    test("round(2.6)")  # round

    # invalid input
    # test("*2+3")
    # test("a2 + 3")
    # test("abcs(2)")
    # test("abs")
    test(
        "12 + abs(int(round(-1.55) + abs(int(-2.3 + 4))))"
    )  # As per the example. Check if parentheses, abs, int, and round are executed in the correct order.
    print("==== Test finished! ====\n")


run_test()

# while True:
#     print("> ", end="")
#     line = input()
#     tokens = tokenize(line)
#     answer = evaluate(tokens)
#     print("answer = %f\n" % answer)
