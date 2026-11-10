"""Tests for soham_py.search — full-text search across practicals."""

from unittest.mock import patch

import pytest

from soham_py.search import search


# ── Sample Multiline Programs ───────────────────────────────────────

SAMPLE_PYTHON_CODE = """\
# Data Science Practical 1: Linear Regression
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

def train_model(csv_file: str):
    data = pd.read_csv(csv_file)
    X = data[['feature1', 'feature2']]
    y = data['target']
    model = LinearRegression()
    model.fit(X, y)
    return model
"""

SAMPLE_HTML_CODE = """\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Registration Form</title>
</head>
<body>
    <h1>Student Portal</h1>
    <form action="/submit" method="POST">
        <label for="username">Username:</label>
        <input type="text" id="username" name="username" required>
        <button type="submit">Submit Form</button>
    </form>
</body>
</html>
"""

SAMPLE_SQL_CODE = """\
-- DBMS Practical 1: Student Database Schema
CREATE TABLE students (
    student_id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE,
    gpa DECIMAL(3, 2) DEFAULT 0.00
);

INSERT INTO students (first_name, last_name, email, gpa)
VALUES ('Soham', 'Pandit', 'soham@example.com', 3.95);

SELECT first_name, last_name, gpa
FROM students
WHERE gpa >= 3.5
ORDER BY gpa DESC;
"""


# ── Empty Practicals Search Tests ───────────────────────────────────

class TestSearchEmpty:
    """Searching when practical files are empty."""

    def test_search_returns_empty_list_when_no_matches(self):
        results = search("regression")
        assert results == []

    def test_search_ignores_empty_files(self):
        results = search("anything")
        assert results == []

    def test_search_result_is_list(self):
        results = search("test")
        assert isinstance(results, list)


# ── Query Validation Tests ──────────────────────────────────────────

class TestSearchValidation:
    """Validation of the search query argument."""

    @pytest.mark.parametrize("empty_query", ["", "   ", "\t", "\n", " \t \n "])
    def test_empty_or_whitespace_query_raises_value_error(self, empty_query):
        with pytest.raises(ValueError, match="non-empty string"):
            search(empty_query)

    @pytest.mark.parametrize("invalid_query", [None, 123, 45.6, [], {}, True, False])
    def test_non_string_query_raises_value_error(self, invalid_query):
        with pytest.raises(ValueError, match="non-empty string"):
            search(invalid_query)  # type: ignore[arg-type]


# ── Multiline Python, HTML, SQL Search Tests ────────────────────────

class TestSearchWithContent:
    """Search with simulated multiline Python, HTML, and SQL practicals."""

    @pytest.fixture(autouse=True)
    def setup_mock_practicals(self):
        """Simulate DS with Python, WT with HTML, and DBMS with SQL."""
        def mock_get(subject, number):
            if subject == "ds" and number == 1:
                return SAMPLE_PYTHON_CODE
            elif subject == "wt" and number == 2:
                return SAMPLE_HTML_CODE
            elif subject == "dbms" and number == 3:
                return SAMPLE_SQL_CODE
            return ""

        with patch("soham_py.search.get_practical", side_effect=mock_get):
            yield

    # Python search
    def test_search_python_keyword(self):
        results = search("LinearRegression")
        assert len(results) == 1
        assert results[0]["subject"] == "ds"
        assert results[0]["practical"] == 1
        assert "LinearRegression" in str(results[0]["snippet"])

    def test_search_python_case_insensitive(self):
        results = search("linearregression")
        assert len(results) == 1
        assert results[0]["subject"] == "ds"
        assert results[0]["practical"] == 1

    def test_search_python_import(self):
        results = search("pandas")
        assert len(results) == 1
        assert results[0]["subject"] == "ds"
        assert results[0]["practical"] == 1
        assert results[0]["snippet"] == "import pandas as pd"

    # HTML search
    def test_search_html_tag(self):
        results = search("<form")
        assert len(results) == 1
        assert results[0]["subject"] == "wt"
        assert results[0]["practical"] == 2
        assert '<form action="/submit" method="POST">' in str(results[0]["snippet"])

    def test_search_html_case_insensitive(self):
        results = search("doctype")
        assert len(results) == 1
        assert results[0]["subject"] == "wt"
        assert results[0]["practical"] == 2
        assert "<!DOCTYPE html>" in str(results[0]["snippet"])

    def test_search_html_button(self):
        results = search("submit form")
        assert len(results) == 1
        assert results[0]["subject"] == "wt"
        assert results[0]["practical"] == 2

    # SQL search
    def test_search_sql_create_table(self):
        results = search("CREATE TABLE")
        assert len(results) == 1
        assert results[0]["subject"] == "dbms"
        assert results[0]["practical"] == 3
        assert results[0]["snippet"] == "CREATE TABLE students ("

    def test_search_sql_case_insensitive(self):
        results = search("select")
        assert len(results) == 1
        assert results[0]["subject"] == "dbms"
        assert results[0]["practical"] == 3
        assert results[0]["snippet"] == "SELECT first_name, last_name, gpa"

    def test_search_sql_author_name(self):
        results = search("soham")
        assert len(results) == 1
        assert results[0]["subject"] == "dbms"
        assert results[0]["practical"] == 3

    # Cross-subject search
    def test_search_common_term_matches_none(self):
        results = search("nonexistent_term_xyz")
        assert results == []

    def test_snippet_is_first_matching_line(self):
        results = search("gpa")
        assert len(results) == 1
        # The first occurrence of "gpa" in SAMPLE_SQL_CODE is "gpa DECIMAL(3, 2) DEFAULT 0.00"
        assert "gpa DECIMAL" in str(results[0]["snippet"])


# ── Code Is Never Executed During Search ─────────────────────────────

class TestSearchNoExecution:
    """Ensure that search examines text purely and never executes it."""

    def test_search_across_malicious_code(self):
        dangerous_code = "import os\nos.system('echo dangerous')\nraise SystemExit('bye')\n"

        def mock_get(subject, number):
            if subject == "ds" and number == 1:
                return dangerous_code
            return ""

        with patch("soham_py.search.get_practical", side_effect=mock_get):
            # This should search the string without executing os.system or SystemExit
            results = search("dangerous")
            assert len(results) == 1
            assert results[0]["subject"] == "ds"
            assert results[0]["practical"] == 1
            assert "os.system" in str(results[0]["snippet"])
