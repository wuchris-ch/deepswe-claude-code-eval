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
                # Check for doubled quote
                if i + 1 < len(text) and text[i + 1] == '"':
                    field += '"'
                    i += 2
                else:
                    # End of quoted field
                    in_quotes = False
                    i += 1
                    # Validate next character is comma, newline, or EOF
                    if i < len(text) and text[i] not in ',\n\r':
                        raise ValueError("Malformed CSV: characters after closing quote")
            else:
                # Regular character in quoted field (including newlines)
                field += ch
                i += 1
        else:
            if ch == '"':
                # Quote must be at start of field
                if field:
                    raise ValueError("Malformed CSV: quote not at start of field")
                in_quotes = True
                i += 1
            elif ch == ',':
                row.append(field)
                field = ""
                i += 1
            elif ch == '\n':
                row.append(field)
                field = ""
                rows.append(row)
                row = []
                i += 1
            elif ch == '\r':
                row.append(field)
                field = ""
                rows.append(row)
                row = []
                i += 1
                # Skip \n if it follows (CRLF case)
                if i < len(text) and text[i] == '\n':
                    i += 1
            else:
                field += ch
                i += 1

    # Check for unterminated quote
    if in_quotes:
        raise ValueError("Malformed CSV: unterminated quoted field")

    # Add final row if there's content (trailing newline case: don't add empty final row)
    if field or row:
        row.append(field)
        rows.append(row)

    return rows
