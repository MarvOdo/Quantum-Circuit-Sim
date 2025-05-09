from simulator import Simulator
from helper import *

# circuit 1
# 3 qutrits
# run H(0), H(2), CSWAP(0,1,2)
sim1 = Simulator(3, qudit=3, circuit=["h3-0", "h3-2", "cswap3-0,1,2"], init_state={0: 1}, trackHistory=True)
sim1.run()
print_sim(sim1, b10=False, f=open("./example_results/circ1.txt", "w"))

# circuit 2
# 5 qutrits
# run H(0), H(1), H(2), CSWAP(0,1,3), CSWAP(4,2,1)
sim2 = Simulator(5, qudit=3, circuit=["h3-0", "h3-1", "h3-2", "cswap3-0,1,3", "cswap3-4,2,1"], init_state={0: 1}, trackHistory=True)
sim2.run()
print_sim(sim2, b10=True, f=open("./example_results/circ2.txt", "w"))

# circuit 3
# 10 qutrits
# run H(0), H(1), H(2), H(3), H(4), CSWAP(0,1,9)
sim3 = Simulator(10, qudit=3, circuit=["h3-0", "h3-1", "h3-2", "h3-3", "h3-4", "cswap3-0,1,9"], init_state={0: 1}, trackHistory=True)
sim3.run()
print_sim(sim3, b10=True, f=open("./example_results/circ3.txt", "w"))