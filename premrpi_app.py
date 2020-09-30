#!/usr/bin/env python
# coding: utf-8

# This app is a prototype to test capability of streamlit.
"""Prem RPI App. 

A python streamlit web app that shows the English Premier League table with RPI.

To run:
    $streamlit premrpi_app.py

History
v1.0.0 - Nov 2016, First published release
v1.1.0 - Oct 2017, Updated gen_prem_table_RPI() to fix error in calculation for P (number of games played)
v1.2.0 - Nov 2017, Updated gen_prem_table_RPI() so that table is generated for 1st week   
v2.0.0 - Sep 2020, Major change, updated app to use python3 and streamlit
"""

import logging
import logging.config
import premrpi_log_config # dict with logging config
import streamlit as st
import sys 
import requests
import datetime as dt
import pickle
from bs4 import BeautifulSoup, SoupStrainer
import os
import pandas as pd

__author__ = "Terry Dolan"
__copyright__ = "Terry Dolan"
__license__ = "MIT"
__email__ = "terrydolan1892@gmail.com"
__status__ = "Beta"
__version__ = "2.0.0"
__updated__ = "September 2020"

# set up logging
logging.config.dictConfig(premrpi_log_config.dictLogConfig)
logger = logging.getLogger('premrpi')

# ************************
# define utility functions

def get_pl_master_data():
    """Return url of latest premier league results file and the date the file was last updated.
    
    Data source is www.football-data.co.uk.
    Format of returned date is "%Y-%m-%d" (the pandas default).
    """
    logger.info('get_pl_master_data, return url of latest premier league results file and the date the file was last updated')
    # scrape the data from football-data website
    URL_FD_ROOT = 'http://www.football-data.co.uk/'
    ENGLAND_LOCATION = 'englandm.php'
    PL_TEXT = 'Premier League'
    with requests.Session() as session:
        response = session.get(URL_FD_ROOT + ENGLAND_LOCATION)
        soup = BeautifulSoup(response.content, 'lxml')

        # scrape last updated date
        last_updated_tag = soup.find_all('i')[0]
        last_updated_date = last_updated_tag.text.split('Last updated: \t')[1]
        # set date format to be same as pandas default
        last_updated_date = dt.datetime.strptime(last_updated_date, '%d/%m/%y').strftime('%Y-%m-%d')
                                                                                         
        # scrape url of premier league results file
        latest_pl_results_file_tag = soup.findAll('a', href=True, text=PL_TEXT)[0]['href']
        url_latest_pl_results_file = URL_FD_ROOT + latest_pl_results_file_tag                                                                         

    logger.info(f"get_pl_master_data, url of prem league results file: {url_latest_pl_results_file}")
    logger.info(f"get_pl_master_data, last updated date: {last_updated_date}")
    return url_latest_pl_results_file, last_updated_date

def get_pl_results_dataframe(update_cache=False):
    """Return latest premier league results as a dataframe and the date of the results data.
    
    Data source is www.football-data.co.uk.
    Cache data locally to avoid unnecessary calls to football-data website.
    Download results from master data source if local data is out of date.
    """
    logger.info('get_pl_results_dataframe, return latest premier league results as a dataframe and the date of the results data')
    LOCAL_RESULTS_DATA_FILE = 'data/E0.csv'
    PICKLE_FILE = 'save.p' # holds date of results data file

    # get master data source data
    url_latest_pl_results_file, master_results_data_date = get_pl_master_data()
    #print(f"master: url_latest_pl_results_file is {url_latest_pl_results_file}, master_results_data_date is {master_results_data_date}")
    logger.info(f"get_pl_results_dataframe, url_latest_pl_results_file is {url_latest_pl_results_file}, master_results_data_date is {master_results_data_date}")
    
    if update_cache:
        if os.path.exists(PICKLE_FILE):
            os.remove(PICKLE_FILE)

    # get local data source date
    if os.path.exists(PICKLE_FILE):
        local_results_data_date = pickle.load(open(PICKLE_FILE, 'rb'))
        #print(f"local: pickle file {PICKLE_FILE} exists, local_results_data_date is {local_results_data_date}")
        logger.info(f"get_pl_results_dataframe, pickle file {PICKLE_FILE} exists, local_results_data_date is {local_results_data_date}")        
    else:
        local_results_data_date = None
        #print(f"local: pickle file doesn't exists, local_results_data_date is {local_results_data_date}")
        logger.info(f"get_pl_results_dataframe, pickle file doesn't exists, local_results_data_date is {local_results_data_date}")

    if not local_results_data_date or local_results_data_date < master_results_data_date:
        #print('local results data out of date, updating from master results data file')
        logger.info('get_pl_results_dataframe, local results data out of date, updating from master results data file')
        parse_dates_col = ['Date']
        df_results = pd.read_csv(url_latest_pl_results_file, parse_dates=parse_dates_col, dayfirst=True)
        df_results.to_csv(LOCAL_RESULTS_DATA_FILE, index=False)
        local_results_data_date = master_results_data_date
        pickle.dump(local_results_data_date, open(PICKLE_FILE, 'wb'))
    else:
        #print('local results data still latest')
        logger.info('get_pl_results_dataframe, local results data still latest')
        parse_dates_col = ['Date']
        df_results = pd.read_csv(LOCAL_RESULTS_DATA_FILE, parse_dates=parse_dates_col, dayfirst=True)
            
    return df_results, local_results_data_date

def validate_date(date_text):
    """Raise error if date format is not YYYY-MM-DD."""
    try:
        dt.datetime.strptime(date_text, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Incorrect date format, should be YYYY-MM-DD")
        
def simple_date(date_text):
    """Return given date in format '%y-%m-%d' to '%d %b %y'."""
    validate_date(date_text)
    return (dt.datetime.strptime(date_text, '%Y-%m-%d').strftime('%d %b %y'))

def gen_prem_table_RPI(before_date=None, update_cache=False):
    """Return prem table with RPI at given before_date and return data source date."""
    
    results = []
    opponents_d = {}
    df_results, results_date = get_pl_results_dataframe(update_cache)
    
    # filter results in dataframe at given before_date
    if before_date:
        validate_date(before_date)
        first_date = df_results.Date.min().date()
        assert dt.datetime.strptime(before_date, "%Y-%m-%d").date() >= first_date, \
                                        f"before_date {before_date} must be on or after date of first game {first_date}"
        df_results = df_results[df_results.Date <= before_date]
        
    for team in set(df_results.HomeTeam.tolist() + df_results.AwayTeam.tolist()):
        home_results = df_results[df_results['HomeTeam'] == team]
        home_played = len(home_results.index)
        home_win = home_results.FTR[home_results.FTR == 'H'].count()
        home_draw = home_results.FTR[home_results.FTR == 'D'].count()
        home_lose = home_results.FTR[home_results.FTR == 'A'].count()
        home_goals_for = home_results.FTHG.sum()
        home_goals_against = home_results.FTAG.sum()
        home_opponents = list(df_results[df_results.HomeTeam == team].AwayTeam.values)

        away_results = df_results[df_results['AwayTeam'] == team]
        away_played = len(away_results.index)
        away_win = away_results.FTR[away_results.FTR == 'A'].count()
        away_draw = away_results.FTR[away_results.FTR == 'D'].count()
        away_lose = away_results.FTR[away_results.FTR == 'H'].count()
        away_goals_for = away_results.FTAG.sum()
        away_goals_against = away_results.FTHG.sum()
        away_opponents = list(df_results[df_results.AwayTeam == team].HomeTeam.values)

        # add team opponents to dictionary
        team_opponents = home_opponents + away_opponents
        opponents_d[team] = team_opponents
        
        # create team results dictionary and add to results list
        result_d = {} 
        result_d['Team'] = team
        result_d['W'] = home_win + away_win
        result_d['D'] = home_draw + away_draw
        result_d['L'] = home_lose + away_lose
        result_d['GF'] = home_goals_for + away_goals_for
        result_d['GA'] = home_goals_against + away_goals_against
        result_d['GD'] = result_d['GF'] - result_d['GA']
        result_d['PTS'] = result_d['W']*3 + result_d['D']
        result_d['P'] = result_d['W'] + result_d['D'] + result_d['L']
        results.append(result_d) # append team result dictionary to list of results

    # create PL table dataframe from team results and sort by points (and then goal difference and goals for)
    # show date of data in Position column
    PLtable = pd.DataFrame(results, columns=['Team', 'P', 'W', 'D', 'L', 'GF', 'GA', 'GD', 'PTS'])
    PLtable.sort_values(['PTS', 'GD', 'GF'], ascending=False, inplace=True)
    col_date = before_date if before_date else results_date
    #pos_title = 'Position at {}'.format(simple_date(col_date))
    PLtable['PL_Pos'] = range(1, len(PLtable)+1) # add new column for position, with highest points first
    #PLtable.set_index([pos_title], inplace=True, drop=True) 
    #PLtable.reset_index(inplace=True)
    
    # Add RPI to the table
    PLtable['PTS%'] = 100*(PLtable.PTS/(PLtable.P*3))
    PLtable['OPP_PTS%'] = PLtable.apply(lambda row: PLtable[PLtable.Team.isin(opponents_d[row.Team])]['PTS%'].mean(), axis=1)
    PLtable['OPP_OPP_PTS%'] = PLtable.apply(lambda row: PLtable[PLtable.Team.isin(opponents_d[row.Team])]['OPP_PTS%'].mean(), axis=1)
    PLtable['RPI'] = (PLtable['PTS%']*.25 + PLtable['OPP_PTS%']*.50 + PLtable['OPP_OPP_PTS%']*.25)
    # replace nan with 0 just in case results are published when all games haven't yet been played 
    PLtable.fillna(0, inplace=True)  
    PLtable['RPI_Pos'] = PLtable['RPI'].rank(ascending=False).astype(int)
    
    # Set column order
    COL_ORDER = ['PL_Pos', 'Team', 'P', 'W', 'D', 'L', 'GF', 'GA', 'GD', 'PTS', 
                 'PTS%', 'OPP_PTS%', 'OPP_OPP_PTS%', 'RPI', 'RPI_Pos']
    PLtable =PLtable[COL_ORDER]
    
    # return PL table with RPI, sorted by RPI and PTS percentage
    return(PLtable.sort_values(['RPI', 'PTS%'], ascending=False).reset_index(drop=True), results_date)

def read_premrpi_about_md(filename='premrpi_about.md'):
    """Read the premrpi about markdown file and return as a string."""
    with open(filename, "r") as f:
        premrpi_about_md = f.read()
    return premrpi_about_md

    
# **************
# create web app

# set-up web page (using streamlit beta capability)
logger.info('Main, Initialise the web app')
st.beta_set_page_config(page_title="Premrpi",
                        page_icon="redglider.ico", 
                        layout="wide",
                        initial_sidebar_state="collapsed")
                        
show_about = st.checkbox('About', False)
if show_about:
    # show about
    logger.info('Main, Show info about premrpi')
    st.title('The Premier League with Rating Percentage Index')
    st.markdown(read_premrpi_about_md())
else:
    # show datatable
    df_premrpi, results_date = gen_prem_table_RPI()
    logger.info(f"Main, Show the premier league table ordered by RPI, date of results data: {results_date}")
    st.title('The Premier League with Rating Percentage Index')
    st.subheader(f"Position at {simple_date(results_date)}")
    selected_cols = ['PTS%', 'OPP_PTS%', 'OPP_OPP_PTS%', 'RPI']
    st.dataframe(df_premrpi.style.format({col: "{:0.1f}" for col in selected_cols}), width=1000, height=600).hide_index()
