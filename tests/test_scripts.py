"""Tests for the helper scripts. Run: python -m unittest discover -s tests -v"""
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent / "skills" / "complete-developers"
SCRIPTS = SKILL / "scripts"
sys.path.insert(0, str(SCRIPTS))

import _color  # noqa: E402
import changelog  # noqa: E402
import charter  # noqa: E402
import logtrim  # noqa: E402
import repomap  # noqa: E402
import tokencount  # noqa: E402


def run(script, *args, stdin=None):
    return subprocess.run([sys.executable, str(SCRIPTS / script), *args], input=stdin,
                          capture_output=True, text=True)


class ColorTests(unittest.TestCase):
    def test_black_white_is_21(self):
        self.assertAlmostEqual(_color.contrast("#000", "#FFF"), 21.0, places=2)

    def test_same_colour_is_1(self):
        self.assertAlmostEqual(_color.contrast("#336699", "#336699"), 1.0, places=3)

    def test_symmetry(self):
        self.assertAlmostEqual(_color.contrast("#123456", "#fedcba"), _color.contrast("#fedcba", "#123456"))

    def test_oklch_roundtrip(self):
        for hx in ("#B4532A", "#3B5BDB", "#00C896", "#777777"):
            L, C, H = _color.hex_to_oklch(hx)
            back = _color.oklch_to_hex(L, C, H)
            diff = max(abs(a - b) for a, b in zip(_color.parse_hex(hx), _color.parse_hex(back)))
            self.assertLessEqual(diff, 2, hx)

    def test_rejects_bad_hex(self):
        with self.assertRaises(ValueError):
            _color.parse_hex("rgb(1,2,3)")

    def test_cli_exit_code(self):
        self.assertEqual(run("contrast.py", "#000", "#fff").returncode, 0)
        self.assertEqual(run("contrast.py", "#999", "#fff").returncode, 1)
        self.assertEqual(run("contrast.py", "#999").returncode, 2)


class CharterTests(unittest.TestCase):
    def test_every_archetype_meets_contrast(self):
        for aid, a in charter.ARCHETYPES.items():
            for rtl in (False, True):
                dials = charter.parse_dials(None, a["dials"])
                t = charter.build_tokens(aid, None, dials, rtl)
                for theme in ("light", "dark"):
                    for name, pair in t["contrast"][theme].items():
                        need = 3.0 if "graphic" in name else 4.5
                        self.assertGreaterEqual(pair["ratio"], need, f"{aid} {theme} {name} rtl={rtl}")

    def test_dial_validation(self):
        with self.assertRaises(SystemExit):
            charter.parse_dials("boldness=9", (3, 3, 3, 3))
        with self.assertRaises(SystemExit):
            charter.parse_dials("sparkle=3", (3, 3, 3, 3))

    def test_seed_override_changes_primary(self):
        d = charter.parse_dials(None, charter.ARCHETYPES["saas-tool"]["dials"])
        a = charter.build_tokens("saas-tool", None, d, False)["light"]["primary"]
        b = charter.build_tokens("saas-tool", "#C2185B", d, False)["light"]["primary"]
        self.assertNotEqual(a, b)

    def test_rtl_uses_arabic_first_and_generous_leading(self):
        d = charter.parse_dials(None, charter.ARCHETYPES["food-hospitality"]["dials"])
        t = charter.build_tokens("food-hospitality", None, d, True)
        self.assertTrue(t["type"]["fonts"]["body"].startswith('"Tajawal"'))
        self.assertGreaterEqual(t["type"]["line_height"]["body"], 1.7)

    def test_single_generic_family_at_end(self):
        d = charter.parse_dials(None, charter.ARCHETYPES["editorial-news"]["dials"])
        body = charter.build_tokens("editorial-news", None, d, False)["type"]["fonts"]["display"]
        self.assertEqual(body.count("serif"), 1)
        self.assertTrue(body.endswith("serif"))

    def test_cli_formats(self):
        for fmt in ("md", "json", "css"):
            r = run("charter.py", "--archetype", "fintech-trust", "--format", fmt)
            self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("--primary", run("charter.py", "--archetype", "fintech-trust", "--format", "css").stdout)
        json.loads(run("charter.py", "--archetype", "fintech-trust", "--format", "json").stdout)
        self.assertNotEqual(run("charter.py", "--archetype", "nope").returncode, 0)

    def test_fonts_url_safe_weights(self):
        url = charter.fonts_url(["Tajawal", "Lalezar", "DM Sans"])
        self.assertIn("Tajawal:wght@400;500;700", url)
        self.assertIn("DM+Sans:wght@400;500;600;700", url)


class LogTrimTests(unittest.TestCase):
    def test_keeps_error_and_reports_drop(self):
        lines = [str(i) for i in range(300)]
        lines[100] = "ERROR: boom"
        out, dropped = logtrim.trim(lines, max_lines=40)
        self.assertIn("ERROR: boom", out)
        self.assertGreater(dropped, 200)
        self.assertLess(len(out), 60)

    def test_folds_repeats(self):
        out = logtrim.fold(["a", "a", "a", "b"])
        self.assertEqual(out, ["a  (x3)", "b"])


class TokenCountTests(unittest.TestCase):
    def test_arabic_costs_more_per_char(self):
        self.assertGreater(tokencount.estimate("م" * 100), tokencount.estimate("a" * 100))

    def test_cli_budget_flag(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d, "a.txt").write_text("hello world " * 500, encoding="utf-8")
            self.assertEqual(run("tokencount.py", d, "--budget", "10").returncode, 1)
            self.assertEqual(run("tokencount.py", d, "--budget", "100000").returncode, 0)


class RepoMapTests(unittest.TestCase):
    def test_symbols_and_secret_withholding(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "node_modules").mkdir()
            (root / "node_modules" / "junk.js").write_text("function junk(){}", encoding="utf-8")
            (root / "app.py").write_text("class A:\n    def go(self): pass\n\ndef main(): pass\n", encoding="utf-8")
            (root / "shop.lua").write_text("local function validate() end\nfunction Shop.buy() end\n", encoding="utf-8")
            (root / ".env").write_text("SECRET=1", encoding="utf-8")
            (root / "web.js").write_text("export const f = (a) => a;\nexport function g() {}\n", encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                self.assertEqual(repomap.main([d]), 0)
            out = buf.getvalue()
            self.assertIn("class A(go)", out)
            self.assertIn("def main", out)
            self.assertIn("validate", out)
            self.assertIn("Shop.buy", out)
            self.assertIn("f, g", out)
            self.assertNotIn("junk", out)
            self.assertNotIn("SECRET", out)
            self.assertIn("1 secret-like file(s) withheld", out)

    def test_missing_dir(self):
        self.assertEqual(run("repomap.py", "/definitely/not/here").returncode, 2)


class ChangelogTests(unittest.TestCase):
    def test_grouping_and_breaking(self):
        log = ("a" * 40 + "\x1ffeat(ui): add hero\n\x1e" + "b" * 40 + "\x1ffix: align\n\x1e"
               + "c" * 40 + "\x1ffeat(api)!: new shape\n\x1e" + "d" * 40 + "\x1fchore: deps\n\x1e"
               + "e" * 40 + "\x1fwhatever\n\x1e")
        md = changelog.build(changelog.parse(log), "1.0.0")
        self.assertIn("### Breaking changes", md)
        self.assertIn("### Features", md)
        self.assertIn("### Fixes", md)
        self.assertIn("### Other", md)
        self.assertNotIn("deps", md)


class InstallTests(unittest.TestCase):
    def test_install_backup_uninstall(self):
        with tempfile.TemporaryDirectory() as d:
            for _ in range(2):
                r = run("install.py", "--dest", d)
                self.assertEqual(r.returncode, 0, r.stderr)
            target = Path(d) / "complete-developers"
            self.assertTrue((target / "SKILL.md").is_file())
            self.assertFalse((target / "tests").exists())
            self.assertEqual(len([p for p in Path(d).iterdir() if ".bak-" in p.name]), 1)
            run("install.py", "--dest", d, "--uninstall")
            self.assertFalse(target.exists())

    def test_dry_run_changes_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            run("install.py", "--dest", d, "--dry-run")
            self.assertEqual(list(Path(d).iterdir()), [])


class SelfcheckTests(unittest.TestCase):
    def test_skill_is_valid(self):
        r = run("selfcheck.py")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
