'''

import os
from qiskit_ibm_runtime import QiskitRuntimeService

QiskitRuntimeService.save_account(
    channel="ibm_quantum_platform",
    token=os.environ["IBM_TOKEN"],
    overwrite=True
)

'''
'''
from qiskit import QuantumCircuit, transpile  # ← missing, you use both
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
import function

# Load credentials and pick backend
service = QiskitRuntimeService()
backend = service.least_busy(operational=True, simulator=False)
print(f"Running on: {backend.name}")

# Build the circuit
n_qubits = 4
solution_indices = [3]

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

import json
from qiskit_ibm_runtime import QiskitRuntimeService

service = QiskitRuntimeService(
    channel='ibm_quantum_platform',
    instance='crn:v1:bluemix:public:quantum-computing:us-east:a/0ac8bb593dd741deaff8b4a1cd4e95fc:3ce300d1-2638-4276-89db-df84422ef186::'
)

job = service.job('placeholder')
job_result = job.result()

# Get counts — 'c' is the default register name for full_grover
pub_result = job_result[0].data.c.get_counts()
print(pub_result)

# Save to JSON
with open("C:\\Users\\albi\\Documents\\Dawson Accelerator\\Quantum Ready\\ibm_results.json", "w") as f:
    json.dump(pub_result, f)

print("Saved!")
