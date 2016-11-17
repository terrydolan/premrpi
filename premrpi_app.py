"""Prem RPI App. 

An python Spyre web app that shows the English Premier League table with RPI.

To run:
    $python premrpi_app.py

History
v1.0.0 - First published release, November 2016
    
"""
from spyre import server
import sys 
import requests
import datetime as dt
import pickle
from bs4 import BeautifulSoup, SoupStrainer
import os
import pandas as pd
import logging
import logging.config
import premrpi_log_config # dict with logging config

__author__ = "Terry Dolan"
__copyright__ = "Terry Dolan"
__license__ = "MIT"
__email__ = "terrydolan1892@gmail.com"
__status__ = "Beta"
__version__ = "1.0.0"
__updated__ = 'November 2016'

# set up logging
logging.config.dictConfig(premrpi_log_config.dictLogConfig)
logger = logging.getLogger('premrpi')

class PremRPI(server.App):
    """Spyre Prem RPI App."""
    title = "The Premier League with \nRating Percentage Index"

    controls = [{"type": "hidden",
                "id": "update_data"}]

    tabs = ["Table", "About"]

    outputs = [{"type": "table",
                "id": "table_id",
                "control_id": "update_data",
                "tab": "Table",
                "on_page_load" : True},
               {"type" : "html",
                "id" : "simple_html_output",
                "control_id" : "update_data",
                "tab" : "About"}]


    def get_pl_master_data(self):
        """Return url of latest premier league results file and the date the file was last updated.
        
        Data source is www.football-data.co.uk.
        Format of returned date is "%Y-%m-%d" (the pandas default).
        """
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

        logger.info('PremRPI.get_pl_master_data, url of prem league results file: {}'.format(url_latest_pl_results_file))
        logger.info('PremRPI.get_pl_master_data, last updated: {}'.format(last_updated_date))
        return url_latest_pl_results_file, last_updated_date


    def get_pl_results_dataframe(self, update_cache=False):
        """Return latest premier league results as a dataframe and the date of the results data.
        
        Data source is www.football-data.co.uk.
        Cache data locally to avoid unnecessary calls to football-data website.
        Download results from master data source if local data is out of date.
        """
        
        LOCAL_RESULTS_DATA_FILE = 'data/E0.csv'
        PICKLE_FILE = 'save.p' # holds date of results data file

        # get master data source data
        url_latest_pl_results_file, master_results_data_date = self.get_pl_master_data()
        
        if update_cache:
            if os.path.exists(PICKLE_FILE):
                os.remove(PICKLE_FILE)

        # get local data source date
        if os.path.exists(PICKLE_FILE):
            local_results_data_date = pickle.load(open(PICKLE_FILE, 'rb'))
        else:
            local_results_data_date = None

        if local_results_data_date < master_results_data_date:
            logger.info('local results data out of date, updating from master results data file')
            parse_dates_col = ['Date']
            df_results = pd.read_csv(url_latest_pl_results_file, parse_dates=parse_dates_col, dayfirst=True)
            df_results.to_csv(LOCAL_RESULTS_DATA_FILE, index=False)
            local_results_data_date = master_results_data_date
            pickle.dump(local_results_data_date, open(PICKLE_FILE, 'wb'))
        else:
            logger.info('local results data still latest')
            parse_dates_col = ['Date']
            df_results = pd.read_csv(LOCAL_RESULTS_DATA_FILE, parse_dates=parse_dates_col, dayfirst=True)

        logger.info('PremRPI.get_pl_results_dataframe, return df_results dataframe')
        logger.info('PremRPI.get_pl_results_dataframe, local_results_date: {}'.format(local_results_data_date))     
        return df_results, local_results_data_date


    def validate_date(self, date_text):
        """Raise error if date format is not '%y-%m-%d'."""
        try:
            dt.datetime.strptime(date_text, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Incorrect date format, should be YYYY-MM-DD")


    def simple_date(self, date_text):
        """Raise error if date format is not YYYY-MM-DD."""
        self.validate_date(date_text)
        return dt.datetime.strptime(date_text, '%Y-%m-%d').strftime('%d %b %y')
    

    def gen_prem_table_RPI(self, before_date=None, update_cache=False):
        """Return prem table with RPI at given before_date and return data source date."""
        
        results = []
        opponents_d = {}
        df_results, results_date = self.get_pl_results_dataframe(update_cache)
        
        
        # filter results in dataframe at given before_date
        if before_date:
            self.validate_date(before_date)
            df_results = df_results[df_results.Date <= before_date]
        
        for team in df_results['HomeTeam'].unique():
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
            result_d['P'] = home_played + away_played
            result_d['W'] = home_win + away_win
            result_d['D'] = home_draw + away_draw
            result_d['L'] = home_lose + away_lose
            result_d['GF'] = home_goals_for + away_goals_for
            result_d['GA'] = home_goals_against + away_goals_against
            result_d['GD'] = result_d['GF'] - result_d['GA']
            result_d['PTS'] = result_d['W']*3 + result_d['D']
            results.append(result_d) # append team result dictionary to list of results

        # create PL table dataframe from team results and sort by points (and then goal difference and goals for)
        # show date of data in Position column
        PLtable = pd.DataFrame(results, columns=['Team', 'P', 'W', 'D', 'L', 'GF', 'GA', 'GD', 'PTS'])
        PLtable.sort_values(['PTS', 'GD', 'GF'], ascending=False, inplace=True)
        col_date = before_date if before_date else results_date
        pos_title = 'Position at {}'.format(self.simple_date(col_date))
        PLtable[pos_title] = range(1, len(PLtable)+1) # add new column for position, with highest points first
        PLtable.set_index([pos_title], inplace=True, drop=True)
        PLtable.reset_index(inplace=True)
        
        # Add RPI to the table
        PLtable['PTS%'] = 100*(PLtable.PTS/(PLtable.P*3))
        PLtable['OPP_PTS%'] = PLtable.apply(lambda row: PLtable[PLtable.Team.isin(opponents_d[row.Team])]['PTS%'].mean(), axis=1)
        PLtable['OPP_OPP_PTS%'] = PLtable.apply(lambda row: PLtable[PLtable.Team.isin(opponents_d[row.Team])]['OPP_PTS%'].mean(), axis=1)
        PLtable['RPI'] = (PLtable['PTS%']*.25 + PLtable['OPP_PTS%']*.50 + PLtable['OPP_OPP_PTS%']*.25)
        PLtable['RPI_Position'] = PLtable['RPI'].rank(ascending=False).astype(int)
        
        # return PL table with RPI, sorted by RPI and win percentage
        return PLtable.sort_values(['RPI', 'PTS%'], ascending=False)


    def getData(self, params):
        """Return the table object."""
        logger.info('PremRPI.getData, return prem table with RPI')
        pd.set_option('precision', 2)
        return self.gen_prem_table_RPI()


    def getHTML(self, params):
        """Return html that describes the app."""
        html = """
        <!DOCTYPE html>
        <html>
        <body>

        <p>
        Prem RPI app by @lfcsorted, your feedback is welcome.</p>
        <a href="https://twitter.com/lfcsorted" class="twitter-follow-button" data-show-count="false">Follow @lfcsorted</a>
        <script>!function(d,s,id){var js,fjs=d.getElementsByTagName(s)[0],p=/^http:/.test(d.location)
        ?'http':'https';if(!d.getElementById(id))
        {js=d.createElement(s);js.id=id;js.src=p+'://platform.twitter.com/widgets.js';fjs.parentNode.insertBefore(js,fjs);}}
        (document, 'script', 'twitter-wjs');</script>
        <br><br>
        </p>
        
        <p>
        The premrpi app automatically generates the latest English Premier League table ordered by the Ratings Percentage Index (RPI).
        </p>

        <p>
        The English Premier League table does not lie at the end of the season.
        But early in the season the table is not accurate, even after 10+ games.
        Some teams will have had more difficult starts, having played many of the stronger teams.
        And other teams will have had easier starts, having played many of the weaker teams.
	So how do you produce a table that takes account of the quality of the opposition?        
        <a href="https://tomkinstimes.com/">The Tomkins Times</a> subscriber Tim O'Brien proposed use of the RPI.
        The idea is based on a technique used in American sports and is described
        <a href="https://tomkinstimes.com/2016/11/comment-of-the-month-october-2016/">here</a>.
        </p>
        
        <p>
        The formula for the RPI is simple.
        It assigns a 25% weight to the team's points percentage, a 50% weight to the average of all of that team's
        opponents' points percentages, and a 25% weight to the average of that team's opponents opponents' points percentage.
        The points percentage is the percentage of points gained (wins and draws) versus those available.
        </p>
        
        <p>
        Special thanks to @12Xpert for the latest English Premier League base data at
        <a href="http://www.football-data.co.uk/englandm.php">www.football-data.co.uk</a>.
        </p>

        <p>
        <br>
        The app is open source software, built using python and several modules, most notably spyre and pandas.
        It is deployed on Heroku's cloud application platform.
        For more information on the data analysis, the app source code and how it is deployed see the
        <a href="https://github.com/terrydolan/premrpi">premrpi github repository</a>.
        </p>
        
        <p>
        Terry Dolan, @lfcsorted<br>
        Blog:  <a href="http://www.lfcsorted.com">www.lfcsorted.com</a><br>
        </p>
        
        </body>
        </html>
        """

        logger.info('PremRPI.getHTML, return the About HTML')
        
        return html


if __name__ == '__main__':
    app = PremRPI()
    app.launch(host='0.0.0.0', port=int(os.environ.get('PORT', '5000')))
