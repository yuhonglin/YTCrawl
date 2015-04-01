# -*- coding: utf-8 -*-
"""
  The crawler to download YouTube video viewcount history
"""
# Author: Honglin Yu <yuhonglin1986@gmail.com>
# License: BSD 3 clause

import urllib2
from urllib2 import Request, build_opener, HTTPCookieProcessor, HTTPHandler
import urllib
import threading
import os
import time
import datetime
import re
import cookielib

from lib.logger import Logger
from lib.sendemail import send_email
from lib.xmlparser import *


class Crawler(object):
    """The crawler class
       - for batch_crawl:
         - input is a file
         - output is a directory
       - for single_crawl
         - input is a video's ID
         - output is a dictionay containing possible information
    """
    
    def __init__(self):
        
        self._input_file = None
        self._output_dir = None
        
        self._num_thread = 20

        self._logger = None

        self._key_done = None

        self._mutex_crawl = threading.Lock()
        self._delay_mutex = None
        
        self._cookie = ''
        self._session_token = ''

        self._is_done = False

        self._update_cookie_period = 1800
        self._update_cookie_maximum_times = 20
        self._last_cookie_update_time = None
        self._current_update_cookie_timer = None

        self._crawl_delay_time = 0.1

        self._cookie_update_delay_time = 0.1
        
        self._cookie_update_on = False

        self._seed_videoID = 'OQSNhk5ICTI'
        
        self._email_from_addr = ''
        self._email_password = ''
        self._email_to_addr = ''


    def set_email_reminder(self, from_addr, password, to_addrs):
        """set the email reminder
        
        Arguments:
        - `from_addr`: from which the email is sent
        - `password`: the password of mailbox "from_addr"
        - `to_addrs`: the mailbox that will recieve the reminder
        """
        self._email_from_addr = from_addr
        self._email_password = password
        self._email_to_addr = to_addrs
        
        
    def set_num_thread(self, n):
        """set the number of threads used in crawling, default is 20
        
        Arguments:
        - `n`: number of threads
        """
        self._num_thread = n
        
    def set_cookie_update_period(self, t):
        """control how long to update cookie once, default is 30 min
        
        Arguments:
        - `t`:
        """
        self._update_cookie_period = t
        

    def set_seed_videoID(self, vID):
        """set the seed videoID used to update cookies
        
        Arguments:
        - `vID`:
        """
        self._seed_videoID = vID
        
        
    def mutex_delay(self, t):
        """ delay some time
        
        Arguments:
        - `t`: the time in minutes
        """
        self._delay_mutex.acquire()
        time.sleep(t)
        self._delay_mutex.release()

        
    def store(self, k, txt):
        """generate the filepath of the output file of key "k"
        
        Arguments:
        - `k`: the key
        - `txt`: the file content
        """
        outdir = self._output_dir + '/data/' + k[0] + '/' + k[1] + '/' + k[2] + '/'
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        open(outdir + k, 'w').write(txt)

    def get_url(self, k):
        """ get the URL
        
        Arguments:
        - `k`:
        """
        return 'https://www.youtube.com/insight_ajax?action_get_statistics_and_data=1&v=' + k


    def update_cookie_and_sectiontoken(self):
        # if already begin to update
        if self._cookie_update_on == True:
            return

        self._cookie_update_on = True

        self.period_update()
    
    
    def period_update(self):
        
        # all the job is done
        if self._is_done == True:
            return
        # begin to update
        self._mutex_crawl.acquire()

        # if self._last_cookie_update_time != None:
        #     time.sleep(10) # wait for the current job to finish


        i = 0
        state = 'fail'
        while i < self._update_cookie_maximum_times:

            # get cookies
            cj = cookielib.CookieJar()
            opener = build_opener(HTTPCookieProcessor(cj), HTTPHandler())
            req = Request("https://www.youtube.com/watch?v="+self._seed_videoID)
            f = opener.open(req)
            src = f.read()

            time.sleep(self._cookie_update_delay_time)
            
            cookiename = ['YSC', 'PREF', 'VISITOR_INFO1_LIVE', 'ACTIVITY']
            self._cookie = ''
            for cookie in cj:
                if cookie.name in cookiename:
                    self._cookie += ( cookie.name + '=' + cookie.value + '; ' )
            self._cookie = self._cookie[0:-2]

            re_st = re.compile('\'XSRF_TOKEN\'\: \"([^\"]+)\"\,')
            self._session_token = re_st.findall(src)[0]

            
            
            # test
            try:
                self.single_crawl(self._seed_videoID)
            except Exception, e:
                if 'Invalid request' in str(e):
                    continue
                else:
                    self._mutex_crawl.release()
                    self.email('meet error when update the cookies, please set a new seed video (%s)' % str(e))
                    raise Exception('meet error when update the cookies, please set a new seed video (%s)' % str(e))
                    
            state = 'success'
            break
        

        if state == 'fail':
            self.email('times of updating cookies reaches maximum, please report this on github (%s)' % str(e))
            self._mutex_crawl.release()
            raise Exception('times of updating cookies reaches maximum, please report this on github (%s)' % str(e))

        self._mutex_crawl.release()

        self._last_cookie_update_time = datetime.datetime.now()

        self._current_update_cookie_timer = threading.Timer(self._update_cookie_period, self.update_cookie_and_sectiontoken)
        self._current_update_cookie_timer.daemon = True
        self._current_update_cookie_timer.start()
        
    def email(self, s):
        send_email('[ acro: video history crawling: ]', s, self._email_from_addr, self._email_password, self._email_to_addr)
    
    def get_header(self, k):
        headers = {}
        headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        #headers['Accept-Encoding'] = 'gzip, deflate'
        headers['Accept-Language'] = 'en-US,en;q=0.5'
        headers['Content-Length'] = '280'
        headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        headers['Cookie'] = self._cookie
        headers['Host'] = 'www.youtube.com'
        headers['Referer'] = 'https://www.youtube.com/watch?v=' + k
        headers['User-Agent'] = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:31.0) Gecko/20100101 Firefox/31.0'
        
        return headers

    def get_post_data(self):
        return urllib.urlencode( {'session_token': self._session_token} )

    def check_key(self, k):
        if len(k) == 11:
            return True
        else:
            return False
    
    def crawl_thread(self, keyfile):
        """ the function to iterate through the keyfile and try to download the data
        
        Arguments:
        - `keyfile`:
        """
        
        while True:
            # read a line from the file
            self._mutex_crawl.acquire()
            l = keyfile.readline()
            self._mutex_crawl.release()

            if l == '':
                # the keyfile is finished
                self._is_done = True
                break

            key = l.strip(' \t\n')

            if key in self._key_done or not self.check_key(key):
                # key has already been crawled or the key is not correct
                continue
            
            url = self.get_url(key)
            data = self.get_post_data()
            header = self.get_header(key)

            txt = ''
            try:
                self.mutex_delay(self._crawl_delay_time)
                request = urllib2.Request(url, data, headers=header)
                txt = urllib2.urlopen(request).read()


                if '<p>Public statistics have been disabled.</p>' in txt:
                    self._logger.log_warn( key, 'statistics disabled', 'disabled' )
                    self._key_done.add( key )
                    continue
                
                if '<error_message><![CDATA[Video not found.]]></error_message>' in txt:
                    self._logger.log_warn( key, 'Video not found', 'notfound' )
                    self._key_done.add( key )
                    continue

                if '<error_message><![CDATA[Sorry, quota limit exceeded, please retry later.]]></error_message>' in txt:
                    self._logger.log_warn( key, 'Quota limit exceeded', 'quotalimit' )
                    continue
                
                if 'No statistics available yet' in txt:
                    self._logger.log_warn( key, 'No statistics available yet', 'nostatyet' )
                    self._key_done.add( key )
                    continue

                if '<error_message><![CDATA[Invalid request.]]></error_message>' in txt:
                    self._logger.log_warn( key, 'Invalid request', 'invalidrequest' )
                    continue

                if '<error_message><![CDATA[Video is private.]]></error_message>' in txt:
                    self._logger.log_warn( key, 'Private video', 'private' )
                
                self._logger.log_done( key )
                self.store(key, txt)
                self._key_done.add(key)
            except Exception, e:
                self._logger.log_warn( key, str(e) )

               
    def batch_crawl(self,  input_file, output_dir ):
        """ 
        
        Arguments:
        - `input_file`: the file that includes the keys (e.g. video IDs)
        - `output_dir`: the dir to output crawled data
        """
        self._input_file = open(input_file)
        self._output_dir = output_dir

        self._logger = Logger(self._output_dir)
        self._logger.add_log({'disabled': 'key.disabled', 'notfound': 'key.notfound', 'quotalimit': 'key.quotalimit', 'nostatyet': 'key.nostatyet', 'invalidrequest': 'key.invalidrequest', 'private': 'key.private'})
        
        self._key_done = set(self._logger.get_key_done(['notfound', 'nostatyet', 'disabled', 'private']))

        self._delay_mutex = threading.Lock()

        
        self.update_cookie_and_sectiontoken()
        threads = []
        for i in range(0, self._num_thread):
            threads.append(threading.Thread(target=self.crawl_thread, args=(self._input_file, )))
            
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self._current_update_cookie_timer.cancel()
        
    
    def single_crawl(self, key):
        """crawl video
        
        Arguments:
        - `key`: videoID
        """
        if self._last_cookie_update_time == None:
            self.update_cookie_and_sectiontoken()

            
        url = self.get_url(key)
        data = self.get_post_data()
        header = self.get_header(key)

        txt = ''

        request = urllib2.Request(url, data, headers=header)
        txt = urllib2.urlopen(request).read()

        if '<p>Public statistics have been disabled.</p>' in txt:
            raise Exception('statistics disabled')

        if '<error_message><![CDATA[Video not found.]]></error_message>' in txt:
            raise Exception('Video not found')

        if '<error_message><![CDATA[Sorry, quota limit exceeded, please retry later.]]></error_message>' in txt:
            raise Exception('Quota limit exceeded')

        if 'No statistics available yet' in txt:
            raise Exception('No statistics available yet')

        if '<error_message><![CDATA[Invalid request.]]></error_message>' in txt:
            raise Exception('Invalid request')

        if '<error_message><![CDATA[Video is private.]]></error_message>' in txt:
            raise Exception('private video')

        
        return parseString(txt)
    
