# Scenario — current tensor backends need device/dtype receipts

`candle` documents `Cpu`, `Cuda`, and `Metal` devices and a device-sensitive BF16 default helper.
That makes runtime device and default-dtype posture part of the support surface, not an incidental implementation detail.
