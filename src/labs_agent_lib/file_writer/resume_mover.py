"""Moves resume files into their target folder."""

import shutil
from pathlib import Path


def _move_resume(sourceFilePath: str, targetPath: str) -> None:
    """Moves `resume_path` into `<resume_dir>/<subdir>`, creating the folder if needed."""
    source = Path(sourceFilePath)
    target_dir = Path(targetPath)
    target_dir.mkdir(parents=True, exist_ok=True)

    shutil.move(sourceFilePath, target_dir / source.name)
