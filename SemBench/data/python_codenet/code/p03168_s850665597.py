def wczytaj_liste(): 
    wczytana_lista = input()
    lista_znakow = wczytana_lista.split()
    ostateczna_lista = []
    for element in lista_znakow:
        ostateczna_lista.append(int(element))
    return ostateczna_lista

def wczytaj_rzeczywiste():
    wczytana_lista = input()
    lista_znakow = wczytana_lista.split()
    ostateczna_lista = []
    for element in lista_znakow:
        ostateczna_lista.append(float(element))
    return ostateczna_lista

def rzuc_grosza_wiedzminowi_migusiem():
    N = wczytaj_liste()[0]
    prawdopodopienstwa = wczytaj_rzeczywiste()
    przed_rzutem = [1.0]
    for moneta in prawdopodopienstwa: 
        po_rzucie = []
        for i in range(len(przed_rzutem)):
            if i > 0: 
                po_rzucie.append(przed_rzutem[i]*(1-moneta)+przed_rzutem[i-1]*(moneta))
            else:
                po_rzucie.append(przed_rzutem[0]*(1-moneta))
        po_rzucie.append(przed_rzutem[-1]*moneta)
        przed_rzutem = po_rzucie
    odp = sum(przed_rzutem[N//2+1:])
    print(odp)
    
rzuc_grosza_wiedzminowi_migusiem()