import requests
from bs4 import BeautifulSoup
import json
import sqlite3
import os


def parse_config(filename):
    f = open(filename, 'r')
    js = json.loads(f.read())
    f.close()
    return js


def get_config(config):
    global URI
    global PAGE_SPT
    global DB_NAME
    URI = config['uri']['clien']
    PAGE_SPT = config['uri']['page_spt']
    DB_NAME = config['db']['name']


def crawl(uri):
    r = requests.get(uri)
    r.encoding = "utf-8"
    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.find('table', {'class': "tb_lst_normal"})
    tbody = table.find('tbody')
    tr_list = tbody.find_all('tr')

    db_insert_list = []

    for tr in tr_list:
        wrap_div = tr.td.div
        wrap_span = tr.td.div.span
        if not wrap_span is None:
            if not wrap_span.img is None:
                continue
            else:
                title = wrap_div.find('span', {"class": "lst_tit"}).get_text()
                href = uri[:-14] + wrap_div['onclick'][15:-1] + PAGE_SPT
                data = (href, title)
                db_insert_list.append(data)

    print(db_insert_list)#15개 중복확인 해야함

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    sql = "INSERT INTO board(href,title) values (?, ?)"
    cur.executemany(sql, tuple(db_insert_list))

    conn.commit()
    conn.close()


CONFIG_FILE = os.path.abspath("settings.json")
config = parse_config(CONFIG_FILE)
if not bool(config):
    print("Err: Setting file is not found")
    exit()
get_config(config)
crawl(URI)
