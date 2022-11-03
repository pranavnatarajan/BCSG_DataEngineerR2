"""
This file contains only the code from codefile.ipynb, bar the sanity checks.
The file contains all the python and SQLite code to complete this project.
All SQLite code is run on objects instantiated from the `sqlite3` module.

Author: Pranav Natarajan
email: pn12@uw.edu
"""

if __name__ == "__main__":

  ### importing the required packages
  import requests
  import pandas as pd
  from bs4 import BeautifulSoup
  import sqlite3


  ### defining functions for later use in the file

  # function that takes in a string of market value as input, and makes it a number
  def str_to_float(str):
    """function to convert market values from string to floating point

    Args:
        str (string): string literal of market value

    Returns:
        float: the floating point representation of the string literal
    """
    # removing all whitespaces around the string
    str = str.strip()
    # get the suffix
    suffix = str[-1]
    # get the number, by removing the $ and suffix
    num = str.replace("$", "")
    # multiplication by respective power of 10
    # based on suffix
    # for a million
    if suffix == "m":
      num = float(num[:len(num)-1])
      num = num * (10 ** 6)
    # for a thousand
    else:
      num = float(num[:len(num)-3])
      num = num * (10 ** 3)
    # returning the floating point number
    return num

  # creating the function to generate the respective general position
  def get_gen_pos(pos):
    """provides the general position, given a position defined by transfermarkt.

    Args:
        pos (string): player position defined by transfermarkt

    Returns:
        string: general position, as required for the query
        mentioned on the specification.
    """
    # coercing to lowercase for easier analysis
    pos = pos.lower()
    # for goalkeeper
    if pos == "goalkeeper":
      return "Goalkeepers"
    elif "back" in pos:
      return "Defenders"
    elif "midfield" in pos:
      return "Midfielders"
    # NOTE: I assume that wingers are an attacking position!
    else:
      return "Forwards"



  ### setting the user agent to prevent blocks for scraping
  header = {'User-Agent':
              'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}

  ### for the clubs values for the 22/23 season
  clubs_url = r"https://www.transfermarkt.us/laliga/startseite/wettbewerb/ES1"

  # instantiating the requests object for the web scraping
  req = requests.get(url=clubs_url, headers=header)
  # instantiatingt he beautifulSoup Object
  bs_obj = BeautifulSoup(req.content, "html.parser")

  # finding the table
  clubs_table = bs_obj.find('table', attrs={'class':'items'})
  # drilling down to body of the table
  table_body = clubs_table.find('tbody')

  # instantiating the list of lists for the dataframe
  clubs_df = []
  # finding all the rows in the table
  rows = table_body.find_all('tr')
  for row in rows:
      # getting the data from each column for each row
      cols = row.find_all('td')
      # removing whitespaces around the column value text
      cols = [val.text.strip() for val in cols]
      # append list of all the value text to clubs_df i.e, each row-tuple
      clubs_df.append([val for val in cols if val]) # Get rid of empty values if they exist


  # creating pandas dataframe of clubs_df
  clubs_df1 = pd.DataFrame(clubs_df)
  # creating the column names
  clubs_df1.columns = ["Name", "Squad", "Avg Squad Age",
  "Foreigners", "Avg Market Value ($)",
  "Total Market Value ($)"]

  # using the apply function on the dataset
  clubs_df1["Avg Market Value ($)"] = clubs_df1["Avg Market Value ($)"].\
    apply(str_to_float)
  clubs_df1["Total Market Value ($)"] = clubs_df1["Total Market Value ($)"].\
    apply(str_to_float)

  # changing the datatypes of the respective columns to numeric
  clubs_df1.loc[:, ["Squad", "Avg Squad Age", "Foreigners"]] = clubs_df1.loc[:,
  ["Squad", "Avg Squad Age", "Foreigners"]].\
    apply(pd.to_numeric)

  ### for the players table

  # getting the list of player page urls from transfermarkt.us
  player_tables_urls_compact = [r"https://www.transfermarkt.us/real-madrid/kader/verein/418/saison_id/2022",
  r"https://www.transfermarkt.us/fc-barcelona/kader/verein/131/saison_id/2022",
  r"https://www.transfermarkt.us/atletico-de-madrid/kader/verein/13/saison_id/2022",
  r"https://www.transfermarkt.us/real-sociedad/kader/verein/681/saison_id/2022",
  r"https://www.transfermarkt.us/villarreal-cf/kader/verein/1050/saison_id/2022",
  r"https://www.transfermarkt.us/sevilla-fc/kader/verein/368/saison_id/2022",
  r"https://www.transfermarkt.us/real-betis-balompie/kader/verein/150/saison_id/2022",
  r"https://www.transfermarkt.us/valencia-cf/kader/verein/1049/saison_id/2022",
  r"https://www.transfermarkt.us/athletic-bilbao/kader/verein/621/saison_id/2022",
  r"https://www.transfermarkt.us/getafe-cf/kader/verein/3709/saison_id/2022",
  r"https://www.transfermarkt.us/celta-de-vigo/kader/verein/940/saison_id/2022",
  r"https://www.transfermarkt.us/ca-osasuna/kader/verein/331/saison_id/2022",
  r"https://www.transfermarkt.us/rcd-espanyol-barcelona/kader/verein/714/saison_id/2022",
  r"https://www.transfermarkt.us/girona-fc/kader/verein/12321/saison_id/2022",
  r"https://www.transfermarkt.us/ud-almeria/kader/verein/3302/saison_id/2022",
  r"https://www.transfermarkt.us/rayo-vallecano/kader/verein/367/saison_id/2022",
  r"https://www.transfermarkt.us/elche-cf/kader/verein/1531/saison_id/2022",
  r"https://www.transfermarkt.us/rcd-mallorca/kader/verein/237/saison_id/2022",
  r"https://www.transfermarkt.us/real-valladolid-cf/kader/verein/366/saison_id/2022",
  r"https://www.transfermarkt.us/cadiz-cf/kader/verein/2687/saison_id/2022"]

  # creating the list of lists object for the players
  players = []

  # over all the teams' detailed table webpages
  for i in range(len(player_tables_urls_compact)):
      # instantiate new request object
      req_1 = requests.get(player_tables_urls_compact[i], headers=header)
      # instantiating the new beautifulSoup Object for the team webpage
      bs_players_obj = BeautifulSoup(req_1.content, "html.parser")
      # finding the table
      player_table = bs_players_obj.find('table', attrs={'class':'items'})
      # drilling down to body of the table
      table_body = player_table.find('tbody')

      # finding all the rows in the table
      rows = table_body.find_all('tr')
      for row in rows:
          # getting the data from each column for each row
          cols = row.find_all('td')
          # removing whitespaces around the column value text
          cols = [val.text.strip() for val in cols]
          # adding the team name
          # since it is the foreign key reference to the clubs table
          cols.append(clubs_df1["Name"][i])
          # Get rid of empty values if they exist
          # NOTE: the nationality & duplicate kit number columns turn up empty
          # due to there being more recursion required to obtain the text fields.
          # Since it isn't relevant to this project it will be removed.
          # We do not need kit number either, so it will be removed as well.
          players.append([val for val in cols])

  # removing the lists of length less than 3
  players = [row for row in players if len(row) > 3]
  # removing the first 2 elements of the remaining lists
  players = [row[2:] for row in players]

  # creating the pandas dataframe for the list of lists
  players_df = pd.DataFrame(players)
  players_df.columns = ["Kit No.", "Name", "Position",
  "Age", "Nationality", "Contract End",
  "Market Value", "Team"]

  # dropping these null columns
  players_df = players_df.drop(["Kit No.", "Nationality"], axis=1)

  # now, getting the market values formatted
  players_df["Market Value"] = players_df["Market Value"].apply(str_to_float)
  # changing the age column's datatype to numeric
  players_df["Age"] = players_df["Age"].apply(pd.to_numeric)

  ### for the player position table

  # we get the unique position values
  players_df_position = players_df.loc[:, ["Position"]].copy().\
    drop_duplicates()
  # creating the position map dataframe
  players_df_position["general_position"] = players_df_position["Position"].\
    apply(get_gen_pos)
  players_df_position = players_df_position.reset_index().\
    drop(["index"], axis=1)

  ### for the Creation of respective tables as in step 5

  # initialising a connection to footy_schema.db, in the CWD
  conn = sqlite3.connect("footy_schema.db")
  # initialising the cursor object to query the database tables,
  # as mentioned in the sqlite3 documentation
  cur = conn.cursor()

  # create table statement for the clubs table
  cur.execute("""
  CREATE TABLE Clubs
  (
    Name VARCHAR(80) PRIMARY KEY NOT NULL,
    Squad INTEGER,
    `Avg Squad Age` FLOAT,
    Foreigners INTEGER,
    `Avg Market Value ($)` DOUBLE,
    `Total Market Value ($)` DOUBLE
  );
  """)
  # create table statement for the position_mapping table
  cur.execute("""
  CREATE TABLE Position_Map
  (
    Position VARCHAR(60) PRIMARY KEY NOT NULL,
    `General Position` VARCHAR(40)
  );
  """)
  # create table statement for the players table
  cur.execute("""
  CREATE TABLE Players
  (
    Name VARCHAR(80) PRIMARY KEY NOT NULL,
    Position REFERENCES Position_Map NOT NULL,
    Age INTEGER,
    `Contract End` INTEGER,
    `Market Value ($)` DOUBLE,
    Team REFERENCES Clubs NOT NULL
  );
  """)

  # checking that the tables actually are created in the database schema
  cur.execute("""
  SELECT name from SQLITE_MASTER WHERE type = "table";
  """).fetchall()
  # EXISTS!

  # creating the list of row tuples for the clubs table
  clubs_list_tuples = list(clubs_df1.itertuples(index=False, name=None))

  # performing bulk insert
  cur.executemany("INSERT INTO Clubs VALUES(?, ?, ?, ?, ?, ?)",
  clubs_list_tuples)
  # committing changes to database
  conn.commit()

  # creating the list of row tuples for the position_mapping table
  position_tuples = list(players_df_position.itertuples(index=False, name=None))

  # performing bulk insert
  cur.executemany("INSERT INTO Position_Map VALUES(?, ?)",
  position_tuples)
  # committing changes to database
  conn.commit()

  # creating the list of row tuples for the players table
  players_tuples = list(players_df.itertuples(index=False, name=None))

  # performing bulk insert
  cur.executemany("INSERT INTO Players VALUES(?, ?, ?, ?, ?, ?)",
  players_tuples)
  # committing changes to database
  conn.commit()

  ### Getting the total market value for each team by position

  # getting the results of the query as a pandas dataframe
  qry_df = pd.read_sql_query("""
  SELECT P.Team, PM.`General Position` as Position,
  SUM(P.`Market Value ($)`) as `Total Market Value ($)`
  FROM Players P JOIN Position_Map PM on P.Position = PM.Position
  GROUP BY P.Team, PM.`General Position`
  """, con=conn)

  # saving the results of the query into the database,
  # into a table called query_results
  cur.execute("""
  CREATE TABLE Query_Results AS
    SELECT P.Team, PM.`General Position` as Position,
    SUM(P.`Market Value ($)`) as `Total Market Value ($)`
    FROM Players P JOIN Position_Map PM on P.Position = PM.Position
    GROUP BY P.Team, PM.`General Position`
  ;
  """)

  # saving the results as a CSV file for future manipulation
  qry_df.to_csv("query_results.csv")
  # storing all the tables as csvs
  pd.read_sql_query("SELECT * FROM Clubs", con=conn).to_csv("clubs.csv")
  pd.read_sql_query("SELECT * FROM Position_Map", con=conn).to_csv("position_map.csv")
  pd.read_sql_query("SELECT * FROM Players", con=conn).to_csv("players.csv")

  # to close connection
  conn.close()
