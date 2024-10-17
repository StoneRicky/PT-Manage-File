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

# 生成tracker站
def tracker(s):
    start_index = s.find('https://') + len('https://')
    end_index = s.find('/announce')
    if start_index < end_index:
        result = s[start_index:end_index]
        return result
    else:
        return ''
    
# 生成name
def name(s):
    start_index = s.find('') + len('')
    end_index = s.find('.')
    if start_index < end_index:
        result = s[start_index:end_index]
        return result
    else:
        return s
    
trs = conn_info.get_torrents(arguments=["name","totalSize","downloadDir","trackerList"])

trList = []

for tr in trs:
    if(tr.download_dir in StatisticDir):
        trList.append(tr.total_size)

# # 统计所有tracker
# trackerList = []
# for tr in trs:
#     trackerList.append(tracker(tr.tracker_list[0]))
# trackerList = list(set(trackerList))
# trackerList = [x for x in trackerList if x is not None and x != '']

# 按大小
# 统计所有文件
sizeList = []
for tr in trs:
    sizeList.append(tr.total_size)
sizeList = list(set(sizeList))
sizeList = [x for x in sizeList if x is not None and x != '']
# 查询某个tracker所有的做种
selectTracker = 'tracker2.leaves.red'

selectsizeList = []
for tr in trs:
    if(selectTracker == tracker(tr.tracker_list[0])):
        selectsizeList.append(tr.total_size)
selectsizeList = list(set(selectsizeList))
selectsizeList = [x for x in selectsizeList if x is not None and x != '']

diffSizes = list(set(sizeList) ^ set(selectsizeList))

# 按名称
nameList = []
for tr in trs:
    # print(name(tr.name))
    nameList.append(name(tr.name))
nameList = list(set(nameList))
nameList = [x for x in nameList if x is not None and x != '']

selectNameList = []
for tr in trs:
    if(selectTracker == tracker(tr.tracker_list[0])):
        # print(tr.name,tr.total_size)
        selectNameList.append(name(tr.name))
selectNameList = list(set(selectNameList))
selectNameList = [x for x in selectNameList if x is not None and x != '']

diffNames = list(set(nameList) ^ set(selectNameList))
print(diffNames)
# for tr in trs:
#     if('Shaolin.Soccer' in tr.name):
#         print(tr.total_size,tracker(tr.tracker_list[0]),tr.name)

print('按大小：')
# reverse True 正序 False 倒序
diffSizes.sort(reverse=True)
for diff in diffSizes:
    for tr in trs:
            if(diff == tr.total_size):
                trName = tr.name
                # 为了对齐，填充空格
                sizeDisplay = round(tr.total_size/1024/1024/1024,2)
                space = ''
                if(sizeDisplay < 100):
                    space = ' '
                if(sizeDisplay < 10):
                    space = '  '
                size = str("{:.2f}".format(sizeDisplay))
                print(Fore.BLUE + space + size + 'G',Fore.RESET + trName , tr.total_size)
                break


print('按名称：')
for diff in diffNames:
    for tr in trs:
            if(diff in tr.name):
                trName = tr.name
                # 为了对齐，填充空格
                sizeDisplay = round(tr.total_size/1024/1024/1024,2)
                space = ''
                if(sizeDisplay < 100):
                    space = ' '
                if(sizeDisplay < 10):
                    space = '  '
                size = str("{:.2f}".format(sizeDisplay))
                print(Fore.GREEN + space + size + 'G',Fore.RESET + trName , tr.total_size)
                break

listContent = ''

# most_common实现排序后转化为list
# cnts = Counter(trList).most_common()
# for cnt in cnts:
#     if(cnt[1] > miniCount):
#         trName = ''
#         for tr in trs:
#             if(tr.total_size == cnt[0]):
#                 trName = tr.name
#                 break
#         # 为了对齐，填充空格
#         sizeDisplay = round(cnt[0]/1024/1024/1024,2)
#         space = ''
#         if(sizeDisplay < 100):
#             space = ' '
#         if(sizeDisplay < 10):
#             space = '  '
#         count = str(cnt[1])
#         size = str("{:.2f}".format(sizeDisplay))
#         print(Fore.GREEN + count,Fore.BLUE + space + size + 'G',Fore.RESET + trName)
        # listContent = listContent + '<font color="#00CD00">' + count + '</font> ' + space + '<font color="#0000CD">' + size + 'G</font> ' + trName + '\n'


# api = 'https://iyuu.cn/'+ IyuuToken +'.send'
# title = 'TR做种统计'
# content = '统计路径：' + StatisticDir + '\n' + '最小统计数：' + str(miniCount) + '\n' + listContent
# data = {
# 		    'text':title,
# 		    'desp':content
# 		}
# req = requests.post(api,data = data)