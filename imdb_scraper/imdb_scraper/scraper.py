import argparse
import pandas as pd
import requests
import os
import json
import logging
import signal
import gc
import sys
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class IMDBMovieManager:
    """Handles fetching, parsing, and storing IMDB movie data efficiently with custom CSV support."""

    def __init__(self, csv_path="imdb_movies.csv"):
        self.csv_path = csv_path
        self.driver = None  # Initialize driver to None for better cleanup
        if not os.path.exists(self.csv_path):
            logging.error(f"CSV file '{self.csv_path}' not found. Fetching fresh data...")
            self.fetch_imdb_top_movies(force_update=True)
        self.movie_lookup = self._load_movie_data_as_dict()

    def fetch_imdb_top_movies(self, force_update=False):
        """Fetches IMDB top movies and saves them to CSV with parallel processing."""
        if not force_update and os.path.exists(self.csv_path):
            logging.info("CSV file exists. Skipping fetch.")
            return

        logging.info("Fetching fresh IMDB data...")
        url = "https://www.imdb.com/chart/toptv"

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "en-US,en;q=0.9"
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            page_source = response.text
        except requests.RequestException as e:
            logging.warning(f"Requests failed: {e}. Switching to Selenium...")
            page_source = self.fetch_imdb_with_selenium()

        if not page_source:
            logging.error("Failed to fetch IMDB data.")
            return

        # Extract JSON-LD Data in parallel
        self.extract_json_to_csv(page_source)

    def fetch_imdb_with_selenium(self):
        """Fetch IMDB page source using Selenium with proper resource management."""
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("start-maximized")

        logging.info("Initializing Selenium WebDriver...")
        service = Service(ChromeDriverManager().install())
        
        # Using a context manager to ensure driver is properly closed
        with webdriver.Chrome(service=service, options=options) as driver:
            self.driver = driver
            driver.get("https://www.imdb.com/chart/toptv")
            page_source = driver.page_source
        
        logging.info("Selenium WebDriver closed.")
        return page_source

    def extract_json_to_csv(self, html_content):
        """Parses JSON-LD from IMDB HTML and saves to CSV using parallel processing."""
        soup = BeautifulSoup(html_content, "html.parser")
        script_tag = soup.find("script", type="application/ld+json")

        if not script_tag:
            logging.error("No JSON-LD data found! IMDB structure might have changed.")
            return

        json_data = json.loads(script_tag.string)

        # Use ThreadPoolExecutor for parallel extraction
        with ThreadPoolExecutor() as executor:
            movie_list = list(executor.map(self._extract_movie_details, json_data.get("itemListElement", [])))

        # Remove None values from failed extractions
        movie_list = [movie for movie in movie_list if movie]

        df = pd.DataFrame(movie_list)
        df.to_csv(self.csv_path, index=False)
        logging.info(f"Movie data saved to {self.csv_path}")

        # Free memory
        del df, movie_list, json_data
        gc.collect()  # Force garbage collection

    @staticmethod
    def _extract_movie_details(item):
        """Extracts movie details efficiently."""
        try:
            movie_details = item.get("item", {})
            return {
                "movie_title": movie_details.get("name", "Unknown"),
                "url": movie_details.get("url", "N/A"),
                "rating": movie_details.get("aggregateRating", {}).get("ratingValue", "N/A"),
                "rating_count": movie_details.get("aggregateRating", {}).get("ratingCount", "N/A"),
                "genre": ", ".join(movie_details.get("genre", [])) if isinstance(movie_details.get("genre", []), list) else movie_details.get("genre", "N/A"),
                "content_rating": movie_details.get("contentRating", "N/A"),
            }
        except Exception as e:
            logging.warning(f"Error extracting movie details: {e}")
            return None

    def _load_movie_data_as_dict(self):
        """Loads movie data from CSV into a dictionary using Pandas chunks for memory efficiency."""
        if not os.path.exists(self.csv_path):
            logging.error(f"CSV file '{self.csv_path}' not found.")
            return {}

        try:
            movie_lookup = {}
            for chunk in pd.read_csv(self.csv_path, usecols=["movie_title", "rating"], chunksize=1000):
                movie_lookup.update({row["movie_title"].lower(): row["rating"] for _, row in chunk.iterrows()})
            return movie_lookup
        except Exception as e:
            logging.error(f"Error loading movie data: {e}")
            return {}

    def find_movie_rating(self, movie_name):
        """Finds a movie's rating in O(1) time complexity with validation."""
        if not movie_name or not movie_name.strip():
            logging.error("Invalid movie name. Please provide a valid movie title.")
            return None

        movie_name_lower = movie_name.strip().lower()
        rating = self.movie_lookup.get(movie_name_lower, None)

        if rating is not None:
            print(f"Found rating: {rating}")  
            return rating
        else:
            print(f"Movie '{movie_name}' not found.") 
            return None  # Ensure a return value


def graceful_exit(signum, frame):
    """Handles graceful termination for the script."""
    logging.info(f"Received termination signal ({signum}). Cleaning up and exiting...")
    gc.collect()  # Force garbage collection
    sys.exit(0)

# Register signal handlers for graceful termination
signal.signal(signal.SIGINT, graceful_exit)  # Handle Ctrl+C
signal.signal(signal.SIGTERM, graceful_exit) # Handle kill command

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IMDB Movie Rating Finder")
    parser.add_argument("-f", "--find", help="Find a movie rating", type=str)
    parser.add_argument("--update", help="Fetch latest IMDB data", action="store_true")
    parser.add_argument("--csv", help="Use a custom CSV file instead of scraping IMDB", type=str)
    args = parser.parse_args()

    # Use custom CSV if provided, else default to imdb_movies.csv
    csv_path = args.csv if args.csv else "imdb_movies.csv"
    imdb_manager = IMDBMovieManager(csv_path)

    # Fetch latest data only if requested and not using a custom CSV
    if args.update and not args.csv:
        imdb_manager.fetch_imdb_top_movies(force_update=True)

    # Validate `--find` argument
    if args.find:
        rating = imdb_manager.find_movie_rating(args.find)
        if rating is not None:
            print(f"Movie: {args.find} has a rating of {rating}")
        else:
            print(f"Movie '{args.find}' not found.")
    else:
        logging.error("No movie name provided. Use --find 'Movie Title' to search for a rating.")
