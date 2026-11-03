import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "skills/japanese-editor/scripts/check.py"
spec = importlib.util.spec_from_file_location("ja_check", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class CheckTests(unittest.TestCase):
    def categories(self, old, new):
        return {item["category"] for item in module.analyze(old, new)}

    def test_same_is_clear(self):
        text = "# 要件\n\n`foo()` は3回まで実行可能。\n"
        self.assertEqual(module.analyze(text, text), [])

    def test_number_change(self):
        self.assertIn("number", self.categories("期限は100ms。", "期限は120ms。"))

    def test_repeated_number_change(self):
        self.assertIn("number", self.categories("1回、1回。", "1回。"))

    def test_inline_code_change(self):
        self.assertIn("inline_code", self.categories("`ERR_A` を返す", "`ERR_B` を返す"))

    def test_fence_change(self):
        before = "```c\nint x = 1;\n```\n"
        after = "```c\nint x = 2;\n```\n"
        self.assertIn("fenced_code", self.categories(before, after))

    def test_negation_change(self):
        self.assertIn("markers_否定", self.categories("実行してはならない", "実行する"))

    def test_obligation_change(self):
        self.assertIn("markers_義務", self.categories("変更すること。", "変更した。"))

    def test_heading_structure_change(self):
        self.assertIn("heading_structure", self.categories("# タイトル", "## タイトル"))

    def test_natural_reword_without_change(self):
        self.assertEqual(self.categories("設定を行います。", "設定します。"), set())

    def test_preserved_example(self):
        root = Path(__file__).resolve().parents[1]
        old = (root / "examples/original.md").read_text(encoding="utf-8")
        new = (root / "examples/revised.md").read_text(encoding="utf-8")
        self.assertEqual(self.categories(old, new), {"markers_条件"})


if __name__ == "__main__":
    unittest.main()
