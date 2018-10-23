import numpy as np

# Spielfeld aus Datei auslesen und in Problem-Matrix schreiben
# Target- und Coordinates-Matrizen aus Problem-Matrix ableiten 
def create():
    gamefile = open('/home/alex/Schreibtisch/Raetsel/Problems/janko103.txt', 'r')
    Prob = []
    Targ = []
    Coord = []
    for idx, line in enumerate(gamefile):
        row = line.split()
        row = [e.replace('-', '-1') for e in row]
        row = [int(e) for e in row]
        for col, e in enumerate(row):
            if e >= 0:
                Targ.append(e)
                Coord.append([idx,col])
        Prob.append(row)
    gamefile.close()
    tuple(Prob)
    tuple(Targ)
    tuple(Coord)

    # Spielfeld-Größe ermitteln
    Size = np.shape(Prob)

    # Resolution-Matrix erzeugen
    Reso = [[0 for n in range(Size[1])] for k in range(Size[0])]
    Reso = np.asarray(Reso)

    # Affected-Matrizen erzeugen
    Aff = []
    for idx, targ in enumerate(Targ):
        Aff.append([[0 for n in range(Size[1])] for k in range(Size[0])])
        for row_offset in [-1, 0, 1]:
            if Coord[idx][0] + row_offset < 0 or Coord[idx][0] + row_offset == Size[0]:
                continue
            for col_offset in [-1, 0, 1]:
                if Coord[idx][1] + col_offset < 0 or Coord[idx][1] + col_offset == Size[1]:
                    continue
                Aff[idx][Coord[idx][0]+row_offset][Coord[idx][1]+col_offset] = 1
    Aff = np.asarray(Aff)
    Aff.flags.writeable = False

    return Prob, Reso, Targ, Coord, Aff

# Ausgabe
def print_reso(Reso):
    for row in Reso:
        line = ''
        for e in row:
            e = str(e)
            e = e.replace('-1', '-')
            e = e.replace('1', chr(9608))
            line += ' '+e
        print(line)

def print_prob(Prob):
    for row in Prob:
        line = ''
        for e in row:
            e = str(e)
            e = e.replace('-1', '-')
            line += ' '+e
        print(line)
