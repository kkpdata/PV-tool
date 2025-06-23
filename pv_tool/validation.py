# In deze file wil ik alle code opslaan wat betreft de validatie van de import
# Kijk in de file van Leo:
# C:\Users\deenekat7271\ARCADIS\30287614 - STOWA PV Tool - 05 Project execution\Deliverables\2. validatie
# welke kolommen we allemaal moeten valideren.

from typing import Optional
from pandas import DataFrame
# import pandas_schema.validation #TODO


class Validation:
    """In deze class staan alle functies die de validatie uitvoeren."""

    def __init__(self, dbase_df: Optional[DataFrame] = None):
        self.dbase_df = dbase_df

    def validate_txt(self):
        """Valideert of kolom 2 t/m 17 volledig is"""
        pass

    def check_txt(self):
        """Deze functie controleert of de triaxiaalproeven zijn uitgevoerd."""
        # of alles leeg dan geef terug False, of
        # check of kolom 2 t/m17 gevuld is. zo ja, geef terug in ALG_TRIAXIAAL = True
        # als 1 of meerdere ontbreken of foute data bevatten, geef warning.

    def check_naam_polder_dijk(self): # TODO: herschijven met pandas_schema
        """Deze functie controleert of de naam van de dijk is opgegeven, zo niet dan geeft hij een melding terug"""
        if self.dbase_df is not None:
            missing_name_mask = self.dbase_df['ALG_NAAM_POLDER_DIJK'].isnull()
            warnings = [
                f"Rij {idx}: ALG_NAAM_POLDER_DIJK is niet ingevuld"
                for idx in self.dbase_df.index[missing_name_mask]
            ]
            return warnings
        return []

    def nieuwe_functie(self):
        """jdjdksdnjdk"""

# TODO Nathan: Je kan helemaal los op alle validaties in het voorbeeldbestand van Leo. Elke validatie een eigen
    #  functie maken en toevoegen aan check_all. Mogelijk wordt de check_all dan straks wel mega groot maar we kunnen
    #  hem later misschien opsplitsen om het wat overzichtelijker te maken, per proef oid.

    def check_all(self):
        """Voert alle validaties uit"""
        warnings = []
        warnings.extend(self.check_naam_polder_dijk())
        return warnings
