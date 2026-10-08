# CELL-317 — Tiny Copy-Head Trained Escalation

Priority: P0

Status: coded-trained-smoke

Question: Does a minimal trained pointer-copy model show different emergence smoothness and speed across softmax, sparsemax, relu-normalized, and cosine/no-exp attention?

Cheap first run: Run experiments/tiny_copy_head_training/tiny_copy_head_train.py; inspect REV0032_TINY_COPY_HEAD_TRAINING_SMOKE.json/csv.

Metrics: mean_final_acc, reached95_step, max_dacc_per_step, transition_width_steps, target_mass, entropy

Required baselines: softmax, sparsemax, relu_norm, cosine_relu

Stop condition: Promote to hardening only if curves differ across seeds and longer-context variants; otherwise revise the task.
