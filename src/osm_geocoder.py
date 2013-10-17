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


class OsmGeocoder(BaseGeocoder):
    url = 'http://nominatim.openstreetmap.org/search?countrycodes=ru&format=json&polygon=0&addressdetails=1&limit=10&accept-language=ru,en-US;&q='

    def _normalize_num(self, num):
        if num is None:
            return None
        result = ''
        for i in range(len(num)):
            if '0' <= num[i] <= '9':
                result += num[i]
            else:
                break
        return result

    def geocode(self, region, rayon, city, street, house_number):
        house_number_norm = self._normalize_num(house_number)
        #try search as is...
        full_addr = self._construct_search_str(region, rayon, city, street, house_number_norm)
        full_addr = urllib.quote(full_addr.encode('utf-8'))
        full_url = unicode(self.url) + unicode(full_addr, 'utf-8')
        f = urllib2.urlopen(full_url.encode('utf-8'))
        resp_str = unicode(f.read(),  'utf-8')
        resp_json = json.loads(resp_str)
        if len(resp_json) == 1:
            #it is found
            pt = QgsPoint(float(resp_json[0]['lon']), float(resp_json[0]['lat']))
            return pt, resp_json[0]['display_name']
        if len(resp_json) > 1:
            #multiple result
            for resp in resp_json:
                if 'address' in resp and 'house_number' in resp['address'] and resp['address']['house_number'].lower().strip() == house_number.lower().strip():
                    #right result
                    pt = QgsPoint(float(resp['lon']), float(resp['lat']))
                    return pt, resp['display_name']
            # The right result is not found. Get first
            pt = QgsPoint(float(resp_json[0]['lon']), float(resp_json[0]['lat']))
            return pt, resp_json[0]['display_name']
        else:
            #try get street or town
            full_addr = self._construct_search_str(region, rayon, city, None, None)
            full_addr = urllib.quote(full_addr.encode('utf-8'))
            full_url = unicode(self.url) + unicode(full_addr, 'utf-8')
            f = urllib2.urlopen(full_url.encode('utf-8'))
            resp_str = unicode(f.read(), 'utf-8')
            resp_json = json.loads(resp_str)
            if resp_json:
                pt = QgsPoint(float(resp_json[0]['lon']), float(resp_json[0]['lat']))
                return pt, resp_json[0]['display_name']
            else:
                pt = QgsPoint(0, 0)
                return pt, 'Not found'