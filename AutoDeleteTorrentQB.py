import qbittorrentapi
import time
import requests
from colorama import Fore

# 种子类

# 用于print输出
class Torrent:
    
    def __init__(self,name,size,lastActiveTime,aveUpSpeed,upSpeed,tag):
        self.name = Fore.GREEN + name
        self.size = Fore.BLUE + str(round(size/1024/1024/1024,2)) + Fore.RESET + "G"
        self.lastActiveTime = Fore.BLUE + str(round((lastActiveTime)/60)) + Fore.RESET + "min"
        self.aveUpSpeed = Fore.BLUE + str(round(upSpeed/1024)) + Fore.RESET + "(" + str(round(aveUpSpeed/1024)) + ")" + "k/s"
        self.tag = Fore.BLUE + tag
    
    def getPrint(self):
        I = Fore.RED + " | "
        print(self.name + '   ' + self.size + I + self.lastActiveTime + I + self.aveUpSpeed + I +self.tag)

# 用于发送微信通知
class TorrentStr:
    
    def __init__(self,name,size,lastActiveTime,aveUpSpeed,upSpeed,tag):
        self.name = '- ' + name.replace('[','\\[').replace(']','\\]')
        self.size = '**' + str(round(size/1024/1024/1024,2)) + '**' + "G"
        self.lastActiveTime = '**' + str(round((lastActiveTime)/60)) + '**' + "min"
        self.aveUpSpeed = '**' + str(round(upSpeed/1024)) + '**' + "(" + str(round(aveUpSpeed/1024)) + ")" + "k/s"
        self.tag = '**' + tag + '**'
    
    def getStr(self):
        I = " | "
        return (self.name + ' \n\n     (' + self.size + I + self.lastActiveTime + I + self.aveUpSpeed + I + self.tag +')\n\n\n\n')
        
    
        
    
    
##########手动填写区域
# 应当改为读取配置文件
# 基本信息

# conn_info = dict(
# host="192.168.0.20",
# port=8088,
# # username="admin",
# # password="adminadmin",
# )

conn_info = dict(
host="http://192.168.0.20",
port=8088,
username="admin",
password="adminadmin",
)


##########执行逻辑

qbt_client = qbittorrentapi.Client(**conn_info)

# 获取列表
trs = qbt_client.torrents_info(status_filter='completed',tag='已整理',sort='name')

# 获取当前时间
t = time.time() 

# 统计列表 目录不在download 且 （ 有2700秒未活动 或 平均速度不足100k）
trSizes = []
for tr in trs:
    p1 = Torrent(tr['name'],tr['size'],t-tr['last_activity'],tr['uploaded']/(t-tr['added_on']),tr['upspeed'],tr['tags'])
    p1.getPrint()
    upspeed = tr['uploaded']/(t-tr['added_on'])/1024
    if (('download'not in tr['save_path'])&(((t-tr['last_activity'])>2700)|(upspeed<100))):
        trSizes.append(tr['size'])
# 去重
trSizes = list(set(trSizes))

# 循环查找
deleteSizes = []

for trSize in trSizes:
    #设置i为0，如果有活动时间低于3600的种子则改为1
    i = 0
    # 总平均速度
    aveUpspeedTotal = 0
    # 瞬时总速度 
    upspeedTotal = 0
    for tr in trs:
        if trSize == tr['size']:
            # 平均速度累加
            aveUpspeedTotal = aveUpspeedTotal + tr['uploaded']/(t-tr['added_on'])/1024
            # 瞬时速度累加
            upspeedTotal = upspeedTotal + tr['upspeed']/1024
            # 白名单判断-1，符合条件继续存在 2700秒内有活动或者同种上传速度共计超过100k/s，可继续存活
            if (((t-tr['last_activity'])<2700) & (aveUpspeedTotal>100)):
                i = 1
            
    # 白名单判断-2，如果当前仍在上传且上传速度能达到200k/s，可继续存活
    if(upspeedTotal > 200):
        i = 1
    #如果i保持0，即同大小的种子无一合格，则可以被删
    if i == 0:
        deleteSizes.append(trSize)

deleteInfo = ''

deleteHashes = []
print("删种列表：")
for deleteSize in deleteSizes:
    for tr in trs:
        if deleteSize == tr['size']:
            deleteHashes.append(tr['hash'])
            
            # print输出
            p1 = Torrent(tr['name'],tr['size'],t-tr['last_activity'],tr['uploaded']/(t-tr['added_on']),tr['upspeed'],tr['tags'])
            p1.getPrint()
            
            # iyuu通知输出
            p2 = TorrentStr(tr['name'],tr['size'],t-tr['last_activity'],tr['uploaded']/(t-tr['added_on']),tr['upspeed'],tr['tags'])
            deleteInfo = deleteInfo + p2.getStr()
            
            # 增加tag，强制汇报
            qbt_client.torrents_add_tags(tags='计划删除',torrent_hashes=tr['hash'])
            qbt_client.torrents_reannounce(torrent_hashes=tr['hash'])


delTag = input("确认删除？")

if(delTag =="1"):
    for deleteHash in deleteHashes:
        qbt_client.torrents_delete(delete_files='true',torrent_hashes=deleteHash)
    print("删除")
    
else:
    print("不删了")

api = 'https://iyuu.cn/xxxx.send'
title = '删种任务执行完成'
content = '实际删除文件' + str(len(deleteSizes)) + '个，大小' + str(round(sum(deleteSizes)/1024/1024/1024,2)) + 'G\n\n' + deleteInfo
data = {
		    'text':title,
		    'desp':content
		}
req = requests.post(api,data = data)
