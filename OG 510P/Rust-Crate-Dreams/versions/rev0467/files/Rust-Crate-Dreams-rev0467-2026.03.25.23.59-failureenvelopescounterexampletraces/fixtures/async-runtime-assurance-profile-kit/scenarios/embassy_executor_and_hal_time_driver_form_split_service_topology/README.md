# Scenario: Embassy executor and HAL time driver form a split service topology

This scenario exists to stop another common flattening move:

> “Embassy provides one flat runtime service surface.”

In practice, the executor, timer queue route, and HAL time-driver activation can be separate truths.
The example topology keeps spawning and time provision distinct so a reviewer can see which piece is actually carrying the capability.
