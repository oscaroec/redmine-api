from flask import Flask, request, send_file, render_template_string
import requests
import csv

app = Flask(__name__)

# Your HTML template
HTML = '''
<!doctype html>
<html>
<head>
    <title>Generate CSV from Redmine</title>
    <script>
    function validateDates() {
        var startDate = new Date(document.getElementById('start_date').value);
        var endDate = new Date(document.getElementById('end_date').value);
        var diffTime = Math.abs(endDate - startDate);
        var diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)); 
        if (diffDays > 31) {
            alert(">31");
            return false;
        }
        return true;
    }
    </script>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
    <h1 class="mb-3">Generate CSV from Redmine Issues</h1>
    <form action="/download-csv" method="post" onsubmit="return validateDates()">
        <div class="mb-3">
            <label for="api_key" class="form-label">Enter API Key here</label>
            <input type="text" name="api_key" class="form-control" required>
        </div>
        
        <div class="mb-3">
            <label for="start_date" class="form-label">Start Date:</label>
            <input type="date" id="start_date" name="start_date" class="form-control" required>
        </div>
        <div class="mb-3">
            <label for="end_date" class="form-label">End Date:</label>
            <input type="date" id="end_date" name="end_date" class="form-control" required>
        </div>
        <br>
        <button type="submit" class="btn btn-primary">Generate and Download CSV</button>
    </form>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/download-csv', methods=['POST'])
def download_csv():
    export_issues_with_notes()
    return send_file('issues_with_notes.csv', as_attachment=True)

def fetch_issues():
    API_KEY = request.form['api_key']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    REDMINE_URL = 'https://redmine.cims.tw/'
    headers = {
        'X-Redmine-API-Key': API_KEY,
        'Content-Type': 'application/json'
    }
    issues = []
    url = f"{REDMINE_URL}/issues.json"
    params = {
        'status_id': '*',
        'created_on': f'><{start_date}|{end_date}',
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
    API_KEY = request.form['api_key']
    REDMINE_URL = 'https://redmine.cims.tw/'
    headers = {
        'X-Redmine-API-Key': API_KEY,
        'Content-Type': 'application/json'
    }
    url = f"{REDMINE_URL}/issues/{issue_id}.json?include=journals"
    response = requests.get(url, headers=headers, verify=False)
    data = response.json()
    return data['issue']

def export_issues_with_notes():
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

if __name__ == '__main__':
    app.run(debug=True)
