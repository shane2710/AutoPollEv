#!/usr/bin/env python2.7

import requests
import os
import re
import sys

## python script to manipulate and automate Poll Everywhere responses

# define some constants
hash = 182936859384     # as far as I can tell, any 12 digit number works
COOKIE_URL = 'https://pollev.com/proxy/api/profile?_={}'
USER_URL = 'https://pollev.com/proxy/api/users/search?login_or_email={}&_={}'
LOGIN_URL = 'https://pollev.com/proxy/api/sessions'
TOKEN_URL = 'https://pollev.com/proxy/api/csrf_token?_={}'
REFERER_URL = 'https://pollev.com/login'
POLL_URL = [ 'https://firehose-production.polleverywhere.com/users/{}/activity/current.json?last_message_sequence=0&_={}',
        'https://pollev.com/proxy/api/polls/{}?_={}' ]


# obtain site cookies first - return integer based on success of retrieval
def get_cookies():
    global hash
    print 'Obtaining cookies...'
    cookie_response = s.get(COOKIE_URL.format(hash))
    # increment hash
    hash = hash + 1

    # ensure we retrieved cookies successfully
    if cookie_response.status_code != 200:
        print 'Can\'t retrieve cookies!'
        return 1
    else:
        print 'Got some yummy cookies!'
        return 0

# check for validity of username - returns integer based on validity
def check_user(USER):
    global hash
    print 'Checking for user {}...'.format(USER)
    user_response = s.head(USER_URL.format(USER,hash))
    hash = hash + 1

    # validity of response corresponds to user validity
    if user_response.status_code == 200:
        print 'User found!'
        return 0
    else:
        print 'User not found :('
        return 1


# login to the site! - returns an integer corresponding to login status
def login(user,password,csrf_token):
    print 'Logging in...'

    login_data = dict(
            login = user,
            password = password)
    login_header = {
            'Referer':REFERER_URL,
            'X-CSRF-Token':csrf_token}

    login_response = s.post(LOGIN_URL, data=login_data, headers=login_header)
    status = login_response.status_code

    if status == 422:
        print 'CSRF-token needs to be updated!'
        return 2
    elif status == 401:
        print 'Unauthorized: Password incorrect.'
        return 1
    elif (status == 204) or (status == 200):
        print 'Login successful!'
        return 0
    else:
        print 'Unknown Error: site returned {}'.format(status)
        return 3


# renew the CSRF token - returns the token value
def get_token():
    global hash
    print 'Renewing CSRF token...'
    csfw_data = dict(Referer = REFERER_URL)

    token_response = s.get(TOKEN_URL.format(hash),headers=csfw_data)
    hash = hash + 1

    token_data = token_response.json()
    csrf_token = token_data['token']

    if token_response.status_code != 200:
        print 'Token renewal failed :('
        return 1
    else:
        print 'Token renewed successfully!'
        return csrf_token


# get the actual poll's data url from the provided web url
def get_poll_hardlink(poll_profile):
    global hash
    print 'Obtaining poll hardlink...'
    response = s.get(POLL_URL[0].format(poll_profile,hash))

    if response.status_code == 200:
        response_json = response.json()
        data_url = re.search('".{15}"',response_json['message'])

        # remove the quotes surrounding the value needed by indexing the string
        fixed_data_url = data_url.group(0)[1:16]
        return fixed_data_url


# get poll data and return JSON dictionary object
def get_poll_data(data_url,target_poll):
    global hash
    print 'Downloading current poll data...'

    download_header = {'Referer':'https://pollev.com/{}'.format(target_poll),
            'Host':'pollev.com',
            'Connection':'keep-alive'}

    response = s.get(POLL_URL[1].format(data_url,hash), headers=download_header)
    if response.status_code == 200:
        print 'Poll data downloaded!'
        return response.json()
    else:
        print 'Poll data not found.  Response status {}'.format(response.status_code)
        print response.text
        sys.exit(1)


## Program flow

# prompt for username and pass
user = raw_input('Enter a username: ')
password = raw_input('Enter the secret password: ')
target_poll = raw_input('Enter the user hosting target poll: ')
# user = 'sryan8@nd.edu'
# password = ''
# target_poll = 'shaneryan239'

## start a session in order to keep track of cookies properly
s = requests.Session()

## start login process
get_cookies()       # simple as that

# check if the username provided is valid
if (check_user(user)):
    sys.exit(1)

csrf_token = get_token()
login_status = login(user,password,csrf_token)

# act on login status - renew token and retry if necessary
if login_status > 0:
    if login_status == 2:
        csrf_token = get_token()
        if csrf_token == 1:
            sys.exit(1)
        print 'Retrying login...'
        login_retry_status = login(user,password,csrf_token)
        if csrf_token != 0:
            sys.exit(1)
    else:
        sys.exit(1)

# obtain the desired poll's data link
data_url = get_poll_hardlink(target_poll)

# download poll data
my_poll_json = get_poll_data(data_url, target_poll)

# check if the poll is open
if my_poll_json['multiple_choice_poll']['state'] == 'opened':
    print 'Poll is open!'
else:
    print 'Poll is closed!'







