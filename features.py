
import re


### NLP ###
def tag_visible(element):
    '''Return true for visible elements'''
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
