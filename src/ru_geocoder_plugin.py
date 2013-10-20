"""
/***************************************************************************
 RuGeocoder
                                 A QGIS plugin
 Geocode your csv files to shp
                              -------------------
        begin                : 2012-02-20
        copyright            : (C) 2012 by Nikulin Evgeniy
        email                : nikulin.e at gmail
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from os import path
import sys
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import QObject, SIGNAL, QSettings, QLocale, QFileInfo, QTranslator, QCoreApplication
from PyQt4.QtGui import QAction, QIcon
#from qgis.core import *
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from batch_geocoding_dialog import BatchGeocodingDialog
from converter_dialog import ConverterDialog


_fs_encoding = sys.getfilesystemencoding()
_current_path = unicode(path.abspath(path.dirname(__file__)), _fs_encoding)


class RuGeocoderPlugin:
    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        self.__converter_dlg = ConverterDialog()
        self.__geocoder_dlg = BatchGeocodingDialog()

        # i18n support
        override_locale = QSettings().value('locale/overrideFlag', False, type=bool)
        if not override_locale:
            locale_full_name = QLocale.system().name()
        else:
            locale_full_name = QSettings().value('locale/userLocale', '', type=unicode)

        self.locale_path = '%s/i18n/rugeocoder_%s.qm' % (_current_path, locale_full_name[0:2])
        if QFileInfo(self.locale_path).exists():
            self.translator = QTranslator()
            self.translator.load(self.locale_path)
            QCoreApplication.installTranslator(self.translator)

    def initGui(self):
        # Setup signals
        self.action_convert = QAction(QIcon(':/plugins/rugeocoderplugin/convert.png'),
                                      QCoreApplication.translate('RuGeocoder', 'Convert CSV to SHP'),
                                      self.iface.mainWindow())
        QObject.connect(self.action_convert, SIGNAL("triggered()"), self.run_convert)

        self.action_batch_geocoding = QAction(QIcon(':/plugins/rugeocoderplugin/icon.png'),
                                              QCoreApplication.translate('RuGeocoder', 'Batch geocoding'),
                                              self.iface.mainWindow())
        QObject.connect(self.action_batch_geocoding, SIGNAL('triggered()'), self.run_batch)

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action_convert)
        self.iface.addPluginToMenu('&RuGeocoder', self.action_convert)

        self.iface.addToolBarIcon(self.action_batch_geocoding)
        self.iface.addPluginToMenu('&RuGeocoder', self.action_batch_geocoding)

    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu('&RuGeocoder', self.action_convert)
        self.iface.removeToolBarIcon(self.action_convert)

        self.iface.removePluginMenu('&RuGeocoder', self.action_batch_geocoding)
        self.iface.removeToolBarIcon(self.action_batch_geocoding)

    def run_convert(self):
        if not self.__converter_dlg.isVisible():
            self.__converter_dlg = ConverterDialog()
            self.__converter_dlg.show()
            self.__converter_dlg.exec_()

    def run_batch(self):
        if not self.__geocoder_dlg.isVisible():
            self.__geocoder_dlg = BatchGeocodingDialog()
            self.__geocoder_dlg.show()
            self.__geocoder_dlg.exec_()
