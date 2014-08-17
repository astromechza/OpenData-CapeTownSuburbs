#!/usr/bin/env python

#
#
#

import json
import urllib2
import traceback
from pyquery import PyQuery as pq
import re

wikiurl = 'http://en.wikipedia.org/wiki/List_of_Cape_Town_suburbs'

coordregex = re.compile('(-?\\d+)\\?(\\d+)\\?(?:(\\d+(?:\\.\\d+)?)\\?)?([NSEW])')

def convert_coordinate(input):
    input = input.encode('ascii', errors='replace')
    m = coordregex.search(input)

    degrees = float(m.group(1))
    minutes = float(m.group(2))
    seconds = float(m.group(3) or 0)

    final = degrees + minutes / 60 + seconds / 3600

    mul = 1 if (m.group(4) in ['N', 'E']) else -1

    return mul * final

def create_suburb_properties(address):
    properties = {}
    try:
        if address.startswith('/wiki/'):
            address = 'http://en.wikipedia.org' + address

            subwikipage = pq(url=address)

            infobox = subwikipage('table.infobox.geography:first')

            if 'City of Cape Town' in infobox.text():
                coordinates = infobox('span.geo-dms:first')
                latitude = coordinates('span.latitude:first').text()
                longitude = coordinates('span.longitude:first').text()

                properties['latitude'] = convert_coordinate(latitude)
                properties['longitude'] = convert_coordinate(longitude)

    except Exception as e:
        print e
        traceback.print_exc()

    return properties



def main():

    data = {}

    # load wiki page source
    wikipage = pq(url=wikiurl)

    tables = wikipage('table.wikitable').filter(lambda i: pq(this).find('th')[0].text == 'Suburb')

    for t in tables.items():
        heading = t.prevAll('h2')[-1].getchildren()[0].text

        rows = t.find('tr td:first-child a')

        suburbs = {}

        for r in rows.items():
            suburb = r.text()
            properties = create_suburb_properties(r.attr('href'))

            suburbs[suburb] = properties

        data[heading] = suburbs

    textdata = json.dumps(data, sort_keys=True, indent=4, separators=(',',': '))

    print textdata

if __name__ == '__main__':
    main()
