import numpy as np
from pathlib import Path

from src.experiment import load_config
from src.residual_policy import (
    ResidualLinearPolicy,
    collect_dataset,
    evaluate_residual,
    split_by_episode,
    run_from_config,
)


def test_dataset_split_keeps_episodes_together() -> None:
    dataset = collect_dataset(episodes=4, steps=40, seed=3)
    train, test = split_by_episode(dataset, train_fraction=0.75)
    assert set(train.episode_ids).isdisjoint(set(test.episode_ids))
    assert len(train.features) + len(test.features) == len(dataset.features)


def test_dataset_supports_dynamics_randomization() -> None:
    dataset = collect_dataset(episodes=3, steps=20, dynamics_randomization=((1.2, 1.8), (0.7, 0.9)), seed=4)
    assert dataset.features.shape == (60, 5)


def test_residual_policy_fit_is_deterministic_and_bounded() -> None:
    dataset = collect_dataset(episodes=4, steps=40, seed=3)
    train, _ = split_by_episode(dataset)
    policy_a = ResidualLinearPolicy.fit(train.features, train.targets)
    policy_b = ResidualLinearPolicy.fit(train.features, train.targets)
    assert np.array_equal(policy_a.weights, policy_b.weights)
    assert np.max(np.abs(policy_a.predict(train.features))) <= policy_a.residual_limit_n


def test_residual_evaluation_preserves_contact_safety() -> None:
    dataset = collect_dataset(episodes=6, steps=100, seed=5)
    train, _ = split_by_episode(dataset)
    policy = ResidualLinearPolicy.fit(train.features, train.targets)
    metrics = evaluate_residual(policy, steps=300, seed=11)
    assert metrics.contacts_seen
    assert metrics.max_penetration_m < 0.001
    assert metrics.max_abs_control_n <= 30.0


def test_config_driven_run_writes_provenance_and_artifacts(tmp_path: Path) -> None:
    config = load_config(Path("configs/residual_policy.yaml"))
    result = run_from_config(config, tmp_path / "run", episodes=3, steps=30, eval_steps=40)
    run_dir = tmp_path / "run"
    assert result["manifest"]["dataset_rows"] == 90
    assert (run_dir / "config.yaml").is_file()
    assert (run_dir / "manifest.json").is_file()
    assert (run_dir / "dataset.npz").is_file()
    assert (run_dir / "policy.npz").is_file()
    assert (run_dir / "metrics.json").is_file()
