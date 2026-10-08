# Scout notes — rev0029

This turn stays performance-core. Fresh sources added: Meta-Attention, Avey/Don't Pay Attention, null-expert data sparsity, MoE expert-wise mixed precision, low-resource MoE routing collapse, edge transformer survey, and transformer-vs-SSM copying guard.

Key idea: spectral/operator routing is interesting only after actual transforms and alias/copy traps. The new C++ probe uses tiny DCT/IDCT, top-k attention, local windows, and hybrid residual repair.

New questions emphasize candidate-set recall, false-skip/rare-miss, route collapse, and exact copying as promotion guards.
