# Module DriverModelized.py

import pylab as pl
import inspect
from types import *
from copy import copy, deepcopy
from ObjectModelized import *
import logging
import sys

logger = logging.getLogger("CarCostSimulator")


class Drivertype(ListManaged, XmlExp):

    def __init__(self, drivertypename = "builder"):
        ListManaged.__init__(self, drivertypename)
        self.drivingcoefficient = 1.0

    @property
    def drivingcoefficient(self):
        return self._drivingcoefficient
    @drivingcoefficient.setter
    def drivingcoefficient(self, value):
        self._drivingcoefficient = float(value)

class Driver(ListManaged, XmlExp):

    def __init__(self, driverName = "builder"):
        ListManaged.__init__(self, driverName)
        self.kmperyear = 0.0
        self.maxkilometers = 0.0
        self.drivertype = ""

    @property
    def drivertype(self):
        if self._drivertype is None:
            return Drivertype()
        elif type(self._drivertype) is not Drivertype:
            self.drivertype = self._drivertype
        return self._drivertype
    @drivertype.setter
    def drivertype(self, value):
        try:
            if hasattr(Drivertype, 'arrayObj') and Drivertype.arrayObj.has_key(str(value)):
                self._drivertype = Drivertype.arrayObj[str(value)]
            else:
                self._drivertype = value
        except:
            self._drivertype = value
            logger.warning("Driver.drivertype setter : " + str(sys.exc_info()))
    @drivertype.deleter
    def drivertype(self):
        self._drivertype = None

    @property
    def kmperyear(self):
        return self._kmPerYear
    @kmperyear.setter
    def kmperyear(self, value):
        self._kmPerYear = float(value)

    @property
    def maxkilometers(self):
        return self._maxkilometers
    @maxkilometers.setter
    def maxkilometers(self, value):
        self._maxkilometers = float(value)


#do for tests
if __name__ == '__main__':
	pass