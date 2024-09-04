import requests
import csv

# Redmine API 的 URL 和 API 金鑰
api_key = '68624274e522eae575b0329e6b6fbf667ee9c4cf'
redmine_url = 'https://redmine.cims.tw/'

# 要查詢的專案 ID
project_id = "2"

# 設定請求的標頭
headers = {
    "X-Redmine-API-Key": api_key
}

# 每次請求返回的資料數量上限
limit = 100

# 初始化資料容器
all_issues = []

# 從第0筆開始
offset = 0

# 設定要查詢的狀態 ID 範圍（1 到 14）
status_ids = '|'.join(map(str, range(1, 15)))

try:
    # 首先取得所有狀態為 1 到 14 的 issue
    while True:
        # API 請求的 URL，包含專案 ID、status_ids、offset 和 limit 參數
        url = f"{redmine_url}/issues.json?project_id={project_id}&status_id={status_ids}&limit={limit}&offset={offset}"

        # 發送 GET 請求並忽略 SSL 驗證
        response = requests.get(url, headers=headers, verify=False)

        # 檢查回應狀態碼
        if response.status_code == 200:
            issues = response.json().get('issues', [])
            all_issues.extend(issues)
            
            # 檢查是否已經取得所有資料
            if len(issues) < limit:
                break
            
            # 更新 offset 以取得下一批資料
            offset += limit
        else:
            print(f"Failed to retrieve issues. Status code: {response.status_code}")
            break

    # 取得每個 issue 的詳細信息和 journal
    detailed_issues = []

    for issue in all_issues:
        issue_id = issue['id']
        detail_url = f"{redmine_url}/issues/{issue_id}.json?include=journals"
        detail_response = requests.get(detail_url, headers=headers, verify=False)

        if detail_response.status_code == 200:
            detailed_issue = detail_response.json().get('issue', {})
            detailed_issues.append(detailed_issue)
        else:
            print(f"Failed to retrieve issue details for issue ID {issue_id}. Status code: {detail_response.status_code}")

    # 打開 CSV 檔案寫入資料
    with open('issues_with_journals_export.csv', mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)

        # 寫入 CSV 標頭
        writer.writerow(['Issue ID', 'Subject', 'Status', 'Journal ID', 'Journal Notes', 'Journal Created On', 'Journal User'])

        # 寫入每個 issue 和其 journal 的資料
        for issue in detailed_issues:
            issue_id = issue['id']
            subject = issue['subject']
            status = issue['status']['name']
            
            journals = issue.get('journals', [])
            if journals:
                for journal in journals:
                    journal_id = journal['id']
                    journal_notes = journal.get('notes', '')
                    journal_created_on = journal['created_on']
                    journal_user = journal['user']['name']
                    writer.writerow([issue_id, subject, status, journal_id, journal_notes, journal_created_on, journal_user])
            else:
                writer.writerow([issue_id, subject, status, 'N/A', 'N/A', 'N/A', 'N/A'])

    print("All issues with journals successfully exported to issues_with_journals_export.csv with UTF-8 encoding.")
except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
