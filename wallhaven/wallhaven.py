import json
import os
import re
from subprocess import call

import requests
from bs4 import BeautifulSoup

# idm程序路径
idm_path = r'D:\Programs\Internet Download Manager\IDMan.exe'

# 图片下载路径
download_path = r'D:\ProgramData\PS\爬虫'

# 获取下载文件夹里包含的文件列表
files = os.listdir(download_path)

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 '
                  'Safari/537.36 Edg/110.0.1587.63'})
with open('cookie.json') as f:
    cookie = json.load(f)
for name in cookie.keys():
    session.cookies.set(name, cookie[name])

# 主要分类，抓取网站分类功能待实现
categories = ['latest', 'hot', 'toplist', 'random']
index = 1
for category in categories:
    print(f'{index}：{category}')
    index += 1
while 1:
    choose = int(input('请输入要爬取页面的分类序号：'))

    if 0 < choose <= len(categories):
        choose = categories[choose - 1]
        print(f'已选择：{choose}')
    else:
        print('请选择正确的序号！')
    pages = int(input('请输入要爬取的页数：'))
    if 0 < pages:
        print(f'已选择{pages}页')
        break

count = 1
for page in range(pages):
    try:
        html = session.get(f'https://wallhaven.cc/{choose}?page={page + 1}')
    except requests.exceptions.RequestException as e:
        print('发生了一些连接错误！要想想增加反爬机制了！')
        print(e)
    else:
        main_html = BeautifulSoup(html.text, 'lxml')
        previews = main_html.find_all('a', class_='preview')
        for preview in previews:
            href = preview.get('href')
            try:
                image_html = requests.get(href)
            except requests.exceptions.RequestException as e:
                print('发生了一些连接错误！要想想增加反爬机制了！')
                print(e)
            else:
                bs = BeautifulSoup(image_html.text, 'lxml')
                images = bs.find('img', id='wallpaper')
                try:
                    image_url = images.get('src')
                except AttributeError:
                    print('页面缺少一些属性！不过不用担心！')
                else:
                    print(f'{count}：{image_url}')
                    file_name = re.search(r'wallhaven-\w+\.(png|jpg)', image_url).group()

                    # 判断该文件是否已下载，如果已下载则跳出循环
                    if file_name in files:
                        print(f'{file_name}：已存在')
                        continue

                    # 把图片链接添加进IDM任务队列，但不开始
                    call([idm_path, '/d', image_url, '/p', download_path, '/f', file_name, '/n', '/a'])
                    count += 1
    # 无论是否出错，最终都开始队列
    finally:
        print('开始队列')
        call([idm_path, '/s'])
