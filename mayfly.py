"""A daily RSS reader by Planck. No read later. Read it today or it's gone"""

import feedparser
import time
import requests
import concurrent.futures as threads
import calendar


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

def get_today():
    x = time.strftime("%Y-%m-%d", time.localtime(time.time() - 2*(86400)))
    return x

def get_today_no_year():
    x = time.strftime("%m-%d", time.localtime(time.time() - 0*(86400)))
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
            print(f"{entry.get('title')}: ({entry.get('link')}), posted {date}")
        else:
            #print(f"{feed.feed.title}, last seen on {date}")
            break
    return






def load_feeds_slowly(urls, today):
    """Input: list of URLS as strings
    Output: list of feedparser feeds that have content from today"""
    output = []
    for url in urls:
        feed = feedparser.parse(url)
        up = getattr(feed, "updated_parsed", None)
        pub = getattr(feed, "published_parsed", None)
        last_updated = time.strftime("%Y-%m-%d", time.localtime(time.mktime(up))) if up else None
        last_published = time.strftime("%Y-%m-%d", time.localtime(time.mktime(pub))) if pub else None
        if last_updated == today or last_published == today:
            output.append(feed)
    print(f"Found {len(output)} feeds that updated today...")
    return output



def retrive_content(feed_list, today):
    """Input: list of feedparser feeds that have content from today
    Output: list where each item is a tuple (title, full text)"""
    output = []
    for feed in feed_list:
        for entry in feed.entries:
            up = getattr(entry, "updated_parsed", None)
            pub = getattr(entry, "published_parsed", None)
            try:
                last_updated = time.strftime("%m-%d", time.localtime(time.mktime(up))) if up else None
            except OverflowError:
                last_updated = None
                print(f"date error for {up}")
            try:
                published = time.strftime("%m-%d", time.localtime(time.mktime(pub))) if pub else None
            except OverflowError:
                published = None
                print(f"date error for {pub}")

            if (published == today) or (published is None and last_updated == today):
                if 'title' in entry:
                    title = entry.title
                elif 'title' in feed:
                    title = feed.title
                else:
                    title = "Couldn't get a title"


                if 'link' in entry:
                    full_text = entry.link
                else:
                    full_text = "We couldn't find anything for this post..."
                output.append((title, full_text))

            elif (published is None and last_updated is None):
                if 'title' in entry:
                    title = entry.title
                elif 'title' in feed:
                    title = feed.title
                else:
                    title = "Couldn't get a title"


                if 'link' in entry:
                    full_text = entry.link
                else:
                    full_text = "We couldn't find anything for this post..."
                output.append((f"{title}, (undated)", full_text))
                break
            else:
                #uncomment for debug
                if 'title' in entry:
                    title = entry.title
                elif 'title' in feed:
                    title = feed.title
                else:
                    title = "Couldn't get a title"


                if 'link' in entry:
                    full_text = entry.link
                else:
                    full_text = "We couldn't find anything for this post..."
                output.append((f"{title}, Published: {published}", full_text))
                break

    if len(output) == 0:
        print("No content found for today")
        output.append(("test1", "test2"))
    return output


def main():
    print("hello world")
    today = get_today_no_year()
    urls = load_urls("list.txt")
    #
    # #fast mode
    fetch(urls, today)


    #slow mode--debug
    # feeds = load_feeds_slowly(urls, today)
    # content = retrive_content(feeds, get_today_no_year())
    # for item in content:
    #     print(item)

    # debug_fast = _fetch("https://foreach.neocities.org/rss.xml")

    # print(debug_fast.entries[0].get("updated"))
    # print(debug_fast.entries[0].get("published"))
    #
    # debug_fast = _fetch("https://daringfireball.net/feeds/main")
    # print(debug_fast.feed.title)
    # print(debug_fast.entries[0].get("published"))
    #
    # fetch(["https://daringfireball.net/feeds/main"], today)
    #fetch(["https://janlukas.blog/.rss"], today)
    # debug_slow = feedparser.parse("https://kevquirk.com/feed")
    # print(debug_slow)
    # print(debug_slow.entries[0].get("published"))



if __name__ == "__main__":
    main()




