#!/usr/bin/env python

#

import json
import urllib2
import traceback
from pyquery import PyQuery as pq
import re

wikiurl = 'http://en.wikipedia.org/wiki/List_of_Cape_Town_suburbs'

# regex for extracting degrees/minutes/seconds and quadrant from coordinate string
coordregex = re.compile('(-?\\d+)\\?(\\d+(?:\\.\\d+)?)\\?(?:(\\d+(?:\\.\\d+)?)\\?)?([NSEW])')

# convert coordinate into decimal coordinate
def convert_coordinate(input):
    # replace all unknown characters with ? (this works for now, but is a bit of a hack)
    input = input.encode('ascii', errors='replace')

    m = coordregex.search(input)

    degrees = float(m.group(1))
    minutes = float(m.group(2))
    seconds = float(m.group(3) or 0)

    # combine
    final = degrees + minutes / 60 + seconds / 3600

    # add multiplier. Negative is South or West
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

    # main data container for areas
    data = {}

    # load wiki page source
    wikipage = pq(url=wikiurl)

    # load all tables from the page that contain 'Suburb' in the first header row cell
    tables = wikipage('table.wikitable').filter(lambda i: pq(this).find('th')[0].text == 'Suburb')

    # loop through the tables
    num_tables, i_table = len(tables), 1
    for t in tables.items():
        # heading is first preceding h2 element
        heading = t.prevAll('h2')[-1].getchildren()[0].text
        print "Processing table %d/%d: %s" % (i_table, num_tables, heading)

        # rows are all normal table rows. we only care about the first cell
        # in each row
        rows = t.find('tr td:first-child a')

        # container for current area
        suburbs = {}

        # loop through the suburbs
        num_rows, i_row = len(rows), 1
        for r in rows.items():
            suburb = r.text()
            print "Processing row %d/%d: %s" % (i_row, num_rows, suburb)

            # fetch properties from page link
            suburbs[suburb] = create_suburb_properties(r.attr('href'))

            i_row += 1

        # add to data set
        data[heading] = suburbs

        i_table += 1

    print "Processing Complete. Writing File."

    # dump as pretty json
    textdata = json.dumps(data, sort_keys=True, indent=4, separators=(',',': '))

    with open('data.json', 'w') as f:
        f.write(textdata)

    print "Done"

if __name__ == '__main__':
    main()
