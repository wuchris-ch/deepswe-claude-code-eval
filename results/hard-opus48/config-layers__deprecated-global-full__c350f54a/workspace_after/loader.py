"""Layered configuration loading.

Spec (this docstring is the agreed contract)
--------------------------------------------
``load_layers(layers, env) -> dict``

- ``layers`` is a list of config dicts ordered lowest precedence first;
  LATER layers override earlier ones.
- All layers are deep-merged (merge.deep_merge semantics, including the
  None-deletes-key marker), and only THEN is the merged result expanded
  (expand.expand semantics) — so a later layer can override a value
  that contains a ``${VAR}`` reference before any expansion happens.
- ``load_layers([], env)`` returns ``{}``.
- No input layer may be mutated.
"""

from expand import expand
from merge import deep_merge


def load_layers(layers, env):
    merged = {}
    for layer in layers:
        merged = deep_merge(merged, layer)
    return expand(merged, env)
