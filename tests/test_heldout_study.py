from src.heldout_study import run_study
from src.experiment import load_config
from src.heldout_study import run_from_config
from pathlib import Path


def test_heldout_study_covers_three_seeds_and_multiple_conditions() -> None:
    rows = run_study(train_episodes=4, train_steps=40, eval_steps=100)
    evaluations = [row for row in rows if "seed" in row]
    assert len(evaluations) == 12
    assert {row["seed"] for row in evaluations} == {101, 202, 303}
    assert {row["target_force_n"] for row in evaluations} == {4.0, 6.0}


def test_config_driven_heldout_run_writes_manifest(tmp_path: Path) -> None:
    config = load_config(Path("configs/residual_policy.yaml"))
    result = run_from_config(config, tmp_path / "heldout", train_episodes=4, train_steps=30, eval_steps=40)
    assert result["manifest"]["evaluation_rows"] == 12
    assert (tmp_path / "heldout" / "manifest.json").is_file()
    assert (tmp_path / "heldout" / "config.yaml").is_file()
    assert (tmp_path / "heldout" / "results.json").is_file()
