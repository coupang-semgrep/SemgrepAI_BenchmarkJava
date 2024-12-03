import json

# Paths to input and output files
api_results_path = '/Users/erickufta/Projects/SemgrepAI_BenchmarkJava/assistant_test_scripts/filter_ai_ignored_results/all_findings.json'  # Path to your API results file
semgrep_json_path = '/Users/erickufta/Projects/SemgrepAI_BenchmarkJava/scorecard_archive/original_test/semgrep.json'  # Path to the Semgrep JSON file
output_path = '/Users/erickufta/Projects/SemgrepAI_BenchmarkJava/results/semgrep.json'  # Output file path for filtered results

def load_json(file_path):
    """Load a JSON file and return its content."""
    with open(file_path, 'r') as file:
        return json.load(file)

def save_json(data, file_path):
    """Save a dictionary as a JSON file."""
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)

def filter_semgrep_json(api_results, semgrep_results):
    """Filter Semgrep JSON results based on `match_based_id` from all_findings.json and `fingerprint` from semgrep.json."""
    # Extract match_based_id values for false positives
    match_based_ids = {
        entry['match_based_id']
        for entry in api_results
        if entry.get('match_based_id') and entry.get('assistant') and entry['assistant'].get('autotriage') and entry['assistant']['autotriage'].get('verdict') == "false_positive"
    }

    print(f"Match-based IDs extracted for filtering: {match_based_ids}")
    
    filtered_results = []
    filtered_out_fingerprints = []

    # Iterate over Semgrep results
    for result in semgrep_results.get('results', []):
        # Access fingerprint from nested 'extra' field
        fingerprint = result.get('extra', {}).get('fingerprint')

        # Debugging: Print fingerprints being checked
        print(f"Checking Semgrep result fingerprint: {fingerprint}")
        if fingerprint in match_based_ids:
            print(f"Filtering out result with fingerprint: {fingerprint}")
            filtered_out_fingerprints.append(fingerprint)
        else:
            filtered_results.append(result)
    
    semgrep_results['results'] = filtered_results
    return semgrep_results, filtered_out_fingerprints

def main():
    # Load the API results and Semgrep JSON files
    api_results = load_json(api_results_path)
    semgrep_results = load_json(semgrep_json_path)
    
    # Filter the Semgrep JSON results
    filtered_semgrep, filtered_out_fingerprints = filter_semgrep_json(api_results, semgrep_results)
    
    # Save the filtered Semgrep JSON
    save_json(filtered_semgrep, output_path)
    print(f"\nFiltered Semgrep JSON saved to {output_path}")
    
    # Output filtered fingerprints and total count
    print("\nFiltered Fingerprints:")
    for fingerprint in filtered_out_fingerprints:
        print(fingerprint)
    
    print(f"\nTotal Results Filtered: {len(filtered_out_fingerprints)}")

if __name__ == '__main__':
    main()
