import qbittorrentapi
import time
import requests
import configparser
from func_timeout import FunctionTimedOut, func_timeout
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

# 读取配置文件
config = configparser.ConfigParser()
config.read("general.config", encoding="utf-8")
# QB服务器信息
conn_info = dict(
host = config.get('QB', 'host'),
port = config.get('QB', 'port'),
username = config.get('QB', 'username'),
password = config.get('QB', 'password'),
)

# 删除所需参数
deletePath = config.get('AutoDelete', 'deletePath')
singleSpeed = int(config.get('AutoDelete', 'singleSpeed'))
groupSpeed = int(config.get('AutoDelete', 'groupSpeed'))
activeTime = int(config.get('AutoDelete', 'activeTime'))
HRTime = 8 * 3600
farmTag = 'Redleaves'
# IyuuToken
IyuuToken = config.get('IYUU', 'token')



##########执行逻辑

qbt_client = qbittorrentapi.Client(**conn_info)

# 获取条件搜索列表
allTrs = qbt_client.torrents_info()
trs = qbt_client.torrents_info(status_filter='completed',tag='已整理',sort='name')

# 获取当前时间
t = time.time() 

# 统计目录内的文件
trSizes = []
for tr in trs:
    # p1 = Torrent(tr['name'],tr['size'],t-tr['last_activity'],tr['uploaded']/(t-tr['added_on']),tr['upspeed'],tr['tags'])
    # p1.getPrint()
    if (tr['save_path'] in deletePath):
        trSizes.append(tr['size'])
# 去重
trSizes = list(set(trSizes))

# 循环查找
deleteSizes = []

for trSize in trSizes:
    #设置白名单状态whiteStatus为0
    whiteStatus = 0
    #设置活动状态为0
    activeStatus = 0
    # 总平均速度
    aveUpspeedTotal = 0
    # 瞬时总速度 
    upspeedTotal = 0
    for tr in allTrs:
        if trSize == tr['size']:
            # 平均速度累加
            aveUpspeedTotal = aveUpspeedTotal + tr['uploaded']/(t-tr['added_on'])/1024
            # 瞬时速度累加
            upspeedTotal = upspeedTotal + tr['upspeed']/1024
            # 确定2700秒内是否有活动
            if((t-tr['last_activity']) < activeTime):
                activeStatus = 1
    
    # 白名单判断1，符合条件继续存在活动或者同种上传速度共计超过100k/s，可继续存活
    if ((activeStatus == 1) & (aveUpspeedTotal > singleSpeed)):
        whiteStatus = 1
                
    # 白名单判断2，如果当前仍在上传且上传速度能达到200k/s，可继续存活
    if(upspeedTotal > groupSpeed):
        whiteStatus = 1
        
    #如果i保持0，即同大小的种子无一合格，则可以被删
    if whiteStatus == 0:
        deleteSizes.append(trSize)

deleteInfo = ''

deleteHashes = []
print("删种列表：")

# 获取全部列表 (辅种失败状态不为'completed'，但需要一并删除)
fullTrs = qbt_client.torrents_info()

for deleteSize in deleteSizes:
    for tr in fullTrs:
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


# 添加定时输入，超时20秒不输入，则直接删除，可适配自动执行脚本
try:
    delTag = func_timeout(20, lambda: input('确认删除？'))
except FunctionTimedOut:
    delTag = '1'

if(delTag =="1"):
    for deleteHash in deleteHashes:
        qbt_client.torrents_delete(delete_files='true',torrent_hashes=deleteHash)
    print("删完了")
    
else:
    print("不删了")

api = 'https://iyuu.cn/'+ IyuuToken +'.send'
title = '删种' +str(len(deleteSizes)) + '个(' + str(round(sum(deleteSizes)/1024/1024/1024,2)) + 'G)'
content = '实际删除文件' + str(len(deleteSizes)) + '个，大小' + str(round(sum(deleteSizes)/1024/1024/1024,2)) + 'G\n\n' + deleteInfo
data = {
		    'text':title,
		    'desp':content
		}
req = requests.post(api,data = data)
