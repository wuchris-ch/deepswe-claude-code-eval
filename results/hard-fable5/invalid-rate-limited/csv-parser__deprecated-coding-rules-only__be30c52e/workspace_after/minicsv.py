"""minicsv — a tiny dependency-free CSV parser.

Spec (this docstring is the agreed contract)
--------------------------------------------
``parse(text) -> list[list[str]]``

- Fields are separated by commas. Rows are separated by ``\\n`` or
  ``\\r\\n`` (both must work, including mixed within one input).
- A field may be quoted with double quotes. Inside a quoted field,
  commas and newlines are literal data, and a doubled quote ``""``
  produces one literal ``"`` character.
- Quotes are only special at the very start of a field; an unquoted
  field is taken verbatim (whitespace preserved).
- Empty fields are preserved: ``"a,,b"`` is ``[["a", "", "b"]]`` and
  ``"a,"`` is ``[["a", ""]]``.
- A completely empty line in the middle of the input is a row with a
  single empty field. A single trailing newline at the very end of the
  input does NOT produce an extra row.
- ``parse("")`` returns ``[]``.
- Malformed input — an unterminated quoted field, or a closing quote
  followed by anything other than a comma or end of row — raises
  ``ValueError``.
"""


def parse(text):
    rows = []
    for line in text.split("\n"):
        if not line:
            continue
        row, field, in_quotes = [], "", False
        for ch in line:
            if ch == '"':
                in_quotes = not in_quotes
            elif ch == "," and not in_quotes:
                row.append(field)
                field = ""
            else:
                field += ch
        row.append(field)
        rows.append(row)
    return rows
