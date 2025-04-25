# PT-Manage-File
一些用于管理PT相关的脚本  

## [general.example.config](https://github.com/StoneRicky/PT-Manage-File/blob/main/general.example.config) 
使用前，将general.example.config文件改名为general.config，并修改文件中的配置项

## [AutoDeleteTorrentQB.py](https://github.com/StoneRicky/PT-Manage-File/blob/main/AutoDeleteTorrentQB.py)  
在青龙面板自动运行的删种脚本，配合NASTOOL的刷流任务及IYUU使用，可通过爱语飞飞通知
具体方法：  
1. NASTOOL定时增加种子  
2. IYUU定时自动辅种  
3. 此脚本定时自动删种（同时删除辅种）  

## [AutoDeleteTorrentQBv2.py](https://github.com/StoneRicky/PT-Manage-File/blob/main/AutoDeleteTorrentQB.py)  
使用实体类的方式实现v1功能，方便代码可读，后续不再更新v1

## [TRList.py](https://github.com/StoneRicky/PT-Manage-File/blob/main/TRList.py)  
用于统计当前Transmission中正在做种的文件的辅种数量，按倒序排列，可通过爱语飞飞通知

## [TRAvailable.py](https://github.com/StoneRicky/PT-Manage-File/blob/main/TRAvailable.py)  
用于统计当前Transmission中可以发种或做种的列表

## [AutoTorrentSelectQB.py](https://github.com/StoneRicky/PT-Manage-File/blob/main/AutoTorrentSelectQB.py)  
批量修改文件优先级，可批量修改文件状态由“不下载”改为“正常”，用于大包拆包刷流