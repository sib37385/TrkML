#!/usr/bin/env python
# coding: utf-8

# **A collection of useful basic functions for manipulating pandas dataframes.**  
# 
# Functionality includes (among others):
# - selecting DCS-bit on data or golden json data.
# - selecting specific runs, lumisections, or types of histograms



### imports

# external modules
import os
import pandas as pd
import numpy as np
import json
import importlib

# local modules
import json_utils
importlib.reload(json_utils)


#merges multiple csvs into one df per lumisection
def merge_ls(df):
    numhistos = 0
    lumi = df.get('fromlumi').get(0)
    #how many histograms are there to merge?
    for i in range(len(df.get('hname'))):
        if df.get('fromlumi').get(i) == lumi: numhistos = numhistos+1
        else: break
    list1 = []
    check = len(df)
    
    #iterator = 0
    for i in range(0, check , numhistos):
        listof = []
        entries = 0
        histo = ""
        Xbins = 0
        #checks for repeat histos, like in chi^2 trk. Appends histograms from multiple csvs to one histogram
        for j in range(0,numhistos,1):
            if (j == 0 and df['hname'][j+i] != df['hname'][j+i+1]):
                length = len(df['histo'][j+i])
                histo = histo + (df['histo'][j+i])[0:length-1]
                entries = entries + df['entries'][i+j]    
                Xbins = Xbins + df['Xbins'][j+i]
            elif (i+j+1 == check):
                length = len(df['histo'][j+i])
                entries = entries + df['entries'][i+j]                
                Xbins = Xbins + df['Xbins'][j+i] + 2 
                histo = histo + ', ' + (df['histo'][j+i])[1:length]
                break
            elif (j == 1 and df['hname'][j+i] == df['hname'][j+i-1]):
                length = len(df['histo'][j+i])
                histo = histo + (df['histo'][j+i])[0:length-1]
                entries = entries + df['entries'][i+j]    
                Xbins = Xbins + df['Xbins'][j+i]     
            elif (j!=0 and df['hname'][j+i] != df['hname'][j+i+1]):                          
                length = len(df['histo'][j+i])
                entries = entries + df['entries'][i+j]                
                Xbins = Xbins + df['Xbins'][j+i] + 2 
                if (j == numhistos-1):                
                    histo = histo + ', ' + (df['histo'][j+i])[1:length]
                else:               
                    histo = histo + ', ' + (df['histo'][j+i])[1:length-1]
                      
        listof = [df['fromrun'][i], df['fromlumi'][i], 'combined', df['fromrun.1'][i], df['fromlumi.1'][i], df['metype'][i], 'combined', histo, entries, df['Xmax'][i], df['Xmin'][i], Xbins , df['Ymax'][i], 1, 1]
        list1.append(listof)
        #iterator = iterator + 1
    newDF = pd.DataFrame(list1, columns = [ 'fromrun', 'fromlumi', 'hname', 'fromrun.1', 'fromlumi.1','metype', 'hname.1', 'histo', 'entries', 'Xmax', 'Xmin', 'Xbins', 'Ymax', 'Ymin', 'Ybins'])    
    return newDF

            


          
# getter and selector for histogram names 

def get_histnames(df):
    ### get a list of (unique) histogram names present in a df
    # df is a dataframe read from an input csv file.
    histnamelist = []
    for i in list(df.index):
        val = df.at[i,'hname'] 
        if val not in histnamelist: 
            histnamelist.append(val)
    return histnamelist
    
def select_histnames(df, histnames):
    ### keep only a subset of histograms in a df
    # histnames is a list of histogram names to keep in the df.
    df = df[df['hname'].isin(histnames)]
    df.reset_index(drop=True,inplace=True)
    return df

# getter and selector for run numbers

def get_runs(df):
    ### return a list of (unique) run numbers present in a df
    # df is a dataframe read from an input csv file.
    runlist = []
    for i in list(df.index):
        val = df.at[i,'fromrun'] 
        if val not in runlist: 
            runlist.append(val)
    return runlist

def select_runs(df, runnbs):
    ### keep only a subset of runs in a df
    # runnbs is a list of run numbers to keep in the df.
    df = df[df['fromrun'].isin(runnbs)]
    df.reset_index(drop=True,inplace=True)
    return df

# getter and selector for lumisection numbers

def get_ls(df):
    ### return a list of ls numbers present in a df
    # note that the numbers are not required to be unique!
    # note: no check is done on the run number!
    lslist = []
    for i in list(df.index):
        val = df.at[i,'fromlumi']
        lslist.append(val)
    return lslist

def select_ls(df, lsnbs):
    ### keep only a subset of lumisection numbers in a df
    # lsnbs is a list of lumisection numbers to keep in the df.
    # note: no check is done on the run number!
    df = df[df['fromlumi'].isin(lsnbs)]
    df.reset_index(drop=True,inplace=True)
    return df

### general getter and selector in json format

def get_runsls(df):
    ### return a dictionary with runs and lumisections in a dataframe (same format as e.g. golden json)
    runslslist = get_runs(df)
    for i,run in enumerate(runslslist):
        runslslist[i] = (run,get_ls(select_runs(df,[run])))
    return json_utils.tuplelist_to_jsondict( runslslist )

def select_json(df, jsonfile):
    ### keep only lumisections that are in the given json file
    dfres = df[ json_utils.injson(df['fromrun'].values,df['fromlumi'].values,jsonfile=jsonfile) ]
    dfres.reset_index(drop=True,inplace=True)
    return dfres

def select_runsls(df, jsondict):
    ### equivalent to select_json but using a pre-loaded json dict instead of a json file on disk
    dfres = df[ json_utils.injson(df['fromrun'].values,df['fromlumi'].values,jsondict=jsondict) ]
    dfres.reset_index(drop=True,inplace=True)
    return dfres

### selectors for golden json and other important json files

def select_golden(df):
    ### keep only golden lumisections in df
    dfres = df[ json_utils.isgolden(df['fromrun'].values,df['fromlumi'].values) ]
    dfres.reset_index(drop=True,inplace=True)
    return dfres

def select_notgolden(df):
    ### keep all but golden lumisections in df
    dfres = df[np.invert( json_utils.isgolden(df['fromrun'].values,df['fromlumi'].values) )]
    dfres.reset_index(drop=True,inplace=True)
    return dfres

def select_dcson(df):
    ### keep only lumisections in df that have DCS-bit on
    dfres = df[ json_utils.isdcson(df['fromrun'].values,df['fromlumi'].values) ]
    dfres.reset_index(drop=True,inplace=True)
    return dfres

def select_dcsoff(df):
    ### keep only lumisections in df that have DCS-bit off
    dfres = df[np.invert( json_utils.isdcson(df['fromrun'].values,df['fromlumi'].values) )]
    dfres.reset_index(drop=True,inplace=True)
    return dfres

def select_pixelgood(df):
    ### keep only lumisections in df that are in good pixel json
    dfres = df[ json_utils.ispixelgood(df['fromrun'].values,df['fromlumi'].values) ]
    dfres.reset_index(drop=True,inplace=True)
    return dfres


def select_pixelbad(df):
    ### keep only lumisections in df that are in bad pixel json
    dfres = df[ json_utils.ispixelbad(df['fromrun'].values,df['fromlumi'].values) ]
    dfres.reset_index(drop=True,inplace=True)
    return dfres

# getter and selector for sufficient statistics

def get_highstat(df, entries_to_bins_ratio=100):
    ### return a select object of runs and ls of histograms with high statistics
    return get_runsls(df[df['entries']/df['Xbins']>entries_to_bins_ratio])

def select_highstat(df, entries_to_bins_ratio=100):
    ### keep only lumisection in df with high statistics
    return select_runsls(df,get_highstat(df,entries_to_bins_ratio))




# functions to obtain histograms in np array format

def get_hist_values(df):
    ### same as builtin "df['histo'].values" but convert strings to np arrays
    # input arguments:
    # - df: a dataframe containing histograms (assumed to be of a single type!)
    # note: this function works for both 1D and 2D histograms,
    #       the distinction is made based on whether or not 'Ybins' is present as a column in the dataframe
    #       update: 'Ybins' is also present for 1D histograms, but has value 1!
    # output:
    # a tuple containing the following elements:
    # - np array of shape (nhists,nbins) (for 1D) or (nhists,nybins,nxbins) (for 2D)
    # - np array of run numbers of length nhists
    # - np array of lumisection numbers of length nhists
    # warning: no check is done to assure that all histograms are of the same type!
    dim = 1
    if 'Ybins' in df.keys():
        if df.at[0,'Ybins']>1: dim=2
    nxbins = df.at[0,'Xbins']+2 # +2 for under- and overflow bins
    vals = np.zeros((len(df),nxbins))
    if dim==2: 
        nybins = df.at[0,'Ybins']+2
        vals = np.zeros((len(df),nybins,nxbins))
    ls = np.zeros(len(df))
    runs = np.zeros(len(df))
    for i in range(len(df)):
        hist = np.array(json.loads(df.at[i,'histo']))
        nxbins = df.at[i,'Xbins']+2
        if dim==2: hist = hist.reshape((nybins,nxbins))
        vals[i,:] = hist
        ls[i] = int(df.at[i,'fromlumi'])
        runs[i] = int(df.at[i,'fromrun'])
    ls = ls.astype(int)
    runs = runs.astype(int)
    return (vals,runs,ls)





