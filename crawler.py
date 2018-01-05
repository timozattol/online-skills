import os
import time
import random
import requests
from urllib.parse import urljoin
from collections import deque
import numpy as np
import pandas as pd

import networkx as nx
from bs4 import BeautifulSoup
from sklearn.externals import joblib

from features import extract_visible
from helpers import get_cached, is_cached, eprint, url_to_filename, cache_page

default_pipeline_path = os.path.join('saved', 'models', 'log_reg_pipeline_general3.pkl')
default_pipeline = joblib.load(default_pipeline_path)

class Node:
    status = {
        True: "class_true",
        False: "class_false",
        "fail": "req_failed",
    }

    def __init__(self, url, status, decision_func):
        self.url = url
        self.status = status
        self.decision_func = decision_func

    def __str__(self):
        # Remove "https://www." part for clarity
        stripped = "".join(self.url.split('://')[1:])
        return stripped

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.url == other.url
        return False

    def __hash__(self):
        return hash(self.url)

def draw_graph(G, plt, print_pos=False, print_neg=False):
    colors = []

    for node in G:
        if node.status == Node.status[True]:
            if print_pos:
                print("TRUE: {} {}".format(node.decision_func, node))
            colors.append('green')
        elif node.status == Node.status[False]:
            if print_neg:
                print("FALSE: {} {}".format(node.decision_func, node))
            colors.append('red')
        else:
            # Download error
            colors.append('grey')

    fig, ax = plt.subplots(figsize=(15, 10))
    nx.draw_kamada_kawai(G, ax=ax, node_color=colors, with_labels=False, node_size=50, width=0.5, alpha=1)

def get_df(graph):
    rows = []

    for node in graph:
        rows.append([node.url, node.status, node.decision_func])

    return pd.DataFrame(rows, columns=["url", "status", "decision_func"])


def BFS_crawl(initial_urls, depth_limit, breadth_limit, save=True, pipeline=default_pipeline):

    # Queue containing: (url, depth)
    queue = deque()
    for initial_url in initial_urls:
        queue.append((initial_url, 0, None))

    G = nx.DiGraph()
    seen_urls = set()

    print("BFS started with params: ")
    print("Depth_limit: {}\nBreadth_limit: {}.".format(depth_limit, breadth_limit))

    # Assuming download+sleep=1s
    estimated_time = len(initial_urls) * np.power(breadth_limit, depth_limit + 1)
    print("Estimated time: {}s".format(estimated_time))
    start_time = time.time()

    while(len(queue) > 0):
        url, depth, parent_node = queue.popleft()

        print(".", end="")

        # Add url to seen_urls here, to avoid infinite loop (if the page links to itself)
        seen_urls.add(url)

        # Fetch from cache or download the page
        if is_cached(url):
            text = get_cached(url)
            status_code = 200
        else:
            try:
                # Sleep to avoid getting banned
                time.sleep(0.5)

                r = requests.get(url)
                status_code = r.status_code
                text = r.text

                # TODO try if cache page works
                cache_page(url, text)
            except Exception as e:
                eprint("Exception while requesting {}".format(url))
                eprint(e)
                status_code = -1


        if status_code != 200:
            node = Node(url, Node.status["fail"], 0)
            G.add_node(node)
        else:
            try:
                soup = BeautifulSoup(text, "lxml")
                visible_text = extract_visible(soup)
            except Exception as e:
                eprint("Exception while parsing {}".format(url))
                eprint(e)
                continue

            # Predict label & get strength of prediction
            label = default_pipeline.predict([visible_text])[0]
            decision_func = default_pipeline.decision_function([visible_text])[0]

            node = Node(url, Node.status[label], decision_func)
            G.add_node(node)

            if depth < depth_limit:
                # Get outgoing url in their absolute form
                out_urls = []
                for a in soup.find_all("a"):
                    try:
                        out_urls.append(urljoin(url, a.get('href', '')))
                    except:
                        # URL is discarded is could not get absolute form
                        print("Exception while joining {} with {}".format(url, a.get('href', '')))

                # Remove already seen urls
                out_urls = [out_url for out_url in out_urls if out_url not in seen_urls]

                # Keeping only <breadth_limit> out_urls
                if len(out_urls) > breadth_limit:
                    out_urls = random.sample(out_urls, breadth_limit)

                queue.extend((out_url, depth + 1, node) for out_url in out_urls)

        if parent_node is not None:
            G.add_edge(parent_node, node)

    print("Crawling finished after {}s".format(time.time() - start_time))

    # Pickle file if asked
    if save:
        save_path = os.path.join('saved', 'graphs', "{}-depth:{}-breadth:{}.pkl"
            .format(url_to_filename(initial_urls[0]), depth_limit, breadth_limit))

        nx.write_gpickle(G, save_path)
        print("Graph saved under {}".format(save_path))

    return G
