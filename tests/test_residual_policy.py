import numpy as np

from src.residual_policy import (
    ResidualLinearPolicy,
    collect_dataset,
    evaluate_residual,
    split_by_episode,
)


def test_dataset_split_keeps_episodes_together() -> None:
    dataset = collect_dataset(episodes=4, steps=40, seed=3)
    train, test = split_by_episode(dataset, train_fraction=0.75)
    assert set(train.episode_ids).isdisjoint(set(test.episode_ids))
    assert len(train.features) + len(test.features) == len(dataset.features)


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
