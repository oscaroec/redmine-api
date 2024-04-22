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
    issues = []
    url = f"{REDMINE_URL}/issues.json"
    params = {
        'status_id': '*',  # 獲取所有狀態的議題
        'created_on': '><2024-03-01|2024-03-31',  # YYYY-MM-DD|YYYY-MM-DD
        'offset': 0
    }
    while True:
        response = requests.get(url, headers=headers, params=params, verify=False)
        data = response.json()
        issues.extend(data['issues'])
        if 'next' in data.keys():
            params['offset'] += 20
        else:
            break
    return issues

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
                        new_value = detail.get('new_value', 'Unknown')
                        if new_value == '4':
                            writer.writerow([issue['id'], project_name, issue['created_on'], journal['id'], journal['notes'], new_value])                  

# 執行匯出功能
export_issues_with_notes()
