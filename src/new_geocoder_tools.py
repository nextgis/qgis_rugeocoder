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
import urllib2
import urllib
import json
import sys
try:
    from osgeo import ogr, osr,  gdal
except ImportError:
    import ogr, osr,  gdal

_fs_encoding = sys.getfilesystemencoding()
_current_path = unicode(path.abspath(path.dirname(__file__)), _fs_encoding)
_data_path= path.join(_current_path, u"data.sqlite")

       
def __get_regions_settl_id():
    ds = ogr.Open(_data_path.encode('utf-8')) #maybe not worked on win + gdal<1.8
    layer = ds['region']
    regions = []
    feat = layer.GetNextFeature()
    while feat is not None:
        id = feat.GetFID()
        name = unicode(feat.GetField('name'), 'utf-8')
        is_town = feat.GetField('is_settlement')
        settl_id = feat.GetField('town_id')
        regions.append({'id':id,  'name':name,  'is_settlement':is_town, 'town_id':settl_id})
        feat = layer.GetNextFeature()
    ds.Destroy()
    return regions

def get_geocoded_regions(search_url, resp_expr):
    regions = __get_regions_settl_id()
    print '{0:2} {1:<50} {2:<50}'.format('id', 'name', 'new_region')
    for region in regions:
        #get response
        full_addr = urllib.quote(region['town_id'])
        full_url = unicode(search_url) + unicode(full_addr, "utf-8")
        f = urllib2.urlopen ( full_url.encode("utf-8") )
        resp_str = unicode( f.read(),  'utf-8')
        resp_json = json.loads(resp_str)
        #get addr
        try:
            new_region = eval('resp_json'+resp_expr)
        except:
            new_region = 'Not found'
        print '{0:2d} {1:<50} {2:<50}'.format(region['id'], region['name'].encode('utf-8'), new_region.encode('utf-8'))

def osm_ru():
    url = 'http://www.openstreetmap.ru/api/search?q='
    resp_expr = "['matches'][0]['display_name']"
    get_geocoded_regions(url, resp_expr)
