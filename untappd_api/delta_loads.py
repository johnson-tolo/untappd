import json
import requests
import math
#import pandas as pd
import csv
from csv import writer
from datetime import datetime
import codecs

clientid = ''
clientsecret = ''
access_token = ''

base_url = 'https://api.untappd.com/v4/'
client_url = '?client_id=' + clientid + '&client_secret=' + clientsecret

# call the untappd api
def api_call(endpoint, user, params):
    return requests.get(base_url+endpoint+user+client_url+params)

# return list of tracked users and clear out the stage table
def tracked_users():
    user_array = []
    with open('tracked_users.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                user_array.append(row[0])
                line_count += 1
    f = open("tracked_users_stg.csv", "w+")
    f.close()
    return user_array

# makes an api call for a list of users
def pull_user_info(user):
    response = api_call('user/info/', user, '&compact=true')
    if str(response.json()["meta"]["code"]) != "200":
        print("Error",str(response.json()["meta"]["code"])," ", str(response.json()["meta"]["error_detail"]))
        quit()
    user_arr = []
    user_arr.append(datetime.now())
    user_arr.append(response.json()["response"]["user"]["uid"])
    user_arr.append(response.json()["response"]["user"]["user_name"])
    user_arr.append(response.json()["response"]["user"]["first_name"])
    user_arr.append(response.json()["response"]["user"]["last_name"])
    user_arr.append(response.json()["response"]["user"]["stats"]["total_badges"])
    user_arr.append(response.json()["response"]["user"]["stats"]["total_friends"])
    user_arr.append(response.json()["response"]["user"]["stats"]["total_checkins"])
    user_arr.append(response.json()["response"]["user"]["stats"]["total_beers"])
    user_arr.append(response.json()["response"]["user"]["stats"]["total_created_beers"])
    user_arr.append(response.json()["response"]["user"]["stats"]["total_followings"])
    user_arr.append(response.json()["response"]["user"]["stats"]["total_photos"])
    user_arr.append(int(math.ceil(response.json()["response"]["user"]["stats"]["total_beers"]/50)))
    user_arr.append(response.json()["response"]["user"]["user_avatar"])
    user_arr.append(response.json()["response"]["user"]["user_avatar_hd"])
    user_arr.append(response.json()["response"]["user"]["user_cover_photo"])
    user_arr.append(response.json()["response"]["user"]["user_cover_photo_offset"])
    user_arr.append(response.json()["response"]["user"]["is_private"])
    user_arr.append(response.json()["response"]["user"]["location"])
    user_arr.append(response.json()["response"]["user"]["url"])
    user_arr.append(response.json()["response"]["user"]["bio"])
    user_arr.append(response.json()["response"]["user"]["is_supporter"])
    user_arr.append(response.json()["response"]["user"]["untappd_url"])
    user_arr.append(response.json()["response"]["user"]["account_type"])
    return user_arr

# append row to given csv
def append_list_as_row(file_name, list_of_elem):
    # Open file in append mode
    with open(file_name, 'a+', newline='', encoding='utf-8') as write_obj:
        # Create a writer object from csv module
        csv_writer = writer(write_obj)
        # Add contents of list as last row in the csv file
        csv_writer.writerow(list_of_elem)

# Update stage table with user, api beers, and beers that have been logged in the csv already to calc the diff
def update_tracked_users(user, api_total_beers):
    beer_count = 0
    with open('user_beers.csv', encoding='utf8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_ct = 0
        for row in csv_reader:
            if line_ct == 0:
                line_ct += 1
            elif row[0].lower() == user.lower():
                beer_count += 1
            else:
                pass
    elements = [user, api_total_beers, beer_count]
    append_list_as_row('tracked_users_stg.csv', elements)

# makes user api call for each user in list
def pull_all_users():
    tracked_users_list = tracked_users()####################################3
    user_info_array = []
    for user in tracked_users_list:
        temp_array = pull_user_info(user)
        user_info_array.append(temp_array)
        update_tracked_users(temp_array[2], int(temp_array[8]))
    return user_info_array

# THIS USES EVERYTHING ABOVE IT
# Does everything USER related
# get user list, pull user data from api, write to user_info.csv, write to stage the diff btwn api and user_beers.csv
def user_script():
    user_data = pull_all_users()
    for item in user_data:
        append_list_as_row('user_info.csv', item)

def get_beers(user, beers_missing):
    page = 0
    max_pages = math.ceil(beers_missing/50)
    response_arr = []
    while page < max_pages:
        api_call_limit = 0
        if page == max_pages-1:
            if beers_missing%50 == 0:
                api_call_limit = 50
            else:
                api_call_limit = beers_missing%50
        else:
            if beers_missing >= 50:
                api_call_limit = 50
            else:
                api_call_limit = beers_missing%50

        response = api_call('user/beers/', user, '&limit='+str(api_call_limit)+'&offset='+str(50*(page)))
        x = 0
        while(x<api_call_limit):
            if str(response.json()["meta"]["code"]) != "200":
                print("Error",str(response.json()["meta"]["code"])," ", str(response.json()["meta"]["error_detail"]))
                quit()
            user_arr = []
            user_arr.append(user),
            user_arr.append(str(response.json()["response"]["beers"]["items"][x]["beer"]["beer_name"]).replace('\n',' ')),
            user_arr.append(str(response.json()["response"]["beers"]["items"][x]["beer"]["bid"]).replace('\n',' ')),
            user_arr.append(float(response.json()["response"]["beers"]["items"][x]["beer"]["beer_abv"])),
            user_arr.append(int(response.json()["response"]["beers"]["items"][x]["beer"]["beer_ibu"])),
            user_arr.append(str(response.json()["response"]["beers"]["items"][x]["beer"]["beer_style"]).replace('\n',' ')),
            #user_arr.append(str(response.json()["response"]["beers"]["items"][x]["beer"]["beer_description"]).replace('\n',' ')),
            user_arr.append(str(response.json()["response"]["beers"]["items"][x]["beer"]["beer_label"]).replace('\n',' ')),
            user_arr.append(float(response.json()["response"]["beers"]["items"][x]["beer"]["rating_score"])),
            user_arr.append(int(response.json()["response"]["beers"]["items"][x]["beer"]["rating_count"])),
            user_arr.append(float(response.json()["response"]["beers"]["items"][x]["rating_score"])),
            user_arr.append(str(response.json()["response"]["beers"]["items"][x]["recent_checkin_id"]).replace('\n',' ')),
            user_arr.append(datetime.strptime(str(response.json()["response"]["beers"]["items"][x]["recent_created_at"])[5:25], '%d %b %Y %H:%M:%S')),
            user_arr.append(str(response.json()["response"]["beers"]["items"][x]["first_checkin_id"]).replace('\n',' ')),
            user_arr.append(datetime.strptime(str(response.json()["response"]["beers"]["items"][x]["first_created_at"])[5:25], '%d %b %Y %H:%M:%S')),
            user_arr.append(str(response.json()["response"]["beers"]["items"][x]["recent_created_at_timezone"]).replace('\n',' ')),
            user_arr.append(str(response.json()["response"]["beers"]["items"][x]["brewery"]["brewery_id"]).replace('\n',' ')),
            user_arr.append(str(response.json()["response"]["beers"]["items"][x]["brewery"]["brewery_name"]).replace('\n',' ')),
            user_arr.append(str(response.json()["response"]["beers"]["items"][x]["brewery"]["brewery_type"]).replace('\n',' ')),
            user_arr.append(str(response.json()["response"]["beers"]["items"][x]["brewery"]["brewery_label"]).replace('\n',' ')),
            user_arr.append(str(response.json()["response"]["beers"]["items"][x]["brewery"]["contact"]["twitter"]).replace('\n',' ')),
            user_arr.append(str(response.json()["response"]["beers"]["items"][x]["brewery"]["contact"]["facebook"]).replace('\n',' ')),
            user_arr.append(str(response.json()["response"]["beers"]["items"][x]["brewery"]["contact"]["instagram"]).replace('\n',' ')),
            user_arr.append(str(response.json()["response"]["beers"]["items"][x]["brewery"]["contact"]["url"]).replace('\n',' ')),
            user_arr.append(str(response.json()["response"]["beers"]["items"][x]["brewery"]["country_name"]).replace('\n',' ')),
            user_arr.append(str(response.json()["response"]["beers"]["items"][x]["brewery"]["location"]["brewery_city"]).replace('\n',' ')),
            user_arr.append(str(response.json()["response"]["beers"]["items"][x]["brewery"]["location"]["brewery_state"]).replace('\n',' ')),
            user_arr.append(str(response.json()["response"]["beers"]["items"][x]["brewery"]["location"]["lat"]).replace('\n',' ')),
            user_arr.append(str(response.json()["response"]["beers"]["items"][x]["brewery"]["location"]["lng"]).replace('\n',' ')),
            user_arr.append(str(response.json()["response"]["beers"]["items"][x]["brewery"]["brewery_active"]).replace('\n',' '))
            response_arr.append(user_arr)  
            x += 1 
        page += 1
    return response_arr


def check_beer_diff():
    diff_array = []
    with open('tracked_users_stg.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if int(row[1]) > int(row[2]):
                diff_array.append([row[0], int(row[1]) - int(row[2])])
            else:
                pass
    return diff_array


def pull_beers(diff_users):
    for drinker in diff_users:
        responses = get_beers(drinker[0], drinker[1])
        beer_row = 0
        for r in responses:
            append_list_as_row('user_beers.csv', r)

## runs the main user script to check users and check for a diff in api vs database beers
user_script()

## pulls beer data for users with new checkins
pull_beers(check_beer_diff())
