# rev0055 router shift stress

This experiment stress-tests the rev0054 row-adaptive attention router under
support-regime shift. The negative control calibrates thresholds only on low
support/easy rows, then evaluates on high-support rows. The repair is a
bucket-robust calibration rule that must satisfy the quality floor separately on
low, middle, and high support calibration slices while minimizing worst-slice
work.

The trace source is still the tiny trained transformer trace generator. This is
not public/pretrained trace evidence and not GPU/fused-kernel timing.
