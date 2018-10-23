import numpy as np

def reso_norm(Reso):
    Reso[Reso > 0] = 1
    Reso[Reso < 0] = -1

def init_single_targ(Reso, Targ, Aff):
    for idx, targ in enumerate(Targ):
        # Prüfen, ob Umfeld durch einzelenen Vorgabewert definiert ist
        if Aff[idx].sum() == targ:
            Reso += Aff[idx]
            reso_norm(Reso)
        # Im Umfeld einer 0 alles streichen
        elif targ == 0:
            Reso -= Aff[idx]
            reso_norm(Reso)
    return Reso

def single_targ(idx, Reso, targ, Aff):
    # Prüfen, ob im Umfeld einer Zahl bereits die richtige 
    # Anzahl an Kästchen ausgemalt ist, den Rest streichen
    print(Reso)
    AR = Aff[idx] * Reso
    AR[AR<0] = 0
    if AR.sum() == targ:
        Reso += AR - Aff[idx]
        reso_norm(Reso)
        return Reso
    # Prüfen, ob im Umfeld einer Zahl bereits die richtige 
    # Anzahl an Kästchen gestrichen ist, den Rest ausmalen
    AR = Aff[idx] * Reso
    AR[AR>0] = 0
    if AR.sum() == (targ - Aff[idx].sum()):
        Reso += AR + Aff[idx]
        reso_norm(Reso)
    return Reso

def find_neighbors(Targ, Coord):
    Neigh = []
    for idx, targ in enumerate(Targ):
        Neigh.append([])
        for kdx, neigh in enumerate(Targ):
            if ((kdx is not idx)
                and Coord[kdx][0] in range(Coord[idx][0]-2,Coord[idx][0]+3)
                and Coord[kdx][1] in range(Coord[idx][1]-2,Coord[idx][1]+3)
                ):
                Neigh[idx].append(kdx)
#       print(idx,' ',targ,' ',Coord[idx],' ',Neigh[idx])
    return Neigh

def neighbors(idx, Reso, Targ, Aff, Neigh):
    for neigh in Neigh[idx]:
        # Prüfen, dass Nachbar nur noch Unbekannte im gem. Bereich hat
        aff_diff = Aff[neigh] - Aff[idx]
        aff_diff[aff_diff<0] = 0
        peri = (np.ones(np.shape(Reso)) - aff_diff) * 2
        if 0 not in (Reso + peri):
            # Anzahl der Felder im Umfeld von target außerhalb des 
            # gemeinsamen Bereichs
            own_aff = Aff[idx] - Aff[neigh]
            own_aff[own_aff<=0] = 0
            if own_aff.sum() == Targ[idx] - Targ[neigh]:
                Reso += own_aff
                reso_norm(Reso)
    return Reso

def solve(Reso,Targ,Coord,Aff,iter_max):
    state, counts = np.unique(Reso, return_counts=True)
    state_counts = dict(zip(state, counts))
    undef_counts = state_counts[0]
    print(undef_counts)
    Neigh = find_neighbors(Targ, Coord)
    Reso = init_single_targ(Reso, Targ, Aff)
    for iter in range(iter_max):
        for idx, targ in enumerate(Targ):
            Reso = single_targ(idx, Reso, targ, Aff)
            Reso = neighbors(idx, Reso, Targ, Aff, Neigh)
        if 0 not in Reso:
            print('Gelöst nach ',iter,' Iterationen.')
            break
        if (iter == iter_max - 1) and 0 in Reso:
            print('Nach ',iter+1,' Iterationen nicht gelöst.')
        state, counts = np.unique(Reso, return_counts=True)
        state_counts = dict(zip(state, counts))
        print(state_counts[0])
        if state_counts[0] == undef_counts:
            print('Nach ',iter+1,' Iterationen nicht gelöst.')
            break
        undef_counts = state_counts[0]

    return Reso
