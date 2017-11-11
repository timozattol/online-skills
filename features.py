
import re
import pandas as pd
from bs4 import BeautifulSoup

from crawler import is_cached, get_cached

### Structural features ###

feature_functions = {
    "a_count": lambda soup: len(soup.find_all("a")),
    "iframe_count": lambda soup: len(soup.find_all("iframe")),
    "h1_count": lambda soup: len(soup.find_all("h1")),
    "h2_count": lambda soup: len(soup.find_all("h2")),
    "h3_count": lambda soup: len(soup.find_all("h3")),
    "video_count": lambda soup: len(soup.find_all("video")),
    "button_count": lambda soup: len(soup.find_all("button"))
}

def construct_structural_features(urls, labels, features):
    '''
    Construct structural features contained in features
    Return a DataFrame containing url, label and features on each row
    '''
    row_list = []
    features_func = [feature_functions[feat] for feat in features]
    columns = ["url", "label"] + features

    for url, label in zip(urls, labels):
        if is_cached(url):
            soup = BeautifulSoup(get_cached(url), "lxml")

        row = [url, label] + [func(soup) for func in features_func]

        row_list.append(row)

    df = pd.DataFrame(row_list, columns=columns)
    df = df.set_index("url")

    return df


### NLP features ###
def tag_visible(element):
    '''Return true for elements that should be visible in the browser'''
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def extract_visible(soup):
    '''Extract all visible text from a BeautifulSoup soup'''
    text = soup.html.body.findAll(text=True)
    s = ' '.join(filter(tag_visible, text))
    return re.sub("\s\s+" , " ", s) # remove all double spaces and tabs/newlines/etc.
