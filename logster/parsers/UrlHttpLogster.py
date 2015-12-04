###  A sample logster parser file that can be used to count the number
###  of response codes found in an Apache access log.
###
###  For example:
###  sudo ./logster --dry-run --output=graphite UrlHttpLogster /var/log/httpd/access_log
###
###
###  Copyright 2011, Etsy, Inc.
###
###  This file is part of Logster.
###
###  Logster is free software: you can redistribute it and/or modify
###  it under the terms of the GNU General Public License as published by
###  the Free Software Foundation, either version 3 of the License, or
###  (at your option) any later version.
###
###  Logster is distributed in the hope that it will be useful,
###  but WITHOUT ANY WARRANTY; without even the implied warranty of
###  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
###  GNU General Public License for more details.
###
###  You should have received a copy of the GNU General Public License
###  along with Logster. If not, see <http://www.gnu.org/licenses/>.
###

import time
import re
import optparse

from logster.logster_helper import MetricObject, LogsterParser
from logster.logster_helper import LogsterParsingException

class UrlHttpLogster(LogsterParser):

    def __init__(self, option_string=None):
        '''Initialize any data structures or variables needed for keeping track
        of the tasty bits we find in the log we are parsing.'''
        self.http_1xx = 0
        self.http_2xx = 0
        self.http_3xx = 0
        self.http_4xx = 0
        self.http_5xx = 0

        self.key_url = 'test'
        self.url_regexp = '\/.*'

        if option_string:
            options = option_string.split(' ')
        else:
            options = []

        optparser = optparse.OptionParser()

        optparser.add_option('--key-url', '-k', dest='key_url', default='test',
        help='Key under which to record the metrics: \'.\'')

        optparser.add_option('--url-regexp', '-u', dest='url_regexp', default='\/.*',
        help='Regexp to constrain the URL match to: \'.\'')

        opts, args = optparser.parse_args(args=options)
        self.key_url = opts.key_url
        self.url_regexp = opts.url_regexp

        # Regular expression for matching lines we are interested in, and capturing
        # fields from the line (in this case, url and http_status_code).
        self.reg = re.compile('.*? \"(GET|POST) (?P<url>'+self.url_regexp+') HTTP/1.\d\" (?P<http_status_code>\d{3}) .*')


    def parse_line(self, line):
        '''This function should digest the contents of one line at a time, updating
        object's state variables. Takes a single argument, the line to be parsed.'''

        try:
            # Apply regular expression to each line and extract interesting bits.
            regMatch = self.reg.match(line)

            if regMatch:
                linebits = regMatch.groupdict()
                status = int(linebits['http_status_code'])
                url = linebits['url']

                if (status < 200):
                    self.http_1xx += 1
                elif (status < 300):
                    self.http_2xx += 1
                elif (status < 400):
                    self.http_3xx += 1
                elif (status < 500):
                    self.http_4xx += 1
                else:
                    self.http_5xx += 1

            else:
                raise LogsterParsingException("regmatch failed to match")

        except Exception as e:
            raise LogsterParsingException("regmatch or contents failed with %s" % e)


    def get_state(self, duration):
        '''Run any necessary calculations on the data collected from the logs
        and return a list of metric objects.'''
        self.duration = float(duration)

        # Return a list of metrics objects
        return [
            MetricObject(self.key_url+".http_1xx", (self.http_1xx / self.duration), "Responses per sec"),
            MetricObject(self.key_url+".http_2xx", (self.http_2xx / self.duration), "Responses per sec"),
            MetricObject(self.key_url+".http_3xx", (self.http_3xx / self.duration), "Responses per sec"),
            MetricObject(self.key_url+".http_4xx", (self.http_4xx / self.duration), "Responses per sec"),
            MetricObject(self.key_url+".http_5xx", (self.http_5xx / self.duration), "Responses per sec"),
        ]
