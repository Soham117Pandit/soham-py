"""Tests for soham_py.core — practical retrieval, listing, and error handling."""

from unittest.mock import MagicMock, patch

import pytest

import soham_py
from soham_py.core import get_practical, list_practicals
from soham_py.subjects import resolve_subject

SUBJECTS = ["ds", "wt", "dbms"]


# ── Retrieval Tests using Isolated Fixtures ─────────────────────────

class TestGetPracticalIsolated:
    """Test get_practical in an isolated environment with known files."""

    def test_existing_populated_practical_returns_code(self, mock_practicals):
        code = "print('Hello, Data Science!')\n"
        (mock_practicals["ds"] / "practical1.txt").write_text(code, encoding="utf-8")
        assert get_practical("ds", 1) == code

    def test_existing_empty_practical_returns_empty_string(self, mock_practicals):
        (mock_practicals["wt"] / "practical2.txt").write_text("", encoding="utf-8")
        assert get_practical("wt", 2) == ""

    def test_missing_practical_returns_friendly_message(self, mock_practicals):
        # File does not exist
        msg = get_practical("dbms", 11)
        assert msg == "There is no file present for DBMS practical 11."

    def test_all_three_subjects_missing_file_message(self, mock_practicals):
        assert get_practical("ds", 99) == "There is no file present for DS practical 99."
        assert get_practical("wt", 50) == "There is no file present for WT practical 50."
        assert get_practical("dbms", 15) == "There is no file present for DBMS practical 15."

    def test_practical_number_greater_than_10_when_present(self, mock_practicals):
        sql = "CREATE TABLE users (id INT PRIMARY KEY);\n"
        (mock_practicals["dbms"] / "practical15.txt").write_text(sql, encoding="utf-8")
        assert get_practical("dbms", 15) == sql

    def test_practical_number_greater_than_10_when_missing(self, mock_practicals):
        assert get_practical("ds", 15) == "There is no file present for DS practical 15."
        assert get_practical("wt", 100) == "There is no file present for WT practical 100."
        assert get_practical("dbms", 42) == "There is no file present for DBMS practical 42."

    def test_additional_practical_files_supported(self, mock_practicals):
        xml_code = "<?xml version='1.0'?><root></root>"
        (mock_practicals["wt"] / "practical75.txt").write_text(xml_code, encoding="utf-8")
        assert get_practical("wt", 75) == xml_code


# ── Practical Number and Subject Validation ─────────────────────────

class TestPracticalValidation:
    """Validate subject names and practical number constraints."""

    def test_invalid_subject_name_raises_value_error(self):
        with pytest.raises(ValueError, match="Invalid subject"):
            get_practical("physics", 1)

    @pytest.mark.parametrize("invalid_subject", [123, None, 45.6, [], {}, True, False])
    def test_invalid_subject_type_raises_meaningful_value_error(self, invalid_subject):
        with pytest.raises(ValueError, match="Subject name must be a string"):
            get_practical(invalid_subject, 1)  # type: ignore[arg-type]

    @pytest.mark.parametrize("empty_subject", ["", "   ", "\t\n"])
    def test_empty_subject_raises_value_error(self, empty_subject):
        with pytest.raises(ValueError, match="Subject name cannot be empty"):
            get_practical(empty_subject, 1)

    # Zero and negative practical numbers must raise ValueError
    @pytest.mark.parametrize("number", [0, -1, -10, -100])
    def test_zero_and_negative_numbers_raise_value_error(self, number):
        with pytest.raises(ValueError, match="positive integer"):
            get_practical("ds", number)

    @pytest.mark.parametrize("invalid_num", ["one", 3.14, None, [], {}])
    def test_non_integer_number_raises_value_error(self, invalid_num):
        with pytest.raises(ValueError, match="must be an integer"):
            get_practical("ds", invalid_num)  # type: ignore[arg-type]

    def test_boolean_number_raises_value_error(self):
        with pytest.raises(ValueError, match="must be an integer"):
            get_practical("ds", True)  # type: ignore[arg-type]


# ── Dynamic List Practicals Tests ───────────────────────────────────

class TestListPracticalsIsolated:
    """Verify dynamic discovery and numerical sorting of practical files."""

    def test_dynamic_discovery_empty_dir(self, mock_practicals):
        assert list_practicals("ds") == []

    def test_dynamic_discovery_and_numerical_sorting(self, mock_practicals):
        # Create files out of order, including numbers > 10
        numbers = [100, 2, 1, 15, 10, 5, 25]
        for n in numbers:
            (mock_practicals["ds"] / f"practical{n}.txt").write_text(f"# p{n}", encoding="utf-8")

        result = list_practicals("ds")
        assert result == [1, 2, 5, 10, 15, 25, 100]

    def test_skips_non_matching_files(self, mock_practicals):
        (mock_practicals["wt"] / "practical1.txt").write_text("ok", encoding="utf-8")
        (mock_practicals["wt"] / "practical2.txt").write_text("ok", encoding="utf-8")
        (mock_practicals["wt"] / "__init__.py").write_text("", encoding="utf-8")
        (mock_practicals["wt"] / "notes.txt").write_text("notes", encoding="utf-8")
        (mock_practicals["wt"] / "practical_temp.txt").write_text("temp", encoding="utf-8")
        (mock_practicals["wt"] / "practicalabc.txt").write_text("abc", encoding="utf-8")

        result = list_practicals("wt")
        assert result == [1, 2]

    def test_skips_subdirectories(self, mock_practicals):
        (mock_practicals["dbms"] / "practical1.txt").write_text("sql", encoding="utf-8")
        sub_dir = mock_practicals["dbms"] / "practical2.txt"
        sub_dir.mkdir()  # directory with matching name

        result = list_practicals("dbms")
        assert result == [1]

    def test_invalid_subject_raises_value_error(self):
        with pytest.raises(ValueError, match="Invalid subject"):
            list_practicals("chemistry")

    def test_missing_package_dir_raises_file_not_found(self):
        with patch("soham_py.core.files", side_effect=ModuleNotFoundError("missing")):
            with pytest.raises(FileNotFoundError, match="Practical package not found"):
                list_practicals("ds")


# ── Error Handling & Resource Isolation ─────────────────────────────

class TestErrorHandling:
    """Missing resources return friendly notice without raising FileNotFoundError."""

    def test_missing_resource_package_returns_notice(self):
        with patch("soham_py.core.files", side_effect=ModuleNotFoundError("fake")):
            res = get_practical("ds", 1)
            assert res == "There is no file present for DS practical 1."

    def test_unrelated_exception_is_not_hidden(self):
        """PermissionError or UnicodeDecodeError must NOT be swallowed or disguised."""
        mock_resource = MagicMock()
        mock_resource.is_file.return_value = True
        mock_resource.read_text.side_effect = PermissionError("Permission denied")

        mock_pkg = MagicMock()
        mock_pkg.joinpath.return_value = mock_resource

        with patch("soham_py.core.files", return_value=mock_pkg):
            with pytest.raises(PermissionError, match="Permission denied"):
                get_practical("ds", 1)


# ── Subject Aliases ─────────────────────────────────────────────────

class TestAliases:
    """Subject alias resolution."""

    @pytest.mark.parametrize(
        "alias, expected_key",
        [
            ("ds", "ds"),
            ("data_science", "ds"),
            ("wt", "wt"),
            ("web", "wt"),
            ("web_technology", "wt"),
            ("dbms", "dbms"),
            ("database", "dbms"),
        ],
    )
    def test_aliases_resolve(self, alias, expected_key):
        assert resolve_subject(alias) == expected_key

    @pytest.mark.parametrize(
        "alias",
        [
            "DS", "Ds", "DATA_SCIENCE", "Data_Science",
            "WT", "Wt", "WEB", "Web", "WEB_TECHNOLOGY",
            "DBMS", "Dbms", "DATABASE", "Database",
        ],
    )
    def test_case_insensitive(self, alias):
        assert resolve_subject(alias) in ["ds", "wt", "dbms"]


# ── Code Is Never Executed ──────────────────────────────────────────

class TestNoExecution:
    """Stored code must NEVER be executed under any circumstances."""

    def test_executable_code_is_not_run(self, mock_practicals):
        dangerous_code = (
            "import sys\n"
            "raise RuntimeError('SHOULD NEVER RUN')\n"
            "sys.exit(1)\n"
        )
        (mock_practicals["ds"] / "practical1.txt").write_text(dangerous_code, encoding="utf-8")
        result = get_practical("ds", 1)
        assert result == dangerous_code
        assert "RuntimeError" in result

    def test_syntax_error_code_does_not_raise(self, mock_practicals):
        broken_code = "def def class for while return ;;;; {{}}"
        (mock_practicals["wt"] / "practical1.txt").write_text(broken_code, encoding="utf-8")
        result = get_practical("wt", 1)
        assert result == broken_code


# ── Real Practical Files (Read-Only Smoke Tests) ────────────────────

class TestRealFilesReadOnly:
    """Read-only smoke tests on real installed practical files without modifying them."""

    @pytest.mark.parametrize("subject", SUBJECTS)
    def test_list_practicals_returns_list_of_positive_ints(self, subject):
        nums = list_practicals(subject)
        assert isinstance(nums, list)
        for n in nums:
            assert isinstance(n, int)
            assert n >= 1

    @pytest.mark.parametrize("subject", SUBJECTS)
    def test_retrieving_existing_practical_returns_string(self, subject):
        nums = list_practicals(subject)
        if nums:
            # Test the first available practical
            content = get_practical(subject, nums[0])
            assert isinstance(content, str)

    def test_retrieving_non_existent_number_returns_notice(self):
        assert get_practical("ds", 99999) == "There is no file present for DS practical 99999."
        assert get_practical("wt", 99999) == "There is no file present for WT practical 99999."
        assert get_practical("dbms", 99999) == "There is no file present for DBMS practical 99999."
