# System and Mechanical Interface Contract

This contract is the boundary between literature, MuJoCo, learning code, and
future hardware. It must be completed before a real robot command path is
added. The platform-neutral baseline lives in
`configs/platform_neutral_interface.yaml`.

## 1. Platform identity

- Platform name, vendor, model, firmware:
- Embodiment: arm / humanoid / other
- CAD or URDF/MJCF revision and SHA-256:
- Controller ownership: position / velocity / torque / hybrid
- Communication path and measured round-trip latency:
- Current status: `platform-neutral`, `hardware-candidate`, or `frozen`

## 2. Mechanical model

For every link and joint, record the revisioned source of the value:

- link frame, joint axis, zero pose, range, velocity and torque limits;
- mass, center of mass, inertia, transmission and actuator model;
- contact geometry, material/friction assumptions and mounting tolerances;
- which values are measured, identified, randomized, or held fixed.

Large CAD files and raw meshes remain on `/mnt/research-data`; Git stores the
small metadata, source revision, exported model hash, and parameter map.

## 3. Sensing and conventions

- Force/torque sensor model, serial/revision, location and frame convention:
- Calibration procedure, bias, noise, range, saturation and sampling rate:
- Joint position/velocity/torque sources and filtering:
- IMU, tactile, vision and contact-state sources:
- Observation names, shapes, units, timestamps and missing-data behavior:

## 4. Control interface

- Fast safety/control rate and slow policy/data rate:
- Action names, shapes, units, bounds and rate limits:
- Delay model and command-hold behavior:
- Contact mode and contact-state ownership:
- Invalid-command behavior: reject, hold-safe-command, or stop:
- MuJoCo mapping for each action and observation:

## 5. Safety gate

Before hardware is enabled, the record must contain measured joint/torque/
velocity/temperature limits, watchdog timeout, independent emergency stop,
safe pose, workspace exclusion zone, operator, and rollback procedure. The
following are mandatory gates:

- [ ] motors-disabled replay passed;
- [ ] low-speed, low-gain supervised test passed;
- [ ] real observations match the versioned observation contract;
- [ ] force, penetration, velocity and command limits are independently checked;
- [ ] every failure is logged with a recoverable run ID.

## 6. Simulation parameter map

Each MuJoCo value must point to one of: measured hardware data, a documented
identification procedure, or a justified randomization interval. A synthetic
fixture must be labeled as such and cannot support a sim-to-real claim.

## 7. Change control

Any change to geometry, frames, rates, limits, calibration, or action/observation
shapes increments the interface version and requires re-running the relevant
simulation tests and offline replay checks.
