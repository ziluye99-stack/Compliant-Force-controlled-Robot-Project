# Two-rate residual study: equations and notation

Read [`docs/PROJECT_VISION.md`](../PROJECT_VISION.md) before changing this
record. This note fixes the equations used by
`src/two_rate_residual.py`; it is a one-dimensional MuJoCo contact fixture,
not a robot hardware controller.

## Signals and units

At fast-loop step `k`, the target normal force is `F*_k` (N), the simulated
contact force is `F_k` (N), the noisy measured force is `Fhat_k` (N), and the
generalized velocity is `v_k` (the MuJoCo joint velocity unit for this fixture).
The controller timestep is `dt = 0.002 s`. The signed force error and bounded
integral state are

```text
e_k = F*_k - Fhat_k                         [N]
I_k = clip(I_(k-1) + e_k * dt, -Imax, Imax) [N*s]
```

The initial integral state is zero at each episode. The force measurement is
generated in simulation as `Fhat_k = max(0, F_k + epsilon_k)`, where
`epsilon_k ~ Normal(0, sigma_force^2)`.

## Fast PI-D command

The baseline command before residual adaptation is

```text
u_PI,k = clip(-(Kp * e_k + Ki * I_k + Kd * v_k), -Umax, Umax) [N]
```

The negative sign follows the slider actuator convention in the MuJoCo XML.
`Kp`, `Ki`, and `Kd` are configurable; the current matrix uses `0.5`, `5.0`,
and `0.3`, respectively. `Umax = 30 N` and `Imax = 10 N*s` in the current
configuration.

## Slow residual and zero-order hold

The residual observes the five-dimensional feature vector

```text
x_k = [e_k, v_k, I_k, u_PI,k, F*_k]
```

Every `M = 25` fast steps (`20 Hz`), a linear ridge policy produces a bounded
action. Between updates, the action is held constant:

```text
a_k = clip(W [x_k, 1], -L, L),  k mod M = 0
a_k = a_(k-1),                    otherwise
```

`L` is variant-specific: `[10]` for a command residual, `[0.5, 5]` for gain
residuals, and `[10, 0.5, 5]` for the joint residual.

The action is decoded as follows:

| Variant | `command_delta` (N) | `kp_delta` | `ki_delta` |
| --- | ---: | ---: | ---: |
| `pi_only` | 0 | 0 | 0 |
| `trajectory_residual` | `a[0]` | 0 | 0 |
| `gain_residual` | 0 | `a[0]` | `a[1]` |
| `joint_residual` | `a[0]` | `a[1]` | `a[2]` |

The adapted command before the final safety clip is

```text
u_raw,k = -( (Kp + kp_delta) * e_k
           + (Ki + ki_delta) * I_k
           + Kd * v_k ) + command_delta
u_k = clip(u_raw,k, -Umax, Umax)
```

The command is then placed in a FIFO of `D` steps for the configured actuator
delay. Non-finite values, limit violations, and penetration above `0.001 m`
increment the safety-gate counter and cause a bounded safe command to be used.

## Training target and split

Dataset rows use the measured feature vector `x_k`. The oracle command is the
same PI equation evaluated with the true force `F_k`; the command-residual
target is

```text
delta_u*_k = u_oracle,k - u_PI,k
```

For gain residuals the implementation uses the minimum-norm two-parameter
projection

```text
[delta_Kp*, delta_Ki*]
  = -delta_u*_k * [e_k, I_k] / (e_k^2 + I_k^2 + 1e-9)
```

The joint target is `[0.5 * delta_u*, -0.5 * delta_Kp*,
-0.5 * delta_Ki*]`. Complete episodes, rather than adjacent timesteps, are
assigned to train and test sets to prevent temporal leakage.

## Reported metrics

For the held-out tail `T = {k >= floor(0.8 * N)}`, true-force RMSE is

```text
RMSE_true = sqrt(mean_(k in T) (F_k - F*_k)^2) [N]
```

The companion measured-force RMSE replaces `F_k` with `Fhat_k`; tail absolute
error is `mean_(k in T) abs(F_k - F*_k)`. Safety reporting additionally keeps
maximum penetration, peak force, contact-loss rate, maximum applied command,
and safety-gate activations. Matrix comparisons use paired residual-minus-PI
deltas and deterministic bootstrap intervals; a small metric improvement is
not promoted to a general or sim-to-real claim.

## Interface traceability

| Quantity | Code/config source | Contract field |
| --- | --- | --- |
| `dt`, fast rate, `M` | `configs/two_rate_residual.yaml` | `timing.simulator_step_s`, `fast_controller_hz`, `action_hold_steps` |
| force and velocity features | `src/two_rate_residual.py::_features` | `observations` in `configs/platform_neutral_interface.yaml` |
| command range | `_pi_control`, `run_two_rate` | `actions.range` |
| penetration and force gates | `run_two_rate` | `limits.penetration_m`, `limits.total_contact_force_n` |
| hardware boundary | experiment/proposal records | `safety.hardware_commands_enabled: false` |

