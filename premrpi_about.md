premrpi v2.3.0

The premrpi app automatically generates the latest English Premier League table sorted by the Ratings Percentage Index (RPI).
The app updates itself when the Premier League results data changes at [www.football-data.co.uk](https://www.football-data.co.uk/englandm.php). 
 
The English Premier League table does not lie at the end of the season.
But earlier in the season the table does not tell the whole truth, even after 10+ games.
Some teams will have had more difficult starts, having played many of the stronger teams.
And other teams will have had easier starts, having played many of the weaker teams.
So how do you produce a league table that takes account of the quality of the opposition?
[The Tomkins Times](https://tomkinstimes.com/) subscriber Tim O'Brien (@Tjobrien17) proposed use of the RPI.
The idea is based on a technique used in American sports and is described by Tim [here](https://tomkinstimes.com/2016/11/comment-of-the-month-october-2016/).
        
The formula for the RPI is simple.
It assigns a 25% weight to the team's points percentage, a 50% weight to the average of all of that team's opponents' points percentages, and a 25% weight to the average of that team's opponents opponents' points percentages.
The points percentage is the percentage of points gained (wins and draws) versus those available.
        
Special thanks to @12Xpert for the latest English Premier League base data at [www.football-data.co.uk](http://www.football-data.co.uk/englandm.php).
        
Known Limitations
- The RPI method of assessing a team's 'strength of schedule' lacks theoretical justification from a statistical standpoint - see [RPI on wikipedia](https://en.wikipedia.org/wiki/Rating_Percentage_Index).
- The RPI implementation method varies by sport. The simple method implemented here does not remove the results against the team in the calculation of the opponents' and the opponents opponents' points percentages.
- The method also does not give a different weight to home and away wins.
- The generated table is more useful after 3 games! And after ~10 games it is arguably more useful than the standard table.

The app is open source software, built using python and several modules, most notably streamlit and pandas.
The app is deployed at [terrydolan-premrpi.streamlit.app](https://terrydolan-premrpi.streamlit.app/) on Streamlit's 
cloud application platform, so there may be a delay waiting for the instance to load.

For more information on the data analysis, the app source code and how it is deployed see the [premrpi github repository](https://github.com/terrydolan/premrpi).        

Terry Dolan, [@TerryDolanUK](https://twitter.com/TerryDolanUK)