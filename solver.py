from prepare import create, print_reso, print_prob
from algorithm import solve, find_neighbors

Prob, Reso, Targ, Coord, Aff = create()
print_prob(Prob)
print()
Reso = solve(Reso, Targ, Coord, Aff, 150)

print()
print_reso(Reso)
