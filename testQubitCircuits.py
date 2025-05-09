import unittest
import cmath
from simulator import Simulator
from helper import *

class TestQubitCircuits(unittest.TestCase):
    def test_entanglement(self):
        sim = Simulator(2, qudit=2, circuit=["h-0", "cx-0,1", "h-0", "h-1"], init_state={0: 1}, trackHistory=True)
        sim.run()
        # final result should be 1/sqrt(2)|00> + 1/sqrt(2)|11>
        self.assertAlmostEqual(sim.state[0], 1/cmath.sqrt(2))
        self.assertAlmostEqual(sim.state[3], 1/cmath.sqrt(2))
    
    def test_interefrence(self):
        sim = Simulator(2, qudit=2, circuit=["h-0", "h-1", "cx-0,1", "h-0", "h-1"], init_state={0: 1}, trackHistory=True)
        sim.run()
        # final result should be back to |00>
        self.assertAlmostEqual(sim.state[0], 1)
    
    def test_bigger_circuit(self):
        sim = Simulator(10, qudit=2, circuit=["h-0", "cx-0,1", "y-2", "x-3", "h-4", "h-5", "cswap-4,5,6", "x-7", "x-8", "z-8"], init_state={0: 1}, trackHistory=True)
        sim.run()
        # final state checked with https://algassert.com/quirk
        for i in [396, 399, 412, 415, 428, 431, 476, 479]:
            self.assertAlmostEqual(sim.state[i], -1j/cmath.sqrt(8))
        
if __name__ == "__main__":
    unittest.main()