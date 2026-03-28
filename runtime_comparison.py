import time
import matplotlib.pyplot as plt
import function
from qiskit import QuantumCircuit
import numpy as np
max_qubit = 30
max_time  = 60
runs  =3
times = []
solution = [0]

for n in range(2, max_qubit + 1):
    qc = QuantumCircuit(n,n)
    start_time = time.perf_counter()
    for i in range(runs):
        function.full_grover(qc,solution, n)
    end_time = time.perf_counter()
    
    elapsed_time = (end_time - start_time)/runs
    times.append(elapsed_time)
    
    print(f"Qubits: {n}, {elapsed_time:.4f} seconds")
    
    if elapsed_time > max_time:
        print("Exceeded maximum time limit. Stopping.")
        break


plt.plot(range(2, max_qubit + 1), times)
plt.xlabel("Qubits")
plt.ylabel("Time (seconds)")
plt.title("Runtime Comparison")
plt.show()

print(list(range(2, max_qubit + 1)))
print(times)
