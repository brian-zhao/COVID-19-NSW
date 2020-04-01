import csv
import requests
from collections import defaultdict
import numpy as np
import matplotlib
import matplotlib.figure
from matplotlib.font_manager import FontProperties
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.patches import Polygon
from mpl_toolkits.basemap import Basemap

LIMIT = 3000

def catch_daily():

    url = ('https://data.nsw.gov.au/data/api/3/action/datastore_search?'
           'resource_id=21304414-1ff1-4243-a5d2-f52778048b29&limit=%s') % LIMIT
    data = requests.get(url=url).json()['result']['records']
    data.sort(key=lambda x:x['notification_date'])

    lga_data = defaultdict(int)
    postcode_data = defaultdict(int)

    for item in data:
        if str(item['postcode']) not in postcode_data.keys():
            postcode_data[str(item['postcode'])] = 1
        else:
            postcode_data[str(item['postcode'])] += 1

        if str(item['lga_code19']) not in lga_data.keys():
            lga_data[str(item['lga_code19'])] = 1
        else:
            lga_data[str(item['lga_code19'])] += 1

    # print(lga_data)
    # print(postcode_data)
    return postcode_data


def get_postcode():
    suburb_to_postcode = {}
    with open('postcode.csv', newline='') as csvfile:
        preader = csv.reader(csvfile, delimiter=',')
        for row in preader:
            suburb_to_postcode[row[1]] = row[0]

    return suburb_to_postcode


def plot_distribution():
    infection = catch_daily()
    suburb_to_postcode = get_postcode()

    font = FontProperties(fname='simsun.ttf', size=14)
    # NSW
    # lat_min = -40
    # lat_max = -25
    # lon_min = 140
    # lon_max = 160

    # Greater Sydney
    lat_min = -34.5
    lat_max = -33.5
    lon_min = 150.5
    lon_max = 151.5

    handles = [
        matplotlib.patches.Patch(color='#ffaa85', alpha=1, linewidth=0),
        matplotlib.patches.Patch(color='#ff7b69', alpha=1, linewidth=0),
        matplotlib.patches.Patch(color='#bf2121', alpha=1, linewidth=0),
        matplotlib.patches.Patch(color='#7f1818', alpha=1, linewidth=0),
    ]
    labels = ['1-9', '10-29', '30-99', '>100']

    fig = matplotlib.figure.Figure()
    fig.set_size_inches(10, 8)
    axes = fig.add_axes((0.1, 0.12, 0.8, 0.8)) # rect = l,b,w,h
    m = Basemap(llcrnrlon=lon_min, urcrnrlon=lon_max, llcrnrlat=lat_min,
                urcrnrlat=lat_max, resolution='l', ax=axes)
    m.readshapefile('nsw_locality/NSW_LOCALITY_POLYGON_shp', 'section',
                    drawbounds=True)
    m.drawcoastlines(color='black')
    m.drawcountries(color='black')
    m.drawparallels(np.arange(lat_min,lat_max,10), labels=[1,0,0,0])
    m.drawmeridians(np.arange(lon_min,lon_max,10), labels=[0,0,0,1])
    # print(m.section_info)
    for info, shape in zip(m.section_info, m.section):
        suburb_name = info['NSW_LOCA_2'].strip('\x00')
        postcode = str(suburb_to_postcode.get(suburb_name, ''))
        color = '#f0f0f0'

        number = infection.get(postcode, 0)
        if number == 0:
            color = '#f0f0f0'
        elif number < 10:
            color = '#ffaa85'
        elif number < 30:
            color = '#ff7b69'
        elif number < 100:
            color = '#bf2121'
        else:
            color = '#7f1818'

        poly = Polygon(shape, facecolor=color, edgecolor=color)
        axes.add_patch(poly)

    axes.legend(handles, labels, bbox_to_anchor=(0.5, -0.11), loc='lower center',
                ncol=4, prop=font)
    axes.set_title("covid19-sydney", fontproperties=font)
    FigureCanvasAgg(fig)
    fig.savefig('covid19-sydney.png')
    # axes.set_title("covid19-nsw", fontproperties=font)
    # FigureCanvasAgg(fig)
    # fig.savefig('covid19-nsw.png')


if __name__ == '__main__':
    # catch_daily()
    # get_postcode()
    plot_distribution()