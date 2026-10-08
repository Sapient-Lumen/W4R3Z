# Rematch worlds should price higher exact uncertainty guarantees by lost dwell freedom, not just cap and checkpoints

The current exact compact repeat-state uncertainty menu already has clean cap and checkpoint pricing, but implementors can still miss the third real operating cost: **dwell freedom**. Tightening the guaranteed preserved-gain floor removes whole certified dwell regions.

The saved exact menu now supports a sharper rule:

- exact `0.95` is the **last** tier with continuous non-precision dwell freedom;
- tightening `0.85 -> 0.95` deletes the relaxed suffix `[19, 32]`, losing `14` live dwell targets while buying `+0.109999` certified floor;
- tightening `0.95 -> 0.99` deletes the surviving non-precision band `[8, 18]`, losing `11` of the remaining `12` live dwell targets for only `+0.019341` more floor;
- so the jump from exact `0.95` to exact `0.99` is not merely a higher-cap or larger-checkpoint move; it is a near-total collapse of retuning freedom.

That makes exact `0.95` more than the current cap knee. It is also the **dwell-freedom knee**. Any deployment that still values continuous non-precision retuning should treat exact `0.95` as the ceiling unless a requirement above floor `0.980481` genuinely forces the singleton precision point at dwell `2`.
