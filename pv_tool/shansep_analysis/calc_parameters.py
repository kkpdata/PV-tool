from pandas import DataFrame

def calc_watergehalte_gem(df: DataFrame) -> float:
    """
    Geeft het gemiddelde watergehalte voor een DataFrame.
    """
    column_name = df.filter(like='WATERGEHALTE_VOOR').columns[0]
    watergehalte = df[column_name]
    return watergehalte.mean()

def calc_watergehalte_sd(df: DataFrame) -> float:
    """
    Geeft de standaarddeviatie van het watergehalte voor een DataFrame.
    """
    column_name = df.filter(like='WATERGEHALTE_VOOR').columns[0]
    watergehalte = df[column_name]
    return watergehalte.std()

def calc_vgwnat_gem(df: DataFrame) -> float:
    """
    Geeft het gemiddelde nat volumegewicht voor een DataFrame.
    """
    column_name = df.filter(like='VOLUMEGEWICHT_NAT').columns[0]
    vgwnat = df[column_name]
    return vgwnat.mean()

def calc_vgwnat_sd(df: DataFrame) -> float:
    """
    Geeft de standaarddeviatie van het nat volumegewicht voor een DataFrame.
    """
    column_name = df.filter(like='VOLUMEGEWICHT_NAT').columns[0]
    vgwnat = df[column_name]
    return vgwnat.std()
