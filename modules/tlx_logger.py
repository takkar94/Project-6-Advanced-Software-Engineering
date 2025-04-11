import os
import csv

def save_tlx_result(result: dict, filename: str = "tlx_results.csv"):
    headers = ["Mental", "Physical", "Temporal", "Performance", "Effort", "Frustration"]
    
    file_exists = os.path.isfile(filename)
    with open(filename, "a", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)

        if not file_exists:
            writer.writeheader()
        writer.writerow({key: result.get(key, "") for key in headers})
