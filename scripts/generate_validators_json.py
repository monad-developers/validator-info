#!/usr/bin/env python3
import json
import os
import glob


def read_validators(directory):
    """Read all validator JSON files from a directory and return dict mapping secp to full validator object."""
    validators_dict = {}
    json_files = glob.glob(os.path.join(directory, "*.json"))
    
    for json_file in json_files:
        try:
            with open(json_file, "r") as f:
                data = json.load(f)
                
            # Extract secp key
            secp = data.get("secp", "")
            
            # Use secp as fallback for name if name is empty
            if not data.get("name", "").strip():
                data["name"] = secp
            
            # Map secp key to full validator object
            validators_dict[secp] = data
            
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Failed to read {json_file}: {e}")
            continue
    
    return validators_dict


def write_json(validators_dict, output_file):
    """Write validators to JSON file with secp as key and full validator object as value."""
    with open(output_file, "w") as f:
        json.dump(validators_dict, f, indent=2)
    
    print(f"✅ Generated {output_file} with {len(validators_dict)} validators")


def main():
    # Get the project root directory (parent of scripts/)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Process mainnet validators
    mainnet_dir = os.path.join(project_root, "mainnet")
    mainnet_validators = read_validators(mainnet_dir)
    mainnet_json = os.path.join(mainnet_dir, "mainnet_validators.json")
    write_json(mainnet_validators, mainnet_json)
    
    # Process testnet validators
    testnet_dir = os.path.join(project_root, "testnet")
    testnet_validators = read_validators(testnet_dir)
    testnet_json = os.path.join(testnet_dir, "testnet_validators.json")
    write_json(testnet_validators, testnet_json)


if __name__ == "__main__":
    main()
