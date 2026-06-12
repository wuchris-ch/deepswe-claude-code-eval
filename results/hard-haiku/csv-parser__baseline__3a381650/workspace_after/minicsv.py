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
                # Check for doubled quote or end of quoted field
                if i + 1 < len(text) and text[i + 1] == '"':
                    # Doubled quote - add one quote to field
                    field += '"'
                    i += 1  # Skip next quote
                else:
                    # End of quoted field
                    in_quotes = False
                    # Check what comes next
                    if i + 1 < len(text):
                        next_ch = text[i + 1]
                        if next_ch not in (',', '\n', '\r'):
                            raise ValueError("Closing quote must be followed by comma or newline")
            else:
                # Regular character inside quoted field (including \n and \r)
                field += ch
        else:
            # Not in quoted mode
            if field == "" and ch == '"':
                # Start of quoted field (quotes only special at start)
                in_quotes = True
            elif ch == ',':
                # Field separator
                row.append(field)
                field = ""
            elif ch == '\n':
                # Row separator
                row.append(field)
                field = ""
                rows.append(row)
                row = []
            elif ch == '\r':
                # Row separator (could be \r or \r\n)
                row.append(field)
                field = ""
                rows.append(row)
                row = []
                # Skip \n if it follows \r
                if i + 1 < len(text) and text[i + 1] == '\n':
                    i += 1
            else:
                # Regular character
                field += ch

        i += 1

    # End of input
    if in_quotes:
        raise ValueError("Unterminated quoted field")

    # Add final row if there's any accumulated data
    if row or field:
        row.append(field)
        rows.append(row)

    return rows
