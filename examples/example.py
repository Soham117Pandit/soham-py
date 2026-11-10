"""Example usage of SohamPy.

Run this file after installing the package:
    pip install soham-py
    python example.py
"""

import soham_py

# ── Show version ────────────────────────────────────────────────────
print(f"SohamPy version: {soham_py.__version__}")
print()

# ── List subjects ──────────────────────────────────────────────────
print("Available subjects:")
for key, description in soham_py.subjects():
    print(f"  {key:6s} — {description}")
print()

# ── Retrieve practicals ────────────────────────────────────────────
print("DS Practical 1:")
code = soham_py.ds(1)
if code:
    print(code)
else:
    print("  (empty — add your code to the .txt file)")
print()

print("WT Practical 1:")
code = soham_py.wt(1)
if code:
    print(code)
else:
    print("  (empty — add your code to the .txt file)")
print()

print("DBMS Practical 1:")
code = soham_py.dbms(1)
if code:
    print(code)
else:
    print("  (empty — add your code to the .txt file)")
print()

# ── List practicals ────────────────────────────────────────────────
print("DS practicals:", soham_py.list_practicals("ds"))
print("WT practicals:", soham_py.list_practicals("wt"))
print("DBMS practicals:", soham_py.list_practicals("dbms"))
print()

# ── Search ──────────────────────────────────────────────────────────
print("Search for 'regression':", soham_py.search("regression"))
print()

# ── Save to file ───────────────────────────────────────────────────
# soham_py.save("ds", 1, "practical1.txt")
# print("Saved DS practical 1 to practical1.txt")

