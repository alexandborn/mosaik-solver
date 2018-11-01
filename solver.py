import time
import numpy as np

class Mosaik:

    def __init__(self, path):
        gamefile = open(path, 'r')
        self.Prob = []
        self.Targs = []
        self.Coord = []
        for row, line in enumerate(gamefile):
            line = line.split()
            line = [e.replace('-', '-1') for e in line]
            line = [int(e) for e in line]
            self.Prob.append(line)
            for col, e in enumerate(line):
                if e >= 0:
                    self.Targs.append(e)
                    self.Coord.append([row,col])
        gamefile.close()
        tuple(self.Prob)
        tuple(self.Targs)
        tuple(self.Coord)

        # Spielfeld-Größe ermitteln
        self.gamesize = np.shape(self.Prob)

        # Resolution-Matrix erzeugen
        self.reset_reso()

        # Affected-Matrizen erzeugen
        self.Aff = []
        for targ, val in enumerate(self.Targs):
            self.Aff.append([[0 for n in range(self.gamesize[1])] for k in range(self.gamesize[0])])
            for row_offset in [-1, 0, 1]:
                if self.Coord[targ][0] + row_offset < 0 or self.Coord[targ][0] + row_offset == self.gamesize[0]:
                    continue
                for col_offset in [-1, 0, 1]:
                    if self.Coord[targ][1] + col_offset < 0 or self.Coord[targ][1] + col_offset == self.gamesize[1]:
                        continue
                    self.Aff[targ][self.Coord[targ][0]+row_offset][self.Coord[targ][1]+col_offset] = 1
        self.Aff = np.asarray(self.Aff)
        self.Aff.flags.writeable = False

        # Neighbors finden
        self.Neigh = []
        for targ, val in enumerate(self.Targs):
            self.Neigh.append([])
            for kdx, neigh in enumerate(self.Targs):
                if ((kdx is not targ)
                    and self.Coord[kdx][0] in range(self.Coord[targ][0]-2,self.Coord[targ][0]+3)
                    and self.Coord[kdx][1] in range(self.Coord[targ][1]-2,self.Coord[targ][1]+3)
                    ):
                    self.Neigh[targ].append(kdx)
        tuple(self.Neigh)

    def reset_reso(self):
        self.Reso = [[-1 for n in range(self.gamesize[1])] for k in range(self.gamesize[0])]
        self.Reso = np.asarray(self.Reso)

    def print_prob(self):
        for row in self.Prob:
            line = ''
            for e in row:
                e = str(e)
                e = e.replace('-1', '-')
                line += ' '+e
            print(line)

    def print_reso(self):
        for row in self.Reso:
            line = ''
            for e in row:
                e = str(e)
                e = e.replace('-1', '-')
                e = e.replace('0', 'x')
                e = e.replace('1', chr(9608))
                line += ' '+e
            print(line)



    ### Solver ############################################################

    ### Count

    def count_colored(self, idx):
        return self.Reso[(self.Aff[idx]==1)&(self.Reso==1)].size

    def count_to_col(self, idx):
        return self.Targs[idx] - self.count_colored(idx)

    def count_own_undef(self, own_idx, other_idx):
        return  self.Reso[(self.Aff[own_idx]==1)
                          &(self.Aff[other_idx]==0)
                          &(self.Reso==-1)].size

    def com_to_col(self, own_idx, other_idx):
        com_undef = self.Reso[(self.Aff[own_idx]==1)
                              &(self.Aff[other_idx]==1)
                              &(self.Reso==-1)].size
        com_min = max([self.count_to_col(own_idx)
                       - self.count_own_undef(own_idx,other_idx), 0])
        com_max = min([self.count_to_col(own_idx), com_undef])
        return range(com_min, com_max + 1)

    def count_all_undef(self):
        state, counts = np.unique(self.Reso, return_counts=True)
        state_counts = dict(zip(state, counts))
        if -1 in state_counts:
            return state_counts[-1]
        return 0


    ### Check

    def is_solved(self):
        return -1 not in self.Reso

    def is_complete(self,idx):
        return -1 not in self.Reso[(self.Aff[idx]==1)]

    def right_num_colored(self, idx):
        return self.count_colored(idx) == self.Targs[idx]

    def right_num_crossed(self, idx):
        return (self.Reso[(self.Aff[idx]==1)&(self.Reso==0)].size ==
                self.Aff[idx].sum() - self.Targs[idx])


    ### Change Reso

    def col_undef(self, idx):
        self.Reso[(self.Aff[idx]==1)&(self.Reso==-1)] = 1

    def cross_undef(self, idx):
        self.Reso[(self.Aff[idx]==1)&(self.Reso==-1)] = 0

    def col_own_undef(self, own_idx, other_idx):
        self.Reso[(self.Aff[own_idx]==1)
                  &(self.Aff[other_idx]==0)
                  &(self.Reso==-1)] = 1

    def cross_own_undef(self, own_idx, other_idx):
        self.Reso[(self.Aff[own_idx]==1)
                  &(self.Aff[own_idx]==0)
                  &(self.Reso==-1)] = 0

    ### Steps to solve

    def _iter_Targs(func):
        def wrapper(self):
            for targ, val in enumerate(self.Targs):
                if self.is_complete(targ):
                    continue
                func(self, targ, val)
        return wrapper

    @_iter_Targs
    def solve_first(self, idx, val):
        # Prüfen, ob Umfeld bereits durch Vorgabewert definiert ist
        if self.Aff[idx].sum() == val:
            self.Reso[self.Aff[idx]==1] = 1
            return
        # Im Umfeld einer 0 alles streichen
        elif val == 0:
            self.Reso[self.Aff[idx]==1] = 0

    @_iter_Targs
    def solve_single(self, idx, val):
        if self.right_num_colored(idx):
            self.cross_undef(idx)
            return
        if self.right_num_crossed(idx):
            self.col_undef(idx)

    @_iter_Targs
    def solve_neighbors(self, targ, val):
        for neigh in self.Neigh[targ]:
            targ_com_to_col = self.com_to_col(targ,neigh)
            neigh_com_to_col = self.com_to_col(neigh,targ)
            intersec_to_col = list(set(targ_com_to_col)
                                   .intersection(neigh_com_to_col))
            targ_own_to_col = self.count_to_col(targ) - intersec_to_col[0]
            if len(intersec_to_col) == 1:
                if targ_own_to_col == self.count_own_undef(targ,neigh):
                    self.col_own_undef(targ,neigh)
                elif self.count_to_col(targ) == intersec_to_col[0]:
                    self.cross_own_undef(targ,neigh)

    def solve(self):
        self.solve_first()
        iterations = 1
        while True:
            all_undef = self.count_all_undef()
            if self.is_solved():
                print('Gelöst nach ', iterations, ' Iterationen.')
                break
            self.solve_single()
            if self.count_all_undef() == all_undef:
                self.solve_neighbors()
                if self.count_all_undef() == all_undef:
                    print('Nach ', iterations, ' Iterationen nicht gelöst.')
                    break
            iterations += 1


if __name__ == "__main__":
    janko = Mosaik('/home/alex/Schreibtisch/Raetsel/Problems/janko103.txt')
    janko.print_prob()
    t0 = time.time()
    for i in range(1):
        janko.reset_reso()
        janko.solve()
    t1 = time.time()
    janko.print_reso()
    print("Benötigte Zeit: ",t1-t0)
