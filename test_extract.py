"""Tests for the extract.py script."""
import unittest
from unittest.mock import patch, MagicMock

import pandas as pd
from freezegun import freeze_time

from extract import get_year, get_team_urls, get_previous_season, get_shooting_link, get_team_name, process_team, collect_data, save_data


class TestExtract(unittest.TestCase):

    @freeze_time("2023-09-14 00:00:00", tz_offset=-4)
    def test_get_year_start_of_season(self):
        self.assertEqual(get_year(), 2024)

    @freeze_time("2024-07-14 00:00:00", tz_offset=-4)
    def test_get_year_end_of_season(self):
        self.assertEqual(get_year(), 2024)

    @patch('extract.requests.get')
    def test_get_team_urls(self, mock_get):
        mock_soup = MagicMock()
        mock_soup.select.return_value = [MagicMock()]
        mock_soup.select()[0].find_all.return_value = [
            MagicMock(get=MagicMock(return_value='/squads/team1')),
            MagicMock(get=MagicMock(return_value='/squads/team2'))
        ]
        team_urls = get_team_urls(mock_soup)
        expected_urls = [
            "https://fbref.com/squads/team1",
            "https://fbref.com/squads/team2"
        ]
        self.assertEqual(team_urls, expected_urls)

    @patch('extract.requests.get')
    def test_get_previous_season(self, mock_get):
        mock_soup = MagicMock()
        mock_soup.select.return_value = [
            MagicMock(get=MagicMock(return_value='previous_season_url'))]
        previous_season_url = get_previous_season(mock_soup)
        self.assertEqual(previous_season_url,
                         "https://fbref.com/previous_season_url")

    @patch('extract.requests.get')
    def test_get_shooting_link(self, mock_get):
        mock_soup = MagicMock()
        mock_soup.find_all.return_value = [
            MagicMock(get=MagicMock(return_value='/all_comps/shooting/'))
        ]
        shooting_link = get_shooting_link(mock_soup)
        self.assertEqual(shooting_link, '/all_comps/shooting/')

    def test_get_team_name(self):
        team_url = "https://fbref.com/squads/team1/Manchester-United-Stats"
        self.assertEqual(get_team_name(team_url), "Manchester United")

    @patch('extract.pd.DataFrame.to_csv')
    def test_save_data(self, mock_to_csv):
        df = pd.DataFrame({'A': [1], 'B': [2]})
        save_data(df)
        mock_to_csv.assert_called_once_with("matches.csv", index=False)
