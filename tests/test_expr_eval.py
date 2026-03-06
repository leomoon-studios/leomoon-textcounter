"""Unit tests for `textcounter.core.expr_eval` (parser & sanitizer only).

The full `evaluate()` function requires `bpy` and is exercised manually in
Blender as part of Step 6's integration test.
"""

from __future__ import annotations

import importlib.util
import os
import sys
import types
import unittest

_MODULE_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "textcounter",
        "core",
        "expr_eval.py",
    )
)

# Stub `bpy` and `mathutils` so the module imports cleanly outside Blender.
# The parser/sanitizer functions don't touch them; only `evaluate()` does, and
# we don't call `evaluate()` here.
sys.modules.setdefault("bpy", types.ModuleType("bpy"))
sys.modules["bpy"].context = types.SimpleNamespace()
sys.modules["bpy"].data = types.SimpleNamespace()
_mathutils = types.ModuleType("mathutils")
for _name in ("Vector", "Matrix", "Euler", "Quaternion", "Color"):
    setattr(_mathutils, _name, type(_name, (), {}))
for _name in ("bvhtree", "geometry", "kdtree", "noise", "interpolate"):
    setattr(_mathutils, _name, types.ModuleType(_name))
sys.modules.setdefault("mathutils", _mathutils)

_spec = importlib.util.spec_from_file_location("expr_eval", _MODULE_PATH)
assert _spec and _spec.loader
_expr_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_expr_mod)
rewrite_deps = _expr_mod.rewrite_deps
sanitize = _expr_mod.sanitize
evaluate = _expr_mod.evaluate


class TestRewriteDeps(unittest.TestCase):
    """Cases ported verbatim from legacy `expr_deps.py` __main__."""

    def test_nested_brackets_with_string(self) -> None:
        self.assertEqual(
            rewrite_deps("scene.objects[foo.bar['Alice ] Bob'].bar[23]].location.x"),
            "scene.evaluated_get(dp).objects[foo.bar['Alice ] Bob'].bar[23]].evaluated_get(dp).location.x",
        )

    def test_simple_index(self) -> None:
        self.assertEqual(
            rewrite_deps("scene.objects['Cube'].location.x"),
            "scene.evaluated_get(dp).objects['Cube'].evaluated_get(dp).location.x",
        )

    def test_get_with_arithmetic(self) -> None:
        self.assertEqual(
            rewrite_deps("scene.objects.get('Cube 1').location.x + 3.156"),
            "scene.evaluated_get(dp).objects.get('Cube 1').evaluated_get(dp).location.x + 3.156",
        )

    def test_complex_index_expression(self) -> None:
        self.assertEqual(
            rewrite_deps(
                "scene.objects['Cube ' + str(int(int(1.real).real.real))].location.x + 3.15"
            ),
            "scene.evaluated_get(dp).objects['Cube ' + str(int(int(1.real).real.real))].evaluated_get(dp).location.x + 3.15",
        )

    def test_index_with_str_concat(self) -> None:
        self.assertEqual(
            rewrite_deps("scene.objects['Cube '+str(1)].location.x + 3.145"),
            "scene.evaluated_get(dp).objects['Cube '+str(1)].evaluated_get(dp).location.x + 3.145",
        )

    def test_int_index(self) -> None:
        self.assertEqual(
            rewrite_deps("scene.objects[0]"),
            "scene.evaluated_get(dp).objects[0].evaluated_get(dp)",
        )

    def test_get_with_str_concat(self) -> None:
        self.assertEqual(
            rewrite_deps("scene.objects.get('Cube ' + str(1))"),
            "scene.evaluated_get(dp).objects.get('Cube ' + str(1)).evaluated_get(dp)",
        )

    def test_simple_index_with_arith(self) -> None:
        self.assertEqual(
            rewrite_deps("scene.objects['Cube 1'].location.x + 3.9"),
            "scene.evaluated_get(dp).objects['Cube 1'].evaluated_get(dp).location.x + 3.9",
        )

    def test_material_slots(self) -> None:
        self.assertEqual(
            rewrite_deps(
                'C.scene.objects["Cube 1"].material_slots[0].material.refraction_depth'
            ),
            'C.scene.evaluated_get(dp).objects["Cube 1"].evaluated_get(dp).material_slots[0].material.evaluated_get(dp).refraction_depth',
        )


class TestSanitize(unittest.TestCase):
    def test_legacy_case(self) -> None:
        self.assertEqual(
            sanitize(
                "__D.objects.preferences.__class__['__Light__\"__'].bpy.ops.do_some().__"
            ),
            "D.objects._.class['__Light__\"__'].bpy._.do_some().",
        )

    def test_strings_unaffected(self) -> None:
        # 'load' inside a string literal must remain.
        self.assertEqual(
            sanitize("D.objects['my_load_target'].x"),
            "D.objects['my_load_target'].x",
        )

    def test_dunder_stripped(self) -> None:
        self.assertIn("class", sanitize("a.__class__"))
        self.assertNotIn("__", sanitize("a.__class__"))


class TestEvaluateSafety(unittest.TestCase):
    """Confirm the runtime sandbox refuses dangerous expressions.

    These use a fake scene/depsgraph; we only assert that evaluation returns
    `0.0` with a non-empty error message rather than executing the payload.
    """

    def _run(self, expr: str):
        return evaluate(expr, scene=None, depsgraph=None)

    def test_import_blocked(self) -> None:
        value, err = self._run("__import__('os').system('echo pwned')")
        self.assertEqual(value, 0.0)
        self.assertTrue(err)

    def test_open_blocked(self) -> None:
        value, err = self._run("open('/etc/passwd').read()")
        self.assertEqual(value, 0.0)
        self.assertTrue(err)

    def test_class_walk_blocked(self) -> None:
        value, err = self._run("(1).__class__.__base__.__subclasses__()")
        self.assertEqual(value, 0.0)
        self.assertTrue(err)

    def test_eval_blocked(self) -> None:
        value, err = self._run("eval('1+1')")
        self.assertEqual(value, 0.0)
        self.assertTrue(err)

    def test_simple_math_works(self) -> None:
        value, err = self._run("3 * 4 + sqrt(16)")
        self.assertEqual(err, "")
        self.assertEqual(value, 16.0)

    def test_empty_expression(self) -> None:
        self.assertEqual(self._run(""), (0.0, ""))


if __name__ == "__main__":
    unittest.main()
