import sys
import xml.parsers.expat
import inspect
from Modelizing import *
import os.path as pth

listClassSimulator = [Car, Fuel, Driver, Drivertype]

class XmlCarManage(object):

	getName = lambda classObj : classObj.__name__
	clsmembers = map(getName, listClassSimulator)

	def __init__(self, databaseFile = "", demomode = False):
		self.indent = 0
		self.tmpObject = None
		self.tmpParentObject = None
		self.actual_element = ""

		self.p = xml.parsers.expat.ParserCreate()
		if demomode:
			self.p.StartElementHandler = self.start_element_show
			self.p.EndElementHandler = self.end_element_show
			self.p.CharacterDataHandler = self.char_data_show
		else:
			self.p.StartElementHandler = self.start_element
			self.p.EndElementHandler = self.end_element
			self.p.CharacterDataHandler = self.char_data

		if databaseFile != "" and pth.exists(databaseFile):
			self.p.ParseFile(open(databaseFile))

    # 3 handler functions
	def start_element_show(self, name, attrs):
		# print 'Start element:', name, attrs
		outp = "<" + name
		for attr in attrs:
			outp += " " + attr + "='" + attrs[attr] + "'"
		outp += ">"
		print outp.rjust(len(outp) + self.indent, ' ')
		self.indent += 2

    # 3 handler functions
	def start_element(self, name, attrs):

		self.actual_element = name

		saveObj = not(attrs.has_key('visibility') and str(attrs['visibility']).lower() == 'hidden')

		formulEval = ""
		if not attrs.has_key('name'):
			formulEval = name + "()"
		else:
			formulEval = name + "('" + str(attrs['name']) + "')"

		tmpObject = None
		try:
			tmpObject = eval(formulEval)
		except:
			return

		if name in XmlCarManage.clsmembers:
			# root object, save into parent
			self.tmpParentObject = tmpObject

			if saveObj:
				try:
					if hasattr(tmpObject.__class__, "appendObj"):
						tmpObject.__class__.appendObj(tmpObject)
				except:
					print "Error in appening object"
		elif self.tmpParentObject is not None and hasattr(self.tmpParentObject, name + 's'):
			if saveObj:
				eval('self.tmpParentObject.' + name + 's.append(tmpObject)')
		# save temporary object
		self.tmpObject = tmpObject
		return

	def end_element_show(self, name):
		#print 'End element:', name
		outp = "</" + name + ">"
		self.indent -= 2
		print outp.rjust(len(outp) + self.indent, ' ')

	def end_element(self, name):
		if self.tmpObject == None:
			return
		#if we leave Wearparts objects, please back to Car
		if name == "Wearpart" and type(self.tmpObject) is Wearpart:
			self.tmpObject = self.tmpParentObject
		# quit object pointer if it's the end of this object
		if type(self.tmpObject).__name__ == name:
			self.tmpObject = None
		return

	def char_data_show(self, data):
		#print 'Character data:', repr(data)
		if len(data.strip()) > 0:
			print data.rjust(len(data) + self.indent, ' ')

	def char_data(self, data):
		if len(data.strip()) > 0:
			if self.tmpObject is not None and hasattr(self.tmpObject, self.actual_element):
				setattr(self.tmpObject, self.actual_element, data)

	@staticmethod
	def ExportDataToXML(strFileName):
		fic = open(strFileName, "w")
		fic.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<database>\n")

		# Export Cars, Drivers, and all classes
		#classList = [Fuel, Drivertype, Driver, Car]
		for objClass in listClassSimulator:
			if not hasattr(objClass, 'arrayObj'):
				continue
			elif len(objClass.arrayObj) == 0:
				continue

			typeArrayObj = type(objClass.arrayObj)
			for tmpObj in objClass.arrayObj:
				idxObj = -1
				objExp = None
				if typeArrayObj is list:
					idxObj = objClass.arrayObj.index(tmpObj) + 1
					objExp = tmpObj
				elif typeArrayObj is dict:
					idxObj = objClass.arrayObj.keys().index(tmpObj) + 1
					objExp = objClass.arrayObj[tmpObj]

				if idxObj > -1 and objExp is not None:
					fic.write(objExp.XmlExport(indent = 2, objID = idxObj) + "\n")

		fic.write("</database>")
		fic.close()

#Do for tests
if __name__ == '__main__':
	testXml = XmlCarManage("../../data/CarDatabase.xml", True)
	if len(Car.arrayObj) > 0:
		print Car.arrayObj
	if len(Fuel.arrayObj) > 0:
		print Fuel.arrayObj
