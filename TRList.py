import configparser
from transmission_rpc import Client
from collections import Counter
from colorama import Fore
import requests

# 读取配置文件
config = configparser.ConfigParser()
config.read("general.config", encoding="utf-8")

# 基础信息
conn_info = Client(
    host = config.get('TR', 'host'),
    port = config.get('TR', 'port'),
    username = config.get('TR', 'username'),
    password = config.get('TR', 'password'),
)
# 统计路径
StatisticDir = config.get('ListCount', 'statisticDir')
# 最小统计数量
miniCount = int(config.get('ListCount', 'miniCount'))
# IyuuToken
IyuuToken = config.get('IYUU', 'token')


trs = conn_info.get_torrents(arguments=["name","totalSize","downloadDir"])

trList = []

for tr in trs:
    if(tr.download_dir in StatisticDir):
        trList.append(tr.total_size)

listContent = ''

# most_common实现排序后转化为list
cnts = Counter(trList).most_common()
for cnt in cnts:
    if(cnt[1] > miniCount):
        trName = ''
        for tr in trs:
            if(tr.total_size == cnt[0]):
                trName = tr.name
                break
        # 为了对齐，填充空格
        sizeDisplay = round(cnt[0]/1024/1024/1024,2)
        space = ''
        if(sizeDisplay < 100):
            space = ' '
        if(sizeDisplay < 10):
            space = '  '
        count = str(cnt[1])
        size = str("{:.2f}".format(sizeDisplay))
        print(Fore.GREEN + count,Fore.BLUE + space + size + 'G',Fore.RESET + trName)
        listContent = listContent + '<font color="#00CD00">' + count + '</font> ' + space + '<font color="#0000CD">' + size + 'G</font> ' + trName[:25] + '…\n'


api = 'https://iyuu.cn/'+ IyuuToken +'.send'
title = 'TR做种统计'
content = '统计路径：' + StatisticDir + '\n' + '最小统计数：' + str(miniCount) + '\n' + listContent
data = {
		    'text':title,
		    'desp':content
		}
req = requests.post(api,data = data)