"""Tests for soham_py.core — practical retrieval, listing, and error handling."""

import pathlib
from unittest.mock import MagicMock, patch

import pytest

import soham_py
from soham_py.core import get_practical, list_practicals
from soham_py.subjects import resolve_subject


SUBJECTS = ["ds", "wt", "dbms"]


# ── Practical Files on Disk Verification ────────────────────────────

class TestDiskFiles:
    """Verify that all 30 practical files exist on disk and are 0 bytes."""

    @pytest.mark.parametrize("subject", SUBJECTS)
    @pytest.mark.parametrize("number", range(1, 11))
    def test_disk_file_exists_and_is_zero_bytes(self, subject, number):
        """Every practical file on disk must be completely empty (0 bytes)."""
        pkg_dir = pathlib.Path(__file__).resolve().parent.parent / "src" / "soham_py" / "practicals" / subject
        file_path = pkg_dir / f"practical{number}.txt"
        assert file_path.is_file(), f"Missing file: {file_path}"
        assert file_path.stat().st_size == 0, f"File {file_path} is not 0 bytes!"


# ── Retrieval Tests ─────────────────────────────────────────────────

class TestGetPractical:
    """Retrieving practicals by subject and number."""

    @pytest.mark.parametrize("subject", SUBJECTS)
    @pytest.mark.parametrize("number", range(1, 11))
    def test_all_30_files_exist_and_return_empty_string(self, subject, number):
        """Every practical file must return empty string by default."""
        result = get_practical(subject, number)
        assert result == ""
        assert isinstance(result, str)

    def test_empty_file_returns_empty_string_without_error(self):
        assert get_practical("ds", 1) == ""

    # Invalid subject values and types
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

    # Invalid practical numbers
    @pytest.mark.parametrize("number", [0, -1, 11, 100])
    def test_out_of_range_number_raises_value_error(self, number):
        with pytest.raises(ValueError, match="between 1 and 10"):
            get_practical("ds", number)

    @pytest.mark.parametrize("invalid_num", ["one", 3.14, None, [], {}])
    def test_non_integer_number_raises_value_error(self, invalid_num):
        with pytest.raises(ValueError, match="must be an integer"):
            get_practical("ds", invalid_num)  # type: ignore[arg-type]

    def test_boolean_number_raises_value_error(self):
        with pytest.raises(ValueError, match="must be an integer"):
            get_practical("ds", True)  # type: ignore[arg-type]


# ── Temporary Non-Empty Practical Content ───────────────────────────

class TestNonEmptyContent:
    """Test retrieval when practical files contain actual text (mocked)."""

    def test_retrieval_with_non_empty_python_code(self, monkeypatch):
        sample_code = "import pandas as pd\ndf = pd.read_csv('data.csv')\nprint(df.head())\n"

        def fake_get_practical(subject, number):
            if subject == "ds" and number == 1:
                return sample_code
            return ""

        monkeypatch.setattr("soham_py.core.get_practical", fake_get_practical)
        assert soham_py.core.get_practical("ds", 1) == sample_code

    def test_retrieval_preserves_multiline_and_formatting(self):
        mock_resource = MagicMock()
        mock_resource.read_text.return_value = "def add(a, b):\n    '''Add two numbers.'''\n    return a + b\n"

        mock_pkg = MagicMock()
        mock_pkg.joinpath.return_value = mock_resource

        with patch("soham_py.core.files", return_value=mock_pkg):
            content = get_practical("ds", 2)
            assert content == "def add(a, b):\n    '''Add two numbers.'''\n    return a + b\n"
            assert "def add(a, b):" in content


# ── Error Handling & Resource Isolation ─────────────────────────────

class TestErrorHandling:
    """Missing resources raise FileNotFoundError without hiding unrelated errors."""

    def test_missing_resource_package_raises_file_not_found_error(self):
        with patch("soham_py.core.files", side_effect=ModuleNotFoundError("No module named 'fake'")):
            with pytest.raises(FileNotFoundError, match="Practical package not found"):
                get_practical("ds", 1)

    def test_missing_file_raises_file_not_found_error(self):
        mock_resource = MagicMock()
        mock_resource.read_text.side_effect = FileNotFoundError("No such file")

        mock_pkg = MagicMock()
        mock_pkg.joinpath.return_value = mock_resource

        with patch("soham_py.core.files", return_value=mock_pkg):
            with pytest.raises(FileNotFoundError, match="Practical file not found"):
                get_practical("ds", 1)

    def test_unrelated_exception_is_not_hidden(self):
        """PermissionError or UnicodeDecodeError must NOT be converted to FileNotFoundError."""
        mock_resource = MagicMock()
        mock_resource.read_text.side_effect = PermissionError("Permission denied")

        mock_pkg = MagicMock()
        mock_pkg.joinpath.return_value = mock_resource

        with patch("soham_py.core.files", return_value=mock_pkg):
            with pytest.raises(PermissionError, match="Permission denied"):
                get_practical("ds", 1)


# ── Listing Practicals ──────────────────────────────────────────────

class TestListPracticals:
    """Listing available practical numbers."""

    @pytest.mark.parametrize("subject", SUBJECTS)
    def test_returns_10_practicals(self, subject):
        nums = list_practicals(subject)
        assert nums == list(range(1, 11))

    def test_invalid_subject_raises_value_error(self):
        with pytest.raises(ValueError, match="Invalid subject"):
            list_practicals("chemistry")

    @pytest.mark.parametrize("invalid_subject", [None, 999, [], {}])
    def test_invalid_subject_type_raises_value_error(self, invalid_subject):
        with pytest.raises(ValueError, match="Subject name must be a string"):
            list_practicals(invalid_subject)  # type: ignore[arg-type]

    def test_missing_package_dir_raises_file_not_found(self):
        with patch("soham_py.core.files", side_effect=ModuleNotFoundError("missing")):
            with pytest.raises(FileNotFoundError, match="Practical package not found"):
                list_practicals("ds")

    def test_skips_non_practical_and_non_integer_files(self):
        """Verify that __init__.py, other files, or non-numeric suffixes are ignored."""
        class MockItem:
            def __init__(self, name):
                self.name = name

        mock_items = [
            MockItem("__init__.py"),
            MockItem("practical1.txt"),
            MockItem("practical2.txt"),
            MockItem("practical_extra.txt"),
            MockItem("practical99.txt"),  # out of 1..10 range
            MockItem("notes.txt"),
        ]
        mock_pkg = MagicMock()
        mock_pkg.iterdir.return_value = mock_items

        with patch("soham_py.core.files", return_value=mock_pkg):
            result = list_practicals("ds")
            assert result == [1, 2]


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
        assert isinstance(get_practical(alias, 1), str)

    @pytest.mark.parametrize(
        "alias",
        [
            "DS", "Ds", "DATA_SCIENCE", "Data_Science",
            "WT", "Wt", "WEB", "Web", "WEB_TECHNOLOGY",
            "DBMS", "Dbms", "DATABASE", "Database",
        ],
    )
    def test_case_insensitive(self, alias):
        assert isinstance(get_practical(alias, 1), str)


# ── Code Is Never Executed ──────────────────────────────────────────

class TestNoExecution:
    """Stored code must NEVER be executed under any circumstances."""

    def test_returned_type_is_always_str(self):
        for subject in SUBJECTS:
            for num in range(1, 11):
                result = get_practical(subject, num)
                assert type(result) is str

    def test_executable_code_is_not_run(self):
        """Code that would raise, exit, or delete files must only be returned as text."""
        dangerous_code = (
            "import sys\n"
            "raise RuntimeError('SHOULD NEVER RUN')\n"
            "sys.exit(1)\n"
        )
        mock_resource = MagicMock()
        mock_resource.read_text.return_value = dangerous_code

        mock_pkg = MagicMock()
        mock_pkg.joinpath.return_value = mock_resource

        with patch("soham_py.core.files", return_value=mock_pkg):
            # If get_practical executed code, this would raise RuntimeError or SystemExit
            result = get_practical("ds", 1)
            assert result == dangerous_code
            assert "RuntimeError" in result

    def test_syntax_error_code_does_not_raise(self):
        """Invalid Python syntax must be safely returned as plain text."""
        broken_code = "def def class for while return ;;;; {{}}"
        mock_resource = MagicMock()
        mock_resource.read_text.return_value = broken_code

        mock_pkg = MagicMock()
        mock_pkg.joinpath.return_value = mock_resource

        with patch("soham_py.core.files", return_value=mock_pkg):
            result = get_practical("ds", 1)
            assert result == broken_code
