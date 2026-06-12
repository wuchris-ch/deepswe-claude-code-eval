"""evaluator — arithmetic expression evaluator.

Spec (this docstring is the agreed contract)
--------------------------------------------
``evaluate(expr: str) -> int | float``

Grammar: numbers (integer or decimal literals), binary ``+ - * / ^``,
unary minus, and parentheses. Whitespace between tokens is ignored.

Semantics:
- Precedence, lowest to highest: ``+ -``  <  ``* /``  <  unary minus
  <  ``^``.
- ``+ - * /`` are left-associative; ``^`` is RIGHT-associative:
  ``2^3^2`` is ``2^(3^2)`` = 512.
- Unary minus binds tighter than ``* /`` but looser than ``^``:
  ``-2^2`` is ``-(2^2)`` = -4, and ``2^-2`` is ``0.25``.
- Unary minus may follow a binary operator: ``2--3`` is ``5``,
  ``2*-3`` is ``-6``.
- ``/`` is true division and always yields a float (``8/2`` == 4.0).
  ``+ - * ^`` between two ints yield an int (Python semantics), except
  ``int ^ negative-int`` which yields a float.
- Malformed input — unbalanced parentheses, dangling operators,
  unexpected characters, empty input — raises ``ValueError`` (never
  any other exception type).
"""


def tokenize(expr):
    tokens, i = [], 0
    while i < len(expr):
        ch = expr[i]
        if ch.isspace():
            i += 1
        elif ch.isdigit() or ch == ".":
            j = i
            while j < len(expr) and (expr[j].isdigit() or expr[j] == "."):
                j += 1
            text = expr[i:j]
            tokens.append(float(text) if "." in text else int(text))
            i = j
        elif ch in "+-*/^()":
            tokens.append(ch)
            i += 1
        else:
            raise ValueError(f"unexpected character: {ch!r}")
    return tokens


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def next(self):
        tok = self.peek()
        self.pos += 1
        return tok

    def parse_expr(self):
        value = self.parse_term()
        while self.peek() in ("+", "-"):
            op = self.next()
            rhs = self.parse_term()
            value = value + rhs if op == "+" else value - rhs
        return value

    def parse_term(self):
        value = self.parse_factor()
        while self.peek() in ("*", "/", "^"):
            op = self.next()
            rhs = self.parse_factor()
            if op == "*":
                value = value * rhs
            elif op == "/":
                value = value // rhs if isinstance(value, int) and isinstance(rhs, int) else value / rhs
            else:
                value = value ** rhs
        return value

    def parse_factor(self):
        tok = self.peek()
        if tok == "-":
            self.next()
            return -self.parse_factor()
        if tok == "(":
            self.next()
            value = self.parse_expr()
            if self.peek() == ")":
                self.next()
            return value
        if isinstance(tok, (int, float)):
            return self.next()
        raise ValueError(f"unexpected token: {tok!r}")


def evaluate(expr):
    parser = Parser(tokenize(expr))
    return parser.parse_expr()
