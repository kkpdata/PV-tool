# Example of abstract classes: i.e. specify a required setup of child classes through the @abstractmethod

from abc import ABC, abstractmethod


class ImportObject(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def import_data(self):
        pass

    @abstractmethod
    def get_df_a(self):
        pass

    @abstractmethod
    def get_df_b(self):
        pass

    @abstractmethod
    def validate_data(self):
        pass


class ImportStowa(ImportObject):

    def __init__(self):
        super().__init__()

    def import_data(self):
        pass

    def get_df_a(self):
        pass

    def get_df_b(self):
        pass

    def validate_data(self):
        pass
