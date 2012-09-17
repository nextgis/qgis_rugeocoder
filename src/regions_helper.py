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
from qgis.core import QgsVectorLayer, QgsFeature, QgsRectangle
from os import path

_current_path = path.abspath(path.dirname(__file__))

def get_regions_names():
    layer = QgsVectorLayer(path.join(_current_path,"data.sqlite"), "regions", "ogr")
    layer.setProviderEncoding('utf-8')
    if layer.isValid():
        feat = QgsFeature()
        names = []
        data_provider = layer.dataProvider()
        region_filed_index = data_provider.fieldNameIndex("name")
        attrs = [region_filed_index,]
        data_provider.select(attrs, QgsRectangle(), False)

        while data_provider.nextFeature(feat):
            attr_map = feat.attributeMap()
            region_name = unicode(attr_map[region_filed_index].toString())
            names.append(region_name)
        return names
    else:
        return []
