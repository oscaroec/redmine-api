import requests
import csv
import urllib3

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Redmine API 配置
API_URL = 'https://redmine.cims.tw/'
API_KEY = '68624274e522eae575b0329e6b6fbf667ee9c4cf'
PROJECT_ID = '2'
LIMIT = 100  # 每次請求返回的資料數量上限

# 初始化資料容器
all_issues = []

# 呼叫 Redmine API 並處理分頁
def fetch_issues(project_id):
    offset = 0  # 從第0筆開始
    while True:
        url = f'{API_URL}/projects/{project_id}/issues.json'
        headers = {'X-Redmine-API-Key': API_KEY}
        params = {
            'project_id': project_id,
            'limit': LIMIT,  # 每次請求返回的資料數量上限
            'offset': offset,  # 偏移量
            'status_id': '1|2|3|4|5|6|7|8|9|10|11|12|13|14'  # 設定狀態 ID 範圍
        }

        # 忽略 SSL 憑證驗證
        response = requests.get(url, headers=headers, params=params, verify=False)

        if response.status_code == 200:
            issues = response.json().get('issues', [])
            if not issues:
                break  # 如果沒有更多資料，結束循環
            all_issues.extend(issues)  # 添加取得的資料到容器中
            offset += LIMIT  # 更新偏移量
        else:
            print(f"Error fetching issues: {response.status_code}")
            break

# 匯出到 CSV 檔案
def export_to_csv(issues, file_name='redmine_issues.csv'):
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = ['Issue ID', 'Tracker Name', 'Categories', 'Issue Description']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for issue in issues:
            writer.writerow({
                'Issue ID': issue['id'],
                'Tracker Name': issue['tracker']['name'] if 'tracker' in issue else '',
                'Categories': issue['category']['name'] if 'category' in issue else '',
                'Issue Description': issue['description']
            })

# 主程式
if __name__ == '__main__':
    fetch_issues(PROJECT_ID)
    export_to_csv(all_issues)
    print("Issues have been exported to CSV file.")
