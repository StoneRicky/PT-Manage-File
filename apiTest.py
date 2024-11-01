from tabulate import tabulate
import requests

headers = ["Name", "Age", "Occupation"]
data = []
tr1 = ["Alice", 28, "Engineer"]
tr2 = ["Bob", 24, "Designer"]
data.append(tr1)
data.append(tr2)
info = tabulate(data, headers=headers, tablefmt="simple")
info = info.replace(' ','&nbsp;')
print('a')
print(info)
api = 'https://iyuu.cn/'+ 'xxx' +'.send'
title = '删种详情'
content = info
print(title)
print(content)
data = {
		'text':title,
		'desp':content
	}
req = requests.post(api,data = data)

print(req.text)