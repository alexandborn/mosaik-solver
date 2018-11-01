import time
import numpy as np

class Mosaik:

    def __init__(self, path):
        gamefile = open(path, 'r')
        self.Prob = []
        self.Targ = []
        self.Coord = []
        for idx, line in enumerate(gamefile):
            row = line.split()
            row = [e.replace('-', '-1') for e in row]
            row = [int(e) for e in row]
            for col, e in enumerate(row):
                if e >= 0:
                    self.Targ.append(e)
                    self.Coord.append([idx,col])
            self.Prob.append(row)
        gamefile.close()
        tuple(self.Prob)
        tuple(self.Targ)
        tuple(self.Coord)

        # Spielfeld-Größe ermitteln
        self.gamesize = np.shape(self.Prob)

        # Resolution-Matrix erzeugen
        self.reset_reso()

        # Affected-Matrizen erzeugen
        self.Aff = []
        for idx, targ in enumerate(self.Targ):
            self.Aff.append([[0 for n in range(self.gamesize[1])] for k in range(self.gamesize[0])])
            for row_offset in [-1, 0, 1]:
                if self.Coord[idx][0] + row_offset < 0 or self.Coord[idx][0] + row_offset == self.gamesize[0]:
                    continue
                for col_offset in [-1, 0, 1]:
                    if self.Coord[idx][1] + col_offset < 0 or self.Coord[idx][1] + col_offset == self.gamesize[1]:
                        continue
                    self.Aff[idx][self.Coord[idx][0]+row_offset][self.Coord[idx][1]+col_offset] = 1
        self.Aff = np.asarray(self.Aff)
        self.Aff.flags.writeable = False

        # Neighbours finden
        self.Neigh = []
        for idx, targ in enumerate(self.Targ):
            self.Neigh.append([])
            for kdx, neigh in enumerate(self.Targ):
                if ((kdx is not idx)
                    and self.Coord[kdx][0] in range(self.Coord[idx][0]-2,self.Coord[idx][0]+3)
                    and self.Coord[kdx][1] in range(self.Coord[idx][1]-2,self.Coord[idx][1]+3)
                    ):
                    self.Neigh[idx].append(kdx)
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

    def _iter_Targ(func):
        def wrapper(self):
            for idx, targ in enumerate(self.Targ):
                if self.targ_is_defined(idx):
                    continue
                func(self, idx, targ)
        return wrapper

    @_iter_Targ
    def solve_first(self, idx, targ):
        # Prüfen, ob Umfeld bereits durch Vorgabewert definiert ist
        if self.Aff[idx].sum() == targ:
            self.Reso[self.Aff[idx]==1] = 1
            return
        # Im Umfeld einer 0 alles streichen
        elif targ == 0:
            self.Reso[self.Aff[idx]==1] = 0

    @_iter_Targ
    def solve_single_targ(self, idx, targ):
        if self.right_num_colored(idx):
            self.cross_undefined(idx)
            return
        if self.right_num_crossed(idx):
            self.color_undefined(idx)

    def count_colored(self, targ_idx):
        return self.Reso[(self.Aff[targ_idx]==1)&(self.Reso==1)].size

    def right_num_colored(self, targ_idx):
        return self.count_colored(targ_idx) == self.Targ[targ_idx]

    def right_num_crossed(self, targ_idx):
        return (self.Reso[(self.Aff[targ_idx]==1)&(self.Reso==0)].size ==
                self.Aff[targ_idx].sum() - self.Targ[targ_idx])

    def color_undefined(self, targ_idx):
        self.Reso[(self.Aff[targ_idx]==1)&(self.Reso==-1)] = 1

    def cross_undefined(self, targ_idx):
        self.Reso[(self.Aff[targ_idx]==1)&(self.Reso==-1)] = 0

    def neighbors(self, idx, targ):
        for neigh in self.Neigh[idx]:
            # Prüfen, ob im eigenen Umfeld von Nachbar nichts undefinert ist
            if -1 not in self.Reso[(self.Aff[neigh]==1)&(self.Aff[idx]==0)]:
                # Anzahl der Felder im eigenen Umfeld von target
                if self.Reso[(self.Aff[idx]==1)
                        &(self.Aff[neigh]==0)].size == targ - self.Targ[neigh]:
                    self.Reso[(self.Aff[idx]==1)&(self.Aff[neigh]==0)] = 1

    @_iter_Targ
    def solve_neighbors(self, idx, targ):
        def count_to_col(idx):
            return self.Targ[idx] - self.count_colored(idx)

        def own_undef(own_idx, other_idx):
            return  self.Reso[(self.Aff[own_idx]==1)
                              &(self.Aff[other_idx]==0)
                              &(self.Reso==-1)].size

        def com_to_col(own_idx, other_idx):
            com_undef = self.Reso[(self.Aff[own_idx]==1)
                                  &(self.Aff[other_idx]==1)
                                  &(self.Reso==-1)].size
            com_min = max([count_to_col(own_idx) - own_undef(own_idx,other_idx), 0])
            com_max = min([count_to_col(own_idx), com_undef])
            return range(com_min, com_max + 1)

        def color_own_undefined(own_idx, other_idx):
            self.Reso[(self.Aff[own_idx]==1)
                      &(self.Aff[other_idx]==0)
                      &(self.Reso==-1)] = 1

        for neigh in self.Neigh[idx]:
            targ_com_to_col = com_to_col(idx,neigh)
            neigh_com_to_col = com_to_col(neigh,idx)
            intersec_to_col = list(set(targ_com_to_col).intersection(neigh_com_to_col))
            if len(intersec_to_col) == 1:
                if count_to_col(idx) - intersec_to_col[0] == own_undef(idx,neigh):
                    color_own_undefined(idx,neigh)
                elif count_to_col(idx) == intersec_to_col[0]:
                    self.Reso[(self.Aff[idx]==1)&(self.Aff[neigh]==0)
                                  &(self.Reso==-1)] = 0

    def targ_is_defined(self,targ_idx):
        return -1 not in self.Reso[(self.Aff[targ_idx]==1)]

    def count_all_undefined(self):
        state, counts = np.unique(self.Reso, return_counts=True)
        state_counts = dict(zip(state, counts))
        if -1 in state_counts:
            return state_counts[-1]
        return 0

    def solved(self):
        return -1 not in self.Reso

    def solve(self):
        self.solve_first()
        iterations = 1
        while True:
            all_undef = self.count_all_undefined()
            if self.solved():
                print('Gelöst nach ', iterations, ' Iterationen.')
                break
            self.solve_single_targ()
            if self.count_all_undefined() == all_undef:
                self.solve_neighbors()
                if all_undef == self.count_all_undefined():
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
