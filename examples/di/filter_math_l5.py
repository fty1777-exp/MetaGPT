import os
import json
import argparse
from pathlib import Path

def filter_level_5_problems(input_dir, output_dir):
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Dictionary to store the count of level 5 problems for each category
    level_5_counts = {}
    
    # Iterate over each category (subdir) in the input directory
    for category in os.listdir(input_dir):
        category_path = Path(input_dir) / category
        if category_path.is_dir():
            level_5_problems = []
            
            # Iterate over each JSON file in the category directory
            for file_name in os.listdir(category_path):
                file_path = category_path / file_name
                if file_path.suffix == '.json':
                    with open(file_path, 'r') as file:
                        data = json.load(file)
                        
                        # Check if the problem is level 5
                        if data.get("level") == "Level 5":
                            level_5_problems.append({**data, 'id': file_name.replace('.json', '')})
            
            # Write the level 5 problems to a new JSON file in the output directory
            output_file_path = Path(output_dir) / f"{category}.json"
            with open(output_file_path, 'w') as output_file:
                json.dump(level_5_problems, output_file, indent=4)
            
            # Store the count of level 5 problems for this category
            level_5_counts[category] = len(level_5_problems)
    
    # Output the number of level 5 problems for each category
    for category, count in level_5_counts.items():
        print(f"{category}: {count} level 5 problems")

def main():
    parser = argparse.ArgumentParser(description='Filter level 5 problems from MATH dataset')
    parser.add_argument('-i', '--input_dir', type=str, required=True, help='Input directory containing the dataset')
    parser.add_argument('-o', '--output_dir', type=str, required=True, help='Output directory to save the filtered problems')
    args = parser.parse_args()

    filter_level_5_problems(args.input_dir, args.output_dir)

if __name__ == "__main__":
    main()
