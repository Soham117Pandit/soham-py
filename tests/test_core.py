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
    """Verify that all 30 practical files exist on disk."""

    @pytest.mark.parametrize("subject", SUBJECTS)
    @pytest.mark.parametrize("number", range(1, 11))
    def test_disk_file_exists(self, subject, number):
        """Every practical file on disk must exist."""
        pkg_dir = pathlib.Path(__file__).resolve().parent.parent / "src" / "soham_py" / "practicals" / subject
        file_path = pkg_dir / f"practical{number}.txt"
        assert file_path.is_file(), f"Missing file: {file_path}"


# ── Retrieval Tests ─────────────────────────────────────────────────

class TestGetPractical:
    """Retrieving practicals by subject and number."""

    @pytest.mark.parametrize("subject", SUBJECTS)
    @pytest.mark.parametrize("number", range(1, 11))
    def test_all_30_files_exist_and_return_string(self, subject, number):
        """Every practical file must return a string."""
        result = get_practical(subject, number)
        assert isinstance(result, str)

    def test_existing_empty_practical_returns_empty_string(self):
        """Existing empty practical files must return empty string."""
        assert get_practical("ds", 1) == ""
        assert get_practical("wt", 1) == ""
        assert get_practical("dbms", 3) == ""

    def test_existing_populated_practical_returns_code(self):
        """Existing populated practical files must return their actual contents."""
        assert get_practical("dbms", 1) == "practical 1"
        assert get_practical("dbms", 2) == "practical 2"

    # Missing practical numbers return friendly plain-text message
    @pytest.mark.parametrize("number", [11, 12, 15, 20, 99, 100])
    def test_missing_practical_returns_plain_text_message_ds(self, number):
        msg = get_practical("ds", number)
        assert msg == f"There is no file present for DS practical {number}."

    @pytest.mark.parametrize("number", [11, 12, 15, 20, 99, 100])
    def test_missing_practical_returns_plain_text_message_wt(self, number):
        msg = get_practical("wt", number)
        assert msg == f"There is no file present for WT practical {number}."

    @pytest.mark.parametrize("number", [11, 12, 15, 20, 99, 100])
    def test_missing_practical_returns_plain_text_message_dbms(self, number):
        msg = get_practical("dbms", number)
        assert msg == f"There is no file present for DBMS practical {number}."

    # Practical number greater than 10
    def test_practical_number_greater_than_10_missing(self):
        assert get_practical("dbms", 11) == "There is no file present for DBMS practical 11."
        assert get_practical("ds", 15) == "There is no file present for DS practical 15."
        assert get_practical("wt", 25) == "There is no file present for WT practical 25."

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

    # Zero and negative practical numbers
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
        mock_resource.is_file.return_value = True
        mock_resource.read_text.return_value = "def add(a, b):\n    '''Add two numbers.'''\n    return a + b\n"

        mock_pkg = MagicMock()
        mock_pkg.joinpath.return_value = mock_resource

        with patch("soham_py.core.files", return_value=mock_pkg):
            content = get_practical("ds", 2)
            assert content == "def add(a, b):\n    '''Add two numbers.'''\n    return a + b\n"
            assert "def add(a, b):" in content


# ── Error Handling & Resource Isolation ─────────────────────────────

class TestErrorHandling:
    """Missing resources return friendly notice without raising FileNotFoundError."""

    def test_missing_resource_package_returns_notice(self):
        with patch("soham_py.core.files", side_effect=ModuleNotFoundError("No module named 'fake'")):
            res = get_practical("ds", 1)
            assert res == "There is no file present for DS practical 1."

    def test_missing_file_returns_notice(self):
        mock_resource = MagicMock()
        mock_resource.is_file.return_value = False

        mock_pkg = MagicMock()
        mock_pkg.joinpath.return_value = mock_resource

        with patch("soham_py.core.files", return_value=mock_pkg):
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
            def __init__(self, name, is_file_val=True):
                self.name = name
                self._is_file = is_file_val

            def is_file(self):
                return self._is_file

        mock_items = [
            MockItem("__init__.py", True),
            MockItem("practical1.txt", True),
            MockItem("practical2.txt", True),
            MockItem("practical_extra.txt", True),
            MockItem("notes.txt", True),
            MockItem("practical3.txt", False),  # Directory, not a file
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
        mock_resource.is_file.return_value = True
        mock_resource.read_text.return_value = dangerous_code

        mock_pkg = MagicMock()
        mock_pkg.joinpath.return_value = mock_resource

        with patch("soham_py.core.files", return_value=mock_pkg):
            result = get_practical("ds", 1)
            assert result == dangerous_code
            assert "RuntimeError" in result

    def test_syntax_error_code_does_not_raise(self):
        """Invalid Python syntax must be safely returned as plain text."""
        broken_code = "def def class for while return ;;;; {{}}"
        mock_resource = MagicMock()
        mock_resource.is_file.return_value = True
        mock_resource.read_text.return_value = broken_code

        mock_pkg = MagicMock()
        mock_pkg.joinpath.return_value = mock_resource

        with patch("soham_py.core.files", return_value=mock_pkg):
            result = get_practical("ds", 1)
            assert result == broken_code
