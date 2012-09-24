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

try:
    from osgeo import ogr, osr,  gdal
except ImportError:
    import ogr, osr,  gdal

_current_path = path.abspath(path.dirname(__file__))
_data_path=path.join(_current_path,"data.sqlite")
        
def get_regions_names():
    ds = ogr.Open(_data_path)
    layer = ds['region']
    regions = []
    feat = layer.GetNextFeature()
    while feat is not None:
        id = feat.GetFID()
        name = unicode(feat.GetField('name'), 'utf-8')
        is_town = feat.GetField('is_settlement')
        regions.append({'id':id,  'name':name,  'is_settlement':is_town})
        feat = layer.GetNextFeature()
    ds.Destroy()
    return regions

def get_specific_region_name(geocoder,  region_id):
    ds = ogr.Open(_data_path)
    layer_name = 'region_'+geocoder.lower()
    layer = ds.GetLayerByName(layer_name.encode('utf-8'))
    if layer == None:
        layer = ds['region']
    specific_name = layer.GetFeature(region_id).GetField("name")
    if specific_name!=None: #maybe Null!
        specific_name = unicode(specific_name, 'utf-8')
    else:
        specific_name = ''
    ds.Destroy()
    return specific_name
