# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
import sys
import threading
import time
from urllib import request

import requests


class DoubanPipeline(object):

    def process_item(self, item, spider):
        data = dict(item)
        # request.urlretrieve(url=data['imgurl'], filename='E://img/' + data['movie_name'] + '.jpg')
        url = data['imgurl']
        path = 'E://img/' + data['movie_name'] + '.jpg'
        t = threading.Thread(target=DoubanPipeline.download, kwargs={'url': url, 'file_path': path})
        t.setDaemon(True)
        t.start()
        # DoubanPipeline.download(url, path)
        return item

    # 屏蔽warning信息
    # requests.packages.urllib3.disable_warnings()

    def download(url, file_path):
        # 计算下载时间
        start_time = time.time()
        # 第一次请求是为了得到文件总大小
        r1 = requests.get(url, stream=True, verify=False)
        total_size = int(r1.headers['Content-Length'])

        # 判断文件是否存在
        if os.path.exists(file_path):
            # 本地已经下载的文件大小
            temp_size = os.path.getsize(file_path)
        else:
            temp_size = 0
        # 显示一下下载了多少
        print(temp_size)
        print(total_size)
        # 核心部分，从本地文件已经下载过的后面下载
        headers = {'Range': 'bytes=%d-' % temp_size}
        # 重新请求网址，加入新的请求头的
        r = requests.get(url, stream=True, verify=False, headers=headers)
        # "ab"表示追加形式写入文件
        with open(file_path, "ab") as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    temp_size += len(chunk)
                    f.write(chunk)
                    f.flush()
                    # 下载进度显示
                    done = int(50 * temp_size / total_size)
                    sys.stdout.write("\r[%s%s] %d%%" % ('█' * done, ' ' * (50 - done), 100 * temp_size / total_size))
                    sys.stdout.flush()
        print()  # 避免上面\r 回车符
        print('下载时间：%ds' % int(time.time() - start_time))
