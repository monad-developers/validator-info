#!/usr/bin/env python3
import csv
import json
import os
import glob


def read_validators(directory):
    """Read all validator JSON files from a directory and return dict mapping secp to name."""
    validators_dict = {}
    json_files = glob.glob(os.path.join(directory, "*.json"))
    
    for json_file in json_files:
        try:
            with open(json_file, "r") as f:
                data = json.load(f)
                
            # Extract fields
            name = data.get("name", "").strip()
            secp = data.get("secp", "")
            
            # Use secp as fallback if name is empty
            if not name:
                name = secp
            
            # Map secp key to validator name
            validators_dict[secp] = name
            
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Failed to read {json_file}: {e}")
            continue
    
    return validators_dict


def write_json(validators_dict, output_file):
    """Write validators to JSON file with secp as key and name as value."""
    with open(output_file, "w") as f:
        json.dump(validators_dict, f, indent=2)
    
    print(f"✅ Generated {output_file} with {len(validators_dict)} validators")


def write_csv(validators_dict, output_file):
    """Write validators to CSV file with secp_key and name columns."""
    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["secp_key", "name"])
        
        for secp, name in validators_dict.items():
            writer.writerow([secp, name])
    
    print(f"✅ Generated {output_file} with {len(validators_dict)} validators")


def main():
    # Get the project root directory (parent of scripts/)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Process mainnet validators
    mainnet_dir = os.path.join(project_root, "mainnet")
    mainnet_validators = read_validators(mainnet_dir)
    write_json(mainnet_validators, "mainnet_validators.json")
    write_csv(mainnet_validators, "mainnet_validators.csv")
    
    # Process testnet validators
    testnet_dir = os.path.join(project_root, "testnet")
    testnet_validators = read_validators(testnet_dir)
    write_json(testnet_validators, "testnet_validators.json")
    write_csv(testnet_validators, "testnet_validators.csv")


if __name__ == "__main__":
    main()

