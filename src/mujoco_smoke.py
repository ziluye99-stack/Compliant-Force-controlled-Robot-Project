"""Headless deterministic MuJoCo smoke test for the local environment."""

from __future__ import annotations

import argparse
import json

import mujoco


MODEL_XML = """
<mujoco model="slider-smoke-test">
  <option timestep="0.002" gravity="0 0 0"/>
  <worldbody>
    <body name="slider" pos="0 0 0">
      <joint name="slide" type="slide" axis="1 0 0"/>
      <geom type="sphere" size="0.05" mass="1"/>
    </body>
  </worldbody>
  <actuator><motor joint="slide" gear="1"/></actuator>
</mujoco>
"""


def run(steps: int) -> float:
    model = mujoco.MjModel.from_xml_string(MODEL_XML)
    data = mujoco.MjData(model)
    data.ctrl[0] = 0.2
    for _ in range(steps):
        mujoco.mj_step(model, data)
    return float(data.qpos[0])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=100)
    args = parser.parse_args()
    if args.steps < 1:
        raise ValueError("--steps must be positive")
    position = run(args.steps)
    if position <= 0:
        raise RuntimeError("MuJoCo smoke test did not move the slider")
    print(json.dumps({"steps": args.steps, "final_position": position}))


if __name__ == "__main__":
    main()
