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
    'scan_type': 'ZAP Scan',
    'minimum_severity': 'Low',
    'engagement': 5,
    'engagement_name': 'juice-shop dast scan results',
    'product_name': 'juice-shop',
    'close_old_findings': True,
    'push_to_jira': False,
    'test_title': f'ZAP Scan {int(time.time())}'
}

files = {
    'file': open(file_name, 'rb')
}

print(f"[*] Uploading ZAP report: {file_name} to DefectDojo")

response = requests.post(
    f'{os.getenv("DD_URL")}/api/v2/import-scan/',
    headers=headers,
    data=data,
    files=files
)

if response.status_code == 201:
    print(f'[+] ZAP results successfully imported: {data["test_title"]}')
else:
    print(f'[!] Failed to import ZAP results: {response.status_code} - {response.text}')
    sys.exit(1)
