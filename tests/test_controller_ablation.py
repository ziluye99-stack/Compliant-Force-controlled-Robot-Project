from src.controller_ablation import run_ablation


def test_controller_ablation_covers_observation_and_randomization_axes() -> None:
    rows = run_ablation(train_episodes=2, train_steps=20, eval_steps=20, seed=7)
    assert len(rows) == 36
    assert {row["observation"] for row in rows} == {"full", "force_error_only", "no_integral"}
    assert {row["randomized_training"] for row in rows} == {False, True}
