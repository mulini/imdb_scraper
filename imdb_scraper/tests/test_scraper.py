import unittest
import os
import pandas as pd
from imdb_scraper.scraper import IMDBMovieManager

class TestIMDBScraper(unittest.TestCase):

    def setUp(self):
        """Setup a temporary movie CSV file for testing"""
        self.test_csv = "test_movies.csv"
        data = {
            "movie_title": ["Breaking Bad", "Game of Thrones"],
            "rating": [9.5, 9.3]
        }
        df = pd.DataFrame(data)
        df.to_csv(self.test_csv, index=False)

        self.manager = IMDBMovieManager(csv_path=self.test_csv)

    def tearDown(self):
        """Cleanup test CSV file"""
        os.remove(self.test_csv)

    def test_find_movie_rating_exists(self):
        """Test if rating is found for an existing movie"""
        rating = self.manager.find_movie_rating("Breaking Bad")
        self.assertEqual(rating, 9.5)

    def test_find_movie_rating_not_found(self):
        """Test for a movie not in the list"""
        rating = self.manager.find_movie_rating("Nonexistent Movie")
        self.assertIsNone(rating)

    def test_find_movie_rating_case_insensitive(self):
        """Test if the search is case insensitive"""
        rating = self.manager.find_movie_rating("breaking bad")
        self.assertEqual(rating, 9.5)

if __name__ == "__main__":
    unittest.main()