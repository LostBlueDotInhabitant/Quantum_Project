import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from qiskit.visualization import plot_histogram
from qiskit.quantum_info import Statevector
from qiskit.visualization import plot_bloch_multivector
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.circuit.library import ZGate, HGate, XGate, SGate, TGate, IGate
import math

import numpy as np
import pylatexenc
import function
import time

st.title("Quantum Circuit Modeling")

# ── create 3 tabs ────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["Introduction", "Circuit Simulator", "Local Simulation of Grover's Algorithm", "Implementation"])

with tab1:
    st.header("Introduction")

    # text
    
    st.markdown("Feel free to explore this app. Please note that bugs may exist.")

    

with tab2:
    st.header("Quantum Circuit Simulator")
    n_qubits = st.slider("Number of qubits", min_value=2, max_value=8, value=6, key = "Simulator")
    if "reset_gates" not in st.session_state:
        st.session_state.reset_gates = False
    st.subheader("Single-qubit gates")
    st.info(
        "Type gate names separated by spaces for each qubit wire. "
        "Repeat gates as many times as you like. "
        "Invalid entries are ignored.\n\n"
        "**Available gates:**\n"
        "- `H` — Hadamard\n"
        "- `X` — Pauli X (bit flip)\n"
        "- `Y` — Pauli Y (imaginary bit flip)\n"
        "- `Z` — Pauli Z (phase flip)\n"
        "- `S` — S gate (π/2 phase)\n"
        "- `T` — T gate (π/4 phase)\n"
        "- `I` — Identity (spacing)\n\n"
        "**Example:** `H X H Z H` applies those gates left to right on that wire."
    )



    
    
    if "cnots" not in st.session_state:
        st.session_state.cnots = []   # ← this line creates it

    left, right = st.columns([1, 2])  # left column narrower than right

    with left:
        st.subheader("Gates")
        st.caption("Select gates for each qubit wire — order matters")

        # allowing you to input text to select gates
        VALID_GATES = {"H", "X", "Y", "Z", "S", "T", "I"}
        wire_gates = {}
        if st.session_state.reset_gates:
            for q in range(n_qubits):
                key = f"wire_{q}"
                if key in st.session_state:
                    st.session_state[key] = ""   # Clear the stored value
            st.session_state.reset_gates = False

        for q in range(n_qubits):
            raw = st.text_input(
                f"q{q}",
                value="",
                placeholder="e.g. H X H Z",
                key=f"wire_{q}"
            )
            wire_gates[q] = [g.upper() for g in raw.split() if g.upper() in VALID_GATES]
        
        st.subheader("Multi-qubit gates")
        #takes in user input
        max_steps = max((len(gates) for gates in wire_gates.values()), default=0)
        cnot_type = st.selectbox("Type of multi-qubit gate", options=["CNOT", "CZ"], index=0) 
        cnot_control = st.multiselect("CNOT control", options=list(range(n_qubits)), default=[0])
        cnot_target  = st.number_input("CNOT target",  0, n_qubits - 1, 1, key="cnot_tgt")
        cnot_step    = st.number_input("At step (column)", 0, max(max_steps, 10), 0, key="cnot_step")

        col_add, col_clear = st.columns(2)

        with col_add: #adding button
            if st.button("Add MultiQubit Gate"):
                if cnot_target in cnot_control:
                    st.error("Control and target must be different qubits")
                else:
           
                     st.session_state.cnots.append((cnot_type, cnot_control, cnot_target, int(cnot_step)))
        with col_clear: #clear button  
            if st.button("Clear All Gates"):
                st.session_state.reset_gates = True
                st.session_state.cnots.clear()

                
                st.rerun()
                
                

    if st.session_state.cnots: #writes what is queued
            st.caption("Queued multi-qubit gates:")
            for i, (gate_type, ctrl, tgt, step) in enumerate(st.session_state.cnots):
                st.caption(f"  {i+1}. {gate_type} q{ctrl} → q{tgt} at step {step}")
    
    
    

    with right:
        st.subheader("Circuit")

        # build circuit from selections
        # interleave gate steps across wires so they appear in columns
        qc = QuantumCircuit(n_qubits, n_qubits)

        # find the max number of gates on any wire
        max_steps = max((len(gates) for gates in wire_gates.values()), default=0)

        # apply gates step by step across all wires
        for step in range(max_steps+1):
            for q in range(n_qubits):
                if step < len(wire_gates[q]):
                    gate = wire_gates[q][step]
                    if gate == "H": qc.h(q)
                    elif gate == "X": qc.x(q)
                    elif gate == "Y": qc.y(q)
                    elif gate == "Z": qc.z(q)
                    elif gate == "S": qc.s(q)
                    elif gate == "T": qc.t(q)
                    elif gate == "I": qc.id(q)
            for (gate_type, ctrl, tgt, s) in st.session_state.cnots:
                if s == step:

                    if gate_type == "CNOT":
                        qc.append(XGate().control(len(ctrl)), ctrl + [tgt])
                    elif gate_type == "CZ":
                        qc.append(ZGate().control(len(ctrl)), ctrl + [tgt])
        qc.barrier()
        qc.measure(list(range(n_qubits)), list(range(n_qubits)))
        fig = qc.draw('mpl')
        fig.set_size_inches(6, 3.75)
        st.pyplot(fig, use_container_width=False)
        plt.close(fig)


        if st.button("Run Circuit"):
            st.markdown("Statevector probabilities:")
            function.present_statevectorProb(qc)
            st.markdown("Experimental counts:")
            st.write("Random classical error is expected. Furthermore, optimal Grover iterations might not be a whole number. This leads to some non-solution states registering counts. ")
            function.runsimulator(qc)
            
            

with tab3:
    st.header("Parameters for Grover's Algorithm")
    st.write(
    """Note that some of these operations might be slow to run, especially for more qubits and iterations.
             """)

    # slider
    n_qubits = st.slider("Number of qubits", min_value=2, max_value=8, value=6)

    

   

    # multiselect
    solutions = st.multiselect("Solution indices", options=list(range(2**n_qubits)), default=[0, 2**n_qubits-1])

    # checkbox
    #show_circuit = st.checkbox("Show circuit diagram", value=True)
     # create and run the circuit
    qc = QuantumCircuit(n_qubits, n_qubits)
    qc_copy= qc.copy() # for animation, so we can keep the original circuit clean of oracle/diffusion gates


    # button — code inside only runs when clicked
    if st.checkbox("Run algorithm", value = False):
        st.header("Results")
        st.success(f"Running Grover's on {n_qubits} qubits targeting index {solutions}")


       
        function.full_grover(qc, solutions, n_qubits)
        #st.markdown("Pure Statevector")
        #function.present_statevectorPure(qc)
        st.markdown("Statevector probabilities:")
        function.present_statevectorProb(qc)
        st.markdown("Experimental counts:")
        st.write("Random classical error is expected. This leads to some none solution states registering counts")
        function.runsimulator(qc)
        st.markdown("Circuit diagram:")
        function.present_circuit(qc)
        




    if st.checkbox("Run probability statevector animation", value = False):
        
        st.header("Animation")
        function.run_animation_prob(qc_copy, n_qubits, solutions, delay=0.8)
    
    if st.checkbox("Run pure statevector animation", value = False):
        st.header("Animation")
        function.run_animation_amp(qc_copy, n_qubits, solutions, delay=0.8)
    


    # display current values so you can see them updating live
    st.write(f"Current settings: {n_qubits} qubits, solution indices: {solutions}")

with tab4:

    st.header("IBM Simulation")
    st.markdown(
    """If time is on our side
    """)

