"""Tests for soham_py.saver — saving practicals to local files."""

import pathlib
from unittest.mock import MagicMock, patch

import pytest

from soham_py.saver import save


class TestSaveBasic:
    """Basic file saving tests."""

    def test_save_creates_file(self, tmp_path):
        dest = tmp_path / "output.txt"
        result = save("ds", 1, str(dest))
        assert dest.exists()
        assert isinstance(result, pathlib.Path)
        assert result == dest.resolve()

    def test_save_writes_correct_content(self, tmp_path):
        dest = tmp_path / "output.txt"
        save("ds", 1, str(dest))
        assert dest.read_text(encoding="utf-8") == ""

    def test_save_uses_utf8(self, tmp_path):
        dest = tmp_path / "output.txt"
        save("wt", 1, str(dest))
        dest.read_text(encoding="utf-8")

    def test_save_preserves_content_across_all_subjects(self, tmp_path):
        dest_ds = tmp_path / "ds.txt"
        save("ds", 1, str(dest_ds))
        assert dest_ds.read_text(encoding="utf-8") == ""

        dest_wt = tmp_path / "wt.txt"
        save("wt", 1, str(dest_wt))
        assert dest_wt.read_text(encoding="utf-8") == ""

        dest_dbms = tmp_path / "dbms.txt"
        save("dbms", 1, str(dest_dbms))
        assert dest_dbms.read_text(encoding="utf-8") == "practical 1"

    def test_save_creates_parent_directories(self, tmp_path):
        dest = tmp_path / "subdir" / "nested" / "deep" / "output.txt"
        save("ds", 1, str(dest))
        assert dest.exists()

    def test_save_with_alias(self, tmp_path):
        dest = tmp_path / "output.txt"
        save("data_science", 1, str(dest))
        assert dest.exists()

    def test_save_accepts_pathlib_path(self, tmp_path):
        dest = tmp_path / "from_pathlib.txt"
        save("ds", 1, dest)
        assert dest.exists()

    def test_save_missing_practical_writes_notice(self, tmp_path):
        dest = tmp_path / "dbms15.txt"
        save("dbms", 15, str(dest))
        assert dest.read_text(encoding="utf-8") == "No practical file present for DBMS practical 15."

        dest_ds = tmp_path / "ds20.txt"
        save("ds", 20, str(dest_ds))
        assert dest_ds.read_text(encoding="utf-8") == "No practical file present for DS practical 20."


# ── Multiline and Unicode Content Tests ─────────────────────────────

class TestSaveUnicodeAndMultiline:
    """Verify that save handles multiline content and rich Unicode correctly."""

    def test_save_multiline_python_code(self, tmp_path):
        multiline_code = (
            "def calculate_mean(values):\n"
            "    '''Calculate the arithmetic mean.'''\n"
            "    total = sum(values)\n"
            "    return total / len(values)\n"
        )
        with patch("soham_py.saver.get_practical", return_value=multiline_code):
            dest = tmp_path / "mean.py"
            save("ds", 1, str(dest))
            assert dest.read_text(encoding="utf-8") == multiline_code

    def test_save_unicode_math_symbols(self, tmp_path):
        math_content = (
            "# Mathematical formulas\n"
            "alpha = α = 0.05\n"
            "beta = β = 0.90\n"
            "pi = π ≈ 3.14159\n"
            "sigma = ∑(x_i - μ)² / N\n"
            "inequality: x ≠ y ∧ a ≤ b\n"
        )
        with patch("soham_py.saver.get_practical", return_value=math_content):
            dest = tmp_path / "math.txt"
            save("ds", 2, str(dest))
            assert dest.read_text(encoding="utf-8") == math_content

    def test_save_unicode_emojis_and_scripts(self, tmp_path):
        rich_unicode = (
            "# Multilingual & Emoji Test 🐍 🚀 🌐 💾\n"
            "# Hindi: नमस्ते दुनिया\n"
            "# Japanese: こんにちは世界\n"
            "# Smart punctuation: “curly quotes”, ‘single quotes’, em—dash, en–dash\n"
            "# Checkmarks: ✓ Passed ✗ Failed\n"
        )
        with patch("soham_py.saver.get_practical", return_value=rich_unicode):
            dest = tmp_path / "unicode_test.txt"
            save("wt", 1, str(dest))
            saved_text = dest.read_text(encoding="utf-8")
            assert saved_text == rich_unicode
            assert "नमस्ते" in saved_text
            assert "🐍" in saved_text
            assert "✓" in saved_text

    def test_save_sql_multiline_with_unicode(self, tmp_path):
        sql_content = (
            "CREATE TABLE employees (\n"
            "    id INT PRIMARY KEY,\n"
            "    name NVARCHAR(100), -- Supports Unicode names like 'José García' or 'शर्मा'\n"
            "    salary DECIMAL(10, 2) -- In ₹ or €\n"
            ");\n"
        )
        with patch("soham_py.saver.get_practical", return_value=sql_content):
            dest = tmp_path / "schema.sql"
            save("dbms", 1, str(dest))
            assert dest.read_text(encoding="utf-8") == sql_content


# ── Error Handling Tests ────────────────────────────────────────────

class TestSaveErrors:
    """Error cases when saving practicals."""

    def test_save_invalid_subject_name_raises_value_error(self, tmp_path):
        dest = tmp_path / "out.txt"
        with pytest.raises(ValueError, match="Invalid subject"):
            save("invalid_subject", 1, str(dest))

    @pytest.mark.parametrize("invalid_subject", [None, 123, [], {}])
    def test_save_invalid_subject_type_raises_value_error(self, tmp_path, invalid_subject):
        dest = tmp_path / "out.txt"
        with pytest.raises(ValueError, match="Subject name must be a string"):
            save(invalid_subject, 1, str(dest))  # type: ignore[arg-type]

    @pytest.mark.parametrize("number", [0, -1, -99])
    def test_save_invalid_number_raises_value_error(self, tmp_path, number):
        dest = tmp_path / "out.txt"
        with pytest.raises(ValueError, match="positive integer"):
            save("ds", number, str(dest))

    @pytest.mark.parametrize("empty_path", ["", "   ", "\t\n"])
    def test_save_empty_output_path_raises_value_error(self, empty_path):
        with pytest.raises(ValueError, match="output_path cannot be empty"):
            save("ds", 1, empty_path)

    @pytest.mark.parametrize("invalid_path", [None, 123, 45.6, [], {}])
    def test_save_invalid_path_type_raises_type_error(self, invalid_path):
        with pytest.raises(TypeError, match="output_path must be a str or Path"):
            save("ds", 1, invalid_path)  # type: ignore[arg-type]

    def test_save_to_directory_raises_os_error(self, tmp_path):
        """Trying to save directly onto an existing directory raises OSError."""
        with pytest.raises(OSError, match="Could not write"):
            save("ds", 1, str(tmp_path))


# ── Code Is Never Executed During Save ───────────────────────────────

class TestSaveNoExecution:
    """Ensure that save only writes text and never executes code."""

    def test_save_code_with_malicious_side_effects(self, tmp_path):
        malicious = (
            "import os\n"
            "os.remove('should_not_be_called')\n"
            "raise RuntimeError('SHOULD NOT EXECUTE')\n"
        )
        with patch("soham_py.saver.get_practical", return_value=malicious):
            dest = tmp_path / "safe.py"
            save("ds", 1, str(dest))
            # If save executed the code, RuntimeError would be raised
            assert dest.read_text(encoding="utf-8") == malicious
