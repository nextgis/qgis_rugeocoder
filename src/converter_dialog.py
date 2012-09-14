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
    from osgeo import ogr, osr,  gdal
except ImportError:
    import ogr, osr,  gdal

import sys
from os import path

from PyQt4.QtGui import QDialog, QMessageBox, QFileDialog
from PyQt4.QtCore import QObject, SIGNAL, QString

from qgis.core import QgsVectorLayer,  QgsMapLayerRegistry

from ui_converter_dialog import Ui_ConverterDialog

class ConverterDialog(QDialog, Ui_ConverterDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.setupUi(self)

        #SIGNALS
        QObject.connect(self.btnSelectCsv, SIGNAL("clicked()"), self.select_csv)
        QObject.connect(self.btnSelectShp, SIGNAL("clicked()"), self.select_shp)
        QObject.connect(self.buttonBox, SIGNAL("accepted()"), self.processing)


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
        #check user input
        in_path = unicode(self.txtCsvPath.text()).encode("utf-8")        
        out_path = unicode(self.txtShpPath.text()).encode("utf-8")
        
        if not in_path:
            self.__show_err(self.tr("Select input CSV file!"))
            return
        if not out_path:
            self.__show_err(self.tr("Select name for output SHP file!"))
            return
        if not path.exists(in_path):
            self.__show_err(self.tr("Selected CSV file not found!"))
            return
        
        #prepare output data source
        drv = ogr.GetDriverByName("ESRI Shapefile")
        #check output datasource exists
        if path.exists(out_path):
            if QMessageBox.question(self,  self.tr("RuGeocoder"),  
                                    self.tr("SHP file with the same name already exists.\r Do you want to overwrite it?"), 
                                    QMessageBox.Yes | QMessageBox.Cancel) == QMessageBox.Yes:
                drv.DeleteDataSource(out_path)
            else:
                return
        
        #create output shp file
        gdal.ErrorReset()
        output_data_source = drv.CreateDataSource(out_path)
        if output_data_source==None:
            self.__show_err(self.tr("Output SHP file can't be created!\r%1")
                                     .arg(unicode(gdal.GetLastErrorMsg())))
            return

        wgs_sr = osr.SpatialReference()
        wgs_sr.ImportFromEPSG(4326)

        layer_name = path.splitext(path.basename(out_path))[0]
        output_layer = output_data_source.CreateLayer( layer_name, srs = wgs_sr, geom_type = ogr.wkbPoint )

        #copy fields
        input_data_source = ogr.Open(in_path)
        csv_layer = input_data_source[0]

        csv_feat_defs = csv_layer.GetLayerDefn()
        for i in range(csv_feat_defs.GetFieldCount()):
            field_def = csv_feat_defs.GetFieldDefn(i)
            if field_def.GetType()==ogr.OFTString:
                field_def.SetWidth(300)
            if output_layer.CreateField(field_def) != 0:
                self.__show_err( self.tr("Unable to create a field %1!").arg(field_def.GetNameRef()))
                return

        #add geocoder additional fields
        out_defs = output_layer.GetLayerDefn()
        if out_defs.GetFieldIndex("settlement") < 0:
            if not self.__add_field(output_layer, "settlement", ogr.OFTString,  300):
                return
        if out_defs.GetFieldIndex("street") < 0:
            if not self.__add_field(output_layer, "street", ogr.OFTString,  300):
                return
        if out_defs.GetFieldIndex("house_num") < 0:
            if not self.__add_field(output_layer, "house_num", ogr.OFTString,  300):
                return
        if out_defs.GetFieldIndex("geocoded") < 0:
            if not self.__add_field(output_layer, "geocoded", ogr.OFTString,  300):
                return

        in_feat = csv_layer.GetNextFeature()
        while in_feat is not None:
            out_feat = ogr.Feature(output_layer.GetLayerDefn())
            #copy fields
            res = out_feat.SetFrom(in_feat)
            if res != 0:
                self.__show_err(self.tr("Unable to construct the feature!"))
                return
            #set geom
            pt = ogr.Geometry(ogr.wkbPoint)
            pt.SetPoint_2D(0, 0, 0)
            out_feat.SetGeometry(pt)
            #add to layer
            if output_layer.CreateFeature(out_feat) != 0:
                self.__show_err(self.tr("Failed to create feature in SHP file!"))
                return
            in_feat = csv_layer.GetNextFeature()
        
        #close DS's
        output_data_source.Destroy()
        input_data_source.Destroy()
        
        
        QMessageBox.information(self, self.tr("RuGeocoder"), self.tr("Converting successfully completed"))
        if self.chkAddToCanvas.isChecked():
            self.add_layer_to_canvas(out_path)
        self.close()
        
    def add_layer_to_canvas(self, shp_path):
        if not path.exists(shp_path):
            return False#message???
        layer_name = path.splitext(path.basename(shp_path))[0]
        vector_layer = QgsVectorLayer(shp_path, layer_name, "ogr")
        if vector_layer.isValid():
            QgsMapLayerRegistry.instance().addMapLayer(vector_layer)
            return True
        else:
            return False
        
    def __add_field(self,  layer, field_name,   field_type=ogr.OFTString,  field_len=None):
        field_def = ogr.FieldDefn(field_name, field_type)
        if field_len:
            field_def.SetWidth(field_len)
        if layer.CreateField (field_def) != 0:
            self.__show_err( self.tr("Unable to create a field %1!").arg(field_def.GetNameRef()))
            return False
        else:
            return True
            
    def __show_err(self,  msg):
         QMessageBox.critical(self, self.tr("RuGeocoder error"), msg)
