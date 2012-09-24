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
from utils import get_vector_layer_by_name, get_layer_names, get_layer_str_fields
import regions_helper


class BatchGeocodingDialog(QDialog, Ui_BatchGeocodingDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.setupUi(self)
        self.setFixedSize(self.size())
        
        #SIGNALS
        QObject.connect(self.btnRun, SIGNAL( "clicked()" ), self.processing)
        QObject.connect(self.cmbLayer, SIGNAL( "currentIndexChanged(QString)"), self.fill_form)
        QObject.connect(self.chkBuilding, SIGNAL( "toggled ( bool )"), self.rename_label)
        
        
        #INIT CONTROLS VALUES
        self.cmbGeocoder.addItems(["OSM", "Google", "Yandex"])
        self.cmbLayer.addItems(get_layer_names([QGis.Point]))
        for region in regions_helper.get_regions_names():
            self.cmbRegion.addItem(region['name'],  region)



    def rename_label(self, build_num_enabled):
        if build_num_enabled:
            self.lblAddress.setText(self.tr("Street:"))
        else:
            self.lblAddress.setText(self.tr("Address:"))
        
    def fill_form(self, layer_name):
        layer = get_vector_layer_by_name(layer_name)        
        str_fields = get_layer_str_fields(layer)
        
        #set cmb's
        self.cmbRayonField.clear()
        self.cmbSettlField.clear()
        self.cmbAddress.clear()
        self.cmbBuildingNum.clear()

        self.cmbRayonField.addItems(str_fields)
        self.cmbSettlField.addItems(str_fields)
        self.cmbAddress.addItems(str_fields)
        self.cmbBuildingNum.addItems(str_fields)



    def processing(self):
        #checks
        if not self.cmbLayer.currentText():
            QMessageBox.warning(self, self.tr("RuGeocoder"), self.tr("You need to choose a point layer!"))
            return

        if self.rbSettlName.isChecked() and not self.txtSettlName.text():
            QMessageBox.warning(self, self.tr("RuGeocoder"), self.tr("You need to enter the city name!"))
            return

        if self.rbSettlField.isChecked() and not self.cmbSettlField.currentText():
            QMessageBox.warning(self, self.tr("RuGeocoder"), self.tr("You need to select the field containing the names of cities!"))
            return

        if self.rbRayonField.isChecked() and not self.cmbRayonField.currentText():
            QMessageBox.warning(self, self.tr("RuGeocoder"), self.tr("You need to select the field containing the names of districts!"))
            return

        if not self.cmbAddress.currentText():
            QMessageBox.warning(self, self.tr("RuGeocoder"), self.tr("You need to select the field containing the addresses!"))
            return

        #select all features
        layer = get_vector_layer_by_name(self.cmbLayer.currentText())
        if not layer.isEditable():
            QMessageBox.warning(self, self.tr("RuGeocoder"),
                                 self.tr("Layer is not in edit mode! Please start editing the layer!"))
            return

        data_provider = layer.dataProvider()
        features_for_update = data_provider.featureCount()
        if  features_for_update > 0:
            self.prgProcess.setMaximum(features_for_update)
            self.prgProcess.setValue(0)


        start =  datetime.now()

        #get num of fields
        rayon_index = data_provider.fieldNameIndex(self.cmbRayonField.currentText())
        settl_index = data_provider.fieldNameIndex(self.cmbSettlField.currentText())
        addr_index = data_provider.fieldNameIndex(self.cmbAddress.currentText())
        build_index = data_provider.fieldNameIndex(self.cmbBuildingNum.currentText())
        geocoded_index = data_provider.fieldNameIndex("geocoded")


        #select geocoder
        if self.cmbGeocoder.currentText()=="OSM":
            coder = OsmGeocoder()
        elif self.cmbGeocoder.currentText()=="Yandex":
            coder = YandexGeocoder()
        else:
            coder = GoogleGeocoder()

        feat = QgsFeature()
        attrs = data_provider.attributeIndexes()
        data_provider.select(attrs, QgsRectangle(), False)
        
        #select region
        geocoder_name = unicode(self.cmbGeocoder.currentText())
        region_id = self.cmbRegion.itemData(self.cmbRegion.currentIndex()).toPyObject()[QString('id')]
        region = regions_helper.get_specific_region_name(geocoder_name,  region_id)
        #region = unicode(self.cmbRegion.currentText()) #for tests!!!

        while data_provider.nextFeature(feat):
            #get values for geocoding
            attr_map = feat.attributeMap()

            if self.rbRayonName.isChecked():
                rayon = unicode(self.txtRayonName.text() )
            else:
                rayon = unicode(attr_map[rayon_index].toString())

            if self.rbSettlName.isChecked():
                settl = unicode(self.txtSettlName.text() )
            else:
                settl = unicode(attr_map[settl_index].toString())

            addr = unicode(attr_map[addr_index].toString())

            if self.chkBuilding.isChecked():
                build_num = unicode(attr_map[build_index].toString())
            else:
                build_num = None
            #geocode
            pt, desc = coder.geocode(region, rayon, settl, addr, build_num)

            #set geom
            layer.changeGeometry(feat.id(), QgsGeometry.fromPoint(pt)) 

            #set additional fields
            if geocoded_index >= 0:
                layer.changeAttributeValue(feat.id(), geocoded_index, desc)

            self.prgProcess.setValue(self.prgProcess.value() + 1)
            #time.sleep(0.2)

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

