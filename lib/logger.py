"""The logger class supporting the crawler"""
# Author: Honglin Yu <yuhonglin1986@gmail.com>
# License: BSD 3 clause

import os
import time

class Logger(object):
    """record the crawling status, error and warnings
    """
    
    def __init__(self, outputDir=""):
        """
        
        Arguments:
        - `outputDir`:
        """
        self._output_dir = outputDir
        self._log_file_dict = {'log' : open(self._output_dir + '/log', 'a+r')}
        
        #self._mutex_done = threading.Lock()
        #self._mutex_log = threading.Lock()

        self._done_file = open(self._output_dir + '/key.done', 'a+r')

    def add_log(self, d):
        """
        
        Arguments:
        - `d`: log_file_key : log_file_name
        """
        for i, j in d.iteritems():
            self._log_file_dict[i] = open(self._output_dir + j, 'a+r')
            
    def get_key_done(self, lfkl):
        """get the keys that have been crawled

        Arguments:
        - `lfkl`: additional list that want to put input done list
        """
        r = []

        for i in lfkl:
            tmp = self._log_file_dict[i]
            for l in tmp:
                r.append( eval(l)[1] )
        
        return r + [x.rstrip('\n') for x in self._done_file]

    def log_done(self, k):
        """ this function is thread safe
        
        Arguments:
        - `k`:
        """
        #self._mutex_done.acquire()
        self._done_file.write( '%s\n' % k )
        self._done_file.flush()
        #self._mutex_done.release()
        
    def log_warn(self, k, m, lfk='log'):
        """log message as warning
        
        Arguments:
        - `k` : the key
        - `m`: the message
        - `lfk`: log_file_key
        """
        #self._mutex_log.acquire()
        self._log_file_dict[lfk].write( str([time.strftime('%Y_%m_%d_%m_%H_%M'), k, m ]) + '\n' )
        self._log_file_dict[lfk].flush()
        #self._mutex_log.release()
    
        

        
