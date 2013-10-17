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
import time
import urllib2
import urllib
from qgis.core import QgsPoint
#from PyQt4.QtGui import QMessageBox

from base_geocoder import BaseGeocoder


class GoogleGeocoder(BaseGeocoder):
    url = 'http://maps.googleapis.com/maps/api/geocode/json?&language=ru&sensor=false&address='

    def geocode(self, region, rayon, city, street, house_number):
        time.sleep(0.2)  # antiban
        full_addr = self._construct_search_str(region, rayon, city, street, house_number)
        full_addr = urllib.quote(full_addr.encode('utf-8'))
        full_url = unicode(self.url) + unicode(full_addr, 'utf-8')
        #QMessageBox.information(None, 'Geocoding debug', full_url)

        f = urllib2.urlopen(full_url.encode('utf-8'))
        resp_str = unicode(f.read(),  'utf-8')
        resp_json = json.loads(resp_str)

        if resp_json['results']:
            res0 = resp_json['results'][0]
            pt = QgsPoint(float(res0['geometry']['location']['lng']), float(res0['geometry']['location']['lat']))
            return pt, res0['formatted_address']
        else:
            pt = QgsPoint(0, 0)
            return pt, 'Not found'
