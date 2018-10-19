import numpy as np

def normieren(Reso):
    Reso[Reso > 0] = 1
    Reso[Reso < 0] = -1

def solve(Reso,Targ,Coord,Aff,iter_max):
    for iter in range(iter_max):
        for idx, targ in enumerate(Targ):
            # Prüfen, ob Umfeld durch einzelenen Vorgabewert definiert ist
            if Aff[idx].sum() == targ:
                Reso += Aff[idx]
            normieren(Reso)
            # Im Umfeld einer 0 alles streichen
            if targ == 0:
                if Aff[idx].sum() > 0:
                    Aff[idx] = -Aff[idx]
                Reso += Aff[idx]
            normieren(Reso)
            # Prüfen, ob im Umfeld einer Zahl bereits die richtige Anzahl an Kästchen ausgemalt ist, den Rest streichen
            AR = Aff[idx] * Reso
            AR[AR<0] = 0
            if AR.sum() == targ:
                Reso += AR - Aff[idx]
            normieren(Reso)
            # Prüfen, ob im Umfeld einer Zahl bereits die richtige Anzahl an Kästchen gestrichen ist, den Rest ausmalen
            AR = Aff[idx] * Reso
            AR[AR>0] = 0
            if AR.sum() == (targ - Aff[idx].sum()):
                Reso += AR + Aff[idx]
            normieren(Reso)
        if 0 not in Reso:
            print('Gelöst nach ',iter,' Iterationen.')
            break
        if (iter == iter_max - 1) and 0 in Reso:
            print('Nach ',iter+1,' Iterationen nicht gelöst.')

    return Reso
