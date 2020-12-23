# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import hashlib
import re
import base64
import os
import sqlite3
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


def page_source(url):
    ''' 读取网页 '''
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Firefox(options=options)
    driver.get(url)
    time.sleep(3)
    html = driver.page_source
    driver.quit()
    return html


def get_page_number(html):
    ''' 得到当前页码 '''
    pattern = re.compile('<span class="current-comment-page">\[(.*?)\]</span>')
    try:
        page_number = re.findall(pattern, html)[0]
    except:
        return
    return page_number


def get_next_page_url(html):
    ''' 得到下一页网页地址 '''
    pattern = re.compile(
        '<a title="Older Comments" href="//(.*?)" class="previous-comment-page">')
    try:
        next_page_url = "http://{}".format(re.findall(pattern, html)[0])
    except:
        return
    return next_page_url


def get_img_comments(html):
    ''' 将jandan页面内容以图片内容划分，热榜是50个，无聊和妹子是25个 '''
    pattern = re.compile(
        '<span class="righttext">((?:.|\n)*?)<a href="javascript:;" class="tucao-btn"')
    img_comments = re.findall(pattern, html)
    return img_comments


def get_img_id(img_comment):
    ''' 获取当前图片内容的id '''
    pattern = re.compile('<a href="/t/(.*?)"')
    img_id = re.findall(pattern, img_comment)
    return img_id[0]


def get_img_url(img_comment):
    ''' 获取当前图片内容的url,其中多个链接以,链接 '''
    img_url = ""
    pattern = re.compile('<a href="//(.*?)" target="_blank" class')
    img_array = re.findall(pattern, img_comment)
    for i in img_array:
        img_url = img_url + "," + i
    img_url = img_url[1:]
    return img_url


def get_img_oo(img_comment):
    ''' 获取当前图片内容的oo '''
    pattern = re.compile('OO</a> \[<span>(.*?)</span>')
    try:
        img_oo = re.findall(pattern, img_comment)[0]
    except:
        img_oo = 0
    return img_oo


def get_img_xx(img_comment):
    ''' 获取当前图片内容的xx '''
    pattern = re.compile('XX</a> \[<span>(.*?)</span>')
    try:
        img_xx = re.findall(pattern, img_comment)[0]
    except:
        img_xx = 0
    return img_xx


def get_page_info(html):
    ''' 当前页面的页码、下一页链接地址，以及所有图片的id,url,oo,xx数据 '''
    imgs = get_img_comments(html)
    page_number = get_page_number(html)
    next_page_url = get_next_page_url(html)
    img_info = []
    for i in imgs:
        img_one_info = [get_img_id(i), get_img_url(
            i), get_img_oo(i), get_img_xx(i)]
        img_info.append(img_one_info)
    return img_info, page_number, next_page_url


def distinct():
    ''' 清除重复图片纪录，只保留最小id的那条数据，以url为判断重复图片的依据。 '''
    conn = sqlite3.connect('jandan.db')
    # 清除所有重复id的数据，保留最早纪录。
    conn.execute(
        "delete from wuliao where rowid not in(select min(rowid) from wuliao group by img_url);"
    )
    conn.execute(
        "delete from meizi where rowid not in(select min(rowid) from meizi group by img_url);"
    )
    conn.commit()
    conn.close()


def check_db(db_name):
    ''' 检查是否有sqlite数据库，如果没有则创建一个新jandan.db数据库。 '''
    if not os.path.isfile(db_name):
        conn = sqlite3.connect(db_name)
        # 创建妹子图表
        conn.execute(
            "CREATE TABLE `meizi` (`id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, `img_id` INTEGER DEFAULT 0, `img_url`	TEXT NOT NULL,`img_oo` INTEGER NOT NULL DEFAULT 0, `img_xx` INTEGER NOT NULL DEFAULT 0, `datetime` TEXT DEFAULT CURRENT_TIMESTAMP);"
        )
        # 创建无聊图表
        conn.execute(
            "CREATE TABLE `wuliao` (`id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, `img_id` INTEGER DEFAULT 0, `img_url`	TEXT NOT NULL,`img_oo` INTEGER NOT NULL DEFAULT 0, `img_xx` INTEGER NOT NULL DEFAULT 0, `datetime` TEXT DEFAULT CURRENT_TIMESTAMP);"
        )
        conn.commit()
        conn.close()


def img_wuliao_sqlite(page_number, img_info):
    ''' 将无聊图图片信息插入到jandan数据库wuliao表格中 '''
    conn = sqlite3.connect('jandan.db')
    cursor = conn.cursor()
    for img_one_info in img_info:
        cursor.execute("select id from wuliao where img_id=?",
                       (img_one_info[0], ))
        values = cursor.fetchone()
        try:
            value = values[0]
        except Exception:
            value = None
        if value is None:
            conn.execute(
                "INSERT INTO wuliao (img_id,img_url,img_oo,img_xx) VALUES (?,?,?,?)",
                img_one_info)
        else:
            cursor.execute(
                'UPDATE wuliao SET img_id=?,img_url=?,img_oo=?,img_xx=? WHERE id = ?',
                (img_one_info[0], img_one_info[1], img_one_info[2],
                 img_one_info[3], value))
    conn.commit()
    conn.close()
    print("wuliao " + page_number + " records successfully.")


def img_meizi_sqlite(page_number, img_info):
    ''' 将妹子图图片信息插入到jandan数据库meizi表格中 '''
    conn = sqlite3.connect('jandan.db')
    cursor = conn.cursor()
    for img_one_info in img_info:
        cursor.execute("select id from meizi where img_id=?",
                       (img_one_info[0], ))
        values = cursor.fetchone()
        try:
            value = values[0]
        except Exception:
            value = None
        if value is None:
            conn.execute(
                "INSERT INTO meizi (img_id,img_url,img_oo,img_xx) VALUES (?,?,?,?)",
                img_one_info)
        else:
            cursor.execute(
                'UPDATE meizi SET img_id=?,img_url=?,img_oo=?,img_xx=? WHERE id = ?',
                (img_one_info[0], img_one_info[1], img_one_info[2],
                 img_one_info[3], value))
    conn.commit()
    conn.close()
    print("meizi " + page_number + " records successfully.")


if __name__ == '__main__':
    check_db('jandan.db')

    # 下载热榜
    url = "http://jandan.net/top"
    html = page_source(url)
    img_info, page_number, next_page_url = get_page_info(html)
    img_wuliao_sqlite('热榜', img_info)

    # 下载无聊图
    url = "http://jandan.net/pic"
    html = page_source(url)
    img_info, page_number, next_page_url = get_page_info(html)
    img_wuliao_sqlite(page_number, img_info)
    while (next_page_url is not None or int(page_number) >= 100):
        html = page_source(next_page_url)
        img_info, page_number, next_page_url = get_page_info(html)
        img_wuliao_sqlite(page_number, img_info)

     # 下载妹子图
    url = "http://jandan.net/ooxx"
    html = page_source(url)
    img_info, page_number, next_page_url = get_page_info(html)
    img_meizi_sqlite(page_number, img_info)
    while (next_page_url is not None or int(page_number) >= 50):
        html = page_source(next_page_url)
        img_info, page_number, next_page_url = get_page_info(html)
        img_meizi_sqlite(page_number, img_info)

    distinct()
