import json
import subprocess
import sys
from pathlib import Path


STEPFG_DIR = Path(__file__).resolve().parent.parent


def test_cli_with_sample_input(tmp_path):
    out_file = tmp_path / "test_output.stp"
    result = subprocess.run(
        [sys.executable, "-m", "stepfg",
         str(STEPFG_DIR / "part_geometry.txt"),
         str(out_file)],
        capture_output=True, text=True,
        cwd=str(STEPFG_DIR),
    )
    assert result.returncode == 0
    assert "[DONE]" in result.stdout
    assert out_file.exists()
    content = out_file.read_text()
    assert content.startswith("ISO-10303-21;")
    assert "CLOSED_SHELL" in content


def test_cli_json_dict_input(tmp_path):
    in_file = tmp_path / "input.json"
    in_file.write_text(json.dumps({
        "polygons": [[[0, 0], [1, 0], [1, 1], [0, 1]]],
        "z_range": [0, 5],
        "scale": 1,
    }))
    out_file = tmp_path / "output.stp"
    result = subprocess.run(
        [sys.executable, "-m", "stepfg", str(in_file), str(out_file)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    content = out_file.read_text()
    assert content.startswith("ISO-10303-21;")
    assert "CLOSED_SHELL" in content


def test_cli_json_dict_default_scale(tmp_path):
    in_file = tmp_path / "input.json"
    in_file.write_text(json.dumps({
        "polygons": [[[0, 0], [1, 0], [1, 1], [0, 1]]],
        "z_range": [0, 5],
    }))
    out_file = tmp_path / "output.stp"
    result = subprocess.run(
        [sys.executable, "-m", "stepfg", str(in_file), str(out_file)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert out_file.exists()


def test_cli_json_array_input(tmp_path):
    in_file = tmp_path / "input.json"
    in_file.write_text(json.dumps([
        [[[0, 0], [1, 0], [1, 1], [0, 1]]],
        [0, 5],
        1,
    ]))
    out_file = tmp_path / "output.stp"
    result = subprocess.run(
        [sys.executable, "-m", "stepfg", str(in_file), str(out_file)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    content = out_file.read_text()
    assert "CLOSED_SHELL" in content


def test_cli_json_missing_key(tmp_path):
    in_file = tmp_path / "input.json"
    in_file.write_text(json.dumps({"polygons": [[[0, 0], [1, 0], [1, 1], [0, 1]]]}))
    result = subprocess.run(
        [sys.executable, "-m", "stepfg", str(in_file), "/dev/null"],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert "z_range" in result.stderr


def test_cli_missing_file(tmp_path):
    result = subprocess.run(
        [sys.executable, "-m", "stepfg", "nonexistent.txt"],
        capture_output=True, text=True,
    )
    assert result.returncode != 0


def test_cli_version():
    result = subprocess.run(
        [sys.executable, "-m", "stepfg", "--version"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "2.1.0" in result.stdout
