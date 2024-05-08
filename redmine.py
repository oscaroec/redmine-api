import requests
import csv

# 設定你的 Redmine 信息
API_KEY = '68624274e522eae575b0329e6b6fbf667ee9c4cf'
REDMINE_URL = 'https://redmine.cims.tw/'

# 配置 API 頭部
headers = {
    'X-Redmine-API-Key': API_KEY,
    'Content-Type': 'application/json'
}

def fetch_issues():
    """ 從 Redmine 獲取所有議題列表 """
    
    url = f"{REDMINE_URL}/issues.json"
    params = {
        'created_on': '><2024-04-01|2024-04-30',  # YYYY-MM-DD|YYYY-MM-DD
        'status_id': '*',
        'limit': 100,  # 每次請求的最大議題數量
        'offset': 0   # 分頁的起始點
    }

    all_issues = []

    while True:
        response = requests.get(url, headers=headers, params=params, verify=False)
        data = response.json()
        issues = data.get('issues', [])
        all_issues.extend(issues)

        # 檢查是否還有更多數據
        if len(issues) < params['limit']:
            break  # 如果返回的議題數少於限制值，則停止循環

        # 更新 offset 以獲取下一頁數據
        params['offset'] += params['limit']

    return all_issues

def fetch_issue_details(issue_id):
    """ 獲取單一議題的詳細資料，包括日誌記錄 """
    url = f"{REDMINE_URL}/issues/{issue_id}.json?include=journals"
    response = requests.get(url, headers=headers, verify=False)
    data = response.json()
    return data['issue']

def export_issues_with_notes():
    """ 將議題和相關的日誌記錄匯出到 CSV 文件 """
    issues = fetch_issues()
    with open('issues_with_notes.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Issue ID','Project Name','Created On', 'Journal ID', 'Note', 'Status'])

        for issue in issues:
            issue_details = fetch_issue_details(issue['id'])
            project_name = issue['project']['name']
            
            for journal in issue_details.get('journals', []):
                if 'notes' in journal and journal['notes'].strip():
                    for detail in journal.get('details', []):
                        name = detail.get('name', 'Unknown')
                        new_value = detail.get('new_value', 'Unknown')
                        if name == 'status_id' and new_value == '4':    
                            writer.writerow([issue['id'], project_name, issue['created_on'], journal['id'], journal['notes'], new_value])                  

# 執行匯出功能
export_issues_with_notes()
