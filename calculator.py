"""Evaluate input.txt using the stack and postfix method from Lecture 3."""
from pathlib import Path
from math import isfinite


class Stack:
    """A fixed-capacity stack; the top index starts at -1."""
    def __init__(self, size):
        if size < 1:
            raise ValueError("Stack size must be positive")
        self.size = size
        self.stack = [None] * size
        self.top = -1

    def is_empty(self):
        return self.top == -1

    def push(self, item):
        if self.top == self.size - 1:
            raise ValueError("Stack overflow")
        self.top += 1
        self.stack[self.top] = item

    def pop(self):
        if self.is_empty():
            raise ValueError("Stack underflow")
        item = self.stack[self.top]
        self.stack[self.top] = None
        self.top -= 1
        return item

    def peek(self):
        if self.is_empty():
            raise ValueError("Stack is empty")
        return self.stack[self.top]


def precedence(operator):
    if operator in ("+", "-"):
        return 1
    if operator in ("*", "/"):
        return 2
    return 0


def tokenize(expression):
    """Read multi-digit numbers, decimal numbers, operators and parentheses."""
    tokens = []
    i = 0
    while i < len(expression):
        ch = expression[i]
        if ch.isspace():
            i += 1
        elif ch in "0123456789.":
            start = i
            while i < len(expression) and expression[i] in "0123456789.":
                i += 1
            number = expression[start:i]
            if number == "." or number.count(".") > 1:
                raise ValueError("Invalid decimal number")
            if not isfinite(float(number)):
                raise ValueError("Number is too large")
            tokens.append(number)
        elif ch in "+-*/()":
            tokens.append(ch)
            i += 1
        else:
            raise ValueError("Unsupported character: " + ch)
    if not tokens:
        raise ValueError("Empty expression")
    return tokens


def infix_to_postfix(tokens):
    operators = Stack(len(tokens))
    postfix = []
    expect_operand = True
    for token in tokens:
        if token == "(":
            if not expect_operand:
                raise ValueError("Missing operator before '('")
            operators.push(token)
        elif token == ")":
            if expect_operand:
                raise ValueError("Missing number before ')'")
            while not operators.is_empty() and operators.peek() != "(":
                postfix.append(operators.pop())
            if operators.is_empty():
                raise ValueError("Unmatched ')'")
            operators.pop()
            expect_operand = False
        elif token in ("+", "-", "*", "/"):
            if expect_operand:
                raise ValueError("Expected a number or '('")
            while (not operators.is_empty() and operators.peek() != "("
                   and precedence(operators.peek()) >= precedence(token)):
                postfix.append(operators.pop())
            operators.push(token)
            expect_operand = True
        else:
            if not expect_operand:
                raise ValueError("Missing operator between numbers")
            postfix.append(token)
            expect_operand = False
    if expect_operand:
        raise ValueError("Expression ends before a number")
    while not operators.is_empty():
        operator = operators.pop()
        if operator == "(":
            raise ValueError("Unmatched '('")
        postfix.append(operator)
    return postfix


def calculate(a, b, operator):
    if operator == "+":
        answer = a + b
    elif operator == "-":
        answer = a - b
    elif operator == "*":
        answer = a * b
    elif operator == "/":
        if b == 0:
            raise ZeroDivisionError("Division by zero")
        answer = a / b
    else:
        raise ValueError("Unsupported operator")
    if not isfinite(answer):
        raise ValueError("Result is too large")
    return answer


def evaluate_postfix(postfix):
    values = Stack(max(1, len(postfix)))
    for token in postfix:
        if token in ("+", "-", "*", "/"):
            if values.top < 1:
                raise ValueError("Missing operand")
            b = values.pop()  # Right operand is removed first.
            a = values.pop()
            values.push(calculate(a, b, token))
        else:
            values.push(float(token))
    if values.top != 0:
        raise ValueError("Invalid expression")
    return values.pop()


def evaluate(expression):
    return evaluate_postfix(infix_to_postfix(tokenize(expression)))


def format_result(answer):
    # Round only the displayed result, not intermediate calculations.
    text = f"{answer:.4f}".rstrip("0").rstrip(".")
    return "0" if text in ("0", "-0") else text


def read_expressions(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return file.read().splitlines()


def process_lines(lines):
    results = []
    for line in lines:
        text = line.strip()
        if not text or (len(text) >= 3 and all(ch == "-" for ch in text)):
            results.append(line)  # Preserve blank and dash-only separator lines.
            continue
        try:
            results.append(format_result(evaluate(text)))
        except (ValueError, ZeroDivisionError) as error:
            results.append("Error: " + str(error))
    return results


def write_results(filename, results):
    with open(filename, "w", encoding="utf-8") as file:
        for result in results:
            file.write(result + "\n")


def main():
    folder = Path(__file__).resolve().parent
    try:
        lines = read_expressions(folder / "input.txt")
        write_results(folder / "output.txt", process_lines(lines))
    except OSError as error:
        print("File error:", error)
        return
    print("Results written to output.txt")


if __name__ == "__main__":
    main()
