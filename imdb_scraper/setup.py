from setuptools import setup, find_packages

setup(
    name="imdb_scraper",
    version="2.0.0",
    author="Mulini Pingili",
    description="A Python tool for scraping IMDB top movie data and retrieving movie ratings.",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "pandas",
        "requests",
        "beautifulsoup4",
        "selenium",
        "webdriver-manager"
    ],
    packages=find_packages(),
    entry_points={
    "console_scripts": [
        "imdb-scraper=imdb_scraper.scraper:fetch_imdb_top_movies"
    ]},
    python_requires=">=3.6",
)
