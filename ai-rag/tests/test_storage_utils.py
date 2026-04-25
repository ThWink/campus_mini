import shutil
import tempfile
import unittest
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from storage_utils import reset_directory_contents


class ResetDirectoryContentsTests(unittest.TestCase):
    def test_keeps_root_directory_and_clears_children(self):
        temp_root = Path(tempfile.mkdtemp())
        target = temp_root / "chroma_db"
        nested = target / "nested"
        nested.mkdir(parents=True)
        (nested / "data.txt").write_text("x", encoding="utf-8")
        (target / "root.txt").write_text("y", encoding="utf-8")

        reset_directory_contents(target)

        self.assertTrue(target.exists())
        self.assertTrue(target.is_dir())
        self.assertEqual(list(target.iterdir()), [])

        shutil.rmtree(temp_root)


if __name__ == "__main__":
    unittest.main()
