from pathlib import Path

from labs_agent_lib.file_writer.resume_mover import file_writer


def test_moves_file_into_target_directory(tmp_path: Path):
    source = tmp_path / "source" / "resume.pdf"
    source.parent.mkdir()
    source.write_text("resume content", encoding="utf-8")
    target_dir = tmp_path / "target"

    file_writer(str(source), str(target_dir))

    assert (target_dir / "resume.pdf").read_text(encoding="utf-8") == "resume content"


def test_creates_target_directory_when_missing(tmp_path: Path):
    source = tmp_path / "resume.pdf"
    source.write_text("resume content", encoding="utf-8")
    target_dir = tmp_path / "missing" / "nested"

    file_writer(str(source), str(target_dir))

    assert target_dir.is_dir()
    assert (target_dir / "resume.pdf").exists()


def test_does_not_fail_when_target_directory_already_exists(tmp_path: Path):
    source = tmp_path / "resume.pdf"
    source.write_text("resume content", encoding="utf-8")
    target_dir = tmp_path / "target"
    target_dir.mkdir()

    file_writer(str(source), str(target_dir))

    assert (target_dir / "resume.pdf").exists()


def test_removes_file_from_source_location(tmp_path: Path):
    source = tmp_path / "resume.pdf"
    source.write_text("resume content", encoding="utf-8")
    target_dir = tmp_path / "target"

    file_writer(str(source), str(target_dir))

    assert not source.exists()


def test_keeps_the_source_file_name_in_the_target_path(tmp_path: Path):
    source = tmp_path / "nested" / "candidate_resume.docx"
    source.parent.mkdir()
    source.write_text("resume content", encoding="utf-8")
    target_dir = tmp_path / "target"

    file_writer(str(source), str(target_dir))

    assert [p.name for p in target_dir.iterdir()] == ["candidate_resume.docx"]
