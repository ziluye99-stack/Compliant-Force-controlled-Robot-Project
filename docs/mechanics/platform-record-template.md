# Platform Record: <platform-id>

Complete this record only from a named platform or an explicitly labelled
synthetic fixture. Read `docs/PROJECT_VISION.md` before starting it.

## Record metadata

- Platform ID and revision:
- Embodiment: arm / humanoid / other
- Vendor, model, firmware:
- Record owner and date:
- Status: `platform-neutral`, `hardware-candidate`, or `frozen`
- Related experiment/proposal:
- CAD/URDF/MJCF source and revision:
- Exported model SHA-256:

## Geometry and kinematics

| Element | Frame/axis/zero pose | Position or joint limits | Source and revision |
| --- | --- | --- | --- |
| Base | | | |
| Link/joint 1 | | | |
| Link/joint 2 | | | |
| Tool/TCP | | | |

Record all lengths in meters, angles in radians, and identify whether each
value is measured, taken from manufacturer data, or estimated.

## Dynamics and transmission

| Link/joint | Mass (kg) | Center of mass (m) | Inertia (kg m^2) | Transmission/actuator | Evidence |
| --- | ---: | --- | --- | --- | --- |
| | | | | | |

- Joint friction model and identified range:
- Backlash, compliance, or drivetrain elasticity:
- Motor current/torque conversion and update rate:
- Temperature dependence or derating:

## Contact, tool, and mounting

- End-effector/tool revision and mounting interface:
- Contact geometry and material pair:
- Friction, restitution, and compliance evidence:
- Tool-center-point measurement and uncertainty:
- Mounting tolerance and repeatability:

## Sensors and calibration

| Sensor | Model/serial/revision | Frame | Rate | Range/saturation | Bias/noise | Calibration evidence |
| --- | --- | --- | ---: | --- | --- | --- |
| Force/torque | | | | | | |
| Joint state | | | | | | |
| Tactile/IMU/vision | | | | | | |

- Calibration procedure and date:
- Calibration artifact path and SHA-256:
- Timestamp source, synchronization error, and measured latency:
- Missing-data, clipping, and invalid-measurement behavior:

## Control and communication

- Controller ownership: position / velocity / torque / hybrid:
- Communication path and measured round-trip latency:
- Fast control rate and policy/data rate:
- Action names, units, bounds, slew limits, and command hold behavior:
- Observation names, shapes, units, timestamps, and frame conventions:
- Invalid-command behavior: reject / hold safe / stop:
- MuJoCo action and observation mapping:

## Limits and safety gate

- Joint position, velocity, torque, current, and temperature limits:
- Contact-force and tool-load limits:
- Watchdog timeout and independent emergency-stop path:
- Safe pose and workspace exclusion zone:
- Operator and approval record:
- Rollback model/config and recovery procedure:

Required evidence before hardware commands:

- [ ] motors-disabled replay passed;
- [ ] low-speed, low-gain supervised test passed;
- [ ] real observations match the versioned interface;
- [ ] force, penetration, velocity, and command limits are independently checked;
- [ ] every failure has a recoverable run ID and archived log.

## MuJoCo parameter map

| MuJoCo parameter | Value or range | Source type (`measured`, `identified`, `randomized`, `fixed`) | Evidence path/hash | Uncertainty or rationale |
| --- | --- | --- | --- | --- |
| Body mass/inertia | | | | |
| Joint damping/friction | | | | |
| Contact friction/compliance | | | | |
| Sensor bias/noise/latency | | | | |

No row may remain unexplained when a transfer claim is made. A synthetic row
must remain labelled synthetic and cannot support a sim-to-real claim.

## Change record

- Interface version before change:
- Changed fields and reason:
- Re-run commands and artifact IDs:
- Reviewer/operator sign-off:
