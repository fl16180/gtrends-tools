#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals
import csv
import datetime
import sys
import time

reload(sys)
sys.setdefaultencoding("utf-8")

from googleapiclient.discovery import build

from healthtrends.decorators import retry, timeit


class TrendsSession(object):
    ''' Calls the Google Trends API on a list of search queries.

        The API is rate-limited so search queries are broken
        up into batches for separate API calls.
    '''
    # server constants
    SERVER = 'https://www.googleapis.com'
    API_NAME = 'trends'
    API_VERSION = 'v1beta'
    DISCOVERY_URL_SUFFIX = '/discovery/v1/apis/trends/' + API_VERSION + '/rest'
    DISCOVERY_URL = SERVER + DISCOVERY_URL_SUFFIX

    # set global start and end dates as defaults for requesting trends
    GLOBAL_START = '2004-01-04'
    GLOBAL_END = time.strftime('%Y-%m-%d')

    def __init__(self, api_key, query_lim=2):
        print('------- Google Trends API session -------')
        print(datetime.datetime.now())

        if api_key is None:
            raise ValueError('API key not set.')
        self.api_key = api_key

        self.query_lim = query_lim
        self.output = {}

        # set up session
        self.service = build(self.API_NAME,
                             self.API_VERSION,
                             developerKey=self.api_key,
                             discoveryServiceUrl=self.DISCOVERY_URL)

        self.geo_level = None
        self.geo_id = None
        self.start_date = None
        self.end_date = None
        self.freq = None

    @timeit
    def request_trends(self, term_list, geo_level, geo_id,
                       start_date=None, end_date=None, freq='week'):
        ''' performs a complete Google Trends request using a list of terms
            and relevant parameters.

            @Params:
                term_list: list of search term queries

                geo_level: geographic location, one of 'country', 'region', or 'dma'

                geo_id: name of the geographic location, e.g. 'US' (country),
                    'US-NY' (region), '501' (dma)

                start_date: first day to download data from, in form 'YYYY-MM-DD'. Defaults to
                    '2004-01-04'.

                end_date: last day to download data from, in form 'YYYY-MM-DD'. Defaults to
                    today's date.

                freq: time interval of data, one of 'day', 'week', 'month', 'year'. Defaults
                    to 'week'.
        '''
        # default behavior for download date range
        if start_date is None:
            start_date = self.GLOBAL_START
        if end_date is None:
            end_date = self.GLOBAL_END

        self.geo_level = geo_level
        self.geo_id = geo_id
        self.start_date = start_date
        self.end_date = end_date
        self.freq = freq

        print('Starting download:')
        print('\tgeo_level: ', geo_level, '\tgeo_id: ', geo_id)

        # split query list into batches and download each batch separately
        dat = {}
        for batch_start in range(0, len(term_list), self.query_lim):
            batch_end = min(batch_start + self.query_lim, len(term_list))
            batch = term_list[batch_start:batch_end]

            dat.update(self._batch_request(batch))

        # Convert dictionary to list of lists that will be written to file
        res = [['date'] + term_list]
        for date in sorted( list( set([x[1] for x in dat] )) ):
            vals = [dat.get((term, date), 0) for term in term_list]
            res.append([date] + vals)
        self.output = res

        print('Download completed.')

    def save_to_csv(self, full_path=None, directory=None, fname='default'):
        ''' save Google Trends output as csv file
        '''
        if full_path:
            csv_out = open(full_path, 'wb')
        elif directory:
            if fname == 'default':
                csv_out = open(directory + '/GTdata_{0}.csv'.format(self.geo_id), 'wb')
            else:
                csv_out = open(directory + '/' + fname, 'wb')
        else:
            raise ValueError('Either full_path or directory must be specified to save file.')

        writr = csv.writer(csv_out)

        for row in self.output:
            writr.writerow(row)
        csv_out.close()

    @staticmethod
    def _date_to_ISO(datestring):
        ''' Default function from Google Trends documentation.

        Convert date from (eg) 'Jul 04 2004' to '2004-07-11'.

        Args:
        datestring: A date in the format 'Jul 11 2004', 'Jul 2004', or '2004'

        Returns:
        The same date in the format '2004-07-11'

        Raises:
         ValueError: when date doesn't match one of the three expected formats.
        '''

        try:
            new_date = datetime.datetime.strptime(datestring, '%b %d %Y')
        except ValueError:
            try:
                new_date = datetime.datetime.strptime(datestring, '%b %Y')
            except ValueError:
                try:
                    new_date = datetime.datetime.strptime(datestring, '%Y')
                except:
                    raise ValueError("Date doesn't match any of '%b %d %Y', '%b %Y', '%Y'.")

        return new_date.strftime('%Y-%m-%d')

    @retry(count=10, delay=2)
    def _batch_request(self, batch):
        ''' executes the API request on a batch of search terms.

            This is default code from Google Trends documentation.
        '''
        if self.geo_level == 'country':
            # Country format is ISO-3166-2 (2-letters), e.g. 'US'
            req = self.service.getTimelinesForHealth(terms=batch,
                                                     time_startDate=self.start_date,
                                                     time_endDate=self.end_date,
                                                     timelineResolution=self.freq,
                                                     geoRestriction_country=self.geo_id)
        elif self.geo_level == 'dma':
            # See https://support.google.com/richmedia/answer/2745487
            req = self.service.getTimelinesForHealth(terms=batch,
                                                     time_startDate=self.start_date,
                                                     time_endDate=self.end_date,
                                                     timelineResolution=self.freq,
                                                     geoRestriction_dma=self.geo_id)
        elif self.geo_level == 'region':
            # Region format is ISO-3166-2 (4-letters), e.g. 'US-NY' (see more examples
            # here: en.wikipedia.org/wiki/ISO_3166-2:US)
            req = self.service.getTimelinesForHealth(terms=batch,
                                                     time_startDate=self.start_date,
                                                     time_endDate=self.end_date,
                                                     timelineResolution=self.freq,
                                                     geoRestriction_region=self.geo_id)
        else:
            raise ValueError("geo_level must be one of 'country', 'region' or 'dma'")

        # execute command and sleep to avoid rate limiting
        res = req.execute()
        time.sleep(1.1)

        # Convert returned data into a dictionary of the form {(query, date): count, ...}
        res_dict = {(line['term'], self._date_to_ISO(point['date'])): point['value']
                        for line in res['lines']
                            for point in line['points']}
        return res_dict
