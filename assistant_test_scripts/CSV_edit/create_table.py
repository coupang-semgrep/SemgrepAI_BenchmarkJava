import pandas as pd

# Load your main Google Sheets CSV or source CSV
input_csv_path = '/Users/erickufta/Projects/SemgrepAI_BenchmarkJava/test_case_for_scripts/CSV_edit/updated_csv_file.csv'
output_summary_path = 'rule_summary.csv'

# Read the main CSV
df = pd.read_csv(input_csv_path)

# Strip leading/trailing spaces from column names
df.columns = df.columns.str.strip()

# Debug: Print the available columns
print(f"Columns in the CSV after stripping spaces: {df.columns.tolist()}")

# Ensure necessary columns exist
required_columns = ['real vulnerability', 'identified by tool', 'pass/fail', 'rule_name']
missing_columns = [col for col in required_columns if col not in df.columns]
if missing_columns:
    raise ValueError(f"Missing required columns: {missing_columns}")

# Debug: Print unique rule names
print(f"Unique rule names: {df['rule_name'].unique()}")

# Initialize a list to collect rows for the summary DataFrame
summary_rows = []

# Group by rule_name
grouped = df.groupby('rule_name')

# Iterate through each group
for rule_name, group in grouped:
    # Ensure the rule_name is correct for each group
    print(f"Processing rule_name: {rule_name}")
    
    # Count the cases
    false_positives = group[(group['real vulnerability'] == False) & 
                            (group['identified by tool'] == True) & 
                            (group['pass/fail'] == 'fail')].shape[0]
    
    true_positives = group[(group['real vulnerability'] == True) & 
                           (group['identified by tool'] == True) & 
                           (group['pass/fail'] == 'pass')].shape[0]
    
    false_negatives = group[(group['real vulnerability'] == True) & 
                            (group['identified by tool'] == False) & 
                            (group['pass/fail'] == 'fail')].shape[0]
    
    true_negatives = group[(group['real vulnerability'] == False) & 
                           (group['identified by tool'] == False) & 
                           (group['pass/fail'] == 'pass')].shape[0]
    
    # Add the row to the list
    summary_rows.append({
        'rule_name': rule_name,
        'False Positives': false_positives,
        'True Positives': true_positives,
        'False Negatives': false_negatives,
        'True Negatives': true_negatives
    })

# Create the summary DataFrame
summary = pd.DataFrame(summary_rows)

# Save the summary to a CSV
summary.to_csv(output_summary_path, index=False)
print(f"Rule summary saved at: {output_summary_path}")
