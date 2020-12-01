from selenium import webdriver
import time
import re
import pyautogui
import os
import sqlite3


def page_source(url):
    ''' 读取网页 '''
    PROXY = "127.0.0.1:10800"
    webdriver.DesiredCapabilities.FIREFOX['proxy'] = {
        "httpProxy": PROXY,
        "ftpProxy": PROXY,
        "sslProxy": PROXY,
        "proxyType": "MANUAL",
    }
    driver = webdriver.Firefox()
    driver.get(url)
    time.sleep(10)
    html = driver.page_source
    driver.quit()
    return html


def parse_imgs(html):
    ''' 解析网页，提取出图片链接 '''
    pattern = re.compile('src="//([-a-zA-Z0-9@:%_+.~#?&//=]*)?.jpg"', re.S)
    imgs = re.findall(pattern, html)
    hd_imgs = [img.replace('tn.nozomi.la', 'i.nozomi.la') for img in imgs]
    return hd_imgs


def parse_urls(html):
    ''' 解析网页，提取出图片网址 '''
    pattern = re.compile('<a href="https://(.*?)"', re.S)
    urls = re.findall(pattern, html)
    return urls


def check_db(db_name):
    ''' 检查是否有sqlite数据库，如果没有则创建一个新imgs.db数据库。 '''
    if not os.path.isfile(db_name):
        conn = sqlite3.connect(db_name)
        # 创建torrents表格
        conn.execute("CREATE TABLE `imgs` (`id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, `url` TEXT NOT NULL, `img` TEXT NOT NULL, `datetime` TEXT DEFAULT CURRENT_TIMESTAMP);")
        conn.commit()
        conn.close()


def save_img(url):
    PROXY = "127.0.0.1:10800"
    webdriver.DesiredCapabilities.FIREFOX['proxy'] = {
        "httpProxy": PROXY,
        "ftpProxy": PROXY,
        "sslProxy": PROXY,
        "proxyType": "MANUAL",
    }
    driver = webdriver.Firefox()
    url = "https://"+url
    driver.get(url)
    driver.maximize_window()
    time.sleep(10)
    pyautogui.leftClick(x=1000, y=500)
    pyautogui.rightClick(x=1000, y=500)
    pyautogui.typewrite(['V'])
    time.sleep(1)
    pyautogui.press('enter')
    driver.quit()

def down_img(url):
    
def img_sqlite(url, img):
    ''' 将图片信息插入到数据库中 '''
    conn = sqlite3.connect('imgs.db')
    cursor = conn.cursor()
    cursor.execute("select id from imgs where url=?",
                   (url,))
    values = cursor.fetchone()
    try:
        value = values[0]
    except:
        value = None
    if value == None:
        cursor.execute(
            "INSERT INTO imgs (url,img) VALUES (?,?)", (url, img))
        print(url+" 出错。")
    else:
        print(url+" 已下载。")
    conn.commit()
    conn.close()


if __name__ == '__main__':
    check_db('imgs.db')
    # html = page_source('https://nozomi.la/search.html?q=kiyo_(kyokyo1220)#1')
    # urls = parse_urls(html)
    # imgs = parse_imgs(html)
    # for i in range(int(len(imgs))):
    #     img_sqlite(urls[i], imgs[i])


