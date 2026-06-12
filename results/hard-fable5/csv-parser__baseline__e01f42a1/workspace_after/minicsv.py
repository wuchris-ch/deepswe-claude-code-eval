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


FIELD_START, UNQUOTED, QUOTED, AFTER_QUOTE = range(4)


def parse(text):
    if text == "":
        return []

    rows = []
    row = []
    field = []
    state = FIELD_START
    i = 0
    n = len(text)

    while i < n:
        ch = text[i]

        if state == QUOTED:
            if ch == '"':
                if i + 1 < n and text[i + 1] == '"':
                    field.append('"')
                    i += 2
                else:
                    state = AFTER_QUOTE
                    i += 1
            else:
                field.append(ch)
                i += 1
            continue

        row_end = ch == "\n" or (
            ch == "\r" and i + 1 < n and text[i + 1] == "\n"
        )
        if row_end:
            row.append("".join(field))
            rows.append(row)
            row, field = [], []
            state = FIELD_START
            i += 2 if ch == "\r" else 1
        elif state == AFTER_QUOTE:
            if ch != ",":
                raise ValueError(
                    "closing quote must be followed by a comma or "
                    "end of row at offset %d" % i
                )
            row.append("".join(field))
            field = []
            state = FIELD_START
            i += 1
        elif ch == ",":
            row.append("".join(field))
            field = []
            state = FIELD_START
            i += 1
        elif state == FIELD_START and ch == '"':
            state = QUOTED
            i += 1
        else:
            state = UNQUOTED
            field.append(ch)
            i += 1

    if state == QUOTED:
        raise ValueError("unterminated quoted field")
    # A pending field exists unless the input ended exactly at a row
    # boundary (trailing newline), in which case no extra row is emitted.
    if row or field or state != FIELD_START:
        row.append("".join(field))
        rows.append(row)
    return rows
