# Changelog

All notable changes to **SohamPy** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.5.0] — 2026-11-18

### Added

- Fully populated practical programs for DS, WT, and DBMS.
- Dynamic practical discovery: `list_practicals()` dynamically discovers all `practical<N>.txt` files and sorts them numerically.
- Support for practical numbers beyond 10 across all retrieval functions (`ds()`, `wt()`, `dbms()`).
- Friendly plain-text notification when a practical file does not exist (no `FileNotFoundError`).
- Dynamic case-insensitive search across all discovered practical files, automatically skipping empty files.
- Robust packaging wildcards in `pyproject.toml` to automatically bundle all practical text files into distributions.

## [0.1.0] — 2026-11-10

### Added

- Initial release.
- Three subjects: **DS** (Data Science), **WT** (Web Technology), **DBMS** (Database Management Systems).
- 10 practical slots per subject (30 total `.txt` files).
- `ds()`, `wt()`, `dbms()` convenience functions.
- `list_practicals()` to list available practicals per subject.
- `subjects()` to list all subjects.
- `search()` for case-insensitive full-text search across practicals.
- `save()` to write a practical's contents to a local file.
- Subject aliases (e.g. `"data_science"` → `"ds"`).
- Comprehensive test suite.
- Professional README with usage examples.

