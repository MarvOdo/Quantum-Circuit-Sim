import sys

def int_to_bstring(n: int, b: int) -> str:
    """Returns a string representation of n in base b\n
    Need b <= 10
    """
    if n == 0:
        return "0"
    result = ""
    while n:
        result += str(n % b)
        n //= b
    return result[::-1]

def print_sim(sim, b10=False, f=sys.stdout):
    """Print the history (or at least the final state) of the simulator\n
    Print basis vectors as |01001...> by default\n
    If b10=True, print as ints in base 10
    """
    hist = [sim.state]
    if sim.trackHistory:
        hist = sim.history
    for t in range(len(hist)):
        if b10:
            basis_states = [(str(num), round(amp.real,4) + round(amp.imag, 4)*1j) for num,amp in sorted(hist[t].items())]
        else:
            basis_states = [(int_to_bstring(num, sim.qudit).zfill(sim.num_qudits), round(amp.real,4) + round(amp.imag, 4)*1j) for num,amp in sorted(hist[t].items())]
        result = ""
        for s,a in basis_states:
            if a.imag == 0:
                a = a.real
            result += f"{a}|{s}> + "
        print(f"|Psi> = {result[:-3]}", file=f)
        if sim.circuit and t < len(hist) - 1:
            print(f"{sim.circuit[t]}", file=f)