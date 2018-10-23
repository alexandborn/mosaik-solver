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
        gamesize = np.shape(self.Prob)

        # Resolution-Matrix erzeugen
        self.Reso = [[0 for n in range(gamesize[1])] for k in range(gamesize[0])]
        self.Reso = np.asarray(self.Reso)

        # Affected-Matrizen erzeugen
        self.Aff = []
        for idx, targ in enumerate(self.Targ):
            self.Aff.append([[0 for n in range(gamesize[1])] for k in range(gamesize[0])])
            for row_offset in [-1, 0, 1]:
                if self.Coord[idx][0] + row_offset < 0 or self.Coord[idx][0] + row_offset == gamesize[0]:
                    continue
                for col_offset in [-1, 0, 1]:
                    if self.Coord[idx][1] + col_offset < 0 or self.Coord[idx][1] + col_offset == gamesize[1]:
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
                self.Reso += self.Aff[idx]
                self.reso_norm()
                return
            # Im Umfeld einer 0 alles streichen
            elif targ == 0:
                self.Reso -= self.Aff[idx]
                self.reso_norm()

    def single_targ(self, idx, targ):
        aff_reso = self.Aff[idx] * self.Reso
        # Prüfen, ob im Umfeld einer Zahl bereits die richtige 
        # Anzahl an Kästchen ausgemalt ist, den Rest streichen
        colored = self.Aff[idx] * self.Reso
        colored[colored<0] = 0
        if colored.sum() == targ:
            self.Reso += colored - self.Aff[idx]
            self.reso_norm()
            return
        # Prüfen, ob im Umfeld einer Zahl bereits die richtige 
        # Anzahl an Kästchen gestrichen ist, den Rest ausmalen
        crossed = self.Aff[idx] * self.Reso
        crossed[crossed>0] = 0
        if crossed.sum() == (targ - self.Aff[idx].sum()):
            self.Reso += crossed + self.Aff[idx]
            self.reso_norm()

    def neighbors(self, idx, targ):
        for neigh in self.Neigh[idx]:
            # Prüfen, dass Nachbar nur noch Unbekannte im gem. Bereich hat
            aff_diff = self.Aff[neigh] - self.Aff[idx]
            aff_diff[aff_diff<0] = 0
            peri = (np.ones(np.shape(self.Reso)) - aff_diff) * 2
            if 0 not in (self.Reso + peri):
                # Anzahl der Felder im Umfeld von target außerhalb des 
                # gemeinsamen Bereichs
                own_aff = self.Aff[idx] - self.Aff[neigh]
                own_aff[own_aff<=0] = 0
                if own_aff.sum() == targ - self.Targ[neigh]:
                    self.Reso += own_aff
                    self.reso_norm()

    def solve(self, iter_max):
        self.print_prob()
        self.init_single_targ()

        state, counts = np.unique(self.Reso, return_counts=True)
        state_counts = dict(zip(state, counts))
        undef_counts = state_counts[0]
        for iter in range(iter_max):
            for idx, targ in enumerate(self.Targ):
                self.single_targ(idx, targ)
#               self.neighbors(idx, targ)

            if 0 not in self.Reso:
                print('Gelöst nach ',iter,' Iterationen.')
                break
            state, counts = np.unique(self.Reso, return_counts=True)
            state_counts = dict(zip(state, counts))
            if state_counts[0] == undef_counts:
                for idx, targ in enumerate(self.Targ):
                    self.neighbors(idx, targ)
                state, counts = np.unique(self.Reso, return_counts=True)
                state_counts = dict(zip(state, counts))
                if state_counts[0] == undef_counts:
                    print('Nach ',iter+1,' Iterationen nicht gelöst.')
                    break
            undef_counts = state_counts[0]
            if (iter == iter_max - 1) and 0 in self.Reso:
                print('Zu wenige Iterationen. Vorgabe erhöhen!')

        print()
        self.print_reso()


if __name__ == "__main__":
    t0 = time.time()
    janko103 = Mosaik('/home/alex/Schreibtisch/Raetsel/Problems/janko103.txt')
    janko103.solve(50)
    t1 = time.time()
    print("Benötigte Zeit: ",t1-t0)
