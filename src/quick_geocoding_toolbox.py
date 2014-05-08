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
from urllib2 import URLError
#import sys

from PyQt4.QtGui import QDockWidget  # , QMessageBox
from PyQt4.QtCore import QThread, pyqtSignal

from geocoder_factory import GeocoderFactory

from ui_quick_geocoding_toolbox import Ui_QuickGeocodingToolbox


class QuickGeocodingToolbox(QDockWidget, Ui_QuickGeocodingToolbox):
    def __init__(self, iface):
        QDockWidget.__init__(self, iface.mainWindow())
        self.setupUi(self)
        
        self.iface = iface
        self.search_threads = None  # []

        if hasattr(self.txtSearch, 'setPlaceholderText'):
            self.txtSearch.setPlaceholderText(self.tr("Address..."))

        self.txtSearch.textChanged.connect(self.start_geocode)
        self.cmbGeocoder.currentIndexChanged.connect(self.start_geocode)
        self.cmbGeocoder.addItems(GeocoderFactory.get_geocoders_names())

    def start_geocode(self):
        search_text = unicode(self.txtSearch.text())
        if not search_text:
            self.lstSearchResult.clear()
            return
        
        geocoder_name = self.cmbGeocoder.currentText()
        
        if 0 == 1 and self.search_thread:
            print 'Kill ', self.search_thread
            self.search_thread.terminate()
            self.search_thread.wait()
            
        self.show_progress()
        searcher = SearchThread(search_text, geocoder_name, self.iface.mainWindow())
        searcher.data_downloaded.connect(self.show_result)
        searcher.error_occurred.connect(self.show_error)
        self.search_threads = searcher  # .append(searcher)
        searcher.start()

    def show_progress(self):
        self.lstSearchResult.clear()
        self.lstSearchResult.addItem("Searching...")
        
    def show_result(self, results):
        print 'show'
        self.lstSearchResult.clear()
        for [pt, desc] in results:
            print 'Result: ', desc
            self.lstSearchResult.addItem(desc)
        self.lstSearchResult.update()
            
    def show_error(self, error_text):
        print error_text
        #QMessageBox.critical(self, self.tr("RuGeocoder"), error_text)
        self.lstSearchResult.clear()
        self.lstSearchResult.addItem(error_text)

    
class SearchThread(QThread):
    
    data_downloaded = pyqtSignal(object)
    error_occurred = pyqtSignal(object)    
    
    def __init__(self, search_text, geocoder_name, parent=None):
        QThread.__init__(self, parent)
        self.search_text = search_text
        self.geocoder_name = geocoder_name
        print 'Search: ', search_text
        #define geocoder
        self.coder = GeocoderFactory.get_geocoder(geocoder_name)

    def __del__(self):
        pass
        #self.wait()

    def run(self):        
        results = []
        results.append([None, self.search_text])  # debug
        pt = None
        desc = None
        
        #geocode
        try:
            pt, desc = self.coder.geocode(None, None, None, None, self.search_text)
            results.append([pt, desc])
        except URLError:
                        #import sys
                        #error_text = (self.tr("Network error!\n%1")).arg(unicode(sys.exc_info()[1]))
                        error_text = 'net'
                        self.error_occurred.emit(error_text)
        except Exception:
                        #import sys
                        #error_text = (self.tr("Error of processing!\n%1: %2")).arg(unicode(sys.exc_info()[0].__name__)).arg(unicode(sys.exc_info()[1]))
                        error_text = 'common'
                        self.error_occurred.emit(error_text)
        
        self.data_downloaded.emit(results)
        #self.terminate()
