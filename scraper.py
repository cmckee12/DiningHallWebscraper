from bs4 import BeautifulSoup
import requests
import praw
import schedule
import time
import datetime

#urls for each umd dining hall menu
south_campus_url = 'https://nutrition.umd.edu/?locationNum=16'
the_y_url = 'https://nutrition.umd.edu/?locationNum=19'
north_251_url = 'https://nutrition.umd.edu/?locationNum=51'

# make boring set
boring = set()
with open('boring.txt', 'r') as f:
    for line in f:
        boring.add(line.strip())


# Gets the menus for every restaurant at a dining hall
def get_menu(url):
    # make a request to get the south campus menu
    page = requests.get(url)

    soup = BeautifulSoup(page.content, 'html.parser')

    #all restaurants at the current dining hall
    lists = soup.find_all('div', class_='card')

    restaurant_to_menu = {}

    for list in lists: 
        name = list.find('h5', class_='card-title').text
        items = list.find_all('a', class_='menu-item-name')

        restaurant_to_menu[name] = []

        for item in items:
            if item.text not in boring:
                restaurant_to_menu[name].append(item.text)

    return restaurant_to_menu

# set each dining hall to a menu
south = get_menu(south_campus_url)
y = get_menu(the_y_url)
north = get_menu(north_251_url)


# Retrieve Reddit API credentials from environment variables
client_id = 'Wws_3rFHBNTWEdsyOWKQqw'
client_secret = 'kgT472kY5gQQOjveylorHj7kG7athA'
username = 'UMD_dining_menu'
password = 'FmGhJbB;zE8,xD-'

# Initialize PRAW instance
reddit = praw.Reddit(client_id=client_id,
                     client_secret=client_secret,
                     username=username,
                     password=password,
                     user_agent='dining_hall_bot/1.0 (by /u/UMD_dining_bot)')


def post_to_reddit():
    subreddit = reddit.subreddit('umd_dining_menu')
    title = 'Menu for ' + datetime.date.today().strftime('%A') + ', ' + time.strftime('%m/%d/%Y')
    
    body = '\n\n**The Y:**\n\n'
    for restaurant in y:
        if (y[restaurant].__len__() == 0):
            continue
        body += '\t' + restaurant + '\n'
        for item in y[restaurant]:
            body += '\t\t- ' + item + '\n'
        body += '\n'
    
    body += '**South Campus:**\n\n'
    for restaurant in south:
        if (south[restaurant].__len__() == 0):
            continue
        body += '\t' + restaurant + '\n'
        for item in south[restaurant]:
            body += '\t\t- ' + item + '\n'
        body += '\n'

    body += '\n\n**North 251:**\n\n'
    for restaurant in north:
        if (north[restaurant].__len__() == 0):
            continue
        body += '\t' + restaurant + '\n'
        for item in north[restaurant]:
            body += '\t\t- ' + item + '\n'
        body += '\n'

    # Post the menu to Reddit    
    subreddit.submit(title=title, selftext=body)
                     

def lambda_handler(event, context):
    post_to_reddit()

