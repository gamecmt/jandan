# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import hashlib
import re
import base64
import os
import sqlite3
import time


def _md5(value):
    '''md5加密'''
    m = hashlib.md5()
    m.update(value.encode('utf-8'))
    return m.hexdigest()


def _base64_decode(data):
    '''bash64解码，要注意原字符串长度报错问题'''
    missing_padding = 4 - len(data) % 4
    if missing_padding:
        data += '=' * missing_padding
    return base64.b64decode(data)


def get_imgurl(m, r=''):
    '''解密获取图片链接'''
    e = "DECODE"
    q = 4
    r = _md5(r)
    o = _md5(r[0:0 + 16])
    n = _md5(r[16:16 + 16])
    l = m[0:q]
    c = o + _md5(o + l)
    m = m[q:]
    k = _base64_decode(m)
    url = 'w'+k.decode('utf', errors='ignore')
    return url


def get_hash(js_url):
    '''获取关键字符串'''
    js = requests.get(js_url).text
    hash_key = re.findall(r'c=[\w\d]+\(e,"(.*?)"\)', js)[0]
    return hash_key


def get_html_comments(url):
    '''获取当前url页面内容'''
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0',
        'Host': 'jandan.net'
    }
    html_comments = requests.get(url, headers=headers).text
    return html_comments


def get_html_page(html_comments):
    ''' 获取html_comments中显示的当前页数 '''
    pattern = r'<span class="current-comment-page">\[(\d+)\]</span>'
    page = re.findall(pattern, html_comments)[0]
    return page


def get_img_comments(html_comments):
    '''获取html_comments中25张图片所有信息'''
    js_url = 'http:' + \
        re.findall(
            r'<script src="(//cdn.jandan.net/static/min/[\w\d]+\.\d+\.js)"></script>', html_comments)[-1]
    hash_key = get_hash(js_url)
    soup = BeautifulSoup(html_comments, 'lxml')
    img_comments = soup.select('li')
    del img_comments[12]
    img_comments = img_comments[9:34]
    return img_comments, hash_key


def get_img_id(img_comment):
    ''' 获取img_comment中图片的煎蛋id '''
    img_comment = img_comment.text
    pattern = r'(\d{6,})'
    try:
        img_id = re.findall(pattern, img_comment)[0]
    except:
        img_id = 0
    return img_id


def get_img_oo(img_comment):
    ''' 得到img_comment里面的点赞数 '''
    img_comment = img_comment.text
    pattern = r'OO \[(\d+)\]'
    try:
        img_oo = re.findall(pattern, img_comment)[0]
    except:
        img_oo = 0
    return img_oo


def get_img_xx(img_comment):
    ''' 得到img_comment里面的反对数 '''
    img_comment = img_comment.text
    pattern = r'XX \[(\d+)\]'
    try:
        img_xx = re.findall(pattern, img_comment)[0]
    except:
        img_xx = 0
    return img_xx


def get_img_url(img_comment, hash_key):
    ''' 获取img_comment中图片的真实链接, 多个链接以 , 链接。 '''
    img_urls = ""
    img_hashs = img_comment.select('.img-hash')
    for img_hash in img_hashs:
        img_hash = img_hash.text
        img_url = get_imgurl(img_hash, hash_key)
        img_url = img_url.replace("/mw600/", "/large/")
        img_url = img_url.replace("/mw1024/", "/large/")
        img_url = img_url.replace("/mw690/", "/large/")
        img_url = img_url.replace("/bmiddle/", "/large/")
        img_url = img_url.replace("/thumb180/", "/large/")
        img_urls = img_urls+","+img_url
    img_urls = img_urls[1:]
    return img_urls


def distinct():
    ''' 清除重复图片纪录，只保留最小id的那条数据，以url为判断重复图片的依据。 '''
    conn = sqlite3.connect('jandan.db')
    # 清除所有重复id的数据，保留最早纪录。
    conn.execute(
        "delete from wuliao where rowid not in(select min(rowid) from wuliao group by img_url);")
    conn.execute(
        "delete from meizi where rowid not in(select min(rowid) from meizi group by img_url);")
    conn.commit()
    conn.close()


def check_db(db_name):
    ''' 检查是否有sqlite数据库，如果没有则创建一个新jandan.db数据库。 '''
    if not os.path.isfile(db_name):
        conn = sqlite3.connect(db_name)
        # 创建妹子图表
        conn.execute("CREATE TABLE `meizi` (`id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, `img_id` INTEGER DEFAULT 0, `img_url`	TEXT NOT NULL,`img_oo` INTEGER NOT NULL DEFAULT 0, `img_xx` INTEGER NOT NULL DEFAULT 0, `datetime` TEXT DEFAULT CURRENT_TIMESTAMP);")
        # 创建无聊图表
        conn.execute("CREATE TABLE `wuliao` (`id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, `img_id` INTEGER DEFAULT 0, `img_url`	TEXT NOT NULL,`img_oo` INTEGER NOT NULL DEFAULT 0, `img_xx` INTEGER NOT NULL DEFAULT 0, `datetime` TEXT DEFAULT CURRENT_TIMESTAMP);")
        conn.commit()
        conn.close()


def img_wuliao_sqlite(page, img_info):
    ''' 将无聊图图片信息插入到jandan数据库wuliao表格中 '''
    conn = sqlite3.connect('jandan.db')
    cursor = conn.cursor()
    for img_one_info in img_info:
        cursor.execute("select id from wuliao where img_id=?",
                       (img_one_info[0],))
        values = cursor.fetchone()
        try:
            value = values[0]
        except:
            value = None
        if value == None:
            conn.execute(
                "INSERT INTO wuliao (img_id,img_url,img_oo,img_xx) VALUES (?,?,?,?)", img_one_info)
        else:
            cursor.execute(
                'UPDATE wuliao SET img_id=?,img_url=?,img_oo=?,img_xx=? WHERE id = ?', (img_one_info[0], img_one_info[1], img_one_info[2], img_one_info[3], value))
    conn.commit()
    conn.close()
    print("wuliao " + page + " records successfully.")
    time.sleep(5)


def img_meizi_sqlite(page, img_info):
    ''' 将妹子图图片信息插入到jandan数据库meizi表格中 '''
    conn = sqlite3.connect('jandan.db')
    cursor = conn.cursor()
    for img_one_info in img_info:
        cursor.execute("select id from meizi where img_id=?",
                       (img_one_info[0],))
        values = cursor.fetchone()
        try:
            value = values[0]
        except:
            value = None
        if value == None:
            conn.execute(
                "INSERT INTO meizi (img_id,img_url,img_oo,img_xx) VALUES (?,?,?,?)", img_one_info)
        else:
            cursor.execute(
                'UPDATE meizi SET img_id=?,img_url=?,img_oo=?,img_xx=? WHERE id = ?', (img_one_info[0], img_one_info[1], img_one_info[2], img_one_info[3], value))
    conn.commit()
    conn.close()
    print("meizi " + page + " records successfully.")
    time.sleep(5)


def page_img_spider(url):
    ''' 爬取当前url的图片信息 '''
    html_comments = get_html_comments(url)
    page = get_html_page(html_comments)
    img_comments, hash_key = get_img_comments(html_comments)
    img_info = []
    for img_comment in img_comments:
        img_id = get_img_id(img_comment)
        img_url = get_img_url(img_comment, hash_key)
        img_oo = get_img_oo(img_comment)
        img_xx = get_img_xx(img_comment)
        img_one_info = [img_id, img_url, img_oo, img_xx]
        img_info.append(img_one_info)
    return page, img_info


if __name__ == '__main__':
    check_db('jandan.db')

    # 爬取所有妹子图
    url_origin = 'http://jandan.net/ooxx'
    html_comments = get_html_comments(url_origin)
    page_origin = get_html_page(html_comments)
    for i in range(1, int(page_origin)):
        url = "http://jandan.net/ooxx/page-"+str(i)+"#comments"
        page, img_info = page_img_spider(url)
        img_meizi_sqlite(page, img_info)

    # 爬取前50页无聊图
    url_origin = 'http://jandan.net/pic'
    html_comments = get_html_comments(url_origin)
    page_origin = int(get_html_page(html_comments))
    for i in range(page_origin-50, page_origin):
        url = "http://jandan.net/pic/page-"+str(i)+"#comments"
        page, img_info = page_img_spider(url)
        img_wuliao_sqlite(page, img_info)

    distinct()
