"""Environment-variable expansion for configuration values.

Spec (this docstring is the agreed contract)
--------------------------------------------
``expand(value, env) -> value``

- Strings: every ``${NAME}`` is replaced by ``env["NAME"]``;
  ``${NAME:default}`` uses the default when NAME is not in env. The
  default is everything after the FIRST colon, so it may itself
  contain colons (``${HOST:http://localhost:8080}``).
- A ``${NAME}`` reference with no default for a NAME missing from env
  raises ``KeyError``.
- ``$$`` is an escape producing one literal ``$`` and never starts a
  reference (``"$${X}"`` -> ``"${X}"``).
- Variable names consist of letters, digits and underscores.
- Dicts and lists are expanded recursively (keys are not expanded,
  values are). Non-string scalars pass through unchanged.
- The input is never mutated; containers are returned as new objects.
"""

import re

_PATTERN = re.compile(r"\$\$|\$\{([A-Za-z0-9_]+)(:([^}]*))?\}")


def expand(value, env):
    if isinstance(value, str):
        def repl(match):
            if match.group(0) == "$$":
                return "$"
            name = match.group(1)
            if name in env:
                return env[name]
            if match.group(2) is not None:
                return match.group(3)
            raise KeyError(name)
        return _PATTERN.sub(repl, value)
    if isinstance(value, dict):
        return {k: expand(v, env) for k, v in value.items()}
    if isinstance(value, list):
        return [expand(v, env) for v in value]
    return value
