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


def test_dataset_and_policy_round_trip(tmp_path) -> None:
    dataset = collect_dataset("joint_residual", episodes=3, steps=20, seed=13)
    train, _ = split_by_episode(dataset)
    policy = TwoRateLinearPolicy.fit(train.features, train.targets, output_limits=np.asarray([10.0, 0.5, 5.0]))
    dataset_path = tmp_path / "dataset.npz"
    policy_path = tmp_path / "policy.npz"
    dataset.save(dataset_path)
    policy.save(policy_path)
    restored_dataset = type(dataset).load(dataset_path)
    restored_policy = TwoRateLinearPolicy.load(policy_path)
    assert np.array_equal(restored_dataset.features, dataset.features)
    assert np.array_equal(restored_dataset.targets, dataset.targets)
    assert np.array_equal(restored_policy.weights, policy.weights)
    assert np.array_equal(restored_policy.predict(train.features), policy.predict(train.features))


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


def test_training_dynamics_randomization_is_reproducible() -> None:
    kwargs = {
        "episodes": 3,
        "steps": 20,
        "seed": 12,
        "dynamics_randomization": {
            "friction_scale": (0.8, 1.2),
            "stiffness_scale": (0.8, 1.2),
            "force_noise_std_n": (0.1, 0.3),
            "actuator_delay_steps": (0.0, 2.0),
        },
    }
    first = collect_dataset("trajectory_residual", **kwargs)
    second = collect_dataset("trajectory_residual", **kwargs)
    assert np.array_equal(first.features, second.features)
    assert np.array_equal(first.targets, second.targets)
    assert np.array_equal(first.episode_ids, second.episode_ids)
