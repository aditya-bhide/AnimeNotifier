from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
from datetime import date, datetime, timedelta
from pymongo import MongoClient
import re
#########mongodb Database########
myclient = MongoClient("")
mydb = myclient['AnimeNotifier']
logs = mydb.logs

main_link = "https://www17.gogoanimes.tv/"

def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 
            and content_type is not None 
            and content_type.find('html') > -1)


def log_error(e):
    """
    It is always a good idea to log errors. 
    This function just prints them, but you can
    make it do anything.
    """
    print(e)

def check_anime_exists(name):
    name = re.sub(r"[^a-zA-Z0-9]+", ' ', name)
    name = name.lower()
    name = name.replace(" ", "-")
    anime_main_link = main_link + "/category/" + name
    # print(anime_main_link)
    raw_html = simple_get(anime_main_link)
    if raw_html == None:
        return False
    return True

def check_in_log(log):
    global logs
    link = [i for i in logs.find({"links":log})]
    now = datetime.now()  # current date and time
    if link == []:
        final = now + timedelta(days=5)
        logs.insert_one({"links":log, "time":str(final.date())})
        return False
    return True

def call_url(anime_name, type):
    raw_html = simple_get(main_link)
    soup = BeautifulSoup(raw_html, 'html.parser')
    mydivs = soup.find_all("div",{"class": "last_episodes loaddub"})
    mydivs = BeautifulSoup(str(mydivs[0]), 'html.parser')
    temp = "a[title='" + anime_name + "']"
    x = mydivs.select(temp)
    if x != []:
        sub_link = x[0]['href']
        final = main_link + sub_link[1:]
        if type == 0:
            if check_in_log(str(sub_link)):
                return 0, None
            return final, None
        return final, str(sub_link)
    return 0, None
