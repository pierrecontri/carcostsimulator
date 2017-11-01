# Module CarModelized.py

import pylab as pl
import inspect
from types import *
from copy import copy, deepcopy
from ObjectModelized import *
from FuelModelized import *
from DriverModelized import *
import sys
import logging

class CostKm(object):

    def __init__(self, kilometers = 0.0, price = 0.0):
        self.km = kilometers
        self.price = price

    def __cmp__(self, itemCmp):
        return cmp(self.km, itemCmp.km)

    @property
    def km(self):
        return self._km
    @km.setter
    def km(self, value):
        self._km = value

    @property
    def price(self):
        return self._price
    @price.setter
    def price(self, value):
        self._price = float(value)


class Wearpart(XmlExp):
    """
    Class permettant de simuler toute piece d'usure (couroie, filtres, ...)
    """

    def __init__(self, nomPiece, periodicity = 0.0, price = 0.0):
        self.name = nomPiece
        self.periodicity = periodicity
        self.price = price

    def __str__(self):
        return self._name

    def getInfos(self):
        return (str(self) + ";" + str(self.price) + ";" + str(self.periodicity))

    def __copy__(self, memo=None):
        myClone = Wearpart(self.name, self.periodicity, self.price)
        return myClone

    def __deepcopy__(self, memo=None):
        myClone = Wearpart(self.name, self.periodicity, self.price)
        return myClone

    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, value):
        self._name = value

    @property
    def periodicity(self):
        return (self._periodicity)
    @periodicity.setter
    def periodicity(self, value):
        self._periodicity = float(value)

    @property
    def price(self):
        return self._price
    @price.setter
    def price(self, value):
        self._price = float(value)


class Car(ListManaged, XmlExp):
    """
    Class Car simulant les principales caracteristiques de la Car
    en fonction du temps, de l'entretien et du cout general
    """

    # variables de classe
    maxkilometers = 301000
    espacementKm = 1000
    nbKmParAnnee = 47000
    maxSizeLengthName = 1
    ids = {}

    def __init__(self, carName = "newCar"):
        ListManaged.__init__(self, carName)
        self._price = 0.0
        self._costs = []
        self._wearparts = []
        self._fuel = None
        self._driver = None
        self._drivertype = None
        self._tanksize = 0.0
        self._insuranceprice = 0.0
        self._consumption = 0.0
        Car.ids[self._name] = -1

    def getInfos(self):
        infoFuel = ""
        if type(self.fuel) is Fuel:
            infoFuel = self.fuel.getInfos()
        else:
            infoFuel = str(self.fuel)
        return (str(self) + ";" + str(self.price) + ";" + str(self.consumption) + ";" + infoFuel)

    def __copy__(self):
        myClone = Car()
        myClone.name = self.name
        myClone.price = self.price
        myClone.Wearparts = copy(self.Wearparts)
        myClone.fuel = str(self.fuel)
        myClone.driver = str(self.driver)
        myClone.tanksize = self.tanksize
        myClone.insuranceprice = self.insuranceprice
        myClone.consumption = self.consumption

        return myClone

    def __deepcopy__(self, memo=None):
        myClone = Car()
        myClone.name = self.name
        myClone.price = self.price
        myClone.Wearparts = deepcopy(self.Wearparts)
        myClone.fuel = str(self.fuel)
        myClone.driver = str(self.driver)
        myClone.tanksize = self.tanksize
        myClone.insuranceprice = self.insuranceprice
        myClone.consumption = self.consumption

        return myClone

    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, value):
        self._name = value
        Car.ids[self.name] = -1
        if Car.maxSizeLengthName < len(self._name):
            Car.maxSizeLengthName = len(self._name)

    # prix d'achat de la Car
    @property
    def price(self):
        return self._price
    @price.setter
    def price(self, value):
        self._price = float(value)

    # fuel type
    @property
    def fuel(self):
        if self._fuel is None:
            return Fuel()
        elif type(self._fuel) is not Fuel:
            self.fuel = self._fuel
        return self._fuel
    @fuel.setter
    def fuel(self, value):
        try:
            if Fuel.arrayObj.has_key(str(value)):
                self._fuel = Fuel.arrayObj[str(value)]
            else:
                self._fuel = value
        except:
            self._fuel = value
            logger.warning("Car.fuel setter : " + str(sys.exc_info()))
        Car.ids[self.name] = -1
    @fuel.deleter
    def fuel(self):
        self._fuel = None

    # driver
    @property
    def driver(self):
        if self._driver is None:
            return Driver()
        elif type(self._driver) is not Driver:
            self.driver = self._driver
        return self._driver
    @driver.setter
    def driver(self, value):
        try:
            if hasattr(Driver, 'arrayObj') and Driver.arrayObj.has_key(str(value)):
                self._driver = Driver.arrayObj[str(value)]
            else:
                self._driver = value
            Car.ids[self.name] = -1
        except:
            self._driver = value
            logger.warning("Car.driver setter : " + str(sys.exc_info()))
    @driver.deleter
    def driver(self):
        self._driver = None

    # car consumption
    @property
    def consumption(self):
        return self._consumption
    @consumption.setter
    def consumption(self, value):
        self._consumption = float(value)

    # taille du reservoir
    @property
    def tanksize(self):
        return self._tanksize
    @tanksize.setter
    def tanksize(self, value):
        self._tanksize = float(value)

    # assurance par an
    @property
    def insuranceprice(self):
        return self._insuranceprice
    @insuranceprice.setter
    def insuranceprice(self, value):
        self._insuranceprice = float(value)

    # pieces d'usures
    @property
    def Wearparts(self):
        return self._wearparts
    @Wearparts.setter
    def Wearparts(self, value):
        del self.Wearparts
        self._wearparts = value
    @Wearparts.deleter
    def Wearparts(self):
        del self._wearparts[:]

    # Tableau des couts
    @property
    def Costs(self):
        tmpId = id(self) + id(self.fuel) + id(self.driver)
        if Car.ids[self.name] != tmpId:
            del self._costs[:]
            Car.ids[self.name] = tmpId
        if len(self._costs) == 0:
            self._costs = self.calculCouts()
        #extract only the cost part of CostKm object
        try:
            return [float(x.price) for x in self._costs]
        except:
            Car.ids[self.name] = -1
            return []

    def calculCouts(self):
        tmpCalc = []
        tmpCalc.append(CostKm(0.0,self.price))
        drivingcoef = 1.0
        # get driving coeeficient if it's possible
        if type(self.driver) is Driver:
            if type(self.driver.drivertype) is Drivertype:
                drivingcoef = self.driver.drivertype.drivingcoefficient
        if not type(tmpCalc[-1]) is CostKm:
            return []
        while tmpCalc[-1].km < Car.maxkilometers :
            previousCostKm = tmpCalc[-1]
            actualCostKm = CostKm(previousCostKm.km + Car.espacementKm, previousCostKm.price)
            # cout par kilometres
            if type(self.fuel) is Fuel:
                actualCostKm.price += Car.espacementKm * self.consumption / 100.0 * self.fuel.price * drivingcoef
            # calcul des prix des pieces d'usure (entretien, couroie, ...)
            for pceUsure in self.Wearparts :
                if pceUsure.periodicity != 0 and (actualCostKm.km % pceUsure.periodicity) == 0.0:
                    actualCostKm.price += pceUsure.price * drivingcoef
            # cout par annee assurance
            if ((actualCostKm.km + self.nbKmParAnnee) % self.nbKmParAnnee) == 0:
                actualCostKm.price += self.insuranceprice
            # ajout cout global
            tmpCalc.append(actualCostKm)
        return tmpCalc

    def refreshCalc(self):
        Car.ids[self.name] = -1
        return

    def __lt__(self, other):
        if type(self) == type(other):
            return self.Costs[-1] < other.Costs[-1]
        return False

    def __le__(self, other):
        if type(self) == type(other):
            return self == other or self < other
        return False

    def __gt__(self, other):
        if type(self) == type(other):
            return self.Costs[-1] > other.Costs[-1]
        return False

    def __ge__(self, other):
        if type(self) == type(other):
            return self == other or self > other
        return False

    def __eq__(self, other):
        if type(self) == type(other):
            return self.Costs[-1] == other.Costs[-1]
        return False

    def __ne__(self, other):
        if type(self) == type(other):
            return self.Costs[-1] != other.Costs[-1]
        return False

    def kmCmp(self, other):
        if type(self) != type(other):
            return False

        tmpCostsV1 = self.Costs
        tmpCostsV2 = other.Costs
        cmpVoit = cmp(self.price, other.price)
        idx = 1
        lenTabKm = Car.maxkilometers / Car.espacementKm
        if lenTabKm > len(tmpCostsV1) or lenTabKm > len(tmpCostsV2):
            return cmpVoit
        while idx < lenTabKm:
            cmpVoitTmp = cmp(tmpCostsV1[idx], tmpCostsV2[idx])
            if cmpVoit != cmpVoitTmp:
                return cmpVoitTmp * Car.espacementKm * idx
            idx += 1
        return cmpVoit

    @staticmethod
    def calcTabDiffAmortissements():
        if not hasattr(Car, 'arrayObj'):
            return [], {}

        if len(Car.arrayObj) <= 1:
            return [], {}

        tabAmortissement = []
        sizeOfMaxNameTabCar = Car.maxSizeLengthName

        matriceCars = {}
        for voit1 in Car.arrayObj.values():
            tabHorizon = {}
            for voit2 in Car.arrayObj.values():
                if True: #voit1 != voit2:
                    strCmpKm = ""
                    tmpKm = voit1.kmCmp(voit2)
                    if tmpKm > 0:
                        strCmpKm = ">"
                    elif tmpKm < 0:
                        strCmpKm = "<"
                    elif tmpKm == 0:
                        strCmpKm = "="
                    else:
                        strCmpKm = "!"
                    tabHorizon[str(voit2)] = tmpKm

                    strTmpKm = str(abs(tmpKm))
                    if strTmpKm == "1": strTmpKm = "/"
                    lineAmortissement = adjustCaract(voit1) + "  " + strCmpKm + "  " + adjustCaract(voit2) + "   ==>   " + strTmpKm.rjust(6)
                    tabAmortissement.append(lineAmortissement)
            matriceCars[str(voit1)] = tabHorizon
        return tabAmortissement, matriceCars

# globals lambda functions
adjustCaract = lambda objTemp: str(objTemp).ljust(Car.maxSizeLengthName)

def sauvComparaisonCSV(strFileName):
    fic = open(strFileName, "w")
    fic.write("Kilometres;" + ";".join(Car.arrayObj.keys()) + "\n")

    idx = 0
    lentab = Car.maxkilometers / Car.espacementKm
    while idx < lentab:
        fic.write(str(idx * Car.espacementKm) + ";")
        for voit in Car.arrayObj.values():
            fic.write(str(voit.Costs[idx]) + ";")
        fic.write("\n")
        idx +=1
    fic.close()

def printCarsCompaired():
    if not hasattr(Car, 'arrayObj'):
        return
    print("======== Liste des differentes voitures comparees ========")
    getCarInfos = lambda objCar: objCar.getInfos()
    carList = map(getCarInfos, Car.arrayObj.values())
    print("\n".join(carList))
    return

def showCurves():
    if not hasattr(Car, 'arrayObj') or len(Car.arrayObj) == 0:
        return False

    # creating absices line
    x = list(range(0, Car.maxkilometers + Car.espacementKm, Car.espacementKm))
    plotCurves = lambda objCar: pl.plot(x, objCar.Costs)
    map(plotCurves, Car.arrayObj.values())
    pl.xlabel = "Kilometers"
    pl.ylabel = "Cost"
    pl.show()
    pl.close()
    return True

def sauvComparaisonText(strFileName = ""):
    tabAmort, matriceCars = Car.calcTabDiffAmortissements()
    sizeOfMaxNameTabCar = Car.maxSizeLengthName

    fic = open(strFileName, "w")
    #header
    fic.write("Matrice de comparaison\n======================\n")
    strLigne = "| " + adjustCaract(" ") + " |"
    for voit1 in Car.arrayObj.keys():
        strLigne += "| " + adjustCaract(voit1) + " |"
    fic.write(strLigne + "\n")

    #content
    for voit1 in Car.arrayObj.keys():
        strLigne = "| " + adjustCaract(voit1) + " |"
        for voit2 in Car.arrayObj.keys():
            strLigne += "| " + adjustCaract((matriceCars[voit1])[voit2]) + " |"
        fic.write(strLigne + "\n")

    #header 2
    fic.write("\n\nComparaison Voitures\n====================\n")
    #content 2
    fic.write("\n".join(tabAmort))
    # close fic
    fic.close()

def main():
	fuelD = Fuel("diesel", 1.39)
	print fuelD.getInfos()
	Fuel.arrayObj[str(fuelD)] = fuelD
	skoda = Car("Skoda Fabia 1.4 TDI")
	skoda.price = 14800.0
	skoda.fuel = "diesel"
	skoda.consumption = 4.7
	skoda.tanksize = 43.0
	skoda.insuranceprice = 534.0
	skoda.Wearparts.append(Wearpart("Entretien", 15000, 120.0))
	skoda.Wearparts.append(Wearpart("Couroie", 90000, 750.0))
	print skoda.getInfos()
	print skoda.XmlExport()
	Car.appendObj(skoda)
	#Car.showCurves()

#do for tests
if __name__ == '__main__':
    main()