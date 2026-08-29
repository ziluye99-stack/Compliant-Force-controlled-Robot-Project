from pathlib import Path
import subprocess


SCRIPT = Path("scripts/server-status.sh")


def test_server_status_script_is_executable_and_syntax_valid() -> None:
    assert SCRIPT.is_file()
    assert SCRIPT.stat().st_mode & 0o111
    subprocess.run(["bash", "-n", str(SCRIPT)], check=True)


def test_server_status_script_has_read_only_scope() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert "ssh research-gpu" in text
    assert "nvidia-smi --query-gpu" in text
    assert "df -h \"$HOME\"" in text
    for forbidden in ("sudo", "sbatch", "srun", "rm -", "pkill", "kill "):
        assert forbidden not in text
