import requests

# Redmine API 的 URL 和 API 金鑰
api_key = '68624274e522eae575b0329e6b6fbf667ee9c4cf'
redmine_url = 'https://redmine.cims.tw/'

# API 請求的 URL
url = f"{redmine_url}/projects.json"

# 設定請求的標頭
headers = {
    "X-Redmine-API-Key": api_key
}

try:
    # 發送 GET 請求並忽略 SSL 驗證
    response = requests.get(url, headers=headers, verify=False)
    
    # 檢查回應狀態碼
    if response.status_code == 200:
        projects = response.json().get('projects', [])
        print("Projects list:")
        for project in projects:
            print(f"- {project['name']} (ID: {project['id']})")
    else:
        print(f"Failed to retrieve projects. Status code: {response.status_code}")
except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
