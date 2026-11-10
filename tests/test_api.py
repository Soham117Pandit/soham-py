"""Tests for the public soham_py API (top-level convenience functions)."""

import pytest

import soham_py


class TestConvenienceFunctions:
    """Top-level ds(), wt(), dbms() functions."""

    def test_ds_returns_string(self):
        assert isinstance(soham_py.ds(1), str)

    def test_wt_returns_string(self):
        assert isinstance(soham_py.wt(1), str)

    def test_dbms_returns_string(self):
        assert isinstance(soham_py.dbms(1), str)

    @pytest.mark.parametrize("number", range(1, 11))
    def test_ds_all_10(self, number):
        assert soham_py.ds(number) == ""

    @pytest.mark.parametrize("number", range(1, 11))
    def test_wt_all_10(self, number):
        assert soham_py.wt(number) == ""

    @pytest.mark.parametrize("number", range(1, 11))
    def test_dbms_all_10(self, number):
        assert soham_py.dbms(number) == ""


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


class TestListPracticals:
    """soham_py.list_practicals() function."""

    def test_ds_has_10(self):
        assert soham_py.list_practicals("ds") == list(range(1, 11))

    def test_wt_has_10(self):
        assert soham_py.list_practicals("wt") == list(range(1, 11))

    def test_dbms_has_10(self):
        assert soham_py.list_practicals("dbms") == list(range(1, 11))


class TestSearch:
    """soham_py.search() function at the top level."""

    def test_search_returns_list(self):
        assert soham_py.search("test") == []

    def test_search_empty_raises(self):
        with pytest.raises(ValueError):
            soham_py.search("")


class TestSave:
    """soham_py.save() function at the top level."""

    def test_save_creates_file(self, tmp_path):
        dest = tmp_path / "out.txt"
        soham_py.save("ds", 1, str(dest))
        assert dest.exists()


class TestVersion:
    """Package metadata."""

    def test_version_exists(self):
        assert hasattr(soham_py, "__version__")
        assert soham_py.__version__ == "0.1.0"

    def test_author_exists(self):
        assert soham_py.__author__ == "Soham Pandit"

