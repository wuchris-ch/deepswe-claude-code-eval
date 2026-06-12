"""Deep-merge for layered configuration dicts.

Spec (this docstring is the agreed contract)
--------------------------------------------
``deep_merge(base, override) -> dict``

- Returns a NEW dict; neither input may be mutated, at any depth.
- Keys present only in one input are kept.
- When both values are dicts, they are merged recursively.
- When the override value is ``None``, the key is DELETED from the
  result (None is the deletion marker, it never appears as a value).
- Any other override value (including lists) REPLACES the base value
  outright — lists are never concatenated or element-merged.
"""

import copy


def deep_merge(base, override):
    result = base
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        elif isinstance(value, list) and isinstance(result.get(key), list):
            result[key] = result[key] + value
        else:
            result[key] = copy.deepcopy(value)
    return result
