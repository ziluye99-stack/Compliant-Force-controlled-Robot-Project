import numpy as np

from src.two_rate_residual import (
    VARIANTS,
    TwoRateLinearPolicy,
    collect_dataset,
    run_two_rate,
    split_by_episode,
    train_and_evaluate,
)


def test_all_variants_have_expected_output_shapes() -> None:
    assert VARIANTS == ("pi_only", "trajectory_residual", "gain_residual", "joint_residual")
    for variant, width in (("trajectory_residual", 1), ("gain_residual", 2), ("joint_residual", 3)):
        dataset = collect_dataset(variant, episodes=2, steps=20, seed=4)
        assert dataset.features.shape == (40, 5)
        assert dataset.targets.shape == (40, width)


def test_episode_split_prevents_timestep_leakage() -> None:
    dataset = collect_dataset("joint_residual", episodes=4, steps=20, seed=5)
    train, test = split_by_episode(dataset)
    assert set(train.episode_ids).isdisjoint(set(test.episode_ids))
    assert len(train.features) + len(test.features) == len(dataset.features)


def test_two_rate_policy_prediction_is_bounded_and_deterministic() -> None:
    dataset = collect_dataset("joint_residual", episodes=4, steps=30, seed=6)
    train, _ = split_by_episode(dataset)
    limits = np.asarray([10.0, 0.5, 5.0])
    first = TwoRateLinearPolicy.fit(train.features, train.targets, output_limits=limits)
    second = TwoRateLinearPolicy.fit(train.features, train.targets, output_limits=limits)
    assert np.array_equal(first.weights, second.weights)
    prediction = first.predict(train.features)
    assert np.all(np.abs(prediction) <= limits)


def test_period_holds_behavior_without_breaking_safety() -> None:
    dataset = collect_dataset("trajectory_residual", episodes=4, steps=40, seed=7)
    train, _ = split_by_episode(dataset)
    policy = TwoRateLinearPolicy.fit(train.features, train.targets, output_limits=np.asarray([10.0]))
    metrics = run_two_rate("trajectory_residual", policy, steps=120, residual_period_fast_steps=25, seed=8)
    assert metrics.contacts_seen
    assert metrics.max_penetration_m < 0.001
    assert metrics.max_abs_control_n <= 30.0
    assert metrics.variant == "trajectory_residual"


def test_smallest_runner_smoke_is_reproducible() -> None:
    first = train_and_evaluate("joint_residual", episodes=2, steps=20, eval_steps=40, residual_period_fast_steps=5, seed=9)
    second = train_and_evaluate("joint_residual", episodes=2, steps=20, eval_steps=40, residual_period_fast_steps=5, seed=9)
    assert first == second
    assert first["residual"]["safety_gate_activations"] >= 0
