import requests
import json

# Replace these variables with your deployment slug and API token
deployment_slug = "coupang_semgrep"
token = "928b2ebbae27c2a8ae8ec8b530bd328decdf07d9ef663edc54e95ab07bc62dba"

# API endpoint and authentication
url = f"https://semgrep.dev/api/v1/deployments/{deployment_slug}/findings"
headers = {
    "Authorization": f"Bearer {token}",
}

# Parameters for the request
params = {
    "page_size": 3000,  
    "page": 0,          
    # You can add additional filters if needed, e.g., issue_type, status, etc.
}

all_findings = []

while True:
    response = requests.get(url, headers=headers, params=params)
    
    response.raise_for_status()
    
    data = response.json()

    findings = data.get('findings', [])
    all_findings.extend(findings)

    print(f"Retrieved {len(findings)} findings on page {params['page']}.")

    if len(findings) < params["page_size"]:
        break

    params["page"] += 1

# Output the total number of findings retrieved
print(f"Total findings retrieved: {len(all_findings)}")

# Save findings to a file
with open('all_findings.json', 'w') as outfile:
    json.dump(all_findings, outfile, indent=4)

print("Findings saved to all_findings.json")
