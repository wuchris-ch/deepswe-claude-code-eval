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
    if text == "":
        return []

    rows = []
    row = []
    i = 0
    n = len(text)

    while True:
        # Read exactly one field starting at index i.
        field_chars = []
        if i < n and text[i] == '"':
            # Quoted field: quotes are only special at the field start.
            i += 1
            while True:
                if i >= n:
                    raise ValueError("unterminated quoted field")
                c = text[i]
                if c == '"':
                    if i + 1 < n and text[i + 1] == '"':
                        field_chars.append('"')  # doubled quote -> one quote
                        i += 2
                    else:
                        i += 1  # consume the closing quote
                        break
                else:
                    field_chars.append(c)  # commas/newlines are literal here
                    i += 1
            # A closing quote may only be followed by a delimiter or end of row.
            if i < n and text[i] not in (",", "\n", "\r"):
                raise ValueError("unexpected character after closing quote")
        else:
            # Unquoted field: taken verbatim up to the next delimiter.
            while i < n and text[i] not in (",", "\n", "\r"):
                field_chars.append(text[i])
                i += 1

        row.append("".join(field_chars))

        if i >= n:
            rows.append(row)
            break

        c = text[i]
        if c == ",":
            i += 1
            continue
        # Row separator: "\n", "\r\n", or a lone "\r".
        if c == "\r" and i + 1 < n and text[i + 1] == "\n":
            i += 2
        else:
            i += 1
        rows.append(row)
        row = []
        if i >= n:
            # A single trailing newline does not produce an extra row.
            break

    return rows
