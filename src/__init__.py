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
 This script initializes the plugin, making it known to QGIS.
"""


def name():
    return "RuGeocoder"


def description():
    return "Geocode your csv files to shp (Russia only)"


def version():
    return "Version 0.3.8"


def icon():
    return "icon.png"


def qgisMinimumVersion():
    return "1.6"


def classFactory(iface):
    from ru_geocoder_plugin import RuGeocoderPlugin
    return RuGeocoderPlugin(iface)


def author():
    return "Nikulin Evgeniy"


def email():
    return "nikulin.e at gmail"