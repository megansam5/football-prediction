"""Script to scrape match stats from the last two seasons into a csv file.
fbref has a rate limit, so this script takes a long time as iit needs to wait to not get banned."""

import time
from io import StringIO

import requests
from bs4 import BeautifulSoup
import pandas as pd

import requests
import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO
import time


def collect_premier_league_data():
    years = list(range(2025, 2023, -1))
    all_matches = []
    standings_url = "https://fbref.com/en/comps/9/Premier-League-Stats"

    for year in years:
        standings_url = process_season(year, standings_url, all_matches)

    return all_matches


def process_season(year, standings_url, all_matches):
    """Processes data for a single season, returning the previous season's standings URL."""
    soup = fetch_page_data(standings_url)
    standings_table = extract_standings_table(soup)

    team_urls = extract_team_urls(standings_table)
    previous_season_url = extract_previous_season_url(soup)

    for team_url in team_urls:
        process_team_data(team_url, year, all_matches)

    return f"https://fbref.com{previous_season_url}"


def fetch_page_data(url):
    """Fetches and parses HTML data from the given URL."""
    data = requests.get(url)
    soup = BeautifulSoup(data.text, 'html.parser')
    return soup


def extract_standings_table(soup):
    """Extracts the standings table from the page."""
    return soup.select('table.stats_table')[0]


def extract_team_urls(standings_table):
    """Extracts and builds full team URLs from the standings table."""
    links = [l.get("href") for l in standings_table.find_all('a')]
    return [f"https://fbref.com{l}" for l in links if '/squads/' in l]


def extract_previous_season_url(soup):
    """Extracts the URL for the previous season."""
    return soup.select("a.prev")[0].get("href")


def process_team_data(team_url, year, all_matches):
    """Processes match and shooting data for a single team."""
    team_name = extract_team_name(team_url)
    matches = fetch_team_matches(team_url)

    if matches is not None:
        shooting_data = fetch_shooting_data(team_url)
        if shooting_data is not None:
            merge_team_data(matches, shooting_data,
                            year, team_name, all_matches)


def extract_team_name(team_url):
    """Extracts and cleans the team name from the team URL."""
    return team_url.split("/")[-1].replace("-Stats", "").replace("-", " ")


def fetch_team_matches(team_url):
    """Fetches the match data for the team."""
    data = requests.get(team_url)
    try:
        matches = pd.read_html(StringIO(data.text),
                               match="Scores & Fixtures")[0]
        return matches
    except ValueError:
        return None


def fetch_shooting_data(team_url):
    """Fetches the shooting stats data for the team."""
    soup = fetch_page_data(team_url)
    links = [l.get("href") for l in soup.find_all('a')]
    shooting_link = next(
        (l for l in links if 'all_comps/shooting/' in l), None)

    if shooting_link:
        shooting_url = f"https://fbref.com{shooting_link}"
        data = requests.get(shooting_url)
        try:
            shooting = pd.read_html(StringIO(data.text), match="Shooting")[0]
            shooting.columns = shooting.columns.droplevel()  # Drop multilevel columns
            return shooting[["Date", "Sh", "SoT", "Dist", "FK", "PK", "PKatt"]]
        except ValueError:
            return None
    return None


def merge_team_data(matches, shooting, year, team_name, all_matches):
    """Merges the matches and shooting data, and appends to the all_matches list."""
    try:
        team_data = matches.merge(shooting, on="Date")
    except ValueError:
        return

    team_data = team_data[team_data["Comp"] == "Premier League"]
    team_data["Season"] = year
    team_data["Team"] = team_name
    all_matches.append(team_data)
    print(f"Processed: {year} - {team_name}")
    time.sleep(30)  # To avoid overwhelming the server


def save_data(all_matches):
    """Concatenates all matches, standardizes column names, and saves to a CSV file."""
    match_df = pd.concat(all_matches)
    # Convert column names to lowercase
    match_df.columns = [c.lower() for c in match_df.columns]
    # Save to CSV without the index
    match_df.to_csv("matches.csv", index=False)
    print("Data saved to matches.csv")


if __name__ == "__main__":
    all_matches = collect_premier_league_data()
    save_data(all_matches)
