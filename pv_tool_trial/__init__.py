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
        df = self.data.stowa.df
        print(df)
        return Figure()

    def plot_input_table(self):
        pass

    def plot_intermediate_data_table(self):
        pass

    def display_results(self):
        pass


class Analyser:

    def __init__(self, data: Data):
        self.data: Data = data

    def c_phi(self, verzameling: str) -> CPhi:
        pass


class DataGraphing:

    def __init__(self, data: Data):
        self.data: Data = data

    def s_t(self, verzameling: str) -> Figure:
        print(self.data.stowa.df, verzameling)
        return Figure()


class Stowa:

    def __init__(self, df: pd.DataFrame):
        self.df: pd.DataFrame = df


class DataLoader:

    def __init__(self, data: Data):
        self.data: Data = data

    def excel_stowa(self):
        self.data.stowa = Stowa(
            df=DUMMY_DF
        )

    def excel_pv_tool(self):
        self.data.stowa = Stowa(
            df=DUMMY_DF
        )


class DataFilters:

    def __init__(self, data: Data):
        self.data = data

    def s_t(self, verzameling: str) -> pd.DataFrame:
        df = self.data.stowa.df
        return df[df["verzameling"] == verzameling][["s", "t"]]


class Data:

    def __init__(self):

        self.stowa: Optional[Stowa] = None

        # Buttons
        self.load = DataLoader(data=self)
        self.filters = DataFilters(data=self)
        self.graphing = DataGraphing(data=self)


class PVTool:

    def __init__(self):
        self.data = Data()
        self.analyser = Analyser(self.data)


tool = PVTool()

##

# Load data
tool.data.load.excel_pv_tool()
tool.data.load.excel_stowa()
print(tool.data.stowa.df)

##

# Filter data (for instance used for graphs and analyses)
print(tool.data.filters.s_t(verzameling="klei licht AL"))

##

# Visualize data
tool.data.graphing.s_t(verzameling="klei licht AL").show()

##

# Analysis
c_phi = tool.analyser.c_phi(
    verzameling="klei",
    # And all other parameters we discussed earlier
)
c_phi.show_analysis()  # Shows all the below methods/properties
fig = c_phi.graph()
fig.show()
c_phi.plot_input_table()
c_phi.plot_intermediate_data_table()
c_phi.display_results()
