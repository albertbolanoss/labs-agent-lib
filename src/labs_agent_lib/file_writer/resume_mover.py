"""Moves resume files into their target folder."""

import shutil
from pathlib import Path


def file_writer(source_file_path: str, target_path: str) -> None:
    """Moves `source_file_path` into `target_path`, creating the folder if needed."""
    source = Path(source_file_path)
    target_dir = Path(target_path)
    target_dir.mkdir(parents=True, exist_ok=True)

    shutil.move(source_file_path, target_dir / source.name)
