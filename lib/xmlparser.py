# -*- coding: utf-8 -*-
"""
  The crawler to download YouTube video viewcount history
"""
# Author: Honglin Yu <yuhonglin1986@gmail.com>
# License: BSD 3 clause

import datetime
from xml.etree import ElementTree
import json


def parseString(s):
    tree = ElementTree.fromstring(s)
    graphData = tree.find('graph_data')

    if graphData == None:
        raise Exception("can not find data in the xml response")


    jsonDict = json.loads(graphData.text)

    # get days
    rawdate = [ datetime.date(1970,1,1) + datetime.timedelta( x/86400000 ) for x in  jsonDict['day']['data'] ]
    uploadDate = rawdate[0]

    # get views
    try:
        raw_views = jsonDict['views']['daily']['data']
    except KeyError:
        raise Exception("can not get viewcount in the xml response")

    tmp = uploadDate
    viewcount = []
    for i, j in enumerate(rawdate):
        viewcount.append(raw_views[i])
        viewcount += [0]*((j - tmp).days - 1)
        tmp = j

    # get watch time
    watchTime = []
    if 'watch-time' in jsonDict:
        raw_wt = jsonDict['watch-time']['daily']['data']
        tmp = uploadDate
        for i, j in enumerate(rawdate):
            watchTime.append(raw_wt[i])
            watchTime += [0]*((j - tmp).days - 1)
            tmp = j


    # get shares
    numShare = []
    if 'shares' in jsonDict:
        raw_ns = jsonDict['shares']['daily']['data']

        tmp = uploadDate
        for i, j in enumerate(rawdate):
            numShare.append(raw_ns[i])
            numShare += [0]*((j - tmp).days - 1)
            tmp = j

    # get numSubscriber
    numSubscriber = []
    if 'subscribers' in jsonDict:
        raw_ns = jsonDict['subscribers']['daily']['data']

        tmp = uploadDate
        for i, j in enumerate(rawdate):
            numSubscriber.append(raw_ns[i])
            numSubscriber += [0]*((j - tmp).days - 1)
            tmp = j

    return {
        'uploadDate' : uploadDate,
        'dailyViewcount' : viewcount,
        'watchTime': watchTime,
        'numShare' : numShare,
        'numSubscriber' : numSubscriber
        }
