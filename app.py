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

# create 3 tabs 
tab1, tab2, tab3, tab4 = st.tabs(["Introduction", "Circuit Simulator", "Local Simulation of Grover's Algorithm", "Observations"])

with tab1:
    st.header("Introduction")

    st.markdown("Feel free to explore this app. Please note that bugs may exist.")


    st.write("An implementing of Grover’s algorithm is constructed. Grover’s algorithm is a well-defined example of quantum amplitude amplification, reducing the search complexity of an unordered list from O(N) to O(√N) operations. Modern applications of this algorithm look to connect theoretical quantum principles with scalable, real-world implementations in fields like cybersecurity, cryptography, and economics. Essentially, any problem that can be reduced to finding solutions in an unordered list can have its runtime greatly improved.")

    st.write("The first step is the initialization step, which is applied only once at the beginning of the circuit. It is an application of a Hadamard (H) gate to every initially ∣0⟩ qubit of the circuit. This produces the equal superposition state, which is important because it gives every possible basis state the same starting amplitude. As a result, no state is privileged at the beginning of the search ")

    st.write("The second step is the oracle. The oracle step marks the desired state by flipping its phase. If x* is the target solution, then the oracle applies O|x⟩ = {-|x⟩, x = x*}. This operation distinguishes the solution state(s) from the others by flipping its sign but does not increase its probability to be measured. The proper state is flipped by the use of select X gates sandwiching a CZ gate applied to all qubits. If multiple solution states exist, the respective Oracle of each solution state is applied sequentially")
    
    st.write("The final step is the diffusion operator. This operator is often described as a reflection about the mean. Essentially, after oracle has made the solution state negative compared to others, then the diffusion step comes and reflects all the amplitudes around the average value. As a result, the flipped negative amplitude grows while the positive ones decrease. When applied to a circuit, the diffusion operator can be understood as a series of gates. Starting with the Hadamard gate to all qubits, followed by the X gates to all qubits, and then a CZ gate to all qubits before reversing the first two steps. Thus, in the circuit demonstration, the complete sequence is H gate, X gate, CZ gate, then X gate and H gate. By design of the H gate, its application to all qubits leads to the singular all-zero multi-qubit state |0000...⟩ coefficient being the sum of all input state amplitudes, divided by √(2ⁿ). Then, similar to the Oracle, X gate application to all qubits followed by an application of the CZ and another application of X gates to all qubits leads to the same |0000...⟩ state having its phase flipped to negative. This flips all the coefficients of |0000...⟩ to negative except the already negative solution state coefficient which now becomes positive. A final application of H gates to all qubits finally returns the coefficients to their respective states, thus subtracting amplitude from non-solution states and adding amplitude to solution states ")

    st.write("The Oracle and Diffusion Operator are repeated one after the other for a number of optimal iterations π/4(√(N/M)) where N = 2n and M[RW1.1] is the number of solutions. The amplitude of the desired state(s) becomes large enough that when measured, the probability is close to 1. In sum, Grover’s algorithm demonstrates how quantum computation can solve the unstructured search problem exponentially faster than classical computing. ")
    
    st.subheader("Logic Display")
    st.info(
        "Given a two-qubit circuit where the solution state is |11⟩. The following represents one iteration of the diffusion operator:"
        "Starting state (after initialization and oracle):\n\n"

        "ψ⟩ = 1/2(|00⟩ + |01⟩ + |10⟩ - |11⟩), |1/2|² = ¼ probability of measuring |11⟩\n\n"

        "Step 1 - Apply H gates:\n\n"
        "|ψ⟩ = 1/2|00⟩ + 1/2|01⟩ + 1/2|10⟩ - 1/2|11⟩\n\n"
        "Step 2 - Apply X gates (bit flip every state):\n\n"
        "|ψ⟩ = 1/2|11⟩ + 1/2|10⟩ + 1/2|01⟩ - 1/2|00⟩\n\n"
        "Step 3 - Apply CZ (phase flip |111⟩ only):\n\n"
        "|ψ⟩ = -1/2|11⟩ + 1/2|10⟩ + 1/2|01⟩ - 1/2|00⟩\n\n"
        "Step 4 - Apply X gates again:\n\n"
        "|ψ⟩ = -1/2|00⟩ + 1/2|01⟩ + 1/2|10⟩ - 1/2|11⟩\n\n"
        "Step 5 - Apply H gates again:\n\n"
        "|ψ⟩ = -|11⟩, P (|11⟩) = |1|² = 1\n\n"

        


    )





















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
        " Note that single-qubit gates are by default applied before multi-qubit gates when they are on the same step/column."
    )



    
    
    if "cnots" not in st.session_state:
        st.session_state.cnots = []   

    left, right = st.columns([1, 2])  

    with left:
        st.subheader("Gates")
        st.caption("Select gates for each qubit wire - order matters")

        # input text to select gates
        VALID_GATES = {"H", "X", "Y", "Z", "S", "T", "I"}
        wire_gates = {}
        if st.session_state.reset_gates:
            for q in range(n_qubits):
                key = f"wire_{q}"
                if key in st.session_state:
                    st.session_state[key] = ""   # Clear values
            st.session_state.reset_gates = False

        for q in range(n_qubits):
            raw = st.text_input(
                f"q{q}",
                value="",
                placeholder="e.g. H X H Z",
                key=f"wire_{q}"
            )
            wire_gates[q] = []
            for g in raw.split():
                if g.upper() in VALID_GATES:
                    wire_gates[q].append(g.upper())
        
        st.subheader("Multi-qubit gates")
        #takes in user input
        max_steps = max((len(gates) for gates in wire_gates.values()), default=0)
        cnot_type = st.selectbox("Type of multi-qubit gate", options=["CNOT", "CZ"], index=0) 
        cnot_control = st.multiselect("CNOT control", options=list(range(n_qubits)), default=[0])
        cnot_target  = st.number_input("CNOT target",  0, n_qubits - 1, 1, key="cnot_tgt")
        cnot_step    = st.number_input("At step (column), can be used to manipulate horizontal placement. ", 0, max(max_steps, 10), 0, key="cnot_step")

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
                st.caption(f"  {i+1}. {gate_type} q{ctrl} → q{tgt} at step {step} ")
    
    
    

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
                    if gate == "H":
                        qc.h(q)
                    elif gate == "X":
                        qc.x(q)
                    elif gate == "Y":
                        qc.y(q)
                    elif gate == "Z":
                        qc.z(q)
                    elif gate == "S":
                        qc.s(q)
                    elif gate == "T":
                        qc.t(q)
                    elif gate == "I":
                        qc.id(q)
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
    
    if st.checkbox("Run amplitude statevector animation", value = False):
        st.header("Animation")
        function.run_animation_amp(qc_copy, n_qubits, solutions, delay=0.8)
    


    # display current values so you can see them updating live
    st.write(f"Current settings: {n_qubits} qubits, solution indices: {solutions}")

with tab4:

    st.header("Quantum Hardware Observations")
    st.markdown(
    """Some observations from running the algorithm on a simulator and real hardware:
    """)

    st.markdown("IBM Quantum Hardware Run")
    st.info(
    """The following results were obtained from running a 6-qubit Grover's algorithm targeting
       the index 31 on IBM's quantum hardware (5s). The results show a distribution of counts across
       various output states, with the target state |011111⟩ (index 31) having a count of only 28,
        this indicates that quantum noise overwhelmed the signal.
    """)
    dic  =  {'101011': 17, '010001': 47, '010101': 45, '011011': 19, '001101': 35, '011101': 41, '010111': 29, '001011': 16, '010011': 33, '100101': 46, '010100': 51, '001110': 25, '101101': 34, '000100': 41, '111101': 34, '000000': 37, '111000': 28, '100001': 31, '001100': 35, '101001': 27, '000001': 55, '011010': 19, '011100': 33, '011110': 36, '110111': 32, '010110': 29, '000101': 47, '111111': 14, '100011': 26, '011001': 29, '100110': 27, '001000': 48, '000111': 45, '000110': 37, '010010': 29, '110101': 43, '101010': 19, '111100': 31, '100000': 34, '110010': 33, '000010': 37, '101111': 32, '101100': 28, '001111': 39, '101110': 29, '110000': 37, '010000': 36, '110110': 35, '000011': 33, '001010': 32, '101000': 24, '011000': 32, '111001': 19, '111011': 21, '111010': 21, '011111': 28, '110001': 34, '100010': 24, '100100': 31, '110011': 25, '111110': 26, '100111': 30, '110100': 26, '001001': 32}
    plt.figure(figsize=(20,10), dpi = 500)
    plt.bar(dic.keys(), dic.values())
    plt.xticks(rotation=45)
    plt.xlabel("Output State")
    plt.ylabel("Counts")
    plt.title("Grover's Algorithm on IBM Quantum Hardware")
    plt.tight_layout()
    st.pyplot(plt)
    plt.close()

    st.info("Compare that to a local classical simulation with the same conditions""")

    qc = QuantumCircuit(6, 6)
    solution = [31]
    function.full_grover(qc, solution, 6)
    function.runsimulator(qc)

    st.info("""What about with lower qubit count? Here the target state  |0011⟩ (index 3)
               has a count of 1005, which is much higher than the other states.
               Noise is much less impactful!""")

    dic1 ={'0101': 71, '1110': 50, '0011': 1005, '0010': 123, '1100': 54, '0001': 107, '0000': 59, '1010': 72, '1101': 59, '1000': 50, '0111': 90, '1011': 82, '0110': 56, '0100': 57, '1001': 59, '1111': 54}
    plt.figure(figsize=(20,10), dpi = 500)
    plt.bar(dic1.keys(), dic1.values())
    plt.xticks(rotation=45)
    plt.xlabel("Output State")
    plt.ylabel("Counts")
    plt.title("Grover's Algorithm on IBM Quantum Hardware (4 qubits)")
    plt.tight_layout()
    st.pyplot(plt)
    plt.close()


    st.header("Local Runtime Comparison")
    st.info("At around 30 qubits, the runtime of the algorithm becomes unwieldly long")
    qubit_number = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30]
    times = [0.0002741276666711201, 0.00029606166663143085, 0.0020666406668775985, 0.00243305766677319, 0.0039748546666184366, 0.005584314000164643, 0.009959818000121837, 0.016104793333397538, 0.018074380666500172, 0.03041212066667261, 0.04446564800006551, 0.0712357786666568, 0.10542257966668937, 0.12172273399998328, 0.22150719599994773, 0.36013912266662373, 0.46439716800008074, 0.6175384059997668, 0.9728065699997993, 1.298776313333292, 1.9792713636667638, 2.732684305666529, 3.936768071333063, 5.659860478999993, 8.433960849666619, 11.907049907333507, 17.847063398333376, 25.34428467333358, 36.9916870650001]

    plt.figure(figsize=(10,6))
    plt.plot(qubit_number, times, marker='o')
    plt.xlabel("Number of Qubits")
    plt.ylabel("Time (seconds)")
    plt.title("Runtime of Grover's Algorithm Simulation")
    plt.xticks(qubit_number)
    plt.grid()
    st.pyplot(plt)
    plt.close()

