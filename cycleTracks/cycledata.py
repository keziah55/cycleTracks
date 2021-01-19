#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 28 19:25:42 2020

@author: keziah
"""

from datetime import datetime
import numpy as np
import pandas as pd


class CycleData:
    
    def __init__(self, df):
        """ Object providing convenience functions for accessing data from 
            a given DataFrame of cycling data.
        """
        self.df = df
        self.propertyNames = {'Distance (km)':self.distance, 
                              'Date':self.date,
                              'Time':self.time,
                              'Calories':self.calories,
                              'Avg speed (km/hr)':self.avgSpeed,
                              'Avg. speed (km/hr)':self.avgSpeed}
        
    def __len__(self):
        return len(self.df)
    
    def __getitem__(self, key):
        if key in self.propertyNames.keys():
            return self.propertyNames[key]
        else:
            raise NameError(f"{key} not a valid property name.")
        
    @staticmethod
    def _timeToSecs(t):
        msg = ''
        # don't actually need the datetime objects returned by strptime, but 
        # this is probably the easist way to check the format
        try:
            datetime.strptime(t, "%H:%M:%S")
            hr, mins, sec = [int(s) for s in t.split(':')]
        except ValueError:
            try:
                datetime.strptime(t, "%M:%S")
                mins, sec = [int(s) for s in t.split(':')]
                hr = 0
            except ValueError:
                msg = f"Could not format time '{t}'"
        if msg:
            raise ValueError(msg)
        
        total = sec + (60*mins) + (60*60*hr)
        return total
    
    @staticmethod
    def _convertSecs(t, mode='hour'):
        valid = ['mins', 'hour']
        if mode not in valid:
            msg = f"Mode '{mode}' not in valid modes: {valid}"
            raise ValueError(msg)
        m = t / 60
        if mode == 'mins':
            return m
        h = m / 60
        if mode == 'hour':
            return h
        
    @property
    def distance(self):
        """ Return 'Distance (km)' column as numpy array. """
        return np.array(self.df['Distance (km)'])
    
    @property
    def time(self):
        """ Return 'Time' column as list. """
        return list(self.df['Time'])
    
    @property
    def date(self):
        """ Return 'Date' column as list. """
        return list(self.df['Date'])
    
    @property
    def calories(self):
        """ Return 'Calories' column as numpy array. """
        return np.array(self.df['Calories'])
    
    @property
    def timeHours(self):
        """ Return numpy array of 'Time' column, where each value is converted
            to hours.
        """
        time = [self._timeToSecs(t) for t in self.df['Time']]
        time = np.array([self._convertSecs(s) for s in time])
        return time
    
    @property
    def dateTimestamps(self):
        """ Return 'Date' column, converted to array of timestamps (time since 
            epoch).
    
            See also: :py:meth:`datetimes`.
        """
        return np.array([dt.timestamp() for dt in self.datetimes])

    @property
    def datetimes(self):
        """ Return 'Date' column, converted to list of datetime objects. """
        fmt = "%Y-%m-%d"
        # 'strptime(d.strftime(fmt), fmt)' this is ugly and is required 
        # because the Date column is a pandas datetime object, but it adds an
        # empty time to the date, which we need to get rid of here, before
        # calling datetime.strptime
        return [datetime.strptime(d.strftime(fmt), fmt) for d in self.df['Date']]
    
    @property
    def dateFmt(self, fmt="%a %d %b %Y"):
        return [dt.strftime(fmt) for dt in self.datetimes]
    
    @property 
    def avgSpeed(self):
        """ Return average speeds as numpy array. """
        return self.distance/self.timeHours
    
    def splitMonths(self):
        """ Split `df` into list of DataFrames, split by month. """
        grouped = self.df.groupby(pd.Grouper(key='Date', freq='M'))
        return [group for _,group in grouped]
    
    def getMonthlyOdometer(self):
        """ Return list of datetime objects and list of floats.
            
            The datetime objects are required, as they add dummy 1st of the 
            month data points to reset the total to 0km.
        """
        
        odo = []
        dts = []
            
        for i, dt in enumerate(self.datetimes):
            if i == 0 or self.datetimes[i-1].month != dt.month:
                tmp = datetime(self.datetimes[i].year, self.datetimes[i].month, 1)
                dts.append(tmp)
                prev = 0
                odo.append(prev)
            else:
                prev = odo[-1]
            dts.append(dt)
            odo.append(prev + self.distance[i-1])
        
        return dts, odo
    