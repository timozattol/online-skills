import grequests
import os

webpages_path = os.path.join("webpages", "manually_selected")
cache_folder = webpages_path + "/cache"

def urls_path(folder, positive=True):
    '''Return path of a given file containing urls'''
    pos = "positive" if positive else "negative"
    path = "{}/urls/{}-{}.txt".format(webpages_path, folder, pos)
    return path

def urls_list_folder(folder, positive=True):
    '''Return the list of urls in given folder'''
    path = urls_path(folder, positive)

    with open(path, 'r') as f:
        urls = list(l.strip() for l in f if l[0] != "#")
    f.close()

    return urls

def urls_list(folders):
    '''
    Construct positive and negative url list, concatenated
    for all given folders
    '''
    positives = []
    negatives = []

    for folder in folders:
        positives.extend(urls_list_folder(folder, positive=True))
        negatives.extend(urls_list_folder(folder, positive=False))

    return positives, negatives

def url_to_filename(url):
    '''Modify url to be accepted as a filename'''
    return url.replace("/", ",")

def filename_to_url(filename):
    '''Revert filename to the original url'''
    return filename.replace(",", "/")

def cache_path(url):
    '''Create the path of the cached file corresponding to the url page'''
    return "{}/{}".format(cache_folder, url_to_filename(url))

def delete_all_files(folder):
    '''Delete all files in given folder (!)'''
    for file in os.listdir(folder):
        file_path = os.path.join(folder, file)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(e)

def is_cached(url):
    '''Return True if url is already cached'''
    return os.path.isfile(cache_path(url))

def get_cached(url):
    '''Get cached version of webpage'''
    if not is_cached(url):
        raise Exception("{} not cached".format(url))

    with open(cache_path(url), 'r') as f:
        s = f.read()
    f.close()

    return s

def get_original_url(response):
    '''
    Return original url from a request/grequests response.
    With redirections, sometimes the response.url is different than original url
    '''
    return response.history[0].url if response.history else response.url

def cache_page(url, text, replace=True):
    '''Cache a already downloaded page'''

    # Do nothing if don't want to replace and page is cached
    if not replace:
        if is_cached(url):
            print("yea")
            return




def async_cache_pages(urls, delete_cache=False, threads=15, try_again_slow=True):
    '''Asychnronously cache pages by downloading them to the cache folder'''
    if delete_cache:
        delete_all_files(cache_folder)

    # Only request for pages not already in the cache folder
    reqs = [grequests.get(url) for url in urls if not is_cached(url)]
    try_again_urls = []


    for r in grequests.imap(reqs, size=threads):
        if r.status_code == 200:
            with open(cache_path(get_original_url(r)), 'w') as f:
                f.write(r.text)
            f.close()
        elif r.status_code == 429:
            try_again_urls.append(get_original_url(r))
        else:
            print("Error while downloading: {}. Status code: {}".format(r.url, r.status_code))

    # Does not work amazingly. TODO should try to sleep in between requests
    if try_again_slow:
        print("Trying again to download {} pages one at a time".format(len(try_again_urls)))

        reqs_slow = [grequests.get(url) for url in try_again_urls if not is_cached(url)]
        for r in grequests.imap(reqs_slow, size=1):
            if r.status_code == 200:
                with open(cache_path(get_original_url(r)), 'w') as f:
                    f.write(r.text)
                f.close()
            else:
                print("Error while downloading: {}. Status code: {}".format(r.url, r.status_code))
