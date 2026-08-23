"""A daily RSS reader by Planck. No read later. Read it today or it's gone"""

import feedparser
import time
import requests
import concurrent.futures as threads
import calendar
import datetime

def date_handler_1(date_string):
    try:
        dt = datetime.datetime.strptime(date_string, "%d %b %Y, %H:%M:%S %z")
        return dt.utctimetuple()
    except ValueError:
        return None

def date_handler_2(date_string):
    try:
        dt = datetime.datetime.strptime(date_string, "%B %d, %Y")
        return dt.utctimetuple()
    except ValueError:
        return None

def date_handler_3(date_string):
    try:
        dt = datetime.datetime.strptime(date_string, "%a, %d %b %Y %H:%M:%S %z")
        if dt.year < 2010:
            dt = dt.replace(year=2010)
        return dt.utctimetuple()
    except ValueError:
        return None

def convert_times(time_object, raw):
    if not time_object:
        print(f"failed on {raw}")
        return None
    else:
        try:
            epoch = calendar.timegm(time_object)
            return time.strftime("%m-%d", time.localtime(epoch))
        except (OverflowError, OSError):
            print(f"error on {raw}")
            return None

def get_today_no_year():
    x = time.strftime("%m-%d", time.localtime(time.time() - 1*(86400)))
    return x

def load_urls(filename):
    f = open(filename, "r")
    lines = f.read().splitlines()
    f.close()
    print(f"Checking {len(lines)} feeds...")
    return lines

def _fetch(url):
    try:
        response = requests.get(url, headers={"User-Agent": "Mayfly RSS reader Alpha Version (+https://github.com/Santero-4/Mayfly)"}, timeout=10)
        feed =  feedparser.parse(response.content)
        return feed
    except requests.exceptions.RequestException as e:
        print(f"{url} threw {e}")
        return None

def fetch(urls, today):
    with threads.ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(_fetch, url): url for url in urls}
        for future in threads.as_completed(futures):
            feed = future.result()
            if feed is not None:
                stream_output(feed, today)

def stream_output(feed, today):
    for entry in feed.entries:
        date = convert_times(entry.get("published_parsed"), entry.get("published"))
        if date is None:
            date = convert_times(entry.get("updated_parsed"), entry.get("updated"))
            if date is None:
                print("Unprocessable dates:", (entry.get("updated"), entry.get("published")))
                break

        if date == today:
            print(f"{entry.get('title')},  by {feed.feed.title:} ({entry.get('link')}), posted {date}")
        else:
            #print(f"{feed.feed.title}, last seen on {date}")
            break
    return

def main():
    feedparser.registerDateHandler(date_handler_1)
    feedparser.registerDateHandler(date_handler_2)
    feedparser.registerDateHandler(date_handler_3)

    today = get_today_no_year()
    urls = load_urls("list.txt")

    fetch(urls, today)

if __name__ == "__main__":
    main()