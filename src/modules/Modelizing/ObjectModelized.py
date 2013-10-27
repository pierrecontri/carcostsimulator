# Module ObjectModelized.py

import pylab as pl
import inspect
from types import *
from copy import copy, deepcopy
import logging

logger = logging.getLogger("CarCostSimulator")

#To transform in interface (with Python update 3)
#Now, compatible to Python 2.6
class XmlExp(object):

    def __init__(self):
        pass

    def XmlExport(self, indent = 0, objID = -1):
        if objID == -1:
            objID = id(self)
        data = "<" + self.__class__.__name__ + " id=\"" + str(objID).rjust(2, '0') + "\" name=\"" + str(self) + "\">"
        xmltxt = data.rjust(len(data) + indent, ' ') + "\n"
        tmpMembers = inspect.getmembers(self.__class__)

        for mbr in tmpMembers:
            propertyType = type(mbr[1])
            propertyName = str(mbr[0])
            propertyObj = self.__getattribute__(propertyName)

            # if the property is not a list of contents
            if propertyType.__name__ == "property" and type(propertyObj) is not ListType:
                data = "<" + propertyName + ">" + str(propertyObj) + "</" + propertyName + ">"
                xmltxt += data.rjust(len(data) + (indent + 2), ' ') + "\n"

            elif propertyType.__name__ == "property": # if it's a content list of objects
                tmpData = ""
                idxSubObj = 1
                for subobj in propertyObj:
                    if hasattr(subobj, 'XmlExport'):
                        #tmpData += subobj.XmlExport(indent + 4, idxSubObj) + "\n"
                        xmltxt += subobj.XmlExport(indent + 2, idxSubObj) + "\n"
                        idxSubObj += 1

                #if tmpData != "":
                    # parent ancrer
                    #data = "<" + propertyName + ">"
                    #xmltxt += data.rjust(len(data) + (indent + 2), ' ') + "\n"
                    # child ancrer
                    #xmltxt += tmpData
                    # end of parent ancrer
                    #data = "</" + propertyName + ">"
                    #xmltxt += data.rjust(len(data) + (indent + 2), ' ') + "\n"

        data = "</" + self.__class__.__name__ + ">"
        xmltxt += data.rjust(len(data) + indent, ' ')
        return xmltxt


class ListManaged(object):

    def __init__(self, name = "") :
        self._name = name
        if not hasattr(self.__class__, 'arrayObj'):
            setattr(self.__class__, 'arrayObj', {})

    def __str__(self):
        return self._name

    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, value):
        if type(self.__class__.arrayObj) is dict and self in self.__class__.arrayObj.values():
            # delete entry
            self.__class__.removeObj(self)
            # rename object
            self._name = value
            # adding with new key
            self.__class__.appendObj(self)
        else:
            self._name = value

    def __cmp__(self, itemCmp):
        return cmp(str(self).lower(), str(itemCmp).lower())

    @classmethod
    def appendObj(cls, newObj):
        if not hasattr(cls, "arrayObj"):
            return False

        cls.arrayObj[str(newObj)] = newObj
        logger.debug("Append " + str(newObj) + " of " + cls.__name__)

    @classmethod
    def updateObj(cls, oldObj, newObj):
        if not hasattr(cls, "arrayObj"):
            return False
        if str(oldObj) == str(newObj):
            cls.arrayObj[str(oldObj)] = newObj
        else:
            cls.removeObj(oldObj)
            cls.appendObj(newObj)

    @classmethod
    def removeObj(cls, objToRemove):
        if not hasattr(cls, "arrayObj"):
            return False

        objname = str(objToRemove)
        if cls.arrayObj.has_key(objname):
            logger.debug("Remove " + str(cls.arrayObj[objname]))
            del cls.arrayObj[objname]
            return True

        return False

    @classmethod
    def clearObj(cls):
        if not hasattr(cls, "arrayObj"):
            return False
        elif len(cls.arrayObj) == 0:
            return False

        cls.arrayObj.clear()
        return True

#do for tests
if __name__ == '__main__':
	pass