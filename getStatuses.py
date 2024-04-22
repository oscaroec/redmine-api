import requests

# 設定你的 Redmine 信息
api_key = '68624274e522eae575b0329e6b6fbf667ee9c4cf'
redmine_url = 'https://redmine.cims.tw/'

# 设置请求的头部，包括 API 密钥
headers = {
    'X-Redmine-API-Key': api_key
}

# 构建请求的 URL
url = f'{redmine_url}/issue_statuses.xml'


# 发送 GET 请求
response = requests.get(url, headers=headers, verify=False)

# 检查请求是否成功
if response.status_code == 200:
    print("请求成功!")
    # 打印返回的 XML 数据
    print(response.text)
else:
    print(f"请求失败，状态码：{response.status_code}")