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
        # --- read one field starting at index i ---
        chars = []
        if i < n and text[i] == '"':
            # Quoted field: quotes are only special at the field start.
            i += 1
            while True:
                if i >= n:
                    raise ValueError("unterminated quoted field")
                ch = text[i]
                if ch == '"':
                    if i + 1 < n and text[i + 1] == '"':
                        chars.append('"')  # doubled quote -> one literal quote
                        i += 2
                    else:
                        i += 1  # closing quote
                        break
                else:
                    chars.append(ch)
                    i += 1
            # A closing quote may only be followed by a separator or EOF.
            if i < n and text[i] not in (",", "\n", "\r"):
                raise ValueError("unexpected text after closing quote")
        else:
            # Unquoted field: taken verbatim until a separator.
            while i < n and text[i] not in (",", "\n", "\r"):
                chars.append(text[i])
                i += 1

        row.append("".join(chars))

        # --- handle the separator (or EOF) that follows the field ---
        if i >= n:
            rows.append(row)
            break

        ch = text[i]
        if ch == ",":
            i += 1
            continue  # another field in the same row

        # Row ending: consume "\r\n" or a bare "\n"/"\r".
        if ch == "\r" and i + 1 < n and text[i + 1] == "\n":
            i += 2
        else:
            i += 1
        rows.append(row)
        row = []
        if i >= n:
            break  # a single trailing newline does not start a new row

    return rows
