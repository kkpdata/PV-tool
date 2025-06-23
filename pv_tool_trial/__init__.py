from __future__ import annotations
from typing import Optional
from plotly.graph_objects import Figure
import pandas as pd
import numpy as np


DUMMY_DF = pd.DataFrame({
    'verzameling': np.random.choice(['klei licht AL', 'klei licht Dijk', 'klei zwaar'], size=25),
    's': np.random.uniform(0, 100, size=25),
    't': np.random.uniform(0, 100, size=25)
})


class CPhi:

    def __init__(self, data: Data):
        self.data: Data = data

    def show_analysis(self):
        pass

    def graph(self) -> Figure:
        df = self.data.data_set.df_a
        print(df)
        return Figure()

    def plot_input_table(self):
        pass

    def plot_intermediate_data_table(self):
        pass

    def display_results(self):
        pass


class Analyses:

    def __init__(self, data: Data):
        self.data: Data = data

    def c_phi(self, verzameling: str) -> CPhi:
        pass


class DataGraphing:

    def __init__(self, data: Data):
        self.data: Data = data

    def s_t(self, verzameling: str) -> Figure:
        print(self.data.data_set.df_a, verzameling)
        return Figure()


class DataSet:

    def __init__(
            self,
            df_a: pd.DataFrame,
            df_b: pd.DataFrame,
            dict_a: dict,
            dict_b: dict,
    ):
        self.df_a: pd.DataFrame = df_a
        self.df_b: pd.DataFrame = df_b
        self.dict_a: dict = dict_a
        self.dict_b: dict = dict_b


class ImportData:

    def __init__(self, data: Data):
        self.data: Data = data

    def excel_stowa(self):
        self.data.data_set = DataSet(
            df_a=DUMMY_DF,
            df_b=DUMMY_DF,
            dict_a={},
            dict_b={},
            # And all other
        )

    def excel_pv_tool(self):
        self.data.stowa = DataSet(
            df_a=DUMMY_DF,
            df_b=DUMMY_DF,
            dict_a={},
            dict_b={},
        )


class DataFilters:

    def __init__(self, data: Data):
        self.data = data

    def s_t(self, verzameling: str) -> pd.DataFrame:
        df = self.data.data_set.df_a
        return df[df["verzameling"] == verzameling][["s", "t"]]


class Data:

    def __init__(self):

        self.data_set: Optional[DataSet] = None

        # Buttons
        self.import_data = ImportData(data=self)
        self.filters = DataFilters(data=self)
        self.graphing = DataGraphing(data=self)


class PVTool:

    def __init__(self):
        self.data = Data()
        self.analyses = Analyses(self.data)


tool = PVTool()

##

# Load data
tool.data.import_data.excel_pv_tool()
tool.data.import_data.excel_stowa()
print(tool.data.data_set.df_a)
print(tool.data.data_set.dict_a)

##

# Filter data (for instance used for graphs and analyses)
print(tool.data.filters.s_t(verzameling="klei licht AL"))

##

# Visualize data
tool.data.graphing.s_t(verzameling="klei licht AL").show()

##

# Analysis
c_phi = tool.analyses.c_phi(
    verzameling="klei",
    # And all other parameters we discussed earlier
)
c_phi.show_analysis()  # Shows all the below methods/properties
fig = c_phi.graph()
fig.show()
c_phi.plot_input_table()
c_phi.plot_intermediate_data_table()
c_phi.display_results()
