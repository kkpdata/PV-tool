# Deze file gaan we gebruiken om alle imports te doen die nodig zijn om de PV-tool te draaien.
# Dus de stowa of een oude PV-tool (mogelijk nog andere dingen in de toekomst)
# We moeten zorgen dat we ondanks de verschillende bronnen 1 eindproduct krijgen,
# dus 1 database met allemaal dezelfde kolommen

from pandas import Dataframe



class Dbase:
    """Deze class bevat alle functies die te maken hebben met het bouwen de Dbase-dataframe"""

    def __init__(self, stowa_df: DataFrame):