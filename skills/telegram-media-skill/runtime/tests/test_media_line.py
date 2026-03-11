from pathlib import Path

from media_line import resolve_file


def test_resolve_file_returns_absolute_existing_file(tmp_path: Path) -> None:
    f = tmp_path / "x.txt"
    f.write_text("ok")
    resolved = resolve_file(str(f))
    assert resolved == f.resolve()
    assert resolved.is_file()
