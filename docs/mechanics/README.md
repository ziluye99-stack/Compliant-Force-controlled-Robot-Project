# Mechanical and Sensor Records

Mechanical design is part of the experiment, not an implementation detail.
Before a controller gain or learned policy is interpreted, record the
platform, geometry, sensing, limits, and the mapping from measured values to
MuJoCo parameters. Use [`platform-record-template.md`](platform-record-template.md)
for one robot/tool/sensor assembly.

## Record boundary

Git stores compact metadata, revision identifiers, exported model hashes, and
parameter maps. Keep CAD, raw meshes, calibration captures, and raw sensor
logs on `/mnt/research-data`. Reference those files by stable path and SHA-256;
do not commit them or credentials.

## Required review order

1. Identify the robot embodiment, firmware, controller ownership, and intended
   task.
2. Freeze link/joint frames, zero pose, limits, mass properties, contact
   geometry, and tool mounting tolerances.
3. Record F/T, encoder, tactile, IMU, and vision calibration, rates, bias,
   noise, saturation, timestamps, and missing-data behavior.
4. Map every MuJoCo value to measured data, an identification procedure, or a
   justified randomization interval.
5. Review the watchdog, independent E-stop, safe pose, operator, rollback, and
   motors-disabled replay before enabling any hardware command path.

## Status vocabulary

- `platform-neutral`: synthetic interface only; no hardware claim.
- `hardware-candidate`: specifications are being collected; commands remain disabled.
- `frozen`: all required parameters and safety evidence are reviewed for a
  named platform. This status still does not authorize a command by itself.

The record is an input to `configs/platform_neutral_interface.yaml` or a
future platform-specific interface. Any change to frames, rates, limits,
calibration, geometry, or action/observation shapes increments the interface
version and reruns the relevant MuJoCo and replay checks.
