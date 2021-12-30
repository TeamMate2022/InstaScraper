# -*- coding: utf-8 -*-
"""
Created on Mon Dec 27 18:38:26 2021

@author: Ali
"""

import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time, json
# import time, urllib.request
# import requests, json
# from bs4 import BeautifulSoup


# config:
DRIVER_PATH = os.path.dirname(__file__) + r"/chromedriver.exe"
driver = webdriver.Chrome(DRIVER_PATH)

USERNAME = 'annonymous_test'
PASSWORD = 'this is a test 123'

PROFILES_PATH = os.path.dirname(__file__) + r"/user_profiles.txt"
BASIC_DATABASE = os.path.dirname(__file__) + r"/base_database.txt"
WATCHLIST = os.path.dirname(__file__) + r"/watchlist.txt"
USER_INFORMATIONS = os.path.dirname(__file__) + r"/user_basic_informations.txt"
RESULT_PATH = os.path.dirname(__file__) + r"/result.txt"


LOADING_PERIOD = 10
PAGE_INTERACT_PERIOD = 6
MAX_POSTS = 5

WATCHLIST_PERIOD = 3600

# TODO :
#  1. check that user_profiles.txt exist, otherwise run script to get profiles (def retrive_usernames)
#  2. check that result.txt file exist, otherwise create a new file

# keys:
KEY_USERNAME = "username"
KEY_POSTS = "posts"
KEY_FOLLOWERS = "followers"
KEY_FOLLOWING = "following"
KEY_ANALYSED_POSTS = "analysed_posts"
KEY_LAST_POST_DATE = "last_post_date"
KEY_LAST_POST_TIME = "last_post_time"
KEY_LIKES = "likes"
KEY_VIEWS = "views"
KEY_ENGAGEMENT = "engagement"
DEBUG = True

CLEANED_FILE = False

def init_instagram():
    """ we will login to instagram and make our bot ready """
    driver.get("https://www.instagram.com/")
    
    # accept cookies:
    # time.sleep(PAGE_INTERACT_PERIOD)
    # driver.find_element_by_xpath("//button[contains(text(), 'Accept All')]").click()

    # login 
    time.sleep(LOADING_PERIOD)
    username = driver.find_element_by_css_selector("input[name='username']")
    password = driver.find_element_by_css_selector("input[name='password']")
    username.clear()
    password.clear()
    username.send_keys(USERNAME)
    password.send_keys(PASSWORD)
    driver.find_element_by_css_selector("button[type='submit']").click()

    # save login info?
    time.sleep(PAGE_INTERACT_PERIOD)
    driver.find_element_by_xpath("//button[contains(text(), 'Not Now')]").click()

    # turn off notif
    time.sleep(PAGE_INTERACT_PERIOD)
    driver.find_element_by_xpath("//button[contains(text(), 'Not Now')]").click()
    
    
def get_usernames(PROFILES_PATH):
    """ this method will read usernames from user_profiles file"""
    return open(PROFILES_PATH, 'r').read().split('\n')

def find_profile(username):
    # searchbox    
    time.sleep(LOADING_PERIOD)
    searchbox = driver.find_element_by_css_selector("input[placeholder='Search']")
    searchbox.clear()
    searchbox.send_keys(username)
    time.sleep(PAGE_INTERACT_PERIOD)
    searchbox.send_keys(Keys.ENTER)
    time.sleep(PAGE_INTERACT_PERIOD)
    searchbox.send_keys(Keys.ENTER)
    
def get_profile_information():
    # extraction followers, posts
    time.sleep(LOADING_PERIOD)
    
    followers = (driver.find_element_by_xpath("//*[@id='react-root']/section/main/div/header/section/ul/li[2]/a/span").get_attribute("title").replace(',', '')) 
    following = (driver.find_element_by_xpath("//*[@id='react-root']/section/main/div/header/section/ul/li[3]/a/span").text.replace('following', '').replace(' ', ''))
    
    posts = int(driver.find_element_by_xpath("//*[@id='react-root']/section/main/div/header/section/ul/li[1]/span/span").text.replace(',',''))
    
    # open last post and get time
    last_post_date, last_post_time = get_last_post_information()

    return ({KEY_FOLLOWERS : followers}, {KEY_FOLLOWING : following}, {KEY_POSTS : posts}, {KEY_LAST_POST_DATE : last_post_date}, {KEY_LAST_POST_TIME : last_post_time})


def get_last_post_information():
    """ get last post url and then open it, finally extract date and time"""    
    #posts
    posts_links = []
    links = driver.find_elements_by_tag_name('a')
    
    for link in links:
        attr = link.get_attribute('href')
        if '/p/' in attr:
            posts_links.append(attr)
            if len(posts_links) == 1:
                break
    # post_date, post_time = ""
    for post in posts_links:
        driver.get(post)
        time.sleep(PAGE_INTERACT_PERIOD)             
        post_datetime = driver.find_element_by_xpath("//*[@id='react-root']/section/main/div/div[1]/article/div/div[2]/div/div[2]/div[2]/a/time").get_attribute('datetime')
        post_date, post_time = post_datetime.split("T")
        post_time = post_time[:len(post_time)-5]
        
        print(post_date, post_time)
    return (post_date, post_time)


# ------------------------------------------------------------------------------
def total_likes(MAX_POSTS):
    likes = []
    view = []
    
    if MAX_POSTS >= 5:
        # scroll
        scrolldown = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var scrolldown=document.body.scrollHeight;return scrolldown;")
        match=False
        while(match==False):
            last_count = scrolldown
            time.sleep(LOADING_PERIOD)
            scrolldown = ("window.scrollTo(0, document.body.scrollHeight);var scrolldown=document.body.scrollHeight;return scrolldown;")
            if last_count==scrolldown:
                match=True 
    #posts
    posts_links = []
    links = driver.find_elements_by_tag_name('a')
    
    for link in links:
        attr = link.get_attribute('href')
        if '/p/' in attr:
            posts_links.append(attr)
            if len(posts_links) == MAX_POSTS:
                break
    
    #get videos and images
    counter = 1
    for post in posts_links:
        print(f'Post {counter} of {len(posts_links)} is in proccessing')
        driver.get(post)
        time.sleep(PAGE_INTERACT_PERIOD)
        try:
            likes.append(((driver.find_element_by_xpath("//*[@id='react-root']/section/main/div/div[1]/article/div/div[2]/div/div[2]/section[2]/div/div/a/span").text).replace(',','')))
            # print(likes)
        except:
            view.append(((driver.find_element_by_xpath("//*[@id='react-root']/section/main/div/div[1]/article/div/div[2]/div/div[2]/section[2]/div/span/span").text).replace(',','')))
            # print(view)
            
        sum_likes = sum(list(map(int,likes)))
        sum_view = sum(list(map(int,view)))
        counter += 1
        
    # return dictionary 
    return ({KEY_LIKES : sum_likes}, {KEY_VIEWS : sum_view}, {KEY_ANALYSED_POSTS: len(posts_links)})
    

def calculate_engagement(likes, views, followers):
    engagement = (((likes+views) / MAX_POSTS) / int(followers)) * 100
    return {KEY_ENGAGEMENT : engagement}


def write_information(file_path, information):
    global CLEANED_FILE
    if not CLEANED_FILE:
        print('Cleaning result file for the first time')
        open(file_path, 'w').close()
        CLEANED_FILE = True
    with open(file_path, 'a') as file:
        print('Saving information in file')
        file.write(json.dumps(information))
        file.write("\n")
        
        

def scrape_instagram_profiles(profiles):
    profiles_count = len(profiles)
    counter = 1
    for profile in profiles:
        print(f'User {counter} of {profiles_count} is in proccessing')
        profile_information = {}
        find_profile(profile)

        followers, posts = get_profile_information()
        likes, views, analysed_posts = total_likes(MAX_POSTS)
        engagement = calculate_engagement(likes[KEY_LIKES], views[KEY_VIEWS], followers[KEY_FOLLOWERS])

        user_information = {KEY_USERNAME : profile}
        profile_information.update(user_information)
        profile_information.update(followers)
        profile_information.update(posts)
        profile_information.update(likes)
        profile_information.update(views)
        profile_information.update(analysed_posts)
        profile_information.update(engagement)
        
        write_information(RESULT_PATH, profile_information)
        
        counter += 1

        

def initial_profile_database(profiles):
    profiles_count = len(profiles)
    counter = 1
    for profile in profiles:
        print(f'User {counter} of {profiles_count} is in proccessing')
        profile_information = {}
        find_profile(profile)

        followers, following, posts, last_post_date, last_post_time = get_profile_information()

        user_information = {KEY_USERNAME : profile}
        profile_information.update(user_information)
        profile_information.update(followers)
        profile_information.update(following)
        profile_information.update(posts)
        profile_information.update(last_post_date)
        profile_information.update(last_post_time)
        
        write_information(BASIC_DATABASE, profile_information)

        counter += 1
    
    

# Main ________________________________________________
driver = webdriver.Chrome(DRIVER_PATH)
# we will sign into instagram and make environment ready to run script


def run_bot():
    """ this method will initialize bot """
    # step A. connect to instagram and create file which contains user followers, username, last post time
    # connect to instagram and login to account
    init_instagram()
    
    #  init a database of users information
    initial_profile_database(profiles)
    
    


# TODO: WARNING - edit here in production
if not DEBUG:    
    profiles = get_usernames(PROFILES_PATH)
else: 
    profiles = get_usernames(PROFILES_PATH)[:2]



run_bot()