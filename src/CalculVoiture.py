#! /usr/bin/env python

from gi.repository import Gtk
#import pygtk
#pygtk.require('2.0')
#import gtk
#import gtk.glade
import gobject
from datetime import date
from copy import *
from types import *

import os
import os.path as pth
import sys
from subprocess import call, Popen

import inspect

#Get abs path about this file
absFilePath = pth.abspath(__file__)
#Get abs directory about this file
absFileDirectoryPath = pth.dirname(absFilePath)
#Join into this directory sub module directory
modulesPyc = pth.join(absFileDirectoryPath, 'modules')
#Calcul GUI path
gui_path = pth.join(absFileDirectoryPath, 'gui', 'CalculVoiture.glade')

#Default data directory
dataDir = pth.normpath(pth.join(absFileDirectoryPath, '..', 'data'))

#import owns application's modules
sys.path.append(modulesPyc)

import logging
import logging.config

logFile = "traceback_20111023.txt"
logConfigFile = 'logging_basil.conf'
#logging.config.fileConfig(logConfigFile)

loggermode = logging.INFO

#create logger
logger = logging.getLogger("CarCostSimulator")
logger.setLevel(loggermode)
#create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(loggermode)
#create formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
#add formatter to ch
ch.setFormatter(formatter)
#add ch to logger
logger.addHandler(ch)

#"application" code
#logger.debug("debug message")
#logger.info("info message")
#logger.warn("warn message")
#logger.error("error message")
#logger.critical("critical message")

#import zipfile module if exist
zipmodule = pth.join(modulesPyc, 'modelizing.zip')
if pth.exists(zipmodule):
	sys.path.append(zipmodule)

from Modelizing import *
from XmlCarManage import *


class winInterface(object):

	def __init__(self, datafilename = ""):
		global gui_path
		self._tmpObjCopy = None
		self._tmpObjEdit = None
		self._datafilename = datafilename
		self.widgets = gtk.glade.XML(gui_path)
		self.autoConnect()
		self.createTreeViews()
		self.dataLoader()
		self._treeviewselected = None

	def __getitem__(self, widgetName):
		return self.widgets.get_widget(widgetName)

	def autoConnect(self):
		events = {}
		for (itemName, value) in self.__class__.__dict__.items():
			if callable(value) and itemName.startswith('gtk_'):
				events[itemName[4:]] = getattr(self, itemName)
		self.widgets.signal_autoconnect(events)
		# main frame managment
		self['windowCalulVoiture'].connect('destroy', self.gtk_main_quit)
		self['windowCalulVoiture'].connect('delete-event', self.delete_event)
		self['windowEditCar'].connect('delete-event', self.delete_event)

	def createTreeViews(self):
		self.createTreeViewByName(Wearpart, 'wearparttreeview', True, [])
		self.createTreeViewByName(CostKm, 'coststreeview', False, [])

		# List of fuel, driver, classes car
		self.createModelForCombobox('comboboxFuel', self.renderer_print_ObjName)
		self.createModelForCombobox('comboboxDriver', self.renderer_print_ObjName)
		self.createModelForCombobox('objcombobox', self.renderer_print_ClassName)

		self.fillObjComboBox()
		return

	def createModelForCombobox(self, cbname, renderer_printing):
		if not self[cbname]:
			return
		self[cbname].set_model(gtk.ListStore(gobject.TYPE_PYOBJECT))
		cell = gtk.CellRendererText() 
		self[cbname].pack_start(cell, True) 
		self[cbname].set_cell_data_func(cell, renderer_printing)

	def fillObjComboBox(self):
		liststore = self['objcombobox'].get_model()

		if len(liststore) > 0:
			liststore.clear()

		for classObj in listClassSimulator: liststore.append([classObj])

	def alpha_or_num_sort(self, treemodel, iter1, iter2, userData = None):
		try:
			item1 = treemodel[iter1][0]
			item2 = treemodel[iter2][0]
			return cmp(item1, item2)
		except:
			return 0
		return

	def append_Column_ComboBox_Into_TreeView(self, treeviewname, idx, columnName, listElems):
		cell_renderer = gtk.CellRendererCombo()
		cell_renderer.set_property('editable', True)
		cell_renderer.set_property('has-entry', False)

		# append list choice elements
		modelCB = gtk.ListStore(str)
		for elem in listElems: modelCB.append([str(elem)])
		cell_renderer.set_property('model', modelCB)
		cell_renderer.set_property('text-column', 0)

		cell_renderer.connect('edited', self.edited_cb, (self[treeviewname], columnName))
		
		column = gtk.TreeViewColumn(columnName, cell_renderer)
		column.set_cell_data_func(cell_renderer, self.renderer_print_data, self[treeviewname])

		self[treeviewname].insert_column(column, idx)
		return

	def createTreeViewByName(self, treeviewobject, treeviewname = "", editable = True, objColName = []):
		objName = treeviewobject.__name__
		if treeviewname == "":
			treeviewname = objName.lower() + 'treeview'

		liststore = gtk.ListStore(object)
		self[treeviewname].connect('state-changed', self.widget_state_changed)
		self[treeviewname].set_model(liststore)
		#liststore.connect('row-deleted', eval('self.row' + treeviewname + '_deleted'))
		#liststore.connect('row-changed', eval('self.row' + treeviewname + '_changed'))
		#liststore.connect('row-inserted', self.rowobjtreeview_inserted)
		#liststore.connect('row-has-child-toggled', self.doAnything)
		#liststore.connect('rows-reordered', self.doAnything)

		# obtain a ModelFilter from our store
		#filtered = liststore.filter_new()

		# define the sortable condition for the ListStore
		liststore.set_sort_func(0, self.alpha_or_num_sort, None)
		liststore.set_default_sort_func(self.alpha_or_num_sort)

		# delete all of columns if exists
		columnsList = self[treeviewname].get_columns()
		if len(columnsList) > 0:
			for colObj in columnsList:
				self[treeviewname].remove_column(colObj)
		# delete items if exist
		self[treeviewname].get_model().clear()

		# Fill column's cells
		if len(objColName) == 0 :
			tmpMembers = inspect.getmembers(treeviewobject)
			for mbr in tmpMembers:
				propertyType = type(mbr[1])
				propertyName = mbr[0]

				# if the property is not a list of contents
				if propertyType.__name__ == "property":
					if propertyName.lower() == "name":
						objColName.insert(0, propertyName)
					else:
						objColName.append(propertyName)

		for colName in objColName:
			cell_renderer = gtk.CellRendererText()
			cell_renderer.set_property('editable', editable)
			#if editable:
			cell_renderer.connect('edited', self.edited_cb, (self[treeviewname], colName))
			column = gtk.TreeViewColumn(colName.title(), cell_renderer)
			column.set_cell_data_func(cell_renderer, self.renderer_print_data, self[treeviewname])
			self[treeviewname].append_column(column)

		return

	def widget_state_changed(self, source = None, event=None):
		logger.debug("def widget_state_changed " + str(source))

	def renderer_print_data(self, column, cell_renderer, mod, itr, user_data = None):
		#logger.debug("renderer_print_data " + str(column) + " " + str(cell_renderer) + " " + str(mod) + " " + str(iter) + " " + str(user_data))
		obj = mod[itr][0]
		if not obj:
			return

		if hasattr(mod[itr][0], column.get_title().lower()):
			cell_renderer.set_property('text', getattr(mod[itr][0], column.get_title().lower()))
		else:
			if hasattr(mod[itr][0], "get" + column.get_title()):
				eval('self.renderer_print_Get' + column.get_title() + '(column, cell_renderer, mod, itr, user_data)')
		return

	def renderer_print_GetInfos(self, column, cell_renderer, mod, itr, user_data = None):
		if mod[itr][0]:
			cell_renderer.set_property('text', mod[itr][0].getInfos())
		return

	def renderer_print_ObjName(self, column, cell_renderer, mod, itr, user_data = None):
		if mod[itr][0]:
		 cell_renderer.set_property('text', mod[itr][0].name)
		return

	def renderer_print_ClassName(self, column, cell_renderer, mod, itr, user_data = None):
		if mod[itr][0]:
		 cell_renderer.set_property('text', mod[itr][0].__name__)
		return

	def doAnything(self, cell = None, path = -1, new_text = "", user_data = None):
		#logger.debug("doAnything " + str(cell) + " " + str(path) + " " + str(new_text) + " " + str(user_data))
		pass

	def edited_cb(self, cell, path, new_text, user_data = None):
		if user_data == None:
			return
		try:
			treeview, propertyName = user_data
			#liststore = treeview.get_model()
			# Get object
			tmpObj = treeview.get_model()[path][0]
			# put new value into propertyname's object
			setattr(tmpObj, propertyName.lower(), new_text)
		except:
			logger.warning("def edited_cb() : " + str(sys.exc_info()))
		return

	def fillObjTreeView(self, listObj, treeviewname):
		if not self[treeviewname]:
			logger.info("def fillObjTreeView: no '" + treeviewname + "' declared")
			return

		logger.debug("def fillObjTreeView('" + str(listObj) + "', " + treeviewname + ")")
		modelLS = self[treeviewname].get_model()
		modelLS.clear()

		for itm in listObj: modelLS.append([itm])
		modelLS.set_sort_column_id(0, gtk.SORT_ASCENDING)
		return

	def gtk_newFile(self, source = None, event = None):
		self.clearAllData()
		self._datafilename = ""
		logger.info("New File")
		return

	def clearAllData(self, clearObjects = True):
		# unselect objcombobox
		self['objcombobox'].set_active(-1)
		for objname in ['objtreeview', 'coststreeview']:
			modelLS = self[objname].get_model()
			if not modelLS is None:
				modelLS.clear()
		# clear objects
		if clearObjects == True:
			for objType in listClassSimulator:
				try:
					if hasattr(objType, 'clearObj'):
						resp = objType.clearObj()
						logger.debug("def clearAllData(); objType.clearObj(" + str(objType) + ")  ==>  " + str(resp))
				except:
					logger.warning("def clearAllData : " + str(objType))

		self['labelCosts'].set_text("Costs")
		return

	def gtk_openFile(self, source = None, event = None):
		global dataDir
		dialog = gtk.FileChooserDialog("Open ...", None, gtk.FILE_CHOOSER_ACTION_OPEN, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		dialog.set_current_folder(dataDir)
		dialog.set_default_response(gtk.RESPONSE_OK)

		filter = gtk.FileFilter()
		filter.set_name("XmlData")
		filter.add_mime_type("data/xml")
		filter.add_pattern("*.xml")
		dialog.add_filter(filter)

		filter = gtk.FileFilter()
		filter.set_name("All files")
		filter.add_pattern("*")
		dialog.add_filter(filter)

		response = dialog.run()
		dialog.hide()
		if response == gtk.RESPONSE_OK:
			self.dataLoader(dialog.get_filename())
		elif response == gtk.RESPONSE_CANCEL:
			logger.info('Closed, no files selected')
		dialog.destroy()
		return

	def gtk_saveFile(self, source = None, event = None):
		if self._datafilename == "":
			self.gtk_saveAsFile()
		else:
			XmlCarManage.ExportDataToXML(self._datafilename)
			logger.info("File '" + self._datafilename + "' saved")
		return

	def gtk_saveAsFile(self, source = None, event = None):
		global dataDir
		dialog = gtk.FileChooserDialog("Save ...", None, gtk.FILE_CHOOSER_ACTION_SAVE, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE, gtk.RESPONSE_OK))
		dialog.set_current_folder(dataDir)
		dialog.set_default_response(gtk.RESPONSE_OK)

		filter = gtk.FileFilter()
		filter.set_name("XmlData")
		filter.add_mime_type("data/xml")
		filter.add_pattern("*.xml")
		dialog.add_filter(filter)

		filter = gtk.FileFilter()
		filter.set_name("CsvData")
		filter.add_mime_type("data/csv")
		filter.add_pattern("*.csv")
		dialog.add_filter(filter)

		filter = gtk.FileFilter()
		filter.set_name("TxtData")
		filter.add_mime_type("data/txt")
		filter.add_pattern("*.txt")
		dialog.add_filter(filter)

		filter = gtk.FileFilter()
		filter.set_name("All files")
		filter.add_pattern("*")
		dialog.add_filter(filter)

		saveFile = False
		response = dialog.run()
		tmpFileName = ""
		if response == gtk.RESPONSE_OK:
			tmpFileName = dialog.get_filename()

			if not pth.exists(tmpFileName):
				saveFile = True
			else:
				msgBox = gtk.MessageDialog(parent=None, flags=0, type=gtk.MESSAGE_QUESTION, buttons=gtk.BUTTONS_YES_NO, message_format=None)
				msgBox.set_markup("The file '" + tmpFileName + "' already exists.\nDo you want to replace it ?")
				resp2 = msgBox.run()
				msgBox.hide()
				if resp2 == gtk.RESPONSE_YES:
					saveFile = True
				msgBox.destroy()
		elif response == gtk.RESPONSE_CANCEL:
			logger.info('Closed, no files selected')
		dialog.hide()
		dialog.destroy()
		# Exports XmlData to tmpFileName
		if saveFile:
			self._datafilename = tmpFileName
			XmlCarManage.ExportDataToXML(self._datafilename)
			logger.info("File saved as '" + tmpFileName + "'")
		return

	def gtk_on_objcombobox_changed(self, source = None, event = None, userData = None):
		logger.debug("def gtk_on_objcombobox_changed : " + str(source))

		model = source.get_model()
		active = source.get_active()
		if active < 0:
			#clear Costs views
			try:
				self['labelCosts'].set_text("Costs")
				modelLS = self['coststreeview'].get_model()
				if not modelLS is None:
					modelLS.clear()
			except:
				pass
			return

		classObj = model[active][0]

		if classObj is Car:
			self.createTreeViewByName(classObj, "objtreeview", False, ["Name", "Infos"])
		elif classObj is Driver:
			self.createTreeViewByName(classObj, "objtreeview", True, ["Name", "Kmperyear", "Maxkilometers"])
			if hasattr(Drivertype, "arrayObj"):
				self.append_Column_ComboBox_Into_TreeView("objtreeview", 1, "Drivertype", Drivertype.arrayObj.values())
			else:
				self.append_Column_ComboBox_Into_TreeView("objtreeview", 1, "Drivertype", [])
		else:
			self.createTreeViewByName(classObj, "objtreeview", True, [])
		logger.debug("self.fillObjTreeView(classObj.arrayObj) : " + str(classObj))

		if hasattr(classObj, 'arrayObj'):
			self.fillObjTreeView(classObj.arrayObj.values(), "objtreeview")

		return

	def gtk_on_treeviews_row_activated(self, source = None, event = None, userData = None):
		# double clic
		selectingRow = source.get_selection()
		if not selectingRow:
			return
		model, iter = selectingRow.get_selected()
		obj = model[iter][0]

		if type(obj) is Car:
			# copy obj for work with rollback
			self._tmpObjEdit = deepcopy(obj)

			self.fillEditableCarWindow(self._tmpObjEdit)
			self['windowEditCar'].run()
			#self['windowEditCar'].hide()
			# update data model
			self.gtk_on_treeviews_cursor_changed(source, event, None)
		return

	def fillEditableCarWindow(self, carSelected = None):
		# fill all properties
		tmpMembers = inspect.getmembers(carSelected.__class__)
		for mbr in tmpMembers:
			propertyType = type(mbr[1])
			propertyName = mbr[0]
			propertyObj = carSelected.__getattribute__(propertyName)

			# if the property is not a list of contents
			if propertyType.__name__ == "property" and type(propertyObj) is not ListType:
				entryName = 'entry' + str(propertyName).title()
				if self[entryName] is not None:
					self[entryName].set_text(str(propertyObj))

		# fill wearpart treeview
		self.fillObjTreeView(self._tmpObjEdit.Wearparts, 'wearparttreeview')

		# fill the two combobox
		self.fillComboBoxObj(Fuel.arrayObj.values(), 'comboboxFuel')
		self.fillComboBoxObj(Driver.arrayObj.values(), 'comboboxDriver')

		# check into the fuel list witch kind of fuel is
		logger.debug("def fillEditableCarWindow " + str(type(carSelected.fuel)))
		self.activeItemCombobox(carSelected.fuel, 'comboboxFuel')
		self.activeItemCombobox(carSelected.driver, 'comboboxDriver')

		return

	def activeItemCombobox(self, searchObj, comboboxname):
		getObj = lambda modelObj : str(modelObj[0])
		# get the name / object
		listObj = map(getObj, self[comboboxname].get_model())
		searchObj = str(searchObj)
		if searchObj in listObj:
			self[comboboxname].set_active(listObj.index(searchObj))
		else:
			logger.info("def activeItemCombobox: " + searchObj + " not found into " + comboboxname)
		return

	def fillComboBoxObj(self, listObj, comboboxname):
		model = self[comboboxname].get_model()
		model.clear()
		for itm in listObj: model.append([itm])
		return

	#def gtk_on_objtreeview_columns_changed(self, source = None, event = None):
	#	print "def gtk_on_objtreeview_columns_changed(" + str(source) + ")"
	#	return

	def gtk_on_buttonValidateCar_clicked(self, source = None, event = None):
		selectingRow = self._treeviewselected.get_selection()
		model, iter = selectingRow.get_selected()
		obj = model[iter][0]

		if type(obj) is not Car:
			logger.info("def gtk_on_buttonValidateCar_clicked(); No Car type for object : '" + str(obj) + "'")
			return

		# get all members in Car class
		tmpMembers = inspect.getmembers(self._tmpObjEdit.__class__)
		for mbr in tmpMembers:
			propertyType = type(mbr[1])
			propertyName = mbr[0]
			propertyObj = self._tmpObjEdit.__getattribute__(propertyName)

			# if the property is not a list of contents
			if propertyType.__name__ == "property" and type(propertyObj) is not ListType:
				entryName = 'entry' + str(propertyName).title()
				if self[entryName] is not None:
					if hasattr(self._tmpObjEdit, propertyName):
						setattr(self._tmpObjEdit, propertyName, self[entryName].get_text())

		# get Fuel type and driver type
		tpNames = ['fuel', 'driver']
		for tpName in tpNames:
			cbName = 'combobox' + tpName.title()
			tmpmodel = self[cbName].get_model()
			iterActiv = self[cbName].get_active_iter()
			if iterActiv:
				setattr(self._tmpObjEdit, tpName, str(tmpmodel[iterActiv][0]))

		# refresh calc cost
		self._tmpObjEdit.refreshCalc()
		# replace Car object into Car list
		Car.updateObj(obj, self._tmpObjEdit)

		# replace Car object into treeview
		#model.set_value(iter, 0, self._tmpObjEdit)
		# refresh treeview
		self.gtk_refreshData(None, None)

		self._tmpObjEdit = None
		self['windowEditCar'].hide()
		return

	#def rowobjtreeview_changed(self, source = None, event = None, userData = None):
	#	#logger.debug("rowobjtreeview_changed " + str(source) + " " + str(event) + " " + str(userData))
	#	pass

	#def rowobjtreeview_inserted(self, source = None, event = None, userData = None):
	#	logger.debug("rowobjtreeview_inserted " + str(source) + " " + str(event) + " " + str(userData))
	#	return

	#def rowobjtreeview_deleted(self, source = None, event = None, userData = None):
	#	#logger.debug("rowobjtreeview_deleted " + str(source) + " " + str(event) + " " + str(userData))
	#	pass

	def gtk_on_buttonAddWearpart_clicked(self, source = None, event = None, userData = None):
		if userData == None:
			userData = Wearpart("newObj")

		self._tmpObjEdit.Wearparts.append(userData)

		modelWp = self['wearparttreeview'].get_model()
		modelWp.append([userData])

		logger.debug("def gtk_on_buttonAddWearpart_clicked")
		return

	def gtk_on_buttonSuppressWearpart_clicked(self, source = None, event = None, userData = None):
		rowselecting = self['wearparttreeview'].get_selection()
		model, iter = rowselecting.get_selected()

		objWearpart = model[iter][0]
		wpName = objWearpart.name
		idxWp = self._tmpObjEdit.Wearparts.index(objWearpart)
		if idxWp >= 0:
			del self._tmpObjEdit.Wearparts[idxWp]
			model.remove(iter)
			logger.info("Suppress Wearpart '" + wpName + "'")

		if self["buttonSuppressWearpart"]:
			self["buttonSuppressWearpart"].set_property('sensitive', False)
		return

	def gtk_on_treeviews_cursor_changed(self, source = None, event = None, userData = None):
		# data selected
		logger.debug("cursor_changed " + str(source) + " " + str(event) + " " + str(userData))
		self._treeviewselected = source

		selectingRow = source.get_selection()
		model, iter = selectingRow.get_selected()
		if not model or not iter:
			return
		obj = model[iter][0]
		if type(obj) is Car:
			# Get the new tmpObj
			self._tmpObjEdit = obj
			self.gtk_showGraph(source, event, obj)
			# view costs
			self.viewCosts(obj)

		# call event to activate edit menu
		self.activeEditMenu()
		return

	def gtk_on_wearparttreeview_cursor_changed(self, source = None, event = None, userData = None):
		if self["buttonSuppressWearpart"]:
			self["buttonSuppressWearpart"].set_property('sensitive', True)
		return

	def activeEditMenu(self):
		self.manageEditMenu(True)
		return

	def desactiveEditMenu(self):
		self.manageEditMenu(False)
		return

	def manageEditMenu(self, sensitiveValue = False):
		listEditableMenu = ["menuitemsuppress", "menuitemcopy", "menuitemcut"]
		# check if there is anything to paste
		# if there is it, please activate paste item menu
		if self["menuitempaste"]:
			self["menuitempaste"].set_property('sensitive', self._tmpObjCopy is not None)

		for tmpMenu in listEditableMenu:
			if self[tmpMenu]:
				self[tmpMenu].set_property('sensitive', sensitiveValue)
		return

	def gtk_main_quit(self, source = None, event = None):
		gtk.main_quit()

	def gtk_on_buttonCancelCar_clicked(self, source = None, event=None):
		if self['windowEditCar'] is not None:
			self['windowEditCar'].hide()

		if self._tmpObjCopy:
			self._tmpObjCopy = None

		return

	def delete_event(self, source = None, event=None):
		# don't destroy window -- just leave it hidden
		# for now .. fix later
		source.hide()
		return

	def viewCosts(self, objCar):
		logger.debug("def viewCosts")
		x_tab = range(0, Car.maxkilometers, Car.espacementKm)
		y_tab = objCar.Costs

		CostKm.arrayObj = []

		for idx in range(0, len(x_tab), 1):
			lgn = CostKm()
			lgn.km = x_tab[idx]
			lgn.price = y_tab[idx]
			CostKm.arrayObj.append(lgn)

		self['labelCosts'].set_text(objCar.name)
		self.fillObjTreeView(CostKm.arrayObj, "coststreeview")
		return

	def gtk_showGraph(self, source = None, event = None, UserData = None):
		if type(UserData) is not Car:
			return

		self['carcurve'].reset()
		self['carcurve'].set_range(0, Car.maxkilometers, 0, 50000)
		self['carcurve'].set_curve_type(gtk.CURVE_TYPE_FREE)
		self['carcurve'].set_vector(UserData.Costs)

		return

	def gtk_saveCalcul(self, source = None, event = None):
		global dataDir
		tmpPath = 'compCars_' + date.today().strftime("%y%m%d") + '.csv'
		tmpPath = pth.join(dataDir, 'results', tmpPath)
		CarModelized.sauvComparaisonCSV(tmpPath)
		self.processViewingFile(tmpPath)
		logger.info("Calculs saved")
		return

	def gtk_saveArrayText(self, source = None, event = None):
		global dataDir
		tmpPath = 'compCars_' + date.today().strftime("%y%m%d") + '.txt'
		tmpPath = pth.join(dataDir, 'results', tmpPath)
		CarModelized.sauvComparaisonText(tmpPath)
		self.processViewingFile(tmpPath)
		logger.info("Array Text saved")
		return

	def gtk_refreshData(self, source = None, event = None):
		# send new car calcul
		logger.debug("refresh data")
		# clear all viewing data
		self.clearAllData(False)
		# reload the first category
		self['objcombobox'].set_active(0)
		return

	def gtk_reloadData(self, source = None, event = None):
		msgBox = gtk.MessageDialog(parent=None, flags=0, type=gtk.MESSAGE_QUESTION, buttons=gtk.BUTTONS_YES_NO, message_format=None)
		msgBox.set_markup("Do you really want to reload the file '" + self._datafilename + "'. It will errase your actually work ?")
		reloadFile = msgBox.run() == gtk.RESPONSE_YES
		msgBox.hide()
		msgBox.destroy()

		if reloadFile:
			self.dataLoader()
			logger.info("Data reloaded")
		return

	def gtk_showCompared(self, source = None, event = None):
		if CarModelized.showCurves() == 0:
			msgBox = gtk.MessageDialog(parent=None, flags=0, type=gtk.MESSAGE_INFO, buttons=gtk.BUTTONS_OK, message_format=None)
			msgBox.set_markup('No data present !')
			msgBox.run()
			msgBox.hide()
			msgBox.destroy()
		return

	def gtk_showAbout(self, source = None, event = None):
		if self['aboutdialogapp'] != None:
			self['aboutdialogapp'].run()
			self['aboutdialogapp'].hide()
		else:
			logger.warning("Error creating widget about for 'def gtk_showAbout'")
		return

	def gtk_dataAppendNewObj(self, source = None, event = None, userData = None):
		objType = None
		idxType = 0
		try:
			idxType = self['objcombobox'].get_active()
			modelType = self['objcombobox'].get_model()
			objType = modelType[idxType][0]
		except:
			logger.warning("error on getting object type in gtk_dataAppendNewObj function")
			return

		# if there is no Type select, says it by pop-up
		if idxType < 0:
			# pop-up
			msgBox = gtk.MessageDialog(parent=None, flags=0, type=gtk.MESSAGE_INFO, buttons=gtk.BUTTONS_OK, message_format=None)
			msgBox.set_markup("Please, selecte one category before inserted object")
			msgBox.run()
			msgBox.hide()
			msgBox.destroy()
			logger.info("error on inserting new object without type model selected")
			return

		if userData is None:
			userData = objType("newObj")
			logger.debug("def gtk_dataAppendNewObj " + str(objType) + '("newObj")')

		# append new data into class array
		objType.appendObj(userData)
		# refresh printed data
		self.gtk_on_objcombobox_changed(self['objcombobox'], None, None)
		self['objcombobox'].set_active(idxType)

		# select the new value
		getObj = lambda modelObj : str(modelObj[0])
		# get the name / object
		listObj = map(getObj, self['objtreeview'].get_model())
		self['objtreeview'].set_cursor(listObj.index(str(userData)))

		self['objtreeview'].get_model().set_default_sort_func(self.alpha_or_num_sort)

		#gtk_on_treeviews_cursor_changed
		logger.debug("def gtk_dataAppendNewObj append new " + userData.__class__.__name__.title())
		return

	def gtk_closeAbout(self, source = None, event = None):
		self['aboutdialogapp'].hide()
		return

	def gtk_dataCopy(self, source = None, event = None):
		selectingRow = self._treeviewselected.get_selection()
		result = selectingRow.get_selected()

		if result: #result could be None
			model, iter = result
			self._tmpObjCopy = model[iter][0]
			#self._tmpObjCopy.name += " (cpy)"

		logger.info("dataCopy " + str(self._tmpObjCopy))

		self.activeEditMenu()
		return

	def gtk_dataPaste(self, source = None, event = None):
		if self._tmpObjCopy is None:
			return

		tmpCpy = copy(self._tmpObjCopy)
		tmpCpy.name += " (cpy)"

		self.gtk_dataAppendNewObj(None, None, tmpCpy)
		logger.info("dataPaste " + str(tmpCpy))
		return

	def gtk_dataCut(self, source = None, event = None):
		self.gtk_dataCopy(source, event)
		self.gtk_dataSuppress(source, event)
		logger.info("dataCut to tmp : " + str(self._tmpObjCopy))
		return

	def gtk_dataSuppress(self, source = None, event = None):
		if self._treeviewselected == None:
			return

		selectingRow = self._treeviewselected.get_selection()
		result = selectingRow.get_selected()

		if result: #result could be None
			model, iter = result

			objToRemove = model[iter][0]
			model.remove(iter)
			objToRemove.__class__.removeObj(objToRemove)
			self.desactiveEditMenu()

		return

	def dataLoader(self, datafilename = ""):
		# test filename
		if datafilename != "":
			self._datafilename = datafilename

		if self._datafilename == "" or not pth.exists(self._datafilename):
			self._datafilename = ""
			return

		# clear all data
		self.clearAllData()
		# load data contented in an other file
		XmlCarManage(self._datafilename)
		# select the first class into objcombobox
		self['objcombobox'].set_active(0)

		CarModelized.printCarsCompaired()
		Car.calcTabDiffAmortissements()
		return

	def processViewingFile(self, filename):
		os.system('"' + filename + '"')
		#Popen('"' + filename + '"', bufsize=0, executable=None, stdin=None, stdout=None, stderr=None, preexec_fn=None, close_fds=False, shell=False, cwd=None, env=None, universal_newlines=False, startupinfo=None, creationflags=0)

### main

if __name__ == '__main__':
	#return_code = call("echo Hello World", shell=True)
	#print return_code
	#Popen('\"C:\\Program Files (x86)\\OpenOffice.org 3\\program\\soffice.exe\" \"C:\\Users\\Pierre\\Documents\\Info\\CalculVoiture\\data\\results\\compCars_110920.csv\"')
	#os.system('C:\\Users\\Pierre\\Documents\\Info\\CalculVoiture\\data\\results\\compCars_110920.csv')
	#fu = Fuel("NA")
	#print fu
	fileName = ""
	if len(sys.argv) > 1:
		fileName = sys.argv[1]
	mainWindow = winInterface(fileName)
	gtk.main()