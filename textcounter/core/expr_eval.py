"""Safe Python expression evaluator for the TextCounter Dynamic mode.

Two responsibilities:

1. **Dependency rewriting** (`rewrite_deps`): walk the user's expression and
   inject ``.evaluated_get(dp)`` after every reference that resolves to a
   Blender ID (object, scene, material, mesh data, parent, ...) so the
   evaluation reads from the depsgraph instead of the original data.

2. **Safe evaluation** (`evaluate`): execute the rewritten expression with an
   explicit allow-listed namespace, ``__builtins__`` set to ``None``, and a
   pre-pass sanitizer that strips dunder access and dangerous attribute
   names. Returns ``0.0`` and records the error string if anything goes
   wrong.

This module imports ``bpy``/``mathutils`` lazily inside `evaluate` so it can
be unit-tested for the parser/sanitizer pieces without Blender installed.
"""

from __future__ import annotations

import math
import re
from typing import Any

# --------------------------------------------------------------------------
# Dependency rewriting
# --------------------------------------------------------------------------

_INCLUSION = ".evaluated_get(dp)"

_REGEX_PARTS: tuple[str, ...] = (
    r"\.active_object\W",
    r"\.object\W",
    r"\.objects[\[\(]",
    r"\.objects\.get\W",
    r"scene\W",
    r"\.scenes[\[\(]",
    r"\.scenes\.get\W",
    r"\.material\W",
    r"\.materials[\[\(]",
    r"\.materials\.get\W",
    r"\.data\.\w+?\W",
    r"\.data\.\w+?\.get\W",
    r"\.data\W",
    r"\.data\.get\W",
    r"\.parent\W",
)
_REGEX = re.compile("|".join(_REGEX_PARTS))


def rewrite_deps(expression: str) -> str:
    """Inject ``.evaluated_get(dp)`` after every ID-typed reference.

    Faithful port of the original ``eval_parser`` from the legacy add-on.
    """
    offset = 0
    read_till = None
    read_till_string = None
    parenthesis_count = 0
    while True:
        m = _REGEX.search(expression, offset)
        if m is None:
            break
        i = m.end() - 1

        # If the match ends on a "." (e.g. `scene.`), inject right before it.
        if expression[i] == ".":
            expression = expression[:i] + _INCLUSION + expression[i:]
            offset = m.end() + len(_INCLUSION) - 1
            continue

        # Otherwise the match ends at "[" or "(" - we have to scan forward
        # to the matching close bracket, ignoring strings, then inject after.
        caret = i - 1
        last_i = 0
        for last_i, c in enumerate(expression[caret:]):  # noqa: B007 — used after loop
            if read_till_string is not None:
                if c == read_till_string:
                    read_till_string = None
                continue
            elif read_till is not None:
                if c == read_till and parenthesis_count == 1:
                    read_till = None
                    parenthesis_count = 0
                    break

            if c in {"'", '"'}:
                read_till_string = c
            elif c == "[":
                if not read_till:
                    read_till = "]"
                if read_till == "]":
                    parenthesis_count += 1
            elif c == "]":
                if read_till == "]":
                    parenthesis_count -= 1
            elif c == "(":
                if not read_till:
                    read_till = ")"
                if read_till == ")":
                    parenthesis_count += 1
            elif c == ")" and read_till == ")":
                parenthesis_count -= 1

        i = caret + last_i
        expression = expression[: i + 1] + _INCLUSION + expression[i + 1 :]
        offset = i + 1 + len(_INCLUSION)
    return expression


# --------------------------------------------------------------------------
# Sanitizer (defense in depth — the real safety comes from the namespace)
# --------------------------------------------------------------------------

_BANNED_TOKENS = (
    "__",            # dunder access
    "ops",           # bpy.ops -> bpy._
    "preferences",
    "utils",
    "new",
    "load",
)


def _sanitize_chunk(s: str) -> str:
    out = s.replace("__", "")
    out = out.replace("ops", "_")
    out = out.replace("preferences", "_")
    out = out.replace("utils", "_")
    out = out.replace("new", "_")
    out = out.replace("load", "_")
    return out


def sanitize(expression: str) -> str:
    """Strip dangerous tokens **outside** of string literals.

    String contents are passed through unchanged so legitimate dictionary
    keys / object names containing 'load', 'new', etc. still work.
    """
    quote_re = re.compile(r"['\"]")

    indexes = []
    qtype = None
    for m in quote_re.finditer(expression):
        if qtype is None:
            qtype = m.group()
            indexes.append(m.start())
        elif qtype == m.group():
            qtype = None
            indexes.append(m.start())

    start_idx = 0
    out = ""
    in_string = False
    while indexes:
        i = indexes.pop(0)
        chunk = expression[start_idx:i]
        out += chunk if in_string else _sanitize_chunk(chunk)
        start_idx = i
        in_string = not in_string
    tail = expression[start_idx:]
    out += tail if in_string else _sanitize_chunk(tail)
    return out


# --------------------------------------------------------------------------
# Evaluation
# --------------------------------------------------------------------------


def _safe_namespace(scene: Any, depsgraph: Any) -> dict:
    """Build the allow-listed namespace handed to `eval`."""
    import bpy  # local import: not needed for parser/sanitizer tests
    from mathutils import (
        Color,
        Euler,
        Matrix,
        Quaternion,
        Vector,
        bvhtree,
        geometry,
        interpolate,  # type: ignore[attr-defined]
        kdtree,
        noise,
    )

    ns: dict = {
        # context / data shortcuts
        "bpy": bpy,
        "C": bpy.context,
        "context": bpy.context,
        "D": bpy.data,
        "S": scene,
        "scene": scene,
        "dp": depsgraph,
        # mathutils
        "Vector": Vector,
        "Matrix": Matrix,
        "Euler": Euler,
        "Quaternion": Quaternion,
        "Color": Color,
        "geometry": geometry,
        "interpolate": interpolate,
        "noise": noise,
        "bvhtree": bvhtree,
        "kdtree": kdtree,
        # constants & math
        "pi": math.pi,
        "e": math.e,
        "tau": math.tau,
        "inf": math.inf,
        "nan": math.nan,
        # safe builtins
        "abs": abs, "all": all, "any": any, "bool": bool, "complex": complex,
        "dict": dict, "divmod": divmod, "enumerate": enumerate, "filter": filter,
        "float": float, "format": format, "frozenset": frozenset, "int": int,
        "len": len, "list": list, "map": map, "max": max, "min": min,
        "oct": oct, "ord": ord, "pow": pow, "range": range, "repr": repr,
        "reversed": reversed, "round": round, "set": set, "slice": slice,
        "sorted": sorted, "str": str, "sum": sum, "tuple": tuple, "zip": zip,
        "True": True, "False": False, "None": None,
    }
    # math.* functions
    for name in (
        "acos", "acosh", "asin", "asinh", "atan", "atan2", "atanh",
        "ceil", "copysign", "cos", "cosh", "degrees", "dist", "erf", "erfc",
        "exp", "expm1", "fabs", "factorial", "floor", "fmod", "frexp", "fsum",
        "gamma", "gcd", "hypot", "isclose", "isfinite", "isinf", "isnan",
        "isqrt", "lcm", "ldexp", "lgamma", "log", "log1p", "log10", "log2",
        "modf", "radians", "remainder", "sin", "sinh", "sqrt", "tan", "tanh",
        "trunc", "prod", "perm", "comb", "nextafter", "ulp",
    ):
        fn = getattr(math, name, None)
        if fn is not None:
            ns[name] = fn
    return ns


def evaluate(
    expression: str,
    *,
    scene: Any,
    depsgraph: Any,
) -> tuple[float, str]:
    """Evaluate `expression` and return ``(value, error_message)``.

    On success ``error_message`` is an empty string.
    On failure the value is ``0.0`` and ``error_message`` describes the
    problem.
    """
    if not expression.strip():
        return 0.0, ""

    try:
        rewritten = sanitize(rewrite_deps(expression))
    except Exception as exc:  # rewriting/sanitizing should never fail, be defensive
        return 0.0, f"Parse error: {exc}"

    try:
        ns = _safe_namespace(scene, depsgraph)
    except Exception as exc:
        return 0.0, f"Namespace error: {exc}"

    try:
        result = eval(rewritten, {"__builtins__": None}, ns)  # noqa: S307
    except Exception as exc:
        return 0.0, f"{type(exc).__name__}: {exc}"

    try:
        return float(result), ""
    except (TypeError, ValueError) as exc:
        return 0.0, f"Result not numeric: {exc}"
