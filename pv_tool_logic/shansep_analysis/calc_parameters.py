from pandas import DataFrame
import numpy as np


def calc_watergehalte_gem_txt(df: DataFrame) -> float:
    """
    Berekent het gemiddelde watergehalte voor TXT-analyses.

    Parameters
    ----------
    df : DataFrame
        DataFrame met TXT-data

    Returns
    -------
    float
        Gemiddelde watergehalte of NaN als geen geldige data beschikbaar is
    """
    try:
        if 'TXT_SS_WATERGEHALTE_VOOR' not in df.columns:
            return np.nan

        watergehalte = df['TXT_SS_WATERGEHALTE_VOOR']

        numeric_values = watergehalte.dropna()
        numeric_values = numeric_values[numeric_values != '']
        numeric_values = numeric_values.apply(
            lambda x: float(x)
            if isinstance(x,
                          (int, float, str)) and str(x).replace('.', '').replace('-', '').isdigit()
            else np.nan).dropna()

        return numeric_values.mean() if len(numeric_values) > 0 else np.nan
    except KeyError:
        # Handle missing column
        return np.nan
    except ValueError:
        # Handle invalid data conversion
        return np.nan


def calc_watergehalte_sd_txt(df: DataFrame) -> float:
    """
    Berekent de standaarddeviatie van het watergehalte voor TXT-analyses.

    Parameters
    ----------
    df : DataFrame
        DataFrame met TXT-data

    Returns
    -------
    float
        Standaarddeviatie watergehalte of NaN als geen geldige data beschikbaar is
    """
    try:
        if 'TXT_SS_WATERGEHALTE_VOOR' not in df.columns:
            return np.nan

        watergehalte = df['TXT_SS_WATERGEHALTE_VOOR']

        numeric_values = watergehalte.dropna()
        numeric_values = numeric_values[numeric_values != '']
        numeric_values = numeric_values.apply(
            lambda x: float(x)
            if isinstance(x, (int, float, str))
            and str(x).replace('.', '').replace('-', '').isdigit() else np.nan).dropna()
        return numeric_values.std() if len(numeric_values) > 1 else np.nan
    except KeyError:
        # Handle missing column
        return np.nan
    except ValueError:
        # Handle invalid data conversion
        return np.nan


def calc_vgwnat_gem_txt(df: DataFrame) -> float:
    """
    Berekent het gemiddelde volumegewicht nat voor TXT-analyses.

    Parameters
    ----------
    df : DataFrame
        DataFrame met TXT-data

    Returns
    -------
    float
        Gemiddelde volumegewicht nat of NaN als geen geldige data beschikbaar is
    """
    try:
        if 'TXT_SS_VOLUMEGEWICHT_NAT' not in df.columns:
            return np.nan

        vgwnat = df['TXT_SS_VOLUMEGEWICHT_NAT']

        numeric_values = vgwnat.dropna()
        numeric_values = numeric_values[numeric_values != '']
        numeric_values = numeric_values.apply(
            lambda x: float(x)
            if isinstance(x, (int, float, str))
            and str(x).replace('.', '').replace('-', '').isdigit() else np.nan).dropna()
        return numeric_values.mean() if len(numeric_values) > 0 else np.nan
    except KeyError:
        # Handle missing column
        return np.nan
    except ValueError:
        # Handle invalid data conversion
        return np.nan


def calc_vgwnat_sd_txt(df: DataFrame) -> float:
    """
    Berekent de standaarddeviatie van het volumegewicht nat voor TXT-analyses.

    Parameters
    ----------
    df : DataFrame
        DataFrame met TXT-data

    Returns
    -------
    float
        Standaarddeviatie volumegewicht nat of NaN als geen geldige data beschikbaar is
    """
    try:
        if 'TXT_SS_VOLUMEGEWICHT_NAT' not in df.columns:
            return np.nan

        vgwnat = df['TXT_SS_VOLUMEGEWICHT_NAT']

        numeric_values = vgwnat.dropna()
        numeric_values = numeric_values[numeric_values != '']
        numeric_values = numeric_values.apply(
            lambda x: float(x)
            if isinstance(x, (int, float, str))
            and str(x).replace('.', '').replace('-', '').isdigit() else np.nan).dropna()
        return numeric_values.std() if len(numeric_values) > 1 else np.nan
    except KeyError:
        # Handle missing column
        return np.nan
    except ValueError:
        # Handle invalid data conversion
        return np.nan


def calc_watergehalte_gem_dss(df: DataFrame) -> float:
    """
    Berekent het gemiddelde watergehalte voor DSS-analyses.

    Parameters
    ----------
    df : DataFrame
        DataFrame met DSS-data

    Returns
    -------
    float
        Gemiddelde watergehalte of NaN als geen geldige data beschikbaar is
    """
    try:
        if 'DSS_WATERGEHALTE_VOOR' not in df.columns:
            return np.nan

        watergehalte = df['DSS_WATERGEHALTE_VOOR']

        numeric_values = watergehalte.dropna()
        numeric_values = numeric_values[numeric_values != '']
        numeric_values = numeric_values.apply(
            lambda x: float(x)
            if isinstance(x, (int, float, str))
            and str(x).replace('.', '').replace('-', '').isdigit() else np.nan).dropna()
        return numeric_values.mean() if len(numeric_values) > 0 else np.nan
    except KeyError:
        # Handle missing column
        return np.nan
    except ValueError:
        # Handle invalid data conversion
        return np.nan


def calc_watergehalte_sd_dss(df: DataFrame) -> float:
    """
    Berekent de standaarddeviatie van het watergehalte voor DSS-analyses.

    Parameters
    ----------
    df : DataFrame
        DataFrame met DSS-data

    Returns
    -------
    float
        Standaarddeviatie watergehalte of NaN als geen geldige data beschikbaar is
    """
    try:
        if 'DSS_WATERGEHALTE_VOOR' not in df.columns:
            return np.nan

        watergehalte = df['DSS_WATERGEHALTE_VOOR']

        numeric_values = watergehalte.dropna()
        numeric_values = numeric_values[numeric_values != '']
        numeric_values = numeric_values.apply(
            lambda x: float(x)
            if isinstance(x, (int, float, str))
            and str(x).replace('.', '').replace('-', '').isdigit() else np.nan).dropna()
        return numeric_values.std() if len(numeric_values) > 1 else np.nan
    except KeyError:
        # Handle missing column
        return np.nan
    except ValueError:
        # Handle invalid data conversion
        return np.nan


def calc_vgwnat_gem_dss(df: DataFrame) -> float:
    """
    Berekent het gemiddelde volumegewicht nat voor DSS-analyses.

    Parameters
    ----------
    df : DataFrame
        DataFrame met DSS-data

    Returns
    -------
    float
        Gemiddelde volumegewicht nat of NaN als geen geldige data beschikbaar is
    """
    try:
        if 'DSS_VOLUMEGEWICHT_NAT' not in df.columns:
            return np.nan

        vgwnat = df['DSS_VOLUMEGEWICHT_NAT']

        numeric_values = vgwnat.dropna()
        numeric_values = numeric_values[numeric_values != '']
        numeric_values = numeric_values.apply(
            lambda x: float(x)
            if isinstance(x, (int, float, str))
            and str(x).replace('.', '').replace('-', '').isdigit() else np.nan).dropna()
        return numeric_values.mean() if len(numeric_values) > 0 else np.nan
    except KeyError:
        # Handle missing column
        return np.nan
    except ValueError:
        # Handle invalid data conversion
        return np.nan


def calc_vgwnat_sd_dss(df: DataFrame) -> float:
    """
    Berekent de standaarddeviatie van het volumegewicht nat voor DSS-analyses.

    Parameters
    ----------
    df : DataFrame
        DataFrame met DSS-data

    Returns
    -------
    float
        Standaarddeviatie volumegewicht nat of NaN als geen geldige data beschikbaar is
    """
    try:
        if 'DSS_VOLUMEGEWICHT_NAT' not in df.columns:
            return np.nan

        vgwnat = df['DSS_VOLUMEGEWICHT_NAT']

        numeric_values = vgwnat.dropna()
        numeric_values = numeric_values[numeric_values != '']
        numeric_values = numeric_values.apply(
            lambda x: float(x)
            if isinstance(x, (int, float, str))
            and str(x).replace('.', '').replace('-', '').isdigit() else np.nan).dropna()
        return numeric_values.std() if len(numeric_values) > 1 else np.nan
    except KeyError:
        # Handle missing column
        return np.nan
    except ValueError:
        # Handle invalid data conversion
        return np.nan
