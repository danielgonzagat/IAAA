# ci/ethics_proofs.py
# Prova simbólica mínima: se (E>=TauE ∧ AI>=TauA ∧ dV<=0 ∧ Risk=0) então ALLOW.
from z3 import Real, Bool, And, Implies, Not, Solver, sat

E, TauE = Real('E'), Real('TauE')
AI, TauA = Real('AI'), Real('TauA')
dV      = Real('dV')
Risk    = Real('Risk')
ALLOW   = Bool('ALLOW')

assumps = And(E >= TauE, AI >= TauA, dV <= 0, Risk == 0)
rule    = Implies(assumps, ALLOW)

s = Solver()
s.add(TauE == 0.95, TauA == 0.99)
s.add(Not(rule))  # tenta refutar a regra
res = s.check()
if res == sat:
    raise SystemExit("Ethics rule refutable — FAIL")
print("Ethics rule holds under model — OK")

