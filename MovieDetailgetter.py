#!/home/root/software/bin/env python3

from os import *
from bs4 import *
import csv
import requests
import os
import re
import pandas as pd

def Printratingofmoviefromfile(input):
    #this method will return the rating of a movie
    #it wad originally witten by connor but I made some changes
    # we can then use the ratiung elsewhere in the code for newfeatures
    # sould be good to go



    #print("Input given: "+input)

    import csv
    # file = open(input, 'r', newline='')
    # reader = csv.DictReader(file)
    # for row in reader:
    #     print(row[0], row[1])
    #filename = 'input.csv'
    #test = open(file='input.csv',mode='r').read()
    #print(test)

    #with open(file=filename, mode='r') as f:
    #    reader = csv.reader(f)
    #    for row in reader:
     #       print(row)
    import pandas as pd
    my_csv = pd.read_csv(input)
    titles = list(my_csv.movie_title)
    rating = list(my_csv.rating)

    for item in titles:
        print('Movie: '+item+' has a rating of: %f'%(rating[titles.index(item)]))


def funny(text):
    import cowsay

    df = pd.read_csv("imdb_top_250_movies.csv", sep = ",", index_col=False)
    cowsay.cow('This movie has got a rating of '+str(list(df[df["movie_title"] == text]['rating'])[0]))

    #df = pd.read_csv("imdb_top_250_movies.csv", sep = ",", index_col=False)
    #row = df[df["movie_title"] == name].to_string(index=False, header=False)
    #print(df[df["movie_title"] == name]['rating'])

    #cowsay.cow(text)

def find(name):
    df = pd.read_csv("imdb_top_250_movies.csv", sep = ",", index_col=False)

    try:
        print('This movie has got a rating of '+str(list(df[df["movie_title"] == name]['rating'])[0]))
    except:
        pass

    # import csv
    # csv_file = csv.reader(open('imdb_top_250_movies.csv', 'rb'), delimiter=',')
    # print(csv_file)

    # df = pd.read_csv('imdb_top_250_movies.csv', header=1)
    # for row in df:
    #
    #     split = name.split(',')
    #     print(split)
    #
    #     if name in split:
    #         print(row)
    #print(df.to_string())

    # with open() as f:
    #     reader=csv.reader(f, delimiter=',')
    #     for row in reader:
    #         if name in row:
    #             print(row)



import argparse

p = argparse.ArgumentParser()
p.add_argument('-l', '--load-csv-from-file')
p.add_argument('-v','--voice')
p.add_argument('-f','--find')

options = p.parse_args()

if options.load_csv_from_file:
    Printratingofmoviefromfile(options.load_csv_from_file)
elif options.voice:
    funny(options.voice)
elif options.find:
    find(options.find)


else:

    url = 'http://www.imdb.com/chart/toptv'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    movies = soup.select('td.titleColumn')
    crew = [a.attrs.get('title') for a in soup.select('td.titleColumn a')]
    ratings = [b.attrs.get('data-value')
               for b in soup.select('td.posterColumn span[name=ir]')]
    list = []

    # Iterating over movies to extract
    # each movie's details
    for index in range(0, len(movies)):

        ms = movies[index].get_text()
        m = (' '.join(ms.split()).replace('.', ''))
        movie_title = m[len(str(index))+1:-7]
        year = re.search('\((.*?)\)', ms).group(1)
        place = m[:len(str(index))-(len(m))]
        data = {"place": place, "movie_title": movie_title, "rating": ratings[index], "year": year, "star_cast": crew[index],}
        list.append(data)

    for m in list:
        print(m['place'], '-', m['movie_title'], '('+m['year'] + ') -', 'Starring:', m['star_cast'], m['rating'])

    df = pd.DataFrame(list)
    df.to_csv('imdb_top_250_movies.csv',index=False)








