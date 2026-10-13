import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("package_mod", ROOT / "tools/package_mod.py")
package_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(package_mod)


class PortablePackageTests(unittest.TestCase):
    def fixture(self, root):
        (root / "descriptor.mod").write_text('version="1.0.0"\nname="TFR Estonia"\nsupported_version="1.19.*"\ndependencies={ "The Fire Rises" }\npath="C:/Users/Example/mod/tfr-estonia"\nremote_file_id="123"\n', encoding="utf-8")
        (root / "README.md").write_text("Development build", encoding="utf-8")
        (root / "thumbnail.png").write_bytes(b"test thumbnail")
        for folder in ("common", "docs", "tests", "tools", ".git", ".cache", "dist", "test-output", "tools/__pycache__"):
            (root / folder).mkdir(parents=True, exist_ok=True)
            (root / folder / "fixture.txt").write_text(folder, encoding="utf-8")

    def test_package_is_portable_excludes_generated_files_and_is_reproducible(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root)
            entries, version = package_mod.package_entries(root)
            self.assertEqual(version, "1.0.0")
            for name in entries:
                self.assertFalse(any(part in package_mod.EXCLUDED_DIRS for part in Path(name).parts), name)
            first, second = root / "first.zip", root / "second.zip"
            package_mod.write_zip(first, entries)
            package_mod.write_zip(second, entries)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            package_mod.verify_zip(first, entries)
            with zipfile.ZipFile(first) as archive:
                launcher = archive.read("tfr-estonia.mod").decode("utf-8")
                self.assertIn('path="mod/tfr-estonia"', launcher)
                self.assertIn('name="TFR Estonia (Development)"', launcher)
                self.assertNotIn("C:/", launcher)
                self.assertNotIn("remote_file_id", launcher)
                self.assertIn("tfr-estonia/tools/fixture.txt", archive.namelist())
                self.assertIn("tfr-estonia/tests/fixture.txt", archive.namelist())

    def test_unexpected_metadata_paths_are_rejected(self):
        descriptor = 'version="1.0.0"\nname="TFR Estonia"\nsupported_version="1.19.*"\ndependencies={ "The Fire Rises" }\ncustom="C:/Users/Example"\n'
        with self.assertRaisesRegex(ValueError, "absolute path"):
            package_mod.portable_descriptors(descriptor)


if __name__ == "__main__":
    unittest.main()
