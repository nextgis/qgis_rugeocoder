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
   
import sys
from datetime import datetime

from osm_geocoder import OsmGeocoder
from google_geocoder import GoogleGeocoder
from yandex_geocoder import YandexGeocoder

from PyQt4.QtGui import QDialog, QMessageBox
from PyQt4.QtCore import QObject, SIGNAL, QString

from qgis.core import QGis, QgsRectangle, QgsFeature, QgsGeometry

from ui_batch_geocoding_dialog import Ui_BatchGeocodingDialog
from utils import get_vector_layer_by_name, get_layer_names, get_layer_str_fields,  get_layer_all_fields
import regions_helper


class BatchGeocodingDialog(QDialog, Ui_BatchGeocodingDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.setupUi(self)
        self.setFixedSize(self.size())
        
        #SIGNALS
        QObject.connect(self.btnRun, SIGNAL( "clicked()" ), self.processing)
        QObject.connect(self.cmbLayer, SIGNAL( "currentIndexChanged(QString)"), self.fill_form)
        
        #INIT CONTROLS VALUES
        self.cmbGeocoder.addItems(["OSM", "Google", "Yandex"])
        self.cmbLayer.addItems(get_layer_names([QGis.Point]))
        for region in regions_helper.get_regions_names():
            self.cmbRegion.addItem(region['name'],  region)


    def fill_form(self, layer_name):
        layer = get_vector_layer_by_name(layer_name)        
        str_fields = get_layer_str_fields(layer)
        all_fields = get_layer_all_fields(layer)
        
        #set cmb's
        self.cmbAddress.clear()
        self.cmbRayonField.clear()
        self.cmbSettlField.clear()
        self.cmbStreet.clear()
        self.cmbBuildingNum.clear()

        self.cmbAddress.addItems(str_fields)
        self.cmbRayonField.addItems(str_fields)
        self.cmbSettlField.addItems(str_fields)
        self.cmbStreet.addItems(str_fields)
        self.cmbBuildingNum.addItems(all_fields)


    def processing(self):
        #checks
        if not self.cmbLayer.currentText():
            QMessageBox.warning(self, self.tr("RuGeocoder"), self.tr("You need to choose a point layer!"))
            return
            
        if self.cmbAddress.isEnabled() and  not self.cmbAddress.currentText():
            QMessageBox.warning(self, self.tr("RuGeocoder"), self.tr("You need to select the field containing the addresses!"))
            return

        if self.chkDistrict.isChecked() and self.rbRayonName.isChecked() and not self.txtSettlName.text():
            QMessageBox.warning(self, self.tr("RuGeocoder"), self.tr("You need to enter the district name!"))
            return

        if self.chkDistrict.isChecked() and self.rbRayonField.isChecked() and not self.cmbRayonField.currentText():
            QMessageBox.warning(self, self.tr("RuGeocoder"), self.tr("You need to select the field containing the names of districts!"))
            return

        if self.chkSettlement.isChecked() and self.rbSettlName.isChecked() and not self.txtSettlName.text():
            QMessageBox.warning(self, self.tr("RuGeocoder"), self.tr("You need to enter the city name!"))
            return

        if self.chkSettlement.isChecked() and self.rbSettlField.isChecked() and not self.cmbSettlField.currentText():
            QMessageBox.warning(self, self.tr("RuGeocoder"), self.tr("You need to select the field containing the names of cities!"))
            return
            
        if self.chkStreet.isChecked() and not self.cmbStreet.currentText():
            QMessageBox.warning(self, self.tr("RuGeocoder"), self.tr("You need to select the field containing the names of streets!"))
            return
            
        if self.chkStreet.isChecked() and not self.cmbBuildingNum.currentText():
            QMessageBox.warning(self, self.tr("RuGeocoder"), self.tr("You need to select the field containing the numbers of buildings!"))
            return

        layer = get_vector_layer_by_name(self.cmbLayer.currentText())
        if not layer.isEditable():
            QMessageBox.warning(self, self.tr("RuGeocoder"),
                                 self.tr("Layer is not in edit mode! Please start editing the layer!"))
            return
        
        #setup ui
        data_provider = layer.dataProvider()
        features_for_update = data_provider.featureCount()
        if  features_for_update > 0:
            self.prgProcess.setMaximum(features_for_update)
            self.prgProcess.setValue(0)
        start =  datetime.now()

        #get num of fields
        addr_index = data_provider.fieldNameIndex(self.cmbAddress.currentText())
        rayon_index = data_provider.fieldNameIndex(self.cmbRayonField.currentText())
        settl_index = data_provider.fieldNameIndex(self.cmbSettlField.currentText())
        street_index = data_provider.fieldNameIndex(self.cmbStreet.currentText())
        build_index = data_provider.fieldNameIndex(self.cmbBuildingNum.currentText())
        geocoded_index = data_provider.fieldNameIndex("geocoded")

        #define geocoder
        if self.cmbGeocoder.currentText()=="OSM":
            coder = OsmGeocoder()
        elif self.cmbGeocoder.currentText()=="Yandex":
            coder = YandexGeocoder()
        else:
            coder = GoogleGeocoder()
        
        #define region
        region = None
        if self.chkRegion.isChecked():
            geocoder_name = unicode(self.cmbGeocoder.currentText())
            region_id = self.cmbRegion.itemData(self.cmbRegion.currentIndex()).toPyObject()[QString('id')]
            region = regions_helper.get_specific_region_name(geocoder_name,  region_id)

        #select all features
        feat = QgsFeature()
        attrs = data_provider.attributeIndexes()
        data_provider.select(attrs, QgsRectangle(), False)
        
        while data_provider.nextFeature(feat):
            #get values for geocoding
            attr_map = feat.attributeMap()

            addr = unicode(attr_map[addr_index].toString())

            rayon = None
            if self.chkDistrict.isChecked():
                if self.rbRayonName.isChecked():
                    rayon = unicode(self.txtRayonName.text() )
                else:
                    rayon = unicode(attr_map[rayon_index].toString())

            settl = None
            if self.chkSettlement.isChecked():
                if self.rbSettlName.isChecked():
                    settl = unicode(self.txtSettlName.text() )
                else:
                    settl = unicode(attr_map[settl_index].toString())

            if self.chkStreet.isChecked():
                street = unicode(attr_map[street_index].toString())
                build_num = unicode(attr_map[build_index].toString())
            else:
                street = addr #ugly! maybe need one more method for geocoders???
                build_num = None

            #geocode
            pt, desc = coder.geocode(region, rayon, settl, street, build_num)

            #set geom
            layer.changeGeometry(feat.id(), QgsGeometry.fromPoint(pt)) 

            #set additional fields
            if geocoded_index >= 0:
                layer.changeAttributeValue(feat.id(), geocoded_index, desc)

            self.prgProcess.setValue(self.prgProcess.value() + 1)

        stop = datetime.now()

        #workaround for python < 2.7
        td = stop - start
        if sys.version_info[:2] < (2, 7):
            total_sec = (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6
        else:
            total_sec = td.total_seconds()

        QMessageBox.information(self, self.tr("Geocoding successfully completed"),
                         self.tr("Geoceded %1 features for %2 seconds")
                         .arg(unicode(features_for_update))
                         .arg(unicode(total_sec)))

