# jandan_spider
## 煎蛋爬虫
你可以利用本脚本爬取煎蛋网热榜、无聊图和妹子图。
2020年12月23日有效测试。

## jandan下载煎蛋网妹子图和无聊图
### 根目录
1. 运行 jandan_spider.py 将jandan网页爬到 pic.db 数据库里。
2. 运行 jandan_down.py 将符合条件的网页图片下载下来，妹子图下载在meizi文件夹里，无聊图和热榜都在wuliao文件夹里。

### 需安装软件
本爬虫使用firefox，需安装firefox和下载geckodriver。 https://github.com/mozilla/geckodriver/releases

## sqlite数据库
数据库表格里面有wuliao、meizi两个表，分别有 id, img\_id, img\_url, img\_oo, img\_xx, datetime 这6个字段。
