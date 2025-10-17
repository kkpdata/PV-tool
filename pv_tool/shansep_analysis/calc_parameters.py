import math
import numpy as np
from scipy.stats import linregress, norm
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pv_tool.shansep_analysis.shansep_analysis import SHANSEP

def calc_watergehalte_gem(self: SHANSEP):
    """Geeft gemiddelde watergehalte bij de geselecteerde pvnaam"""
    column_name = self.shansep_data_df.filter(like='WATERGEHALTE_VOOR').columns[0]
    watergehalte = self.shansep_data_df[column_name]
    return watergehalte.mean()

def calc_watergehalte_sd(self: SHANSEP):
    """Geeft standaard deviatie watergehalte bij de geselecteerde pvnaam"""
    column_name = self.shansep_data_df.filter(like='WATERGEHALTE_VOOR').columns[0]
    watergehalte = self.shansep_data_df[column_name]
    return watergehalte.std()

def calc_vgwnat_gem(self: SHANSEP):
    """Geeft gemiddelde nat volumegewicht bij de geselecteerde pvnaam [[[VOLUMEGEWICHT_NAT]]]"""
    column_name = self.shansep_data_df.filter(like='VOLUMEGEWICHT_NAT').columns[0]
    vgwnat = self.shansep_data_df[column_name]
    return vgwnat.mean()

def calc_vgwnat_sd(self: SHANSEP):
    """Geeft standaard deviatie nat volumegewicht bij de geselecteerde pvnaam"""
    column_name = self.shansep_data_df.filter(like='VOLUMEGEWICHT_NAT').columns[0]
    vgwnat = self.shansep_data_df[column_name]
    return vgwnat.std()