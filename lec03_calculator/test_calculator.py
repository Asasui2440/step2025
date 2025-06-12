# python -m unittest test_calculator.py

import unittest
from calculator import tokenize, evaluate


class TestCalculator(unittest.TestCase):
    def test_basic_operations(self):
        self.assertAlmostEqual(evaluate(tokenize("1+2")), 3.0)
        self.assertAlmostEqual(evaluate(tokenize("1.0+2.1-3")), 0.1)
        self.assertAlmostEqual(evaluate(tokenize("1+2*3")), 7.0)
        self.assertAlmostEqual(evaluate(tokenize("1+2/3")), 1.6666666666666667)

    def test_parentheses(self):
        self.assertAlmostEqual(evaluate(tokenize("(2+3)")), 5.0)
        self.assertAlmostEqual(evaluate(tokenize("2*(3+4)")), 14.0)
        self.assertAlmostEqual(evaluate(tokenize("3*(2+5)*(3+2)")), 105.0)
        self.assertAlmostEqual(evaluate(tokenize("((3+2)*2+1)")), 11.0)

    def test_functions(self):
        self.assertAlmostEqual(evaluate(tokenize("abs(-2)")), 2.0)
        self.assertAlmostEqual(evaluate(tokenize("int(2.2)")), 2.0)

        self.assertAlmostEqual(evaluate(tokenize("round(2.6)")), 3.0)
        self.assertAlmostEqual(evaluate(tokenize("round(-1.55)")), -2.0)

    def test_complex_expression(self):
        self.assertAlmostEqual(
            evaluate(tokenize("12 + abs(int(round(-1.55) + abs(int(-2.3 + 4))))")),
            13.0,
        )

    def test_invalid_syntax(self):
        test_cases = [
            "*2+3",
            "a2 + 3",
            "abcs(2)",
            "intround(2)",
            "2-3*",
            "(2-3))",
            "++2-9*3",
        ]

        for case in test_cases:
            with self.subTest(case=case):
                with self.assertRaises(Exception):
                    evaluate(tokenize(case))


if __name__ == "__main__":
    unittest.main()
