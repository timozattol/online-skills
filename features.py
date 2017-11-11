
import re
import pandas as pd

from bs4 import BeautifulSoup
from bs4.element import Comment

from nltk.corpus import stopwords

from sklearn.model_selection import train_test_split
from sklearn import metrics

from crawler import is_cached, get_cached

### Classification ###

def analyse_classification(X, y, predictor, seed=0):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=seed)
    predictor.fit(X_train, y_train)
    y_pred = predictor.predict(X_test)

    print(metrics.classification_report(y_test, y_pred))
    print(metrics.confusion_matrix(y_test, y_pred))

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
def construct_text_df(urls, labels):
    '''

    '''
    row_list = []
    columns = ["url", "label", "visible_text"]

    for url, label in zip(urls, labels):
        if is_cached(url):
            soup = BeautifulSoup(get_cached(url), "lxml")

        row = [url, label] + [extract_visible(soup)]

        row_list.append(row)

    df = pd.DataFrame(row_list, columns=columns)
    df = df.set_index("url")

    return df


def tag_visible(element):
    '''Return true for elements that should be visible in the browser'''
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def clean_string(string):
    # Remove all double spaces and tabs/newlines/etc.
    string = re.sub("\s\s+" , " ", string)

    # Remove stopwords
    words_no_stopwords = (word for word in string.split() if word not in stopwords.words('english'))
    return ' '.join(words_no_stopwords)

def extract_visible(soup):
    '''Extract all visible text from a BeautifulSoup soup'''
    text = soup.html.body.findAll(text=True)
    s = ' '.join(filter(tag_visible, text))
    return clean_string(s)
