'''

import os
from qiskit_ibm_runtime import QiskitRuntimeService

QiskitRuntimeService.save_account(
    channel="ibm_quantum_platform",
    token=os.environ["IBM_TOKEN"],
    overwrite=True
)


from qiskit import QuantumCircuit, transpile  # ← missing, you use both
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
import function

# Load credentials and pick backend
service = QiskitRuntimeService()
backend = service.least_busy(operational=True, simulator=False)
print(f"Running on: {backend.name}")

# Build the circuit
n_qubits = 6
solution_indices = [31]

qc = QuantumCircuit(n_qubits, n_qubits)
function.full_grover(qc, solution_indices, n_qubits)

# Transpile for real hardware
qc_transpiled = transpile(qc, backend)

# Submit
sampler = Sampler(backend)  # ← was SamplerV2, but you aliased it as Sampler
job = sampler.run([qc_transpiled], shots=2**11)

print(f"Job ID: {job.job_id()}")
print("Submitted!")
'''

from qiskit_ibm_runtime import QiskitRuntimeService

service = QiskitRuntimeService()
job = service.job("YOUR_JOB_ID_HERE")
print(f"Status: {job.status()}")

if job.status().name == "DONE":
    result = job.result()
    pub_result = result[0].data.meas.get_counts()
    for state, count in sorted(pub_result.items(), key=lambda x: -x[1]):
        bar = "█" * (count // 20)
        print(f"|{state}> : {count:4d} {bar}")