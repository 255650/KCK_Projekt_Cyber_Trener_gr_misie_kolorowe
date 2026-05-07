def analizuj_przod(punkty):
    alerty = []

    lewy_bark = [punkty[11].x, punkty[11].y]
    prawy_bark = [punkty[12].x, punkty[12].y]
    lewe_biodro = [punkty[23].x, punkty[23].y]
    prawe_biodro = [punkty[24].x, punkty[24].y]
    lewe_kolano = [punkty[25].x, punkty[25].y]
    prawe_kolano = [punkty[26].x, punkty[26].y]
    lewa_kostka = [punkty[27].x, punkty[27].y]
    prawa_kostka = [punkty[28].x, punkty[28].y]

    szerokosc_bioder = abs(lewe_biodro[0] - prawe_biodro[0])
    szerokosc_stop = abs(lewa_kostka[0] - prawa_kostka[0])

    stosunek_rozkroku = szerokosc_stop / szerokosc_bioder

    if stosunek_rozkroku < 1.0:
        alerty.append("ROZKROK: Za wąsko! Rozstaw stopy szerzej niż biodra.")
    elif stosunek_rozkroku > 1.5:
        alerty.append("ROZKROK: Za szeroko! Zbliż stopy do siebie.")

    roznica_barkow = abs(lewy_bark[1] - prawy_bark[1])
    if roznica_barkow > 0.03:
        alerty.append("SYMETRIA: Barki nierówno! Wyrównaj linię ramion.")

    if lewe_kolano[0] > lewa_kostka[0]:
        alerty.append("KOLANA: Lewe kolano ucieka do środka!")
    if prawe_kolano[0] < prawa_kostka[0]:
        alerty.append("KOLANA: Prawe kolano ucieka do środka!")

    return alerty