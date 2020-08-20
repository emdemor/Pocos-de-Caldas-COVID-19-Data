#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Description
----------
The country object contains information and actions 
related the countries that are important to understand 
the Covid dissemination

Informations
----------
    Author: Eduardo M.  de Morais
    Maintainer:
    Email: emdemor415@gmail.com
    Copyright:
    Credits:
    License:
    Version:
    Status: in development
    
"""

import pandas as pd
import numpy as np

from .functions import set_dir_struct, riffle, file_names, set_directory, distribute_among_walkers
from os import path

# empty dataframe to use in case of error
__EMPTY_DATAFRAME__ = pd.DataFrame({'ID' :[],
                                  'Updated' :[],
                                  'Confirmed' :[],
                                  'ConfirmedChange' :[],
                                  'Deaths' :[],
                                  'DeathsChange' :[],
                                  'Recovered' :[],
                                  'RecoveredChange' :[],
                                  'Latitude' :[],
                                  'Longitude' :[],
                                  'ISO2' :[],
                                  'ISO3' :[],
                                  'Country_Region' :[],
                                  'AdminRegion1' :[],
                                  'AdminRegion2' :[]})



# global variables to use as standard 
__DATASET_URL__ = 'https://raw.githubusercontent.com/microsoft/Bing-COVID-19-Data/master/data/Bing-COVID19-Data.csv'

__DATASET_FILENAME__ = 'Bing-COVID19-Data.csv'





def read_dataset(update_data = False,
                 url         = __DATASET_URL__,
                 local_dataset_filename = __DATASET_FILENAME__,
                 dataset_struct = "microsoft-bing"):
    '''
    Description
    ----------
    This function imports the Microsoft dataset from local source. If
    required, downloads the updated date from online source and saves 
    it on the tables directory, owerwritten the previous file.

    After import, converts the columns to the right types, change the
    name of some countries and creates a new column for active infections.

    Arguments
    ----------
    update_data: bool
        Controls if the data will be updated

    url: str
        URL to download the online sourde

    local_dataset_filename: str
        Name (without path) of localbase dataset

    Return
    ----------
    df: Pandas.DataFrame
        Final dataset
        
    '''

    if dataset_struct == "microsoft-bing":
	    # join filename with directory
	    #filename = path.join(tables_directory, local_dataset_filename)
	    filename = local_dataset_filename

	    # updating when required
	    if update_data:
	        update_local_base(url,filename)
	    
	    #importing dataset
	    df = import_from_localbase(filename)[0]

	    # Filling NA values
	    df[['ISO2','ISO3','Country_Region','AdminRegion1','AdminRegion2']] = df[['ISO2','ISO3','Country_Region','AdminRegion1','AdminRegion2']].fillna('')
	    df[['Confirmed','ConfirmedChange','Deaths','DeathsChange','Recovered','RecoveredChange']] = df[['Confirmed','ConfirmedChange','Deaths','DeathsChange','Recovered','RecoveredChange']].fillna(0)
	    
	    # Type coversion
	    df[['Confirmed','ConfirmedChange','Deaths','DeathsChange','Recovered','RecoveredChange']] = df[['Confirmed','ConfirmedChange','Deaths','DeathsChange','Recovered','RecoveredChange']].astype(float)
	    df[['ISO2','ISO3','Country_Region','AdminRegion1','AdminRegion2']] = df[['ISO2','ISO3','Country_Region','AdminRegion1','AdminRegion2']].astype(str)
	    
	    # Replacing Countries names
	    df['Country_Region'] = df['Country_Region'].replace('China (mainland)','China')
	    
	    # Creating a new column
	    df['Actives'] = df['Confirmed']-df['Deaths']-df['Recovered']

	    return df


def import_from_url(url):
    '''
    Description
    ----------
    
    Arguments
    ----------
        
    '''

    try:
        print('[status]: Downloading dataset from source.')
        dataframe = pd.read_csv(url,sep=",",parse_dates=['Updated'])
        return [dataframe,True]

    except:
        # When occours some
        print('[error]: It was not possible to download data from online source.')
        return [__EMPTY_DATAFRAME__,False]



def import_from_localbase(filename):
    '''
    Description
    ----------
    
    Arguments
    ----------
        
    '''
    try:
        if not path.exists(filename):
            print('[warng]: There is no previous dataset on the localfile. Dataset must be downloaded from online source.')
            print('[mssge]: Getting data from online source :'+__DATASET_URL__+'.')
            update_local_base(__DATASET_URL__,filename)

        print('[status]: Importing dataset from localbase.')
        dataframe = pd.read_csv(filename,sep=",",parse_dates=['Updated'])
        return [dataframe,True]

    except:
        print('[error]: There is no local base file.')
        return [__EMPTY_DATAFRAME__,False]


def export_to_local_base(df,address):
    '''
    Description
    ----------
    
    Arguments
    ----------
        
    '''
    try:
        print('[status]: Updating local dataset base.')
        df.to_csv(address,sep=',',index=False)
    except:
        print('[error]: It was not possible to export data to local base.')


def update_local_base(url,address):
    '''
    Description
    ----------
    
    Arguments
    ----------
        
    '''

    try:
        df,__IMPORT_STATUS__ = import_from_url(url)

        if __IMPORT_STATUS__ :
            export_to_local_base(df,address)
        else:
            if not path.exists(address):
                print('[error]: Is impossible to access the data from local base or online source.')
            else:
                print('[mssge]: Keeping the previous data on local base.')
    except:
        print('[error]: It was not possible update local base.')





class region_dataset:
    '''
    Description
    ----------
    The region_dataset object contains information and actions related the regions
    that are important to understand the Covid dissemination

    Arguments
    ----------
    name: str
        String passed by the user to label the country
        
    population: int
        Integer number passed by the user counting people in the related 
        country

    Parameters
    ----------
    self.name: str
        String used to label the country.
        
    self.population: int
        Integer number with the number of people in the related country
        
    self.dataframe: pandas.DataFrame
        DataFrame object with data about covid cases.
        
    self.days_list: numpy.ndarray
        Numpy array with the days after first confirmed covid case
        
    self.confirmed_list: numpy.ndarray
        Numpy array with the number of confirmed cases. Must have the same 
        length of self.days_list
        
    self.recovered_list: numpy.ndarray
        Numpy array with the number of recovered cases. Must have the same 
        length of self.days_list
        
    self.death_list: numpy.ndarray
        Numpy array with the number of deaths cases. Must have the same 
        length of self.days_list
        
    '''
    
    def __init__(self,
        data,
        name,
        population,
        rescaling_by  = 1,
        last_index    = -1,
        time_col      = 'Updated',
        confirmed_col = 'Confirmed',
        recovered_col = 'Recovered',
        deaths_col    = 'Deaths',
        actives_col   = 'Actives'
        ):
        
        """
        Receive a global dataframe with COVID data from microsoft repository,
        select those related to informed country and sets the country class' 
        parameters

        Parameters
        ----------
        data_Country : pandas dataframe
            Filter the information related to the country
            
        first_case : timestamp
            Date of fist covid case
        
        Returns
        -------
        void
        
        """
        
        # getting the first case
        first_case = data[time_col].min()
        
        # couting the days after first case
        data['Days'] = (data[time_col] - first_case).dt.days.astype(float)
        
        # rescaling cases by a factor
        data[[confirmed_col,actives_col,deaths_col,recovered_col]] = data[[confirmed_col,actives_col,deaths_col,recovered_col]]*rescaling_by

        self.dataframe = data[[time_col,'Days',confirmed_col,recovered_col,deaths_col,actives_col]]
        self.dataframe.rename(columns={
        	time_col : 'Updated',
        	'Days' : 'Days',
        	confirmed_col : 'Confirmed',
        	recovered_col : 'Recovered',
        	deaths_col : 'Deaths',
        	actives_col : 'Actives'
        	},inplace = True)
        
        # converting columns to lists
        self.days_list = data['Days'].to_numpy()
        self.confirmed_list = data[confirmed_col].to_numpy()
        self.death_list = data[deaths_col].to_numpy()
        self.recovered_list = data[recovered_col].fillna(0).to_numpy()
        
        