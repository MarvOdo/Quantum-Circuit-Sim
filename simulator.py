import cmath
from collections import defaultdict
from helper import *

class Simulator:
    def __init__(self, num_qudits, qudit=2, circuit=[], init_state={0: 1}, trackHistory=False):
        """Initialize a Simulator object with the number and type of qudits,\n
        a circuit of gates, and an initial state for the system\n
        Can also keep track of the history of states at each time-step / gate
        """
        self.num_qudits = num_qudits # number of qubits/qutrits
        self.circuit = circuit # list of gates in the circuit
        self.qudit = qudit # 2 for qubits, 3 for qutrits
        self.state = init_state # current state of the system
        self.clean_state() # remove VERY small amplitudes b/c equivalent to rounding errors
        self.normalize() # normalize initial state
        self.remove_global_phase() # make lowest-integer state have real+positive phase
        self.trackHistory = trackHistory # bool flag to track history
        if trackHistory: self.history = [init_state] # used to possibly story history of states

    def clean_state(self):
        """Remove zero or low amplitude states that are likely rounding errors\n
        from the current state
        """
        for basis_state,amp in list(self.state.items()):
            if abs(amp) <= 1e-8:
                del self.state[basis_state]
    
    def check_normalization(self):
        """Ensure that state is normalized (magnitude is 1)"""
        mag = 0
        for amp in self.state.values():
            mag += abs(amp)**2
        if abs(1 - mag) > 1e-8:
            raise Exception(f"State is not normalized: {self.state}")
        
    def normalize(self):
        """Normalize the current state. Normally only used for the initial state."""
        mag = 0
        for amp in self.state.values():
            mag += abs(amp)**2
        for basis_vector in self.state.keys():
            self.state[basis_vector] /= cmath.sqrt(mag)

    def remove_global_phase(self):
        """Updates global phase such that lowest-integer state has real and positive phase"""
        amp_lowest_state = self.state[min(self.state.keys())]
        real_pos_amp = abs(amp_lowest_state)
        new_phase = real_pos_amp / amp_lowest_state
        for basis_state in self.state.keys():
            self.state[basis_state] *= new_phase
    
    def run(self):
        """Run the simulator using self.circuit"""
        for gate in self.circuit:
            gate_name, targets = gate.split("-")
            targets = [int(qi) for qi in targets.split(",")]
            apply_gate = getattr(self, f"apply_{gate_name}")
            apply_gate(*targets)
        return self.state

    def apply_z(self, qi):
        """Apply the Pauli Z gate on qubit qi
        """
        if self.qudit != 2: raise Exception("This gate can only be applied on qubits")
        new_state = defaultdict(int)
        for basis_state,amp in self.state.items():
            # if qi == 1, multiply amplitude by -1
            if ((basis_state >> qi) & 1):
                new_state[basis_state] += amp * -1
            else:
                new_state[basis_state] += amp
        self.state = new_state
        self.clean_state()
        self.check_normalization()
        if self.trackHistory: self.history.append(self.state)
        return self.state

    def apply_x(self, qi):
        """Apply the Pauli X gate on qubit qi
        """
        if self.qudit != 2: raise Exception("This gate can only be applied on qubits")
        new_state = defaultdict(int)
        for basis_state,amp in self.state.items():
            # flip qi 0-->1 and 1-->0
            new_state[basis_state ^ (1 << qi)] += amp
        self.state = new_state
        self.clean_state()
        self.check_normalization()
        if self.trackHistory: self.history.append(self.state)
        return self.state
    
    def apply_y(self, qi):
        """Apply the Pauli Y gate on qubit qi
        """
        if self.qudit != 2: raise Exception("This gate can only be applied on qubits")
        new_state = defaultdict(int)
        for basis_state,amp in self.state.items():
            # flip qi, multiply amplitude by i, also multiply by -1 if starting in |1>
            if ((basis_state >> qi) & 1):
                new_state[basis_state ^ (1 << qi)] += amp * -1j
            else:
                new_state[basis_state ^ (1 << qi)] += amp * 1j
        self.state = new_state
        self.clean_state()
        self.check_normalization()
        if self.trackHistory: self.history.append(self.state)
        return self.state

    def apply_h(self, qi):
        """Apply the Hadamard gate on qubit qi
        """
        if self.qudit != 2: raise Exception("This gate can only be applied on qubits. Did you mean to use h3?")
        new_state = defaultdict(int)
        for basis_state,amp in self.state.items():
            if ((basis_state >> qi) & 1): # if qubit i == 1
                # |1>  --> 1/sqrt(2)|0> - 1/sqrt(2)|1>
                new_state[basis_state ^ (1 << qi)] += amp * 1/cmath.sqrt(2)
                new_state[basis_state] += amp * -1/cmath.sqrt(2)
            else: # qubit i == 0
                # |0> --> 1/sqrt(2)|0> + 1/sqrt(2)|1>
                new_state[basis_state] += amp * 1/cmath.sqrt(2)
                new_state[basis_state ^ (1 << qi)] += amp * 1/cmath.sqrt(2)
        self.state = new_state
        self.clean_state()
        self.check_normalization()
        if self.trackHistory: self.history.append(self.state)
        return self.state
    
    def apply_phase(self, qi, phi):
        """Apply the phase (P) gate on qubit qi with angle phi"""
        if self.qudit != 2: raise Exception("This gate can only be applied on qubits.")
        new_state = defaultdict(int)
        for basis_state,amp in self.state.items():
            # if qi == 1, multiply amplitude by -1
            if ((basis_state >> qi) & 1):
                new_state[basis_state] += amp * cmath.exp(phi*1j)
            # if qi == 0, no phase added
            else:
                new_state[basis_state] += amp
        self.state = new_state
        self.clean_state()
        self.check_normalization()
        if self.trackHistory: self.history.append(self.state)
        return self.state

    def apply_Rx(self, qi, theta):
        """Apply the Rx (Rotation around X) gate on qubit qi with angle theta"""
        if self.qudit != 2: raise Exception("This gate can only be applied on qubits.")
        new_state = defaultdict(int)
        for basis_state,amp in self.state.items():
            if ((basis_state >> qi) & 1): # if qubit i == 1
                # |1>  --> -isin(theta/2)|0> + cos(theta/2)|1>
                new_state[basis_state ^ (1 << qi)] += amp * cmath.sin(theta/2) * -1j
                new_state[basis_state] += amp * cmath.cos(theta/2)
            else: # qubit i == 0
                # |0> --> cos(theta/2)|0> -isin(theta/2)|1>
                new_state[basis_state] += amp * cmath.cos(theta/2)
                new_state[basis_state ^ (1 << qi)] += amp * cmath.sin(theta/2) * -1j
        self.state = new_state
        self.clean_state()
        self.check_normalization()
        if self.trackHistory: self.history.append(self.state)
        return self.state
    
    def apply_Ry(self, qi, theta):
        """Apply the Ry (Rotation around Y) gate on qubit qi with angle theta"""
        if self.qudit != 2: raise Exception("This gate can only be applied on qubits.")
        new_state = defaultdict(int)
        for basis_state,amp in self.state.items():
            if ((basis_state >> qi) & 1): # if qubit i == 1
                # |1>  --> -sin(theta/2)|0> + cos(theta/2)|1>
                new_state[basis_state ^ (1 << qi)] += amp * -1 * cmath.sin(theta/2)
                new_state[basis_state] += amp * cmath.cos(theta/2)
            else: # qubit i == 0
                # |0> --> cos(theta/2)|0> + sin(theta/2)|1>
                new_state[basis_state] += amp * cmath.cos(theta/2)
                new_state[basis_state ^ (1 << qi)] += amp * cmath.sin(theta/2)
        self.state = new_state
        self.clean_state()
        self.check_normalization()
        if self.trackHistory: self.history.append(self.state)
        return self.state
    
    def apply_Rz(self, qi, theta):
        """Apply the Rz (Rotation around Z) gate on qubit qi with angle theta"""
        if self.qudit != 2: raise Exception("This gate can only be applied on qubits.")
        new_state = defaultdict(int)
        for basis_state,amp in self.state.items():
            if ((basis_state >> qi) & 1): # if qubit i == 1
                # |1>  --> exp(itheta/2)|1>
                new_state[basis_state] += amp * cmath.exp(1j * theta / 2)
            else: # qubit i == 0
                # |0> --> exp(-itheta/2)|0>
                new_state[basis_state] += amp * cmath.exp(-1j * theta / 2)
        self.state = new_state
        self.clean_state()
        self.check_normalization()
        if self.trackHistory: self.history.append(self.state)
        return self.state

    def apply_swap(self, qi, qj):
        """Apply the Swap gate, with target qubits qi and qj
        """
        if self.qudit != 2: raise Exception("This gate can only be applied on qubits. Did you mean to use swap3?")
        if qi == qj: raise Exception("Target qubits need to be unique")
        new_state = defaultdict(int)
        for basis_state,amp in self.state.items():
            i = (basis_state >> qi) & 1 # state of qi
            j = (basis_state >> qj) & 1 # state of qj
            # following XORs set the states to 0 for qi,qj, and then place the swapped values
            #    at those qubits
            new_basis_state = basis_state ^ (i << qi) ^ (j << qj) ^ (i << qj) ^ (j << qi)
            new_state[new_basis_state] += amp
        self.state = new_state
        self.clean_state()
        self.check_normalization()
        if self.trackHistory: self.history.append(self.state)
        return self.state
    
    def apply_cx(self, qc, qi):
        """Apply the Controlled X / Controlled Not gate, with control qubit qc,\n
        and target qubit qi
        """
        if self.qudit != 2: raise Exception("This gate can only be applied on qubits")
        if qc == qi: raise Exception("Control and target qubits need to be unique")
        new_state = defaultdict(int)
        for basis_state,amp in self.state.items():
            if ((basis_state >> qc) & 1): # if qubit c == 1, flip qubit i
                new_state[basis_state ^ (1 << qi)] += amp
            else: # qubit c == 0, no change
                new_state[basis_state] += amp
        self.state = new_state
        self.clean_state()
        self.check_normalization()
        if self.trackHistory: self.history.append(self.state)
        return self.state
    
    def apply_cswap(self, qc, qi, qj):
        """Apply the Controlled Swap gate, with control qubit qc, and target\n
        qubits qi and qj
        """
        if self.qudit != 2: raise Exception("This gate can only be applied on qubits. Did you mean to use cswap3?")
        if len({qc, qi, qj}) != 3: raise Exception("Control and target qubits need to be unique")
        new_state = defaultdict(int)
        for basis_state,amp in self.state.items():
            if ((basis_state >> qc) & 1): # if qubit c == 1, swap qubits i and j
                i = (basis_state >> qi) & 1 # state of qi
                j = (basis_state >> qj) & 1 # state of qj
                # following XORs set the states to 0 for qi,qj, and then place the swapped values
                #    at those qubits
                new_basis_state = basis_state ^ (i << qi) ^ (j << qj) ^ (i << qj) ^ (j << qi)
                new_state[new_basis_state] += amp
            else: # qubit c == 0, no swap
                new_state[basis_state] += amp
        self.state = new_state
        self.clean_state()
        self.check_normalization()
        if self.trackHistory: self.history.append(self.state)
        return self.state
    
    def apply_ccx(self, qc1, qc2, qi):
        """Apply the Double Controlled  X / Not gate, with control qubits qc1\n
        and qc2, and target qubit qi
        """
        if self.qudit != 2: raise Exception("This gate can only be applied on qubits")
        if len({qc1, qc2, qi}) != 3: raise Exception("Control and target qubits need to be unique")
        new_state = defaultdict(int)
        for basis_state,amp in self.state.items():
            if ((basis_state >> qc1) & 1) and ((basis_state >> qc2) & 1): # if both controls
                new_state[basis_state ^ (1 << qi)] += amp
            else: # one of the controls is 0, no change
                new_state[basis_state] += amp
        self.state = new_state
        self.clean_state()
        self.check_normalization()
        if self.trackHistory: self.history.append(self.state)
        return self.state
    
    def apply_controlled(self, gate_name, qc, qi, *args):
        """Apply an arbitrary Controlled gate on qubits\n
        Supports an arbitrary number of control qubits qc, and the correct number\n
        of qubits for the given gate as targets in qi\n
        Use *args for values like theta/phi for rotation gates"""
        if self.qudit != 2: raise Exception("This gate can only be applied on qubits")
        if len(set(qc).add(set(qi))) != len(qc) + len(qi): raise Exception("Control and target qubits need to be unique")
        new_state = defaultdict(int)
        for basis_state,amp in self.state.items():
            if all(((basis_state >> q) & 1) for q in qc): # check all control qubits are 1
                apply_gate = getattr(self, f"apply_{gate_name}")
                apply_gate(*qi, *args)
            else: # one of the controls is 0, no change
                new_state[basis_state] += amp
        self.state = new_state
        self.clean_state()
        self.check_normalization()
        if self.trackHistory: self.history.append(self.state)
        return self.state

    def apply_h3(self, qi):
        """Apply the Hadamard gate to qutrit qi"""
        if self.qudit != 3: raise Exception("This gate can only be applied on qutrits. Did you mean to use h?")
        new_state = defaultdict(int)
        for basis_state,amp in self.state.items():
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
        self.state = new_state
        self.clean_state()
        self.check_normalization()
        if self.trackHistory: self.history.append(self.state)
        return self.state
    
    def apply_cswap3(self, qc, qi, qj):
        """Apply the Controlled Swap gate, with control qutrit qc, and target
        qutrits qi and qj
        """
        if self.qudit != 3: raise Exception("This gate can only be applied on qutrits. Did you mean to use cswap?")
        if len({qc, qi, qj}) != 3: raise Exception("Control and target qutrits need to be unique")
        new_state = defaultdict(int)
        for basis_state,amp in self.state.items():
            if ((basis_state // 3**qc) % 3) == 1: # if qutrit c == 1, swap i and j
                i = (basis_state // 3**qi) % 3
                j = (basis_state // 3**qj) % 3
                # Just as with the qubit swap, we set the states at qi,qj to 0, and
                #     then add in the swapped values
                new_basis_state = basis_state - i*3**qi - j*3**qj + i*3**qj + j*3**qi
                new_state[new_basis_state] += amp
            else: # qutrit c == 0 or 2, no swap
                new_state[basis_state] += amp
        self.state = new_state
        self.clean_state()
        self.check_normalization()
        if self.trackHistory: self.history.append(self.state)
        return self.state