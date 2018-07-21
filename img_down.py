# -*- coding: utf-8 -*-
import os
import sqlite3
import urllib.request
import time


def pic_comments():
    conn = sqlite3.connect('jandan.db')
    # 设置下载条件
    wuliao_comments = conn.execute(
        "select * from wuliao where img_oo - img_xx > 500")
    meizi_comments = conn.execute(
        "select * from meizi where img_oo - img_xx > 200")
    conn.close
    return wuliao_comments, meizi_comments


def url_open(url):
    # 将url里面的图片读取出来
    req = urllib.request.Request(url)
    req.add_header(
        'User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:36.0) Gecko/20100101 Firefox/36.0')
    response = urllib.request.urlopen(req)
    return response.read()


def save_imgs(pic_comment):
    img_id = pic_comment[1]
    img_urls = pic_comment[2]
    img_urls = img_urls.split(',')
    i = 1
    for img_url in img_urls:
        pic_postfix = img_url.split('.')[-1]
        img_url = "http://" + img_url
        if len(img_urls) > 1:
            filename = str(img_id) + '-' + str(i) + '.' + pic_postfix
        else:
            filename = str(img_id) + '.' + pic_postfix
        i = i + 1

        if not os.path.isfile(filename):
            try:
                pic = url_open(img_url)
            except:
                continue
            try:
                with open(filename, 'wb') as f:
                    f.write(pic)
            except:
                print(filename + " could not down!")
                continue
            time.sleep(2)

        print(filename)


def download_imgs():
    folder_top = os.getcwd()
    wuliao_folder = 'wuliao'
    meizi_folder = 'meizi'
    wuliao_comments, meizi_comments = pic_comments()

    # 下载无聊图
    if not os.path.exists(wuliao_folder):
        os.mkdir(wuliao_folder)
    os.chdir(wuliao_folder)
    for wuliao_comment in wuliao_comments:
        save_imgs(wuliao_comment)
    os.chdir(folder_top)

    # 下载妹子图
    if not os.path.exists(meizi_folder):
        os.mkdir(meizi_folder)
    os.chdir(meizi_folder)
    for meizi_comment in meizi_comments:
        save_imgs(meizi_comment)
    os.chdir(folder_top)


if __name__ == '__main__':
    download_imgs()
