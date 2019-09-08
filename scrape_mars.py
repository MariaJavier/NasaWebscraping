from flask import Flask, jsonify, request, redirect, url_for, render_template
from flask_pymongo import PyMongo
from pymongo import MongoClient
from bs4 import BeautifulSoup
from splinter import Browser
import requests
import pprint
import datetime as dt
from mongoengine import *
import numpy as np
import pandas as pd
from pandas import *
from bson.json_util import dumps


def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {'executable_path': 'chromedriver.exe'}
    return Browser("chrome", **executable_path, headless=False)


def scrape():
    browser = init_browser()
    results = {}

    # NASA MARS NEWS
    url = "https://mars.nasa.gov/news/" 
    browser.visit(url)

    # convert the browser.html to a soup
    html = browser.html
    nasa_soup = BeautifulSoup(html, 'html.parser')

    # Find the latest news title
    first_title = nasa_soup.select_one("ul.item_list li.slide div.content_title").text

    # Find the latest paragraph text
    latest_paragraph_text = nasa_soup.select_one("ul.item_list li.slide div.article_teaser_body").text

    # SPACE IMAGES
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # Find and click the full image button
    full_image_id = browser.find_by_id('full_image')
    full_image_id.click()

    # Find the more info button and click that
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_elem = browser.find_link_by_partial_text('more info')
    more_info_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = BeautifulSoup(html, 'html.parser')

    # find the relative image url
    image_url = img_soup.select_one('figure.lede a img').get("src")

    # get a complete URL
    featured_image_url = f'https://www.jpl.nasa.gov{image_url}'

    # MARS WEATHER - TWITTER
    url = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(url)

    # convert the browser.html to a soup
    html = browser.html
    weather_soup = BeautifulSoup(html, 'html.parser')

    # this only works if the 1st tweet is the weather which it usually is but not this time around
    mars_weather = weather_soup.select_one("p.TweetTextSize").text

    # First, find a tweet with the data-name `Mars Weather`
    mars_weather_tweet_container = weather_soup.find('ol', attrs={"id": "stream-items-id"})
    mars_weather_tweet_container

    # Next, search within the tweet for the p tag containing the tweet text
    mars_weather_tweet_texts = mars_weather_tweet_container.findAll('p', 'TweetTextSize TweetTextSize--normal js-tweet-text tweet-text')

    # Loop through our tweet texts to find 'InSight sol' 
    weather_data = None

    for t_text in mars_weather_tweet_texts:
        # get a list of all words in each tweet text
        words = t_text.get_text().split(' ')
        if words[0] == 'InSight':
            weather_data = t_text.get_text()
            break
        print('---')

    # MARS FACTS: 
    url = 'https://space-facts.com/mars/'
    browser.visit(url)

    html = browser.html
    facts_soup = BeautifulSoup(html, 'html.parser')

    # convert the html to a dataframe
    df = pd.read_html('https://space-facts.com/mars/')[0]

    # convert the html to a dataframe
    df = pd.read_html('https://space-facts.com/mars/')[0]

    # change the column names and make the Description the index
    df.columns = ['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    # we are only interested in the Description & Mars columns
    mars = df.iloc[:, 0]
    mars.to_frame()

    mars = pd.DataFrame(mars)

    mars_html = mars.to_html()


    # MARS HEMISPHERES:
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    # convert the browser.html to a soup
    html = browser.html
    hsoup = BeautifulSoup(html, 'html.parser')

    links = [a['href'] for a in hsoup.find_all('a', href=True)]

    base_url = 'https://astrogeology.usgs.gov'

    cerebrus_url = f'{base_url}{links[4]}'

    schiaparelli_url = f'{base_url}{links[6]}'

    syrtis_major_url = f'{base_url}{links[8]}'

    valles_marineris_url = f'{base_url}{links[10]}'

    # visit the Cerebrus site
    url = cerebrus_url
    browser.visit(url)

    # convert the browser.html to a soup
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    cerberus = soup.select_one('li a')['href']

    # visit the schiaparelli_url 
    url = schiaparelli_url 
    browser.visit(url)

    # convert the browser.html to a soup
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    schiaparelli = soup.select_one('li a')['href']

    # visit the syrtis_major_url 
    url = syrtis_major_url 
    browser.visit(url)

    # convert the browser.html to a soup
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    syrtis_major  = soup.select_one('li a')['href']

    # visit the valles_marineris_url 
    url = valles_marineris_url  
    browser.visit(url)

    # convert the browser.html to a soup
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    valles_marineris  = soup.select_one('li a')['href']

    # Append the dictionary with the image url & hemisphere title to a list.
    # This list will contain one dictionary for each hemisphere.
    app = Flask(__name__)
    app.config['MONGO_URI'] = 'mongodb://locahose:27017'
    mongo = PyMongo(app)

    client = MongoClient('mongodb://localhost:27017')
    mars_db = client.mars_db
    mars_db.mars.drop()
    mars = mars_db.mars

    hemispheres = [
        {'title': 'Cerberus Hemisphere', 'img_url': cerberus},
        {'title': 'Schiaparelli Hemisphere', 'img_url': schiaparelli},
        {'title': 'Syrtis Major Hemisphere', 'img_url': syrtis_major},
        {'title': 'Valles Marineris Hemisphere', 'img_url': valles_marineris}
    ]; 

    mars_data = {
        "first_title": first_title,
        "latest_paragraph_text": latest_paragraph_text,
        "featured_image": featured_image_url,
        "weather": weather_data,
        "facts": mars_html,
        "hemispheres": hemispheres
        };
    results = mars.insert(mars_data)

    # if result.acknowledged:
    # print('Mars Collection added' + str(result.inserted_id))

    # Iterate through the collection to confirm    
    # mars = mars.find()
    # for info in mars:
    #     pprint.pprint(info)
        
    # try:
    #     mars.save()
    # except NotUniqueError:
    #     print("")


    # listings["headline"] = soup.find("a", class_="result-title").get_text()
    # listings["price"] = soup.find("span", class_="result-price").get_text()
    # listings["hood"] = soup.find("span", class_="result-hood").get_text()

    return results


