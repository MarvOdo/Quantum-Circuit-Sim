import unittest
import cmath
from simulator import Simulator
from helper import *

class TestQutritCircuits(unittest.TestCase):
    def test_circuit1(self):
        sim = Simulator(3, qudit=3, circuit=["h3-0", "h3-2", "cswap3-0,1,2"], init_state={0: 1}, trackHistory=True)
        sim.run()
        # final result should be equal superposition of states 0,1,2,4,7,9,11,18,20 (using basic math)
        for i in [0, 1, 2, 4, 7, 9, 11, 18, 20]:
            self.assertAlmostEqual(sim.state[i], 1/3)
    
    def test_circuit2(self):
        sim = Simulator(5, qudit=3, circuit=["h3-0", "h3-1", "h3-2", "cswap3-0,1,3", "cswap3-4,2,1"], init_state={0: 1}, trackHistory=True)
        sim.run()
        # the last gate should not change anything, since qutrit 4 = |0>
        self.assertEqual(sim.history[-2], sim.history[-1])
        # last state can be found using basic math again, and it's an equal superposition
        for i in range(26):
            # after the first 3 gates, we have states 0...26
            # whenever st%3 = 1 (q0 = |1>), we swap the 1st and 3rd trit
            if i%3 == 1:
                q1 = (i//3**1)%3
                q3 = (i//3**3)%3
                i = i - q1*3**1 - q3*3**3 + q1*3**q3 + q3*3**q1
            self.assertAlmostEqual(sim.state[i], 1/cmath.sqrt(27))
    
    def test_circuit3(self):
        sim = Simulator(10, qudit=3, circuit=["h3-0", "h3-1", "h3-2", "h3-3", "h3-4", "cswap3-0,1,9"],
                        init_state={0: 1}, trackHistory=True)
        sim.run()
        for i in range(3**5):
            # after the first 5 gates, we have 3^5 states in equal superposition
            self.assertAlmostEqual(sim.history[-2][i], 1/cmath.sqrt(3**5))
            # last gate swaps, so check that, still same amplitudes
            if (i % 3) == 1:
                q1 = (i//3**1)%3 # value of q1
                i = i - q1*3**1 + q1*3**9 # q9 never changed, so we just set q1=0, and q9=old_q1
            self.assertAlmostEqual(sim.state[i], 1/cmath.sqrt(3**5))

if __name__ == "__main__":
    unittest.main()