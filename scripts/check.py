"""Run the same lint, tests and coverage gate locally and in GitHub Actions."""

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
MINIMUM_COVERAGE = 95


def main():
    commands = [
        ["flake8", "."],
        ["coverage", "run", "--branch", "--source=src", "-m", "unittest",
         "discover", "-s", "tests", "-v"],
        ["coverage", "report", "-m", f"--fail-under={MINIMUM_COVERAGE}"],
    ]
    for arguments in commands:
        command = [sys.executable, "-m", *arguments]
        print("\n> " + " ".join(command), flush=True)
        result = subprocess.run(command, cwd=ROOT, check=False)
        if result.returncode:
            return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
