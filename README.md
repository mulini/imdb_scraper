## Challenge 1

## Current design

- The existing code does the following:
    - Takes a csv input from the user and prints the ratings **(python MovieDetailgetter.py -l input.csv)**
    - If a csv input is not given it but options **"-find"** or **"-voice"** are given it will look for **"imdb_top_250_movies.csv"** and print the ratings. If the input is **"-voice"** it prints the ratings using **cowsay** **(python MovieDetailgetter.py -f "Breaking Bad")** **(python MovieDetailgetter.py -v "Breaking Bad" -> uses cowsay)**
    - If none of the input options are given it scrapes site and saves the top tv shows to imdb_top_250_movies.csv **(python MovieDetailgetter.py)**


I have included indepth code comments in the **MovieDetailgetter.py** file under pull requests

### Pitfalls of the above approach

- We are not fetching new data to keep up with IMDB changes.
- We are looking for fetched file first, the data should be fetched even before we look for the file.
- The functions funny and find are redundant.
- We can employ better logging and error/exception handling processes.
- We can encapsulate the functions into one class and follow the object oriented programming principles.



## New design

- The new code is structured in the following way:
    - step1 : start with imdb data, give user the freedom to
      - use a user input file if it exists
      - it may not be a good practice to scrape the imdb site each time we run the script if there is a stored version of the imdb ratings csv the script uses that first
      - if the user wants to fetch new/updated data scrape imdb site
        
      
    - step2 : Saves the fetched file
    - step3 : looks up for a given movie rating
 

## Pointers I have considered in the new design

- Follow object oriented principles
- Graceful termination of the program including selenium driver and other resources are properly closed
- Added KeyboardInterrupt (Ctrl+C) and SIGTERM signals for cleanup.
- Memory Management (gc.collect and pandas chunk size)
- Parallel processing (to handle large datasets incase there a need to scale the data in the future)
- Multi-threading for faster processing
- Ensure robust error and exception handling
- Code reusability
- Added flexibility for debugging and triaging
- Logging the outputs
- Follow do not repeat yourself principles
- Robust retry mechanism


## Project Structure


```
imdb_scraper/
│── imdb_scraper/         # Main package directory
│   │── __init__.py       # Package initialization
│   │── scraper.py        # IMDB scraping logic
│── tests/                # Unit tests
│   │── __init__.py       # Test package initialization
│   │── test_scraper.py   # Test cases for scraper
│── setup.py              # Package setup configuration
│── imdb_movies.csv       # Csv file with top 250 movies from imdb if not found in folder the script will create it
│── requirements.txt      # Dependencies list
│── README.md             # Project documentation
```

## Installation/Setup

1. **Clone the repository:**

   bash:
   
   ```bash
   git clone https://github.com/mulini/imdb_scraper.git
   cd imdb_scraper
   ```
3. **Install Dependencies:**

   bash:
   
   ```bash
    pip install -r requirements.txt
    ```
5. **Install Package:**

   bash:
   
   ```bash
    pip install -e .
   ```

## Usage

1. **Running the first time - Downloads the imdb top 250 movies and saves to imdb_movies.csv**

   python:
   
   ```python
    from imdb_scraper import IMDBMovieManager
    manager = IMDBMovieManager()
   ```


   bash:

   ```bash
    python imdb_scraper/scraper.py --find "Breaking Bad"
   ```

2. **Subsequent runs - uses the downloaded imdb_movies.csv file**

   python:
   
   ```python
    from imdb_scraper import IMDBMovieManager
    manager = IMDBMovieManager()
   ```

    bash:
   
    ```bash
      python imdb_scraper/scraper.py --find "Breaking Bad"
    ```
3. **Force download new data from imdb in subsequent runs**

    python:
    ```python
    from imdb_scraper import IMDBMovieManager
    manager = IMDBMovieManager()
    manager.fetch_imdb_top_movies(force_update=True)
    ```
    bash:
   
    ```bash
    python imdb_scraper/scraper.py --update
    ```
    
5. **Looking for movie rating**

   python:
   ```python
   from imdb_scraper import IMDBMovieManager
   manager = IMDBMovieManager()
   manager.find_movie_rating("Breaking Bad")
    ```
   bash:
   
   ```bash
   python imdb_scraper/scraper.py --find "Breaking Bad"
   ```
   
   **Example output - Movie: Breaking Bad, Rating: 9.5**

7. **Looking for movie rating from a custom file**

   python:
   ```python
   manager = IMDBMovieManager(csv_path="custom.csv")
   rating = manager.find_movie_rating("Inception")
   ```
   bash:
   ```bash
   python imdb_scraper/scraper.py --csv custom.csv --find "Breaking Bad"
   ```
## Running with tests

1. **Running with unit test cases found in tests/test_scraper.py file**

   ```bash
   python -m unittest discover tests
   ```
