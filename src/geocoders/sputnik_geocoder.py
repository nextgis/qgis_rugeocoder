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
from os import path

from qgis.core import QgsPoint
import sys

from base_geocoder import BaseGeocoder

_fs_encoding = sys.getfilesystemencoding()
_current_path = unicode(path.abspath(path.dirname(__file__)), _fs_encoding)

class SputnikGeocoder(BaseGeocoder):
    url = 'http://search.maps.sputnik.ru/search?q='
    terms_url = 'http://corp.sputnik.ru/maps'
    icon_path = path.join(_current_path, 'icons/', 'sputnik.png')


    def geocode_components(self, region, rayon, city, street, house_number):
        full_addr = self._construct_reverse_search_str(region, rayon, city, street, house_number)
        return self.geocode(full_addr)

    def geocode_components_multiple_results(self, region, rayon, city, street, house_number):
        full_addr = self._construct_reverse_search_str(region, rayon, city, street, house_number)
        return self.geocode_multiple_results(full_addr)

    def geocode(self, search_str):
        res = self.geocode_multiple_results(search_str)
        if len(res) > 0:
            return res[0]
        else:
            return (QgsPoint(0, 0), 'Not found')

    def geocode_multiple_results(self, search_str):
        full_addr = urllib.quote(search_str.encode('utf-8'))
        if not full_addr:
            return []
        full_url = unicode(self.url) + unicode(full_addr, 'utf-8')

        f = urllib2.urlopen(full_url.encode('utf-8'))
        resp_str = unicode(f.read(),  'utf-8')
        resp_json = json.loads(resp_str)

        result = []
        if resp_json['result']:
            for feat_mem in resp_json['result']:
                lat = feat_mem['position']['lat']
                long = feat_mem['position']['lon']
                pt = QgsPoint(float(long), float(lat))
                result.append((pt, feat_mem['display_name']))

        return result

