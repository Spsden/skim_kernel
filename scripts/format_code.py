import subprocess
import sys
from pathlib import Path


def run_black(target: str = ".") -> None:
    """
    Format the entire codebase using Black.
    """
    try:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "black",
                target,
                "--line-length",
                "88",
            ],
            check=True,
        )
        print("Code formatted successfully using Black")
    except subprocess.CalledProcessError:
        print("Black formatting failed")
        sys.exit(1)


if __name__ == "__main__":
    project_root = Path(__file__).parent
    run_black("../")
