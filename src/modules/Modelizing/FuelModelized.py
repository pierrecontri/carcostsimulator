# Module FuelModelized.py

import pylab as pl
import inspect
from types import *
from copy import copy, deepcopy
from ObjectModelized import *
import logging

logger = logging.getLogger("CarCostSimulator")

class Fuel(ListManaged, XmlExp):
    """
    Class Fuel simulant les differents Fuels possibles
    """

    def __init__(self, fuelName = "NA", price = 0.0):
        ListManaged.__init__(self, fuelName)
        _price = 0.0
        self.price = price

    def __copy__(self):
        myClone = Fuel()
        myClone.name = self.name
        myClone.price = self.price
        return myClone

    def __deepcopy__(self, Memo = None):
        myClone = Fuel()
        myClone.name = self.name
        myClone.price = self.price
        return myClone

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        self._price = float(value)

    def getInfos(self):
        return (str(self) + ";" + str(self.price))

#do for tests
if __name__ == '__main__':
    pass