"""
Creates partly using an LLM 
so as to avoid having to write 
everything manually and for getting appealing visuals
"""

#will need to also display as qiskit circuit diagram

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from qiskit import QuantumCircuit
from qiskit.circuit.library import GroverOperator
from qiskit.quantum_info import Statevector

# ── Config ────────────────────────────────────────────────────────────────────
N_QUBITS    = 6
N           = 2 ** N_QUBITS          # 64 states
MAX_ITER    = 20                      # how many Grover steps to animate through
SOLUTION    = N - 1                   # index 63  →  |111111⟩ in little-endian

# ── Build oracle that phase-flips |111111⟩ ────────────────────────────────────
# A multi-controlled-Z on all 6 qubits flips the phase of |111111⟩ only.
oracle = QuantumCircuit(N_QUBITS)
oracle.h(N_QUBITS - 1)               # convert last qubit CX → CZ trick
oracle.mcx(list(range(N_QUBITS - 1)), N_QUBITS - 1)   # multi-controlled X
oracle.h(N_QUBITS - 1)

# ── Build the full Grover operator (oracle + diffusion) ───────────────────────
grover_op = GroverOperator(oracle)

# ── Simulate: collect probability of |solution⟩ after each iteration ─────────
probabilities    = []
all_distributions = []       # full probability distribution at each step

for i in range(1, MAX_ITER + 1):
    qc = QuantumCircuit(N_QUBITS)
    qc.h(range(N_QUBITS))           # uniform superposition  |ψ⟩

    for _ in range(i):
        qc.compose(grover_op, inplace=True)

    sv   = Statevector(qc)
    amps = sv.data                   # complex amplitudes, length 64

    # Qiskit uses little-endian bit ordering:
    # state index k  ↔  basis string bin(k) read right-to-left
    prob_solution = abs(amps[SOLUTION]) ** 2
    probabilities.append(prob_solution)
    all_distributions.append(np.abs(amps) ** 2)

    print(f"Iter {i:2d}  |  P(solution) = {prob_solution:.4f}")

optimal_iter = int(np.argmax(probabilities)) + 1
print(f"\nOptimal iterations: {optimal_iter}  (theoretical ≈ {np.pi/4 * np.sqrt(N):.1f})")

# ── Animation ─────────────────────────────────────────────────────────────────
fig, (ax_top, ax_bot) = plt.subplots(
    2, 1, figsize=(12, 8),
    gridspec_kw={"height_ratios": [1, 2]}
)
fig.patch.set_facecolor("#0d0d1a")
for ax in (ax_top, ax_bot):
    ax.set_facecolor("#0d0d1a")

# ── Top panel: solution probability vs iteration ──────────────────────────────
iters = np.arange(1, MAX_ITER + 1)
ax_top.plot(iters, probabilities, color="#00d4ff", linewidth=1.5, alpha=0.4)
sol_dot,   = ax_top.plot([], [], "o", color="#00d4ff", markersize=8)
trail_line, = ax_top.plot([], [], color="#00d4ff", linewidth=2)
ax_top.axvline(optimal_iter, color="#ff6b6b", linestyle="--", linewidth=1,
               label=f"optimal = {optimal_iter}")
ax_top.set_xlim(0.5, MAX_ITER + 0.5)
ax_top.set_ylim(-0.05, 1.05)
ax_top.set_xlabel("Grover Iterations", color="#aaaacc")
ax_top.set_ylabel("P(|111111⟩)", color="#aaaacc")
ax_top.set_title("Solution Probability Over Iterations", color="white", fontsize=13)
ax_top.tick_params(colors="#aaaacc")
ax_top.legend(facecolor="#1a1a2e", labelcolor="white")
for spine in ax_top.spines.values():
    spine.set_edgecolor("#333355")

# ── Bottom panel: full amplitude distribution ─────────────────────────────────
x = np.arange(N)
bars = ax_bot.bar(x, all_distributions[0], color="#4444aa", width=0.9)
sol_bar = bars[SOLUTION]
sol_bar.set_color("#00d4ff")

ax_bot.set_xlim(-1, N)
ax_bot.set_ylim(0, 1.05)
ax_bot.set_xlabel("Basis State Index", color="#aaaacc")
ax_bot.set_ylabel("Probability", color="#aaaacc")
iter_title = ax_bot.set_title("Iteration 1 — Amplitude Distribution", color="white", fontsize=13)
ax_bot.tick_params(colors="#aaaacc")
for spine in ax_bot.spines.values():
    spine.set_edgecolor("#333355")

# mark the solution index on x-axis
ax_bot.axvline(SOLUTION, color="#ff6b6b", linestyle="--", linewidth=0.8, alpha=0.6)
ax_bot.text(SOLUTION + 0.5, 0.95, "|111111⟩", color="#ff6b6b", fontsize=8)

fig.tight_layout(pad=2)

def update(frame):
    i = frame          # 0-indexed → iteration = frame+1
    dist = all_distributions[i]

    # update bars
    for bar, h in zip(bars, dist):
        bar.set_height(h)
    bars[SOLUTION].set_color("#00d4ff")

    # update top panel trail
    trail_line.set_data(iters[:i+1], probabilities[:i+1])
    sol_dot.set_data([iters[i]], [probabilities[i]])

    iter_title.set_text(
        f"Iteration {i+1}  —  P(solution) = {probabilities[i]:.4f}"
    )
    return list(bars) + [sol_dot, trail_line, iter_title]

ani = animation.FuncAnimation(
    fig, update,
    frames=MAX_ITER,
    interval=600,       # ms between frames
    blit=False,
    repeat=True
)

plt.show()

