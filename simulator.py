import itertools
import sympy
import cmath
from collections import defaultdict

def int_to_bstring(n, b):
    if n == 0:
        return "0"
    result = ""
    while n:
        result += str(n % b)
        n //= b
    return result[::-1]

class Simulator:
    def __init__(self, num_qudits, circuit=[], qudit=2, init_state={0: 1}):
        self.num_qudits = num_qudits # number of qubits/qutrits
        self.circuit = circuit # gates in the circuit
        self.qudit = qudit # 2 for qubits, 3 for qutrits
        self.history = [init_state] # store state after each gate

    def clean_state(self):
        for basis_state,amp in list(self.history[-1].items()):
            if amp == 0:
                del self.history[-1][basis_state]

    def z(self, qi):
        new_state = defaultdict(int)
        for basis_state,amp in self.history[-1].items():
            # if qi == 1, multiply amplitude by -1
            if ((basis_state >> qi) & 1):
                new_state[basis_state] += amp * -1
            else:
                new_state[basis_state] += amp
        self.history.append(new_state)
        self.clean_state()

    def x(self, qi):
        new_state = defaultdict(int)
        for basis_state,amp in self.history[-1].items():
            # flip qi 0-->1 and 1-->0
            new_state[basis_state ^ (1 << qi)] += amp
        self.history.append(new_state)
        self.clean_state()
    
    def y(self, qi):
        new_state = defaultdict(int)
        for basis_state,amp in self.history[-1].items():
            # flip qi, multiply amplitude by i, also multiply by -1 if starting in |1>
            if ((basis_state >> qi) & 1):
                new_state[basis_state ^ (1 << qi)] += amp * -1j
            else:
                new_state[basis_state ^ (1 << qi)] += amp * 1j
        self.history.append(new_state)
        self.clean_state()

    def h(self, qi):
        new_state = defaultdict(int)
        # go through each basis ket / amplitude combo of the current state
        for basis_state,amp in self.history[-1].items():
            if ((basis_state >> qi) & 1): # if qubit i == 1
                # |1>  --> 1/sqrt(2)|0> - 1/sqrt(2)|1>
                new_state[basis_state ^ (1 << qi)] += amp * 1/cmath.sqrt(2)
                new_state[basis_state] += amp * -1/cmath.sqrt(2)
            else: # qubit i == 0
                # |0> --> 1/sqrt(2)|0> + 1/sqrt(2)|1>
                new_state[basis_state] += amp * 1/cmath.sqrt(2)
                new_state[basis_state ^ (1 << qi)] += amp * 1/cmath.sqrt(2)
        self.history.append(new_state)
        self.clean_state()
    
    def cx(self, qc, qi):
        new_state = defaultdict(int)
        for basis_state,amp in self.history[-1].items():
            if ((basis_state >> qc) & 1): # if qubit c == 1, flip qubit i
                new_state[basis_state ^ (1 << qi)] += amp
            else: # qubit c == 0, no change
                new_state[basis_state] += amp
        self.history.append(new_state)
        self.clean_state()
    
    def cswap(self, qc, qi, qj):
        new_state = defaultdict(int)
        for basis_state,amp in self.history[-1].items():
            if ((basis_state >> qc) & 1): # if qubit c == 1, swap qubits i and j
                i = (basis_state >> qi) & 1 # state of qi
                j = (basis_state >> qj) & 1 # state of qj
                new_basis_state = basis_state ^ (i << qi) ^ (j << qj) ^ (i << qj) ^ (j << qi)
                new_state[new_basis_state] += amp
            else: # qubit c == 0, no swap
                new_state[basis_state] += amp
        self.history.append(new_state)
        self.clean_state()

    def h3(self, qi):
        new_state = defaultdict(int)
        # go through each basis ket / amplitude combo of the current state
        for basis_state,amp in self.history[-1].items():
            if ((basis_state // 3**qi) % 3) == 0: # qutrit i == 0
                # |0>  --> 1/sqrt(3)|0> + 1/sqrt(3)|1> + 1/sqrt(3)|2>
                new_state[basis_state] += amp * 1/cmath.sqrt(3)
                new_state[basis_state + 3**qi] += amp * 1/cmath.sqrt(3)
                new_state[basis_state + 2*3**qi] += amp * 1/cmath.sqrt(3)
            elif ((basis_state // 3**qi) % 3) == 1: # qutrit i == 1
                # |1> --> 1/sqrt(3)|0> + e^(i*2pi/3)/sqrt(3)|1> + e^(i*4pi/3)/sqrt(3)|2>
                new_state[basis_state - 3**qi] += amp * 1/cmath.sqrt(3)
                new_state[basis_state] += amp * (-0.5 + 1j*cmath.sqrt(3)/2)/cmath.sqrt(3)
                new_state[basis_state + 3**qi] += amp * (-0.5 - 1j*cmath.sqrt(3)/2)/cmath.sqrt(3)
            else: # qutrit i == 2
                # |2> --> 1/sqrt(3)|0> + e^(i*4pi/3)/sqrt(3)|1> + e^(i*2pi/3)/sqrt(3)|2>
                new_state[basis_state - 2*3**qi] += amp * 1/cmath.sqrt(3)
                new_state[basis_state - 3**qi] += amp * (-0.5 - 1j*cmath.sqrt(3)/2)/cmath.sqrt(3)
                new_state[basis_state] += amp * (-0.5 + 1j*cmath.sqrt(3)/2)/cmath.sqrt(3)
        self.history.append(new_state)
        self.clean_state()
    
    def cswap3(self, qc, qi, qj):
        new_state = defaultdict(int)
        for basis_state,amp in self.history[-1].items():
            if ((basis_state // 3**qc) % 3) == 1: # if qutrit c == 1, swap i and j
                i = (basis_state // 3**qi) % 3
                j = (basis_state // 3**qj) % 3
                new_basis_state = basis_state - i*3**qi - j*3**qj + i*3**qj + j*3**qi
                new_state[new_basis_state] += amp
            else: # qutrit c == 0 or 2, no swap
                new_state[basis_state] += amp
        self.history.append(new_state)
        self.clean_state()

n = 3
sim = Simulator(n, qudit=3)
sim.h3(0)
sim.h3(2)
sim.cswap3(0, 1, 2)
"""sim.h(0)
sim.cx(0, 1)
sim.z(1)
sim.cx(1, 2)
sim.h(0)
sim.h(1)
sim.cx(1, 0)
sim.h(1)"""

def print_qubit(sim):
    for timestep in sim.history:
        basis_states = [(format(num, f'0{n}b'), round(amp.real,4) + round(amp.imag, 4)*1j) for num,amp in sorted(timestep.items())]
        result = ""
        for s,a in basis_states:
            if a.imag == 0:
                a = a.real
            result += f"{a}|{s}> + "
        print(f"|Ψ> = {result[:-3]}")

def print_qutrit(sim):
    for timestep in sim.history:
        basis_states = [(int_to_bstring(num, 3).zfill(n), round(amp.real,4) + round(amp.imag, 4)*1j) for num,amp in sorted(timestep.items())]
        result = ""
        for s,a in basis_states:
            if a.imag == 0:
                a = a.real
            result += f"{a}|{s}> + "
        print(f"|Ψ> = {result[:-3]}")

print_qutrit(sim)