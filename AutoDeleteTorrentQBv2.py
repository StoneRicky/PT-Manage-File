import qbittorrentapi
import time
import requests
import configparser
# import TorrentEntity
from func_timeout import FunctionTimedOut, func_timeout
from colorama import Fore

# 种子类
class TorrentEntity:

    def __init__(self):
        pass
    
    # 文件名 
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self,value):
        self._name = value
    
    # 大小
    @property
    def size(self):
        return self._size
    
    @size.setter
    def size(self,value):
        self._size = str(round(value/1024/1024/1024,2)) + "G"
    
    # 上次活跃时间
    @property
    def lastActiveTime(self):
        return self._lastActiveTime
    
    @lastActiveTime.setter
    def lastActiveTime(self,value):
        self._lastActiveTime = str(round((value)/60)) + "min"
    
    # 上传大小
    @property
    def uploadedSize(self):
        return self._uploadedSize
    
    @uploadedSize.setter
    def uploadedSize(self,value):
        self._uploadedSize = str(round(value/1024/1024/1024,3)) + "G"
    
    # 添加时间 
    @property
    def addTime(self):
        return self._addTime
    
    @addTime.setter
    def addTime(self,value):
        self._addTime = str(round((t-value)/60))  + "min"
    
    # 上传速度
    @property
    def upSpeed(self):
        return self._upSpeed
    
    @upSpeed.setter
    def upSpeed(self,value):
        self._upSpeed = str(round(value/1024))  + "k/s"
    
    # 标签
    @property
    def tag(self):
        return self._tag
    
    @upSpeed.setter
    def tag(self,value):
        self._tag = value
    
    # 平均上传速度
    @property
    def aveUpSpeed(self):
        return self._aveUpSpeed
    
    def countAveUpSpeed(self,uploaded,addon):
        self._aveUpSpeed = str(round((uploaded/(t-addon))/1024)) + "k/s"
       
# 用于print输出
class TorrentPrint:
    # __init__是构造方法，在实例化时自动执行
    # self是实例本身，调用时不用传递
    def __init__(self,torrent):
        self.name = Fore.GREEN + torrent.name
        self.size = Fore.BLUE + torrent.size + Fore.RESET
        self.lastActiveTime = Fore.BLUE + torrent.lastActiveTime + Fore.RESET 
        self.uploadedSize = Fore.BLUE + torrent.uploadedSize + Fore.RESET 
        self.aveUpSpeed = Fore.BLUE + torrent.upSpeed + Fore.RESET + "(" + torrent.aveUpSpeed + ")"
        self.tag = Fore.BLUE + torrent.tag
    
    def getPrint(self):
        I = Fore.RED + " | "
        print(self.name + '(' + self.size + ')   '+ self.lastActiveTime + I + self.uploadedSize + I +self.aveUpSpeed + I + self.tag)

# 用于发送微信通知
class TorrentNotice:
    
    def __init__(self,torrent):
        self.name = '- ' + torrent.name.replace('[','\\[').replace(']','\\]')
        self.size = '**' + torrent.size + '**'
        self.addTime = '已添加时间：**' + torrent.addTime + '**'
        self.lastActiveTime = '距上次活跃时间：**' + torrent.lastActiveTime + '**'
        self.uploadedSize = '已上传大小：**' + torrent.uploadedSize + '**'
        self.nowUpSpeed = '当前上传速度：**' + torrent.upSpeed + '**'
        self.aveUpSpeed = '平均上传速度：**' + torrent.aveUpSpeed + '**' 
        self.tag = '标签：**' + torrent.tag + '**'
    
    def getStr(self):
        I = " | "
        return (self.name + '('  + self.size + ') \n\n '+ self.addTime + '\n ' + self.lastActiveTime + '\n ' + self.uploadedSize + '\n ' + self.nowUpSpeed  + '\n ' + self.aveUpSpeed + '\n ' + self.tag +'\n\n\n\n')

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
completed = int(config.get('AutoDelete', 'completed'))
HRTime = 8 * 3600
farmTag = 'Redleaves'

# IyuuToken
IyuuToken = config.get('IYUU', 'token')



##########执行逻辑

qbt_client = qbittorrentapi.Client(**conn_info)

# 获取条件搜索列表
allTrs = qbt_client.torrents_info()

trs = qbt_client.torrents_info(status_filter='completed',tag='已整理',sort='name')


downloadTrs = []
if(completed == 1):
    downloadTrs = qbt_client.torrents_info(status_filter='downloading',tag='已整理',sort='name')


# 获取当前时间
t = time.time() 

# 统计目录内的文件
trSizes = []
for tr in trs:
    if (tr['save_path'] in deletePath):
        trSizes.append(tr['size'])
# 去重
trSizes = list(set(trSizes))


# 统计目录内的文件
downloadTrSizes = []
for tr in downloadTrs:
    if (tr['save_path'] in deletePath):
        trSizes.append(tr['size'])
# 去重
downloadTrSizes = list(set(trSizes))


# 循环查找
deleteSizes = []

# 已完成的判断
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

# 下载中的判断
for trSize in downloadTrSizes:
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

    
    # 白名单判断1，符合条件继续存在活动或者同种上传速度共计超过100k/s，可继续存活
    if (aveUpspeedTotal > singleSpeed):
        whiteStatus = 1
                
    # 白名单判断2，如果当前仍在上传且上传速度能达到200k/s，可继续存活
    if(upspeedTotal > groupSpeed):
        whiteStatus = 1
        
    #如果i保持0，即同大小的种子无一合格，则可以被删
    if whiteStatus == 0:
        deleteSizes.append(trSize)

deleteInfo = ''

# 去重
deleteSizes = list(set(deleteSizes))

deleteHashes = []
print("删种列表：")

# 辅种失败状态不为'completed'，但需要一并删除

sizeCount = 0

for deleteSize in deleteSizes:
    for tr in allTrs:
        if deleteSize == tr['size']:
            deleteHashes.append(tr['hash'])
            
            torrent = TorrentEntity()
            torrent.name = tr['name']
            torrent.size = tr['size']
            torrent.lastActiveTime = t-tr['last_activity']
            torrent.uploadedSize = tr['uploaded']
            torrent.addTime = tr['added_on']
            torrent.upSpeed = tr['upspeed']
            torrent.tag = tr['tags']
            torrent.countAveUpSpeed(tr['uploaded'],tr['added_on'])
            # print输出
            p1 = TorrentPrint(torrent)
            p1.getPrint()
            
            # iyuu通知输出
            p2 = TorrentNotice(torrent)
            deleteInfo = deleteInfo + p2.getStr()
            
            # 上传累加
            sizeCount  = sizeCount + tr['uploaded']
            
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
    print("删除操作已完成")
    
else:
    print("删除操作已取消")

api = 'https://iyuu.cn/'+ IyuuToken +'.send'
title = '删种' +str(len(deleteSizes)) + '|' + str(round(sum(deleteSizes)/1024/1024/1024,2)) + 'G|上传:'+str(round(sizeCount/1024/1024/1024,2)) + 'G'
content = '实际删除文件' + str(len(deleteSizes)) + '个，大小' + str(round(sum(deleteSizes)/1024/1024/1024,2)) + 'G\n\n' + deleteInfo
data = {
		    'text':title,
		    'desp':content
		}
req = requests.post(api,data = data)
