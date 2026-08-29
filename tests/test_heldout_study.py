from src.heldout_study import run_study


def test_heldout_study_covers_three_seeds_and_multiple_conditions() -> None:
    rows = run_study(train_episodes=4, train_steps=40, eval_steps=100)
    evaluations = [row for row in rows if "seed" in row]
    assert len(evaluations) == 12
    assert {row["seed"] for row in evaluations} == {101, 202, 303}
    assert {row["target_force_n"] for row in evaluations} == {4.0, 6.0}
