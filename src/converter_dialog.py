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
try:
    from osgeo import ogr, osr
except ImportError:
    import ogr, osr

import sys
import datetime
from os import path
from osm_geocoder import OsmGeocoder
from google_geocoder import GoogleGeocoder

from PyQt4.QtGui import QDialog, QMessageBox, QFileDialog
from PyQt4.QtCore import QObject, SIGNAL, QString

from ui_converter_dialog import Ui_ConverterDialog

class ConverterDialog(QDialog, Ui_ConverterDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.setupUi(self)

        #SIGNALS
        QObject.connect(self.btnSelectCsv, SIGNAL("clicked()"), self.select_csv)
        QObject.connect(self.btnSelectShp, SIGNAL("clicked()"), self.select_shp)
        QObject.connect(self, SIGNAL("accepted()"), self.processing)


    def select_shp(self):
        shp_path = QString()
        if self.txtShpPath.text():
            shp_path = unicode(self.txtShpPath.text())


        file_name = QFileDialog.getSaveFileName(self,
                                                self.tr('Select output SHP file'),
                                                shp_path,
                                                self.tr('SHP files (*.shp *.shp)'))
        if not file_name.isEmpty():
            self.txtShpPath.setText(file_name)



    def select_csv(self):
        file_name = QFileDialog.getOpenFileName(self, self.tr('Select input CSV file'), '', self.tr('CSV files (*.csv *.CSV)'))
        if not file_name.isEmpty():
            self.txtCsvPath.setText(file_name)
            #set output path
            if not self.txtShpPath.text():
                shp_path = path.splitext(unicode(file_name))[0]+'.shp'
                self.txtShpPath.setText(shp_path)


    def processing(self):
        out_path = unicode(self.txtShpPath.text()).encode("utf-8")
        drv = ogr.GetDriverByName("ESRI Shapefile")
        #check exists
        if path.exists(out_path):
            #message
            drv.DeleteDataSource(out_path)
        #create output shp file
        try:
            drv = ogr.GetDriverByName("ESRI Shapefile")
            output_data_source = drv.CreateDataSource(out_path)
        except:
            QMessageBox.critical(self, self.tr("Geocoding helper error"),
                                     self.tr("Output SHP file can't be created!\r%1: %2")
                                     .arg(unicode(sys.exc_info()[0].__name__))
                                     .arg(unicode(sys.exc_info()[1])))
            return
 

        wgs_sr = osr.SpatialReference()
        wgs_sr.ImportFromEPSG(4326)

        layer_name = path.basename(out_path).strip(".shp")
        output_layer = output_data_source.CreateLayer( layer_name, srs = wgs_sr, geom_type = ogr.wkbPoint )

        #copy fields
        in_path = unicode(self.txtCsvPath.text()).encode("utf-8")
        input_data_source = ogr.Open(in_path)
        csv_layer = input_data_source[0]

        csv_feat_defs = csv_layer.GetLayerDefn()
        for i in range(csv_feat_defs.GetFieldCount()):
            field_def = csv_feat_defs.GetFieldDefn(i)
            if field_def.GetType()==ogr.OFTString:
                field_def.SetWidth(300)
            if output_layer.CreateField(field_def) != 0:
                print "Can't create field %s" % field_def.GetNameRef()
                return

        #add geocoder additional fields
        out_defs = output_layer.GetLayerDefn()
        if out_defs.GetFieldIndex("settlement") < 0:
            field_def = ogr.FieldDefn("settlement", ogr.OFTString)
            field_def.SetWidth( 300 )
            if output_layer.CreateField ( field_def ) != 0:
                print "Can't create field %s" % field_def.GetNameRef()
                return
        if out_defs.GetFieldIndex("street") < 0:
            field_def = ogr.FieldDefn( "street", ogr.OFTString )
            field_def.SetWidth( 300 )
            if output_layer.CreateField (field_def) != 0:
                print "Can't create field %s" % field_def.GetNameRef()
                return
        if out_defs.GetFieldIndex("house_num") < 0:
            field_def = ogr.FieldDefn("house_num", ogr.OFTString)
            field_def.SetWidth( 300 )
            if output_layer.CreateField(field_def) != 0:
                print "Can't create field %s" % field_def.GetNameRef()
                return
        if out_defs.GetFieldIndex("geocoded") < 0:
            field_def = ogr.FieldDefn("geocoded", ogr.OFTString)
            field_def.SetWidth(300)
            if output_layer.CreateField (field_def) != 0:
                print "Can't create field %s" % field_def.GetNameRef()
                return

        in_feat = csv_layer.GetNextFeature()
        while in_feat is not None:
            out_feat = ogr.Feature(output_layer.GetLayerDefn())
            #copy fields
            res = out_feat.SetFrom(in_feat)
            if res != 0:
                print "Can't copy feature"
                continue
            #set geom
            pt = ogr.Geometry(ogr.wkbPoint)
            pt.SetPoint_2D(0, 0, 0)
            out_feat.SetGeometry(pt)

            if output_layer.CreateFeature(out_feat) != 0:
                print "Failed to create feature in shapefile.\n"
                sys.exit(1)

            in_feat = csv_layer.GetNextFeature()

        QMessageBox.information(self, self.tr("RuGeocoder"), self.tr("Converting successfully completed"))
