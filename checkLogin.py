#!/usr/bin/env python2.7

import requests
import os
import sys

## python script to check the validity of a username / email on Poll Everywhere

user = raw_input('Enter a username: ')
hash = 148814357018     # as far as I can tell, any 12 digit number works

COOKIE_URL = 'https://pollev.com/proxy/api/profile?_={}'
USER_URL = 'https://pollev.com/proxy/api/users/search?login_or_email={}&_={}'

# start a session in order to keep track of cookies properly
s = requests.Session()

# obtain site cookies first
def get_cookies(hash):
    cookie_response = s.get(COOKIE_URL.format(hash))
    if cookie_response.status_code != 200:
        print 'Can\'t retrieve cookies!'
        sys.exit(1)

    # increment hash
    hash = hash + 1

# check for validity of username
def check_user(USER,hash):
    user_response = s.head(USER_URL.format(USER,hash))

    if user_response.status_code == 200:
        print 'User found!'
    else:
        print 'User not found :('

    hash = hash + 1

get_cookies(hash)
check_user(user,hash)

