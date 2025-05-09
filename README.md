# Basic Quantum Computing Circuit Simulator
This is a basic quantum circuit simulator that supports both qubits and qutrits.
It is based on a simulator class that takes in some initial conditions for the 
simulation, and can run a quantum circuit.

## The Simulator
``Simulator(num_qudits, qudit=2, circuit=[], init_state={0: 1}, trackHistory=False)``

`num_qudits` is an integer that specifies how may qubits or qutrits the simulator 
is working with.

`qudit` is either 2 or 3 specifying whether we're working with qubits or qutrits.

`circuit` takes in a list of string, where each string represents a gate. These take
the general form "gateName-target,target,target". gateName can be any of the currently
supported gates: `x,y,z,h,cx,cswap` for qubits or `h3,cswap3` for qutrits. Targets are just
integers to specify which qubit the gate is applied on. For example, we can have 
`circuit = ["h-0", "cx-0,1"]` to apply the hadamard gate to qubit 0, and a Controlled-X gate
with control qubit 0 and target qubit 1. This creates an entangled state. 

`init_state` gives the initial state of the system as a dictionary of (basis-vector : amplitude)
Since basis vectors can be represented as integers, `{0:1}` for a 2-qubit system would
mean an initial state `1|00>`. Another example is `{0:0.5, 1:0.5, 2:0.5, 3:-0.5j}` for 
a 2-qutrit system, which would represent an initial state `0.5|00> + 0.5|01> + 0.5|02> - 0.5i|10>`.
The simulator normalizes the initial state if it's not already normalized.

`track_history` will track the state at each time-step / after each gate, and will store
it in sim.history as a list of states.

Use the `run()` method of the simulator object to run the circuit simulation based on
the circuit that was fed in on initialization:
``sim = Simulator(2, circuit=["h-0", "cx-0,1"])``
``sim.run()``
``print_sim(sim)``
The function `print_sim(sim, b10=False, f=sys.stdout)` is in the `helper.py` file, and prints out the history
(or just final state if `trackHistory=False` in the simulator) of the system.
It prints out the state after each gate operation, with complex amplitudes, and
the gate that was applied at each step. If `b10=True`, the printed states are shown
in base10, i.e., |10011> --> |19>. Optionally, print to a specific file using `f`.

## The Gates
Once you have a simulator object, you can also use methods for gates, instead of
the circuit itself. For example, to apply the Hadamard gate on the 0th (least significant)
qubit, use ``sim.apply_h(0)``.
The supported gates are the Pauli `x,y,z`, Hadamard `h`, and controlled `cx,cswap` for qubits.
There is also support for Hadamard `h3` and controlled `cswap3` for qutrits. The
"3" simply indicates that the gate is meant for 3-state quantum objects.

# Testing
There are a few testing circuits already created. Run the testQubit/QutritCircuits.py files, which check a
couple of assertions for those circuits. To check the accuracy of qubit circuits, I recommend
comparing to https://algassert.com/quirk. Qutrits and qubits can also be checked mathematically.

The qutrit circuits for the tests are also in the `example.py` file. Running that file
will output the results into the `example_results` folder. The amplitudes at each step
can be found there, for all 3 qutrit circuits. I use `b10=True` in order to write the result
slightly shorter, but that can be easily changed.

# Design Choices
1. Amplitudes are all numerical in order to allow for arbitrary amplitudes, instead of only simple
1/sqrt(2) states. For visual purposes, this could be improved using sympy to allow arbitrary 
amplitudes using radicals and complex exponentials.
2. There is rounding error of course, so I never check for exact amplitude equivalence when testing.
For example, for normalization checks, I allow error in the order `1e-8`, as some rounding error is bound
to give total magnitudes that slightly differ from exactly 1. `1e-8` is an arbitrary choice, but I thought
it was a good mix of accuracy and not-too-strict requirements.
3. I keep track of basis-states as integers rather than strings, in order to hopefully save some memory.
For example, the state `|010>` is simply `2`. I then use integers as keys for dictionaries, where I
store the amplitude of each state. This means that the main bottleneck to the simulator is not necessarily
the number of qubits/trits itself, but rather the number of non-zero-amplitude intermediate states.
Optimizations are needed for dense intermediate-state circuits.

# Things to Improve
- optimizations / performance
- testing suite
- better visualization
- OpenQASM input
- maybe add command-line support?