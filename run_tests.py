"""Run each standalone standard-library test suite in its own process."""

from pathlib import Path
import subprocess
import sys


def main() -> int:
    directories = sorted(p for p in (Path(__file__).resolve().parent / "examples").iterdir()
                         if p.is_dir() and any(p.glob("test_*.py")))
    if not directories:
        print("No example test suites found.", file=sys.stderr)
        return 1
    failures = []
    for path in directories:
        print(f"\n{path.name}", flush=True)
        result = subprocess.run(
            [sys.executable, "-B", "-m", "unittest", "discover", "-v"],
            cwd=path,
            check=False,
        )
        if result.returncode:
            failures.append(path.name)
    if failures:
        print("Failed: " + ", ".join(failures), file=sys.stderr)
        return 1
    print(f"\nAll {len(directories)} example suites passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
