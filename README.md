# Basic Quantum Computing Circuit Simulator
This is a simple and not-yet-efficient quantum circuit simulator that supports 
both qubits and qutrits. Still a work-in-progress.

## The Simulator
Create a simulator object using
``Simulator(num_qudits, circuit=[], qudit=2, init_state={0: 1})``

`num_qudits` is an integer that specifies how may qubits or qutrits the simulator 
is working with

`circuit` is non-functional right now, but it will take in a list of gates to run

`qudit` is either 2 or 3 specifying whether we're working with qubits or qutrits

`init_state` gives the initial state of the system as a dictionary of (basis-vector : amplitude)
Since basis vectors can be represented as integers, `{0:1}` for a 2-qubit system would
mean an initial state `1|00>`. Another example is `{0:0.5, 1:0.5, 2:0.5, 3:-0.5j}` for 
a 2-qutrit system would represent an initial state `0.5|00> + 0.5|01> + 0.5|02> - 0.5i|10>`

## The Gates
Once you have a simulator object, you can just use methods for gates. For example,
to apply the Hadamard gate on the 0th (least significant) qubit, use
``sim.h(0)``
The supported gates are `x,y,z,h,cx,cswap` for qubits, and `h3,cswap3` for qutrits. The
"3" simply indicates that the gate is meant for 3-state quantum objects.

## System State Vector
After applying gates through the simulator, use the print_qubit(sim) and print_qutrit(sim)
functions to display the state-vector history at each time-step / gate. This will
show the state vector in terms of basis vectors and amplitudes.

## TODO
- clean up code
- add sanity checks and error catching (e.g. can't run h3 gate with qubits)
- optimizations
- testing suite
- better visualization
- OpenQASM input