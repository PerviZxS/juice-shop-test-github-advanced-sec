import requests, sys, os, time

file_name = sys.argv[1]
if not os.path.exists(file_name):
    print(f"Report file not found: {file_name}")
    sys.exit(1)

headers = {
    'Authorization': f'Token {os.getenv("DD_API_KEY")}'
}

data = {
    'active': True,
    'verified': True,
    'scan_type': 'Gitleaks Scan',   
    'minimum_severity': 'Low',
    'engagement': 2,
    'engagement_name': 'juice-shop gitleak scan results',
    'close_old_findings': True,
    "product_name": "juice-shop",
    'push_to_jira': False,
    'test_title': f'Trivy Scan {int(time.time())}'
}

files = {
    'file': open(file_name, 'rb')
}

response = requests.post(
    f'{os.getenv("DD_URL")}/api/v2/import-scan/',  
    headers=headers,
    data=data,
    files=files
)

if response.status_code == 201:
    print('GitLeaks results successfully reimported into DefectDojo')
else:
    print(f'Failed to reimport GitLeaks results: {response.status_code} - {response.text}')
