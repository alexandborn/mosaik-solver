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
        self.reset()

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

    def reset(self):
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

    def reso_norm(self):
        self.Reso[self.Reso > 0] = 1
        self.Reso[self.Reso < 0] = -1

    def init_single_targ(self):
        for idx, targ in enumerate(self.Targ):
            # Prüfen, ob Umfeld bereits durch Vorgabewert definiert ist
            if self.Aff[idx].sum() == targ:
                self.Reso[self.Aff[idx]==1] = 1
                return
            # Im Umfeld einer 0 alles streichen
            elif targ == 0:
                self.Reso[self.Aff[idx]==1] = 0

    def single_targ(self, idx, targ):
        # Prüfen, ob im Umfeld einer Zahl bereits die richtige 
        # Anzahl an Kästchen ausgemalt ist, den Rest streichen
        if self.Reso[(self.Aff[idx]==1)&(self.Reso==1)].size == targ:
            self.Reso[(self.Reso==-1)&(self.Aff[idx]==1)] = 0
            return
        # Prüfen, ob im Umfeld einer Zahl bereits die richtige 
        # Anzahl an Kästchen gestrichen ist, den Rest ausmalen
        if self.Reso[(self.Aff[idx]==1)&(self.Reso==0)].size == (
                self.Aff[idx].sum() - targ):
            self.Reso[(self.Aff[idx]==1)&(self.Reso==-1)] = 1

    def neighbors(self, idx, targ):
        for neigh in self.Neigh[idx]:
            # Prüfen, ob im eigenen Umfeld von Nachbar nichts undefinert ist
            if -1 not in self.Reso[(self.Aff[neigh]==1)&(self.Aff[idx]==0)]:
                # Anzahl der Felder im eigenen Umfeld von target
                if self.Reso[(self.Aff[idx]==1)
                        &(self.Aff[neigh]==0)].size == targ - self.Targ[neigh]:
                    self.Reso[(self.Aff[idx]==1)&(self.Aff[neigh]==0)] = 1

    def neighbors_2(self, idx, targ):
        targ_col = self.Reso[self.Aff[idx]==1]
        targ_col = targ_col[targ_col==1]
        targ_left = targ - targ_col.sum()
        for neigh in self.Neigh[idx]:
            neigh_col = self.Reso[self.Aff[neigh]==1]
            neigh_col = neigh_col[neigh_col==1]
            neigh_left = self.Targ[neigh] - neigh_col.sum()
#           print(targ_left, neigh_left)
#           aff_both = Aff[idx] + Aff[neigh]
#           aff_both[aff_both>1] = 1
#           undefined = self.Reso * aff_both
#           undefined[undefined>(-1)] = 0

    def solve(self, iter_max):
        self.init_single_targ()

        state, counts = np.unique(self.Reso, return_counts=True)
        state_counts = dict(zip(state, counts))
        undef_counts = state_counts[0]
        for iter in range(iter_max):
            for idx, targ in enumerate(self.Targ):
                if self.Reso[(self.Aff[idx]==1)&(self.Reso==-1)].size == 0:
                    continue
                self.single_targ(idx, targ)
#               self.neighbors(idx, targ)

            if -1 not in self.Reso:
                print('Gelöst nach ',iter,' Iterationen.')
                break
            state, counts = np.unique(self.Reso, return_counts=True)
            state_counts = dict(zip(state, counts))
            if state_counts[-1] == undef_counts:
                for idx, targ in enumerate(self.Targ):
                    self.neighbors(idx, targ)
                    self.neighbors_2(idx, targ)
                state, counts = np.unique(self.Reso, return_counts=True)
                state_counts = dict(zip(state, counts))
                if state_counts[-1] == undef_counts:
                    print('Nach ',iter+1,' Iterationen nicht gelöst.')
                    break
            undef_counts = state_counts[-1]
            if (iter == iter_max - 1) and 0 in self.Reso:
                print('Zu wenige Iterationen. Vorgabe erhöhen!')

        print()


if __name__ == "__main__":
    janko103 = Mosaik('/home/alex/Schreibtisch/Raetsel/Problems/janko103.txt')
    janko103.print_prob()
    t0 = time.time()
    for i in range(100):
        janko103.reset()
        janko103.solve(50)
    t1 = time.time()
    janko103.print_reso()
    print("Benötigte Zeit: ",t1-t0)
