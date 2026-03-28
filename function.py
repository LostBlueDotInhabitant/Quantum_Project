from qiskit.quantum_info import Statevector
from qiskit.visualization import plot_histogram
from qiskit import transpile
from qiskit_aer import AerSimulator
from qiskit.circuit.library import ZGate
import pylatexenc
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import time
import math

def present_run(qc):
    
    #statevector probabilities
    qc_sv = qc.copy()
    qc_sv.remove_final_measurements(inplace=True)
    sv = Statevector(qc_sv)
    probs = np.abs(sv.data) ** 2

    fig, ax = plt.subplots(figsize=(14, 4))
    ax.bar(range(len(probs)), probs, color='steelblue', width=0.8)
    ax.set_xlabel('Basis state index')
    ax.set_ylabel('Probability')
    ax.set_title('Statevector probabilities')
    ax.set_xticks(range(0, len(probs), 4))
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
   

    # experimental counts
    from qiskit import transpile
    simulator = AerSimulator()
    compiled = transpile(qc, simulator)
    job = simulator.run(compiled, shots=2**8)
    counts = job.result().get_counts()
    
    st.pyplot(plot_histogram(counts))
    st.pyplot(qc.draw('mpl'))

    print("Done")

def present_statevectorProb(qc):
    qc_sv = qc.copy()
    qc_sv.remove_final_measurements(inplace=True)
    sv = Statevector(qc_sv)
    probs = np.abs(sv.data) ** 2

    fig, ax = plt.subplots(figsize=(14, 4))
    ax.bar(range(len(probs)), probs, color='steelblue', width=0.8)
    ax.set_xlabel('Basis state index')
    ax.set_ylabel('Probability')
    ax.set_title('Statevector probabilities')
    ax.set_xticks(range(0, len(probs), 4))
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

def present_statevectorPure(qc):
    qc_sv = qc.copy()
    qc_sv.remove_final_measurements(inplace=True)
    sv = Statevector(qc_sv)
    probs = sv.data

    fig, ax = plt.subplots(figsize=(14, 4))
    ax.bar(range(len(probs)), probs, color='steelblue', width=0.8)
    ax.set_xlabel('Basis state index')
    ax.set_ylabel('Probability')
    ax.set_title('Statevector probabilities')
    ax.set_xticks(range(0, len(probs), 4))
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
def runsimulator(qc, n = 2**12):

    try:
        simulator = AerSimulator()
        compiled = transpile(qc, simulator)
        job = simulator.run(compiled, shots=n)
        counts = job.result().get_counts()
        st.pyplot(plot_histogram(counts))
    except Exception as e:
        st.warning(f"Could not run circuit: {e}")
    
    
def present_circuit(qc):
    st.pyplot(qc.draw('mpl'))







def initialization(qc, n_qubits):
    # Apply Hadamard to all qubits
    for i in range(n_qubits):
        qc.h(i)

def oracle_single(solution_index, qc, n_qubits):
    #Important to note that for qiskit: the upper most qubit (le least significant)
    # is placed at the extreme right in brac ket notation ex: |q1 q0> where q0 is top and q1 is bottom
    # index 1 = |00>, index 2 = |01>, index 3 = |10>, index 4 = |11>
    # 6 qubits can have up to 64 = 2^6 possible states
    # We will denote this as going from position 0 to position 63
    
    # Also, note that there is only one solution here, not multiple
    
    # Convert index to binary string, then flips it to that the top qubit is on the left
    bits = format(solution_index, f'0{n_qubits}b')[::-1]  

    # Step 1: X on every qubit whose bit is '0'
    zero_qubits = [i for i, b in enumerate(bits) if b == '0'] #Index of 0 qubits
    if zero_qubits:
        qc.x(zero_qubits) #applies X to all qubits in zero_qubits list

    # Step 2: multi-controlled Z (CZ) 
    # Fires only on |111111⟩
    # clean multi-controlled Z — no H trick needed
    qc.append(ZGate().control(n_qubits - 1), list(range(n_qubits)))

    #Reapply X to original "0"
    if zero_qubits:
        qc.x(zero_qubits)

def oracle_multi( solution_indices, qc, n_qubits):
    
    #Applies oracle_single once per solution — this stacks
    
    for index in solution_indices:
        oracle_single(index, qc, n_qubits)    

def diffusion_operator(qc, n_qubits,):
    # Apply Hadamard to all qubits

   
    for i in range(n_qubits):
        qc.h(i)
    for i in range(n_qubits):
        qc.x(i)

    qc.append(ZGate().control(n_qubits - 1), list(range(n_qubits)))

    for i in range(n_qubits):
        qc.x(i)
    for i in range(n_qubits):
        qc.h(i)
    
def full_grover(qc, solution_indices, n_qubits):

    import math
    
    initialization(qc, n_qubits)
    iterations = round(math.pi*math.sqrt(2**n_qubits/len(solution_indices))/4)
    qc.barrier()

    for i in range(iterations):
        oracle_multi(solution_indices, qc, n_qubits)
        qc.barrier()
        diffusion_operator(qc, n_qubits)
        qc.barrier()
    
    qc.measure(list(range(n_qubits)), list(range(n_qubits)))


def run_animation_prob(qc_base, n_qubits, solutions, delay=0.5):
    """
    qc_base     — circuit with only initialization (no oracle/diffusion yet)
    n_qubits    — number of qubits
    solutions   — list of solution indices
    iterations  — number of grover iterations to animate through
    delay       — seconds between frames
    """
    iterations = round(math.pi*math.sqrt(2**n_qubits/len(solutions))/4)


    N = 2 ** n_qubits

    # ── precompute all distributions first ───────────────────────────────────
    all_distributions = []
    probabilities = []


    qc = qc_base.copy()
    initialization(qc, n_qubits)
    sv = Statevector(qc)
   
    probs = np.abs(sv.data) ** 2
    all_distributions.append(probs)
    probabilities.append(sum(probs[s] for s in solutions))
    for i in range(1, iterations*2 + 1):
        qc = qc_base.copy()
        initialization(qc, n_qubits)
        for _ in range(i):
            oracle_multi(solutions, qc, n_qubits)
            diffusion_operator(qc, n_qubits)

        sv = Statevector(qc)
        probs = np.abs(sv.data) ** 2
       
        all_distributions.append(probs)
        probabilities.append(sum(probs[s] for s in solutions))

    # ── layout: two placeholders ──────────────────────────────────────────────
    st.markdown("### Probability Evolution")
    top_placeholder = st.empty()    # top chart — solution probability over time
    bot_placeholder = st.empty()    # bottom chart — full distribution

    iters = np.arange(0, iterations*2 + 1)

    # ── animate ───────────────────────────────────────────────────────────────
    while True:
        for i in range(iterations*2+1):
            fig, (ax_top, ax_bot) = plt.subplots(
                2, 1, figsize=(12, 8),
                gridspec_kw={"height_ratios": [1, 2]}
            )
            fig.patch.set_facecolor("#0d0d1a")
            for ax in (ax_top, ax_bot):
                ax.set_facecolor("#0d0d1a")

            # top panel ──
            ax_top.plot(iters, probabilities, color="#00d4ff", linewidth=1.5, alpha=0.3)
            ax_top.plot(iters[:i+1], probabilities[:i+1], color="#00d4ff", linewidth=2)
            ax_top.plot(iters[i], probabilities[i], "o", color="#00d4ff", markersize=8)
            ax_top.set_xlim(0.5, iterations*2 + 0.5)
            ax_top.set_ylim(-0.05, 1.05)
            ax_top.set_xlabel("Grover Iterations", color="#aaaacc")
            ax_top.set_ylabel("P(solution)", color="#aaaacc")
            ax_top.set_title("Solution Probability Over Iterations", color="white", fontsize=13)
            ax_top.tick_params(colors="#aaaacc")
            for spine in ax_top.spines.values():
                spine.set_edgecolor("#333355")

            # bottom panel ──
            dist = all_distributions[i]
            colors = ["#00d4ff" if idx in solutions else "#4444aa" for idx in range(N)]
            ax_bot.bar(range(N), dist, color=colors, width=0.9)
            ax_bot.set_xlim(-1, N)
            ax_bot.set_ylim(0, 1.05)
            ax_bot.set_xlabel("Basis State Index", color="#aaaacc")
            ax_bot.set_ylabel("Probability", color="#aaaacc")
            ax_bot.set_title(
                f"Iteration {i+1}  —  P(solution) = {probabilities[i]:.4f}",
                color="white", fontsize=13
            )
            ax_bot.tick_params(colors="#aaaacc")
            for spine in ax_bot.spines.values():
                spine.set_edgecolor("#333355")

            # mark solution indices
            for s in solutions:
                ax_bot.axvline(s, color="#ff6b6b", linestyle="--", linewidth=0.8, alpha=0.6)

            fig.tight_layout(pad=2)

           
            top_placeholder.pyplot(fig)
            plt.close(fig)

            time.sleep(delay)


def run_animation_amp(qc_base, n_qubits, solutions, delay=0.5):
    iterations = round(math.pi * math.sqrt(2**n_qubits / len(solutions)) / 4)
    N = 2 ** n_qubits

    # ── precompute: store real amplitudes (signed) not probabilities ──────────
    all_amplitudes = []   # real part of amplitude — can be negative after oracle
    probabilities  = []
    labels         = []

    qc = qc_base.copy()
    initialization(qc, n_qubits)

    def snapshot(label):
        sv = Statevector(qc)
        amps = np.real(sv.data)          # real part — shows negative phase
        prob = float(sum(np.abs(sv.data[s])**2 for s in solutions))
        all_amplitudes.append(amps)
        probabilities.append(prob)
        labels.append(label)

    snapshot("Initial superposition")

    for i in range(1, iterations * 2 + 1):
        oracle_multi(solutions, qc, n_qubits)
        snapshot(f"Iteration {i} — after oracle (phase flip)")

        diffusion_operator(qc, n_qubits)
        snapshot(f"Iteration {i} — after diffusion (amplification)")

    total_frames = len(all_amplitudes)
    frame_indices = np.arange(total_frames)

    st.markdown("### Amplitude Evolution")
    top_placeholder = st.empty()

    while True:
        for i in range(total_frames):
            amps = all_amplitudes[i]
            mean_amp = np.mean(amps)      # mean amplitude for horizontal line

            fig, (ax_top, ax_bot) = plt.subplots(
                2, 1, figsize=(12, 8),
                gridspec_kw={"height_ratios": [1, 2]}
            )
            fig.patch.set_facecolor("#0d0d1a")
            for ax in (ax_top, ax_bot):
                ax.set_facecolor("#0d0d1a")

            # ── top panel — solution probability trace ────────────────────────
            ax_top.plot(frame_indices, probabilities, color="#00d4ff", linewidth=1.5, alpha=0.3)
            ax_top.plot(frame_indices[:i+1], probabilities[:i+1], color="#00d4ff", linewidth=2)
            ax_top.plot(frame_indices[i], probabilities[i], "o", color="#00d4ff", markersize=8)
            ax_top.set_xlim(-0.5, total_frames - 0.5)
            ax_top.set_ylim(-0.05, 1.05)
            ax_top.set_xlabel("Step", color="#aaaacc")
            ax_top.set_ylabel("P(solution)", color="#aaaacc")
            ax_top.set_title("Solution Probability", color="white", fontsize=13)
            ax_top.tick_params(colors="#aaaacc")
            for spine in ax_top.spines.values():
                spine.set_edgecolor("#333355")

            # ── bottom panel — signed amplitudes ──────────────────────────────
            colors = ["#00d4ff" if idx in solutions else "#4444aa" for idx in range(N)]
            ax_bot.bar(range(N), amps, color=colors, width=0.9)

            # mean line
            ax_bot.axhline(mean_amp, color="#ffcc00", linewidth=1.5,
                           linestyle="--", label=f"mean = {mean_amp:.4f}")
            ax_bot.legend(facecolor="#1a1a2e", labelcolor="white", fontsize=9)

            # zero line so it's clear where negative starts
            ax_bot.axhline(0, color="#ffffff", linewidth=0.5, alpha=0.3)

            # y axis needs to accommodate negative values
            amp_max = max(np.max(np.abs(amps)) * 1.15, 0.1)
            ax_bot.set_xlim(-1, N)
            ax_bot.set_ylim(-amp_max, amp_max)
            ax_bot.set_xlabel("Basis State Index", color="#aaaacc")
            ax_bot.set_ylabel("Amplitude", color="#aaaacc")
            ax_bot.set_title(
                f"{labels[i]}  —  P(solution) = {probabilities[i]:.4f}",
                color="white", fontsize=13
            )
            ax_bot.tick_params(colors="#aaaacc")
            for spine in ax_bot.spines.values():
                spine.set_edgecolor("#333355")

            for s in solutions:
                ax_bot.axvline(s, color="#ff6b6b", linestyle="--",
                               linewidth=0.8, alpha=0.6)

            fig.tight_layout(pad=2)
            top_placeholder.pyplot(fig)
            plt.close(fig)
            time.sleep(delay)