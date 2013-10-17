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
import json
import urllib2
import urllib
from qgis.core import QgsPoint
#from PyQt4.QtGui import QMessageBox

from base_geocoder import BaseGeocoder


class YandexGeocoder(BaseGeocoder):
    url = 'http://geocode-maps.yandex.ru/1.x/?key=APbJTE8BAAAAwUV4ZgIAWchAMdqatI8n3SLIv26SUw2telQAAAAAAAAAAABJnzuIcf3RGjjl50cTEPtvjEbW8w==&format=json&geocode='

    def geocode(self, region, rayon, city, street, house_number):
        full_addr = self._construct_reverse_search_str(region, rayon, city, street, house_number)
        full_addr = urllib.quote(full_addr.encode('utf-8'))
        full_url = unicode(self.url) + unicode(full_addr, 'utf-8')
        #QMessageBox.information(None, 'Geocoding debug', full_url)
                
        f = urllib2.urlopen(full_url.encode('utf-8'))
        resp_str = unicode(f.read(),  'utf-8')
        resp_json = json.loads(resp_str)
                
        if resp_json['response']['GeoObjectCollection']['featureMember']:
            res0 = resp_json['response']['GeoObjectCollection']['featureMember'][0]
            pt_str = res0['GeoObject']['Point']['pos']
            pt = QgsPoint(float(pt_str.split(' ')[0]), float(pt_str.split(' ')[1]))
            return pt, res0['GeoObject']['metaDataProperty']['GeocoderMetaData']['text']
        else:
            pt = QgsPoint(0, 0)
            return pt, 'Not found'
