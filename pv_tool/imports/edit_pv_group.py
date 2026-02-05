"""Een python file om een proevenverzameling groep (PVNaam) te veranderen

Input:
- een lijst met boring nummers (die bijvoorbeeld uit een omcirkeling in een functie komt)
- De dbase
- De nieuwe proevenverzameling naam (PVNaam)

Output:
- De aangepaste dbase met de nieuwe proevenverzameling naam voor de opgegeven boringen
"""


# TODO: Verder uitwerken
def edit_pv_group(boring_nummers, dbase, nieuwe_pv_naam):
    """
    Wijzigt de proevenverzameling naam voor de opgegeven boringen in de dbase.

    Parameters:
    boring_nummers (list): Lijst van boring nummers die aangepast moeten worden.
    dbase (dict): De database waarin de boringen zijn opgeslagen.
    nieuwe_pv_naam (str): De nieuwe proevenverzameling naam.

    Returns:
    dict: De aangepaste database met de nieuwe proevenverzameling naam.
    """
    oude_pv_naam = []
    for boring_nummer in boring_nummers:
        if boring_nummer in dbase:
            oude_pv_naam.append(dbase[boring_nummer]['PVNaam'])
            dbase[boring_nummer]['PVNaam'] = nieuwe_pv_naam
        else:
            print(f"Boring nummer {boring_nummer} niet gevonden in de database.")

    for i in range(len(oude_pv_naam)):
        print(
            f"De proevenverzameling naam van boring {boring_nummers[i]} is aangepast van {oude_pv_naam[i]} naar {nieuwe_pv_naam}.")

    oude_pv_naam_groepen = list(set(oude_pv_naam))  # Unieke oude namen
    print(
        f"WAARSCHUWING: er zijn groepen veranderd waarvan een eventueel uitgevoerde analyse niet meer klopt: {oude_pv_naam_groepen}")

    return dbase


# Voorbeeld gebruik
if __name__ == "__main__":
    # Voorbeeld database
    dbase = {
        'B001': {'PVNaam': 'GroepA', 'data': '...'},
        'B002': {'PVNaam': 'GroepB', 'data': '...'},
        'B003': {'PVNaam': 'GroepA', 'data': '...'},
    }

    # Lijst van boring nummers om aan te passen
    boring_nummers = ['B001', 'B003']

    # Nieuwe proevenverzameling naam
    nieuwe_pv_naam = 'GroepC'

    # Aanpassen van de database
    aangepaste_dbase = edit_pv_group(boring_nummers, dbase, nieuwe_pv_naam)

    # Resultaat tonen
    print(aangepaste_dbase)
