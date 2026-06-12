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
    row = []
    field = ""
    field_start = True   # True when the parser is at the start of a field
    dirty = False        # True when the current row has pending content to flush
    i = 0
    n = len(text)

    while i < n:
        ch = text[i]

        if field_start and ch == '"':
            # Quoted field: quotes are only special at the very start.
            i += 1
            chars = []
            while True:
                if i >= n:
                    raise ValueError("unterminated quoted field")
                c = text[i]
                if c == '"':
                    if i + 1 < n and text[i + 1] == '"':
                        chars.append('"')  # doubled quote -> one literal quote
                        i += 2
                        continue
                    i += 1  # consume the closing quote
                    break
                chars.append(c)
                i += 1
            field = "".join(chars)
            field_start = False
            dirty = True

            # A closing quote may only be followed by a comma or end of row.
            if i >= n:
                continue
            c = text[i]
            if c == ",":
                row.append(field)
                field = ""
                field_start = True
                i += 1
            elif c == "\n":
                row.append(field)
                rows.append(row)
                row, field = [], ""
                field_start, dirty = True, False
                i += 1
            elif c == "\r" and i + 1 < n and text[i + 1] == "\n":
                row.append(field)
                rows.append(row)
                row, field = [], ""
                field_start, dirty = True, False
                i += 2
            else:
                raise ValueError("quoted field followed by unexpected data")
            continue

        if ch == ",":
            row.append(field)
            field = ""
            field_start = True
            dirty = True
            i += 1
        elif ch == "\n":
            row.append(field)
            rows.append(row)
            row, field = [], ""
            field_start, dirty = True, False
            i += 1
        elif ch == "\r" and i + 1 < n and text[i + 1] == "\n":
            row.append(field)
            rows.append(row)
            row, field = [], ""
            field_start, dirty = True, False
            i += 2
        else:
            field += ch
            field_start = False
            dirty = True
            i += 1

    # Flush the final row unless the input ended on a row separator (a single
    # trailing newline does not produce an extra row).
    if dirty:
        row.append(field)
        rows.append(row)

    return rows
