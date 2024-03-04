import qbittorrentapi
import configparser
import requests

##########手动填写区域
# 基本信息

# 此处应该改为输入
# 种子信息
hash = input('请输入哈希值:')
# 测试文件大小 0-测试(仅统计) 1-修改
testStatus = int(input('是否真实修改文件状态？ (0-测试,仅统计 1-修改):'))
# 设置信息 0-不下载 1-正常
status = 0
if(testStatus == 1):
    status = input('请输入设置状态？(0-不下载 1-正常)：')
# 文件类型
fileTyle = input('请输入文件类型：')
# 文件包含字符串
inName = input('文件包含字符串：')
# 文件大小
fileSize = int(input('请输入最大文件大小(MB)：')) * 1024 * 1024

# 读取配置文件
config = configparser.ConfigParser()
config.read("general.config", encoding="utf-8")
# IyuuToken
IyuuToken = config.get('IYUU', 'token')
# QB服务器信息

conn_info = dict(
host = config.get('QB', 'host'),
port = config.get('QB', 'port'),
username = config.get('QB', 'username'),
password = config.get('QB', 'password'),
)

##########执行逻辑
qbt_client = qbittorrentapi.Client(**conn_info)
a = qbt_client .torrents_files(torrent_hash=hash)
# print(a)

size = 0
count = 0
#状态
statusCN = '下载'
if(status == 0):statusCN = '不下载'


for i in a:
    # print(i)
    if inName in i['name']:
            if i['name'].endswith(fileTyle):
                if (i['size'] < fileSize)&(i['name'].endswith(fileTyle)):
                    size = size + i['size']
                    count = count + 1
                    t = i['index']
                    if(testStatus == 1):
                        qbt_client .torrents_file_priority(torrent_hash=hash,file_ids=t,priority=status)
            
            # print ("文件名为{"+i['name']+"}的文件优先级已修改为["+statusCN+"]当前总大小为%.2fG\n" %(size/1024/1024/1024))

    

print("已结束,总文件%d个，大小为%.2fG\n" %(count,size/1024/1024/1024))

api = 'https://iyuu.cn/'+ IyuuToken +'.send'
title = "已结束,总文件%d个，大小为%.2fG" %(count,size/1024/1024/1024)
content = ''
data = {
		    'text':title,
		    'desp':content
		}
req = requests.post(api,data = data)
