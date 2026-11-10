# SohamPy

**College practical programs stored as plain text — retrieve them with a simple Python import.**

SohamPy is a lightweight Python package that bundles college practical programs for three subjects as plain `.txt` files. Once installed, you can retrieve any practical from any computer using a simple import statement — no internet connection required after installation.

> **Important:** SohamPy stores and returns source code as **plain text**. It never executes the stored code.

---

## Supported Subjects

| Key    | Subject                      | Practicals |
|--------|------------------------------|------------|
| `ds`   | Data Science                 | 10         |
| `wt`   | Web Technology               | 10         |
| `dbms` | Database Management Systems  | 10         |

**Total: 30 practical files.**

> **Note:** SQL, MySQL, and MongoDB are topics within DBMS — they are not separate subjects.

---

## Installation

```bash
pip install soham-py
```

After installation, the package works **completely offline**. Internet is only needed for the initial install and future updates.

---

## Quick Start

```python
import soham_py

# Retrieve a Data Science practical
print(soham_py.ds(1))

# Retrieve a Web Technology practical
print(soham_py.wt(1))

# Retrieve a DBMS practical
print(soham_py.dbms(1))
```

---

## Available Functions

### Retrieve a Practical

```python
soham_py.ds(1)       # Data Science practical 1
soham_py.wt(5)       # Web Technology practical 5
soham_py.dbms(10)    # DBMS practical 10
```

Returns the complete contents of the `.txt` file as a Python string. Empty files return `""`. If the requested practical file does not exist, returns a friendly notice (e.g., `"There is no file present for DBMS practical 11."`).

### List Practicals

```python
soham_py.list_practicals("ds")
# [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

soham_py.list_practicals("wt")
soham_py.list_practicals("dbms")
```

### Show Subjects

```python
soham_py.subjects()
# [('dbms', 'Database Management Systems'),
#  ('ds', 'Data Science'),
#  ('wt', 'Web Technology')]
```

### Search Practicals

```python
soham_py.search("regression")
soham_py.search("database")
soham_py.search("HTML")
```

- Searches all three subjects.
- Case-insensitive.
- Skips empty files.
- Returns a list of `{"subject", "practical", "snippet"}` dicts.
- Returns `[]` when there are no matches.
- Raises `ValueError` for empty or whitespace-only queries.

### Save a Practical to a File

```python
soham_py.save("ds", 1, "practical1.txt")
```

- Saves the practical contents to a local file.
- Uses UTF-8 encoding.
- Preserves the original text exactly.
- You can choose any output filename.

---

## Subject Aliases

You can use alternative names for subjects:

| Alias              | Resolves To |
|--------------------|-------------|
| `ds`               | `ds`        |
| `data_science`     | `ds`        |
| `wt`               | `wt`        |
| `web`              | `wt`        |
| `web_technology`   | `wt`        |
| `dbms`             | `dbms`      |
| `database`         | `dbms`      |

All aliases are **case-insensitive**.

---

## Adding Your Practical Programs

All 30 practical files are **initially empty**. To add your code:

1. Find the package source in `src/soham_py/practicals/`.
2. Open the appropriate `.txt` file (e.g., `ds/practical1.txt`).
3. Paste your practical program as plain text.
4. Rebuild and reinstall the package.

```text
src/soham_py/practicals/
├── ds/
│   ├── practical1.txt    ← Add your DS practical 1 code here
│   ├── practical2.txt
│   └── ...
├── wt/
│   ├── practical1.txt    ← Add your WT practical 1 code here
│   └── ...
└── dbms/
    ├── practical1.txt    ← Add your DBMS practical 1 code here
    └── ...
```

> **Note:** After modifying practicals in a published package, you must create a new version and upgrade via `pip install --upgrade soham-py` for the changes to take effect on other computers.

---

## Error Handling

| Situation                                  | Behavior / Error Raised                        |
|--------------------------------------------|------------------------------------------------|
| Invalid subject name                       | `ValueError`                                   |
| Invalid practical number (<= 0, non-int)   | `ValueError`                                   |
| Missing practical file                     | Returns friendly notice string (no error)      |
| Empty search query                         | `ValueError`                                   |
| Empty practical file                       | Returns `""` (no error)                        |

---

## Development

```bash
# Clone the repository
git clone https://github.com/soham-pandit/soham-py.git
cd soham-py

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest -v

# Build distributions
python -m build
```

---

## Contributing

1. Fork the repository.
2. Create a feature branch.
3. Make your changes.
4. Run the tests.
5. Submit a pull request.

---

## License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## Author

**Soham Pandit**

