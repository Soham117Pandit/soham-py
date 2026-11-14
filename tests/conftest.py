"""Shared test fixtures for SohamPy."""

import pytest
from importlib.resources import files as orig_files


@pytest.fixture
def mock_practicals(tmp_path, monkeypatch):
    """Provide an isolated, configurable practicals environment for all 3 subjects."""
    ds_dir = tmp_path / "ds"
    wt_dir = tmp_path / "wt"
    dbms_dir = tmp_path / "dbms"
    ds_dir.mkdir(parents=True, exist_ok=True)
    wt_dir.mkdir(parents=True, exist_ok=True)
    dbms_dir.mkdir(parents=True, exist_ok=True)

    mapping = {
        "soham_py.practicals.ds": ds_dir,
        "soham_py.practicals.wt": wt_dir,
        "soham_py.practicals.dbms": dbms_dir,
    }

    def fake_files(pkg):
        if pkg in mapping:
            return mapping[pkg]
        return orig_files(pkg)

    monkeypatch.setattr("soham_py.core.files", fake_files)
    return {
        "ds": ds_dir,
        "wt": wt_dir,
        "dbms": dbms_dir,
    }

