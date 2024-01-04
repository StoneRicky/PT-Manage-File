import configparser
from transmission_rpc import Client
from collections import Counter
from colorama import Fore

# 读取配置文件
config = configparser.ConfigParser()
config.read("general.config", encoding="utf-8")
conn_info = Client(
    host = config.get('TR', 'host'),
    port = config.get('TR', 'port'),
    username = config.get('TR', 'username'),
    password = config.get('TR', 'password'),
)

trs = conn_info.get_torrents(arguments=["name","totalSize","downloadDir"])

trList = []

for tr in trs:
    if(tr.download_dir == '/MagicSATA'):
        trList.append(tr.total_size)
        
# most_common实现排序后转化为list
cnts = Counter(trList).most_common()
for cnt in cnts:
    if(cnt[1] > 4):
        trName = ''
        for tr in trs:
            if(tr.total_size == cnt[0]):
                trName = tr.name
                break
        print(Fore.GREEN + str(cnt[1]),Fore.BLUE + str(round(cnt[0]/1024/1024/1024,2)) + 'G',Fore.RESET + trName)