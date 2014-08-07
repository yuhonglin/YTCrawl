A YouTube video history metadata crawler (ytcrawl)
========================================

Author: Honglin Yu
Email: yuhonglin1986@gmail.com



About
-----
*ytcrawl* is a YouTube video viewcount (can also crawl subscribers/shares/watchtimes when available) history crawler. During middle 2013, YouTube has published videos' history daily viewcount (when uploaders make it public, see the image below). These can be precious data for computational social science research. This crawler aims to help researchers efficiently download the data.

![Alt text](https://github.com/yuhonglin/YTCrawl/edit/master/img/dailyViewcount.png "videoID: OQSNhk5ICTI")



Basic functionalities
---------------------
1. There are two ways to use the crawler: ```single_crawl``` and  ```batch_crawl```.
2. When using ```batch_crawl```, due to the limitation of YouTube's server, it can access about 36,000 videos per hour (would meet lots of "quota exceeded" error when faster). The actual number of downloaded viewcounts depends on how many videos' data are public (more than 60% in former experiments). 
3. It fully logs the crawling status. Easy to continue crawling from breakpoint.
4. Optionally, it can send you email to report "errors" or "job finished".


Usage
-----
The following example shows how to crawl the history viewcount of video "WoUsHkdb12A"

1. Put the code somewhere, add its folder to python library path and then import ```Crawler```, for example,
```python
import sys
sys.path.append('/path/to/ytcrawl')
from crawler import Crawler
```
2. Create an crawler object
```python
c = Crawler()
```
The configuration of this object is explained in below
3. Begin to crawl,
```python
c.single_crawl("OQSNhk5ICTI")  # crawl a single video by ID "OQSNhk5ICTI"
c.batch_crawl("/path/to/videoID/file", "/output/path") # crawl all the videos in a file. Output the crawled data and log files input an output folder.
```

Input/Output Format
-------------------

* For ```batch_crawl```
  - every line in the input file is a videoID
* For ```single_crawl```
  - ```data``` folder

Continue from Breakpoint
------------------------


Optional: Email Reminder
------------------------

LICENSE
--------
BSD 3 clause
