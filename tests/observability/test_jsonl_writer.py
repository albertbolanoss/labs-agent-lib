"""Tests for the shared JSONL append helper."""

import json
from pathlib import Path

from labs_agent_lib.observability._jsonl_writer import append_jsonl, file_stem_for, utc_now_iso


def test_append_jsonl_creates_the_directory_and_writes_one_line(tmp_path: Path):
    append_jsonl(str(tmp_path / "sub"), "corr-1", {"a": 1})

    lines = (tmp_path / "sub" / "corr-1.jsonl").read_text(encoding="utf-8").splitlines()
    assert json.loads(lines[0]) == {"a": 1}


def test_append_jsonl_appends_successive_calls_to_the_same_file(tmp_path: Path):
    append_jsonl(str(tmp_path), "corr-1", {"a": 1})
    append_jsonl(str(tmp_path), "corr-1", {"a": 2})

    lines = (tmp_path / "corr-1.jsonl").read_text(encoding="utf-8").splitlines()
    assert [json.loads(line)["a"] for line in lines] == [1, 2]


def test_utc_now_iso_returns_an_iso_formatted_string():
    assert "T" in utc_now_iso()


def test_file_stem_for_returns_the_correlation_id_when_no_agent_is_given():
    assert file_stem_for("corr-1") == "corr-1"
    assert file_stem_for("corr-1", agent=None) == "corr-1"


def test_file_stem_for_combines_correlation_id_and_agent_when_given():
    assert file_stem_for("corr-1", agent="extract_technical_skills") == (
        "corr-1__extract_technical_skills"
    )


def test_file_stem_for_falls_back_to_a_placeholder_when_correlation_id_is_empty():
    assert file_stem_for("") == "no-correlation-id"
    assert file_stem_for("", agent="extract_technical_skills") == (
        "no-correlation-id__extract_technical_skills"
    )
