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
    if not text:
        return []

    rows = []
    row = []
    field = ""
    in_quotes = False
    i = 0

    while i < len(text):
        ch = text[i]

        if in_quotes:
            if ch == '"':
                if i + 1 < len(text) and text[i + 1] == '"':
                    field += '"'
                    i += 2
                else:
                    in_quotes = False
                    i += 1
                    if i < len(text):
                        if text[i] == ',':
                            row.append(field)
                            field = ""
                            i += 1
                        elif text[i] == '\n':
                            row.append(field)
                            field = ""
                            i += 1
                            rows.append(row)
                            row = []
                        elif text[i] == '\r':
                            row.append(field)
                            field = ""
                            if i + 1 < len(text) and text[i + 1] == '\n':
                                i += 2
                            else:
                                i += 1
                            rows.append(row)
                            row = []
                        else:
                            raise ValueError("Character after closing quote must be comma or newline")
            else:
                field += ch
                i += 1
        else:
            if ch == '"' and not field:
                in_quotes = True
                i += 1
            elif ch == ',':
                row.append(field)
                field = ""
                i += 1
            elif ch == '\n':
                row.append(field)
                field = ""
                i += 1
                rows.append(row)
                row = []
            elif ch == '\r':
                row.append(field)
                field = ""
                if i + 1 < len(text) and text[i + 1] == '\n':
                    i += 2
                else:
                    i += 1
                rows.append(row)
                row = []
            else:
                field += ch
                i += 1

    if in_quotes:
        raise ValueError("Unterminated quoted field")

    if not (text and text[-1] in '\r\n'):
        row.append(field)
        rows.append(row)

    return rows
