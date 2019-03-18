import requests
import json
import os,re
import threading
from queue import Queue
import random,time
import urllib.request

class Bzhan:
    def __init__(self):
        self.video = "B站-python视屏"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
        }
        self.start_url = 'https://space.bilibili.com/ajax/member/getSubmitVideos?mid=182475938&pagesize=30&tid=0&page=2&keyword=&order=pubdate'
        self.aid_url = 'https://www.bilibili.com/video/av'
        self.cid_url = 'https://api.bilibili.com/x/web-interface/view?aid='
        self.video_url = 'https://api.bilibili.com/x/player/playurl?avid=%d&cid=%d&qn=80&type=&otype=json'

    # 获取单个视频的url，aid
    def getpage(self):
        url_list = []
        res = requests.get(self.start_url,headers=self.headers).text
        dpage = json.loads(res)['data']['vlist']
        for x in dpage:
            title = x['title'].strip().replace('【小琦资源】','').replace("？",'').replace("|",'').replace('\\','')
            if "小米" in  title:
                title = "小米9SE初体验"
            # 创建一个总目录 “B站-python视频”
            if not os.path.exists(self.video):
                os.mkdir(self.video)
            # 在主目录下创建每个视频分目录
            path_title = os.path.join(self.video,title)
            if not os.path.exists(path_title):
                os.mkdir(path_title)
            # print(title)
            aid = x['aid']
            true_cid_url = self.cid_url + str(x['aid'])
            # print(true_aid_url,true_cid_url)
            url_list.append((true_cid_url,title,aid))
            # self.parseurl(true_cid_url,title,aid)
        return url_list

    # 获取单个视频下每个节点视屏cid，part（标题）
    def parseurl(self,true_cid_url,title,aid):
        url_list = []
        res = requests.get(true_cid_url,headers=self.headers).text
        html = json.loads(res)
        videos = html['data']['pages']
        for x in videos:
            page = x['page']
            cid = x['cid']
            part = x['part']
            # print(page)
            # 创建视频下节点分目录
            path_part = os.path.join(self.video,title,part)
            if not os.path.exists(path_part):
                os.mkdir(path_part)
            url = self.video_url %(aid,cid)
            url_list.append((url,path_part,part,aid,page))
            # self.get_video_url(url,path_part,part)
        return url_list

    # 获取视频的url
    def get_video_url(self,url,path_part,part,aid,page):
        response = requests.get(url,headers=self.headers).text
        html = json.loads(response)
        # 视频url
        video_url = html['data']['durl'][0]['url']
        # print(video_url)
        self.downloads(video_url,path_part,part,aid,page)

    def downloads(self,url,path_part,part,aid,page):
        referer = 'https://www.bilibili.com/video/av%d/?p=%d'%(aid,page)
        headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            # 'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1',
            'Referer': referer,
            'cookie': 'CURRENT_FNVAL=16; buvid3=D6746DBB-BF82-4092-BCD3-76D9A2BC7D6484629infoc; stardustvideo=1; LIVE_BUVID=AUTO1915507402956764; rpdid=olmkxiilwpdosswmpwixw; DedeUserID=389904562; DedeUserID__ckMd5=1e302c4346ab4bfd; SESSDATA=3a568a03%2C1554428067%2C421f7f31; bili_jct=4c36c81d5eaba2b17b0a675febe2a7be; UM_distinctid=1697c9748bb127-05942d22d65ad2-671b197c-100200-1697c9748bc35; sid=599o1fer; bp_t_offset_389904562=226215231697805000; _dfcaptcha=0fc6682edd4cc29b4aa5da9618ecff46; CURRENT_QUALITY=80; dssid=93gm0b4f0e72d7c48; dsess=BAh7CkkiD3Nlc3Npb25faWQGOgZFVEkiFTBiNGYwZTcyZDdjNDg1MDIGOwBG%0ASSIJY3NyZgY7AEZJIiUzODQwMDRkMDRlOTE0MTczMzQxOTJhYmI3OTlmMzdj%0AYQY7AEZJIg10cmFja2luZwY7AEZ7B0kiFEhUVFBfVVNFUl9BR0VOVAY7AFRJ%0AIi1mMGIzMWFjZjU0MmRlMDM2ZmFjOTU0MWNjZjY0NmJjOTk1ZGM3NjNlBjsA%0ARkkiGUhUVFBfQUNDRVBUX0xBTkdVQUdFBjsAVEkiLWJiMGUwM2Q3ZWEyZDk4%0AYTc1ODA4YmNkYmIxNzgxYWExYmI4NjA0ZTQGOwBGSSIKY3RpbWUGOwBGbCsH%0ADgKNXEkiCGNpcAY7AEYiEjU5LjU1LjIxMC4xOTk%3D%0A--359943e32f149bb306c04631762f8a38ca25e9e9; fts=1552744976'
        }
        video_name = part + '.flv'
        video_path = os.path.join(path_part,video_name)
        # print(video_path)
        if not os.path.exists(video_path):
            # response = requests.get(url,headers=headers)
            # res = response.content
            req = urllib.request.Request(url,headers=headers)
            response = urllib.request.urlopen(req)
            res = response.read()
            print("正在下载:", video_name)
            with open(video_name, 'wb')as f:
                f.write(res)
            print("下载完成:", video_name)

    def work(self):
        queue_url = Queue()
        url_list = self.getpage()
        for x in url_list:
            true_cid_url, title, aid = x
            parserutls = self.parseurl(true_cid_url, title, aid)
            for i in parserutls:
                # url, path_part, part,aid = i
                # print(i)
                queue_url.put(i)
        for x in range(10):
            t = threading.Thread(target=self.threa,args=(queue_url,))
            t.start()
            time.sleep(random.randint(1,5))

    def threa(self,queue_url):
        while True:
            if not queue_url.empty():
                url, path_part, part,aid,page = queue_url.get()
                self.get_video_url(url,path_part,part,aid,page)
                # print(url, path_part, "*******", part.aid)
            else:
                break




if __name__ == '__main__':
    bi = Bzhan()
    bi.work()