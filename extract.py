"""Script to scrape match stats from the last two seasons into a csv file.
fbref has a rate limit, so this script takes a long time as iit needs to wait to not get banned."""

import time
from io import StringIO
from datetime import date

import requests
from bs4 import BeautifulSoup
import pandas as pd


def get_year() -> int:
    """Returns the currents seasons end year."""
    today = date.today()
    current_year = today.year
    august_15 = date(current_year, 8, 15)

    if today > august_15:
        return current_year + 1
    else:
        return current_year


def get_team_urls(soup) -> list[str]:
    """Returns the team urls from the page soup."""
    standings_table = soup.select('table.stats_table')[0]
    links = [l.get("href") for l in standings_table.find_all('a')]
    links = [l for l in links if '/squads/' in l]
    team_urls = [f"https://fbref.com{l}" for l in links]
    return team_urls


def get_previous_season(soup) -> str:
    """Returns the url for the previous season."""
    previous_season = soup.select("a.prev")[0].get("href")
    return f"https://fbref.com/{previous_season}"


def get_shooting_link(soup) -> str:
    """Returns the url for the current team page."""
    links = [l.get("href") for l in soup.find_all('a')]
    return [l for l in links if l and 'all_comps/shooting/' in l][0]


def get_team_name(team_url: str) -> str:
    """Returms the team name from the url."""
    return team_url.split(
        "/")[-1].replace("-Stats", "").replace("-", " ")


def process_team(team_url: str, year: int) -> pd.DataFrame | None:
    """Returns a dataframe from a specific team."""
    team_name = get_team_name(team_url)

    data = requests.get(team_url)
    time.sleep(15)  # To not exceed rate limit
    matches = pd.read_html(StringIO(data.text),
                           match="Scores & Fixtures")[0]
    soup = BeautifulSoup(data.text, 'html.parser')
    link = get_shooting_link(soup)
    data = requests.get(f"https://fbref.com{link}")
    time.sleep(15)  # To not exceed rate limit
    shooting = pd.read_html(StringIO(data.text), match="Shooting")[0]
    shooting.columns = shooting.columns.droplevel()

    try:
        team_data = matches.merge(
            shooting[["Date", "Sh", "SoT", "Dist", "FK", "PK", "PKatt"]], on="Date")
    except ValueError:
        return None
    team_data = team_data[team_data["Comp"] == "Premier League"]
    team_data["Season"] = year
    team_data["Team"] = team_name
    print(f"Processed: {year} - {team_name}")
    return team_data


def collect_data() -> pd.DataFrame:
    """Returns a dataframe of matches for all teams this and last season."""
    current_year = get_year()
    years = list(range(current_year, current_year-2, -1))
    all_matches = []
    standings_url = "https://fbref.com/en/comps/9/Premier-League-Stats"

    for year in years[:1]:
        data = requests.get(standings_url)
        time.sleep(15)  # To not exceed rate limit
        soup = BeautifulSoup(data.text, 'html.parser')
        team_urls = get_team_urls(soup)
        standings_url = get_previous_season(soup)
        for team_url in team_urls[:2]:
            team_data = process_team(team_url, year)
            if team_data is not None:
                all_matches.append(team_data)
    match_df = pd.concat(all_matches)
    match_df.columns = [c.lower() for c in match_df.columns]

    return match_df


def save_data(data: pd.DataFrame) -> None:
    """Saves the dataframe to a csv"""
    data.to_csv("matches.csv", index=False)
    print("Data saved to matches.csv.")


if __name__ == "__main__":
    data = collect_data()
    print('data collected')
    save_data(data)
