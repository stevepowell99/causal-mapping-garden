"""The one place the Garden scripts look for secrets.

The Garden's secrets live outside the Drive folder, in ~/.secrets/19aCMgarden.env,
because a file inside the folder syncs to everyone it is shared with. The file is
filled from keys.docx with `python ~/.claude/bin/keys.py env <file>`.
A missing file behaves like a missing .env: the key is simply not found.
"""

from pathlib import Path
from typing import Iterable, List, Optional

GARDEN_ENV = Path.home() / ".secrets" / "19aCMgarden.env"


def env_key_names(file: Path = GARDEN_ENV) -> List[str]:
    """Names (never values) of the keys a file defines."""
    if not file.exists():
        return []
    names = []
    for line in file.read_text(encoding="utf-8", errors="replace").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            names.append(line.split("=", 1)[0].strip())
    return names


def read_env_key(name: str, files: Iterable[Path] = (GARDEN_ENV,)) -> Optional[tuple]:
    """(value, file) for the first of `files` that defines `name`, else None."""
    for f in files:
        f = Path(f)
        if not f.exists():
            continue
        for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.strip().startswith(name + "="):
                return line.split("=", 1)[1].strip().strip("\"'"), f
    return None


if __name__ == "__main__":
    print(f"{GARDEN_ENV} exists={GARDEN_ENV.exists()} keys={env_key_names()}")
