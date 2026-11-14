"""Tests for the public soham_py API (top-level convenience functions)."""

import pytest

import soham_py


class TestConvenienceFunctionsIsolated:
    """Top-level ds(), wt(), dbms() functions using isolated environment."""

    def test_existing_populated_practicals(self, mock_practicals):
        (mock_practicals["ds"] / "practical1.txt").write_text("import pandas as pd", encoding="utf-8")
        (mock_practicals["wt"] / "practical1.txt").write_text("<!DOCTYPE html>", encoding="utf-8")
        (mock_practicals["dbms"] / "practical1.txt").write_text("SELECT 1;", encoding="utf-8")

        assert soham_py.ds(1) == "import pandas as pd"
        assert soham_py.wt(1) == "<!DOCTYPE html>"
        assert soham_py.dbms(1) == "SELECT 1;"

    def test_existing_empty_practicals(self, mock_practicals):
        (mock_practicals["ds"] / "practical2.txt").write_text("", encoding="utf-8")
        (mock_practicals["wt"] / "practical2.txt").write_text("", encoding="utf-8")
        (mock_practicals["dbms"] / "practical2.txt").write_text("", encoding="utf-8")

        assert soham_py.ds(2) == ""
        assert soham_py.wt(2) == ""
        assert soham_py.dbms(2) == ""

    def test_missing_practicals_return_friendly_message(self, mock_practicals):
        assert soham_py.dbms(11) == "There is no file present for DBMS practical 11."
        assert soham_py.dbms(15) == "There is no file present for DBMS practical 15."
        assert soham_py.ds(20) == "There is no file present for DS practical 20."
        assert soham_py.wt(30) == "There is no file present for WT practical 30."

    def test_practical_number_greater_than_10_when_present(self, mock_practicals):
        (mock_practicals["ds"] / "practical15.txt").write_text("model = None", encoding="utf-8")
        (mock_practicals["wt"] / "practical42.txt").write_text("alert(1);", encoding="utf-8")
        (mock_practicals["dbms"] / "practical100.txt").write_text("COMMIT;", encoding="utf-8")

        assert soham_py.ds(15) == "model = None"
        assert soham_py.wt(42) == "alert(1);"
        assert soham_py.dbms(100) == "COMMIT;"

    @pytest.mark.parametrize("invalid_num", [0, -1, -50])
    def test_zero_and_negative_raise_value_error(self, invalid_num):
        with pytest.raises(ValueError, match="positive integer"):
            soham_py.ds(invalid_num)
        with pytest.raises(ValueError, match="positive integer"):
            soham_py.wt(invalid_num)
        with pytest.raises(ValueError, match="positive integer"):
            soham_py.dbms(invalid_num)

    @pytest.mark.parametrize("invalid_type", ["one", None, 3.14, True])
    def test_non_integer_numbers_raise_value_error(self, invalid_type):
        with pytest.raises(ValueError, match="must be an integer"):
            soham_py.ds(invalid_type)  # type: ignore[arg-type]


class TestSubjects:
    """soham_py.subjects() function."""

    def test_returns_three_subjects(self):
        result = soham_py.subjects()
        assert len(result) == 3

    def test_returns_tuples(self):
        for key, desc in soham_py.subjects():
            assert isinstance(key, str)
            assert isinstance(desc, str)

    def test_subject_keys(self):
        keys = [k for k, _ in soham_py.subjects()]
        assert set(keys) == {"ds", "wt", "dbms"}


class TestListPracticalsTopLevel:
    """soham_py.list_practicals() function."""

    def test_list_practicals_reflects_files(self, mock_practicals):
        (mock_practicals["ds"] / "practical1.txt").write_text("code", encoding="utf-8")
        (mock_practicals["ds"] / "practical15.txt").write_text("code", encoding="utf-8")
        (mock_practicals["ds"] / "practical3.txt").write_text("code", encoding="utf-8")

        assert soham_py.list_practicals("ds") == [1, 3, 15]


class TestSearchTopLevel:
    """soham_py.search() function at the top level."""

    def test_search_finds_code(self, mock_practicals):
        (mock_practicals["ds"] / "practical1.txt").write_text("import pandas as pd", encoding="utf-8")
        results = soham_py.search("pandas")
        assert len(results) == 1
        assert results[0]["subject"] == "ds"
        assert results[0]["practical"] == 1

    def test_search_empty_raises(self):
        with pytest.raises(ValueError):
            soham_py.search("")


class TestSaveTopLevel:
    """soham_py.save() function at the top level."""

    def test_save_creates_file(self, mock_practicals, tmp_path):
        (mock_practicals["ds"] / "practical1.txt").write_text("some code", encoding="utf-8")
        dest = tmp_path / "out.txt"
        soham_py.save("ds", 1, str(dest))
        assert dest.exists()
        assert dest.read_text(encoding="utf-8") == "some code"


class TestVersion:
    """Package metadata."""

    def test_version_exists(self):
        assert hasattr(soham_py, "__version__")
        assert isinstance(soham_py.__version__, str)

    def test_author_exists(self):
        assert soham_py.__author__ == "Soham Pandit"
