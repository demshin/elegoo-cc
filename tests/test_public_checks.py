"""Verify public CI never needs private archive files."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class PublicDocumentationChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / ".gitignore").write_text((ROOT / ".gitignore").read_text())
        self.readme = self.root / "README.md"
        self.readme.write_text("# FAQ\n\n[42](data/archive/messages.html#message42)\n")

    def check(self, *args):
        return subprocess.run(
            [sys.executable, str(ROOT / "scripts/check_docs.py"), *args],
            cwd=self.root, capture_output=True, text=True,
        )

    def test_public_mode_works_without_archive(self):
        result = self.check("--public")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("archive not read", result.stdout)
        self.assertFalse((self.root / "data").exists())

    def test_local_mode_still_requires_archive(self):
        result = self.check()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Missing link", result.stderr)

    def test_public_mode_rejects_non_archive_private_link(self):
        self.readme.write_text("# FAQ\n\n[Private](data/.local/beget-api.json)\n")
        result = self.check("--public")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Invalid archive pointer", result.stderr)


if __name__ == "__main__":
    unittest.main()
