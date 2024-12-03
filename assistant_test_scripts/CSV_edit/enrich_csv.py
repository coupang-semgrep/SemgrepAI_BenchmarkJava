import pandas as pd
import json
import os

# Define file paths
csv_path = '/Users/erickufta/Projects/SemgrepAI_BenchmarkJava/scorecard/Benchmark_v1.2_Scorecard_for_Semgrep_PRO_v1.96.0.csv'
json_path = '/Users/erickufta/Projects/SemgrepAI_BenchmarkJava/assistant_test_scripts/CSV_edit/all_findings.json'
output_csv_path = 'updated_csv_file.csv'

# Load the CSV file
try:
    df = pd.read_csv(csv_path)
    print(f"CSV loaded successfully. Columns: {df.columns.tolist()}")
except Exception as e:
    print(f"Error loading CSV: {e}")
    exit()

# Load the JSON file
try:
    with open(json_path, 'r') as json_file:
        api_data = json.load(json_file)
    print(f"JSON loaded successfully. Total findings: {len(api_data)}")
except Exception as e:
    print(f"Error loading JSON: {e}")
    exit()

# Validate JSON structure and create a mapping of test names to ids, rule names, vulnerability classes, verdict, and reasoning
file_to_id_rule_vuln_map = {}
for finding in api_data:
    location = finding.get("location", {})
    file_path = location.get("file_path")
    finding_id = finding.get("id")
    rule_name = finding.get("rule_name")
    vulnerability_classes = finding.get("rule", {}).get("vulnerability_classes", [])
    autotriage = finding.get("assistant", {}).get("autotriage")
    
    # Safely extract verdict and reason
    verdict = autotriage.get("verdict") if autotriage else None
    reason = autotriage.get("reason") if autotriage else None
    
    if file_path and finding_id and rule_name is not None:
        # Extract the test name from the file path (e.g., "BenchmarkTest00814.java" -> "BenchmarkTest00814")
        test_name = os.path.basename(file_path).split('.')[0]
        file_to_id_rule_vuln_map[test_name] = {
            "id": finding_id,
            "rule_name": rule_name,
            "vulnerability_classes": ", ".join(vulnerability_classes) if vulnerability_classes else None,
            "verdict": verdict,
            "reason": reason
        }
    else:
        print(f"Skipping finding due to missing file_path, id, or rule_name: {finding}")

# Debug: Show a sample of the mapping
print(f"Sample of test_name to id, rule_name, vulnerability_classes, verdict, and reasoning mapping (up to 10 items):")
for key, value in list(file_to_id_rule_vuln_map.items())[:10]:
    print(f"{key}: {value}")

# Add new columns to the DataFrame, leaving blanks if not found
if '# test name' in df.columns:
    df['findings id'] = df['# test name'].map(lambda x: file_to_id_rule_vuln_map.get(x, {}).get("id") if x in file_to_id_rule_vuln_map else None)
    df['rule_name'] = df['# test name'].map(lambda x: file_to_id_rule_vuln_map.get(x, {}).get("rule_name") if x in file_to_id_rule_vuln_map else "")
    df['vulnerability_classes'] = df['# test name'].map(lambda x: file_to_id_rule_vuln_map.get(x, {}).get("vulnerability_classes") if x in file_to_id_rule_vuln_map else "")
    df['ai_triage_verdict'] = df['# test name'].map(lambda x: file_to_id_rule_vuln_map.get(x, {}).get("verdict") if x in file_to_id_rule_vuln_map else "")
    df['ai_triage_reasoning'] = df['# test name'].map(lambda x: file_to_id_rule_vuln_map.get(x, {}).get("reason") if x in file_to_id_rule_vuln_map else "")
    print(f"Mapping applied. Number of matches found: {df['findings id'].notna().sum()}")
else:
    print("CSV does not contain the '# test name' column. Please check the CSV structure.")
    exit()

# Add a new column "finding_link" based on the "findings id" column
df['finding_link'] = df['findings id'].apply(
    lambda finding_id: f"https://semgrep.dev/orgs/-/findings/{finding_id}" if pd.notna(finding_id) else None
)

# Save the updated CSV
try:
    df.to_csv(output_csv_path, index=False)
    print(f"Updated CSV saved at: {output_csv_path}")
except Exception as e:
    print(f"Error saving updated CSV: {e}")
