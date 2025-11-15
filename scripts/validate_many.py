#!/usr/bin/env python3
import json
import os
import sys
import glob
import argparse

import requests
from staking_sdk_py.callGetters import call_getter
from web3 import Web3

BASE_DIR = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]


def get_rpc_url(network):
    mainnet_rpc_url = os.environ.get("MAINNET_RPC_URL")
    if network == "mainnet" and mainnet_rpc_url:
        rpc_url = mainnet_rpc_url
    else:
        rpc_url = f"https://rpc-{network}.monadinfra.com/"
    return rpc_url


def get_validator_keys(id, network):
    """Return the on-chain data for a given validator"""
    staking_contract_address = "0x0000000000000000000000000000000000001000"
    w3 = Web3(Web3.HTTPProvider(get_rpc_url(network)))
    validator_info = call_getter(w3, "get_validator", staking_contract_address, id)
    secp = validator_info[10].hex()
    bls = validator_info[11].hex()
    return secp, bls


def check_schema(test_data):
    """Ensure that test_data has same structure and value types as the example schema"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    example_file = f"{script_dir}/../example/000000000000000000000000000000000000000000000000000000000000000000.json"
    with open(example_file, "r") as f:
        example = json.load(f)

    ok = True
    output = []

    for key, example_value in example.items():
        if key not in test_data:
            output.append(f"❌ Missing field: '{key}'")
            ok = False
            continue
        test_value = test_data[key]
        if type(test_value) is not type(example_value):
            output.append(
                f"❌ Type mismatch for '{key}': expected {type(example_value).__name__}, got {type(test_value).__name__}"
            )
            ok = False
    # Extra keys not in example
    for key in test_data.keys():
        if key not in example:
            output.append(f"⚠️ Extra field not in schema: '{key}'")
    return ok, output


def check_logo(logo_url):
    ok = True
    output = []

    if not isinstance(logo_url, str) or not logo_url.strip():
        output.append("❌ Invalid 'logo': field is missing or empty")
        ok = False
    if not logo_url.startswith("https://"):
        output.append("❌ Invalid 'logo': must start with https://")
        ok = False

    try:
        resp = requests.get(logo_url, timeout=10, stream=True)
        content_type = resp.headers.get("Content-Type", "")
        if resp.status_code != 200:
            output.append(f"❌ Logo URL returned HTTP {resp.status_code}")
            ok = False
        if not content_type.startswith("image/"):
            output.append(f"❌ Logo URL is not an image (Content-Type: {content_type})")
            ok = False
    except Exception as e:
        output.append(f"❌ Failed to fetch logo: {e}")
        ok = False
    return ok, output


# filename ends with .json
def check_filename(network, filename):
    file = os.path.join(BASE_DIR, network, filename)
    basename = os.path.basename(filename)

    output = []
    is_valid = True
 
    # --- Check 0: ensure JSON is loadable ---
    try:
        with open(file, "r") as f:
            content = f.read()
        data = json.loads(content)
    except json.JSONDecodeError as e:
        output.append(f"❌ Invalid JSON format: {e}")
        return False, output
    except Exception as e:
        output.append(f"❌ Failed to read file: {e}")
        return False, output

    validator_id = data.get("id")
    secp_local = data.get("secp")
    bls_local = data.get("bls")

    output.append(f"\n🌐 Network: {network}")
    output.append(f"🆔 Validator ID: {validator_id}")
    output.append(f"🔑 SECP: {secp_local}")
    output.append(f"🔑 BLS : {bls_local}\n")
    output.append("✅ JSON is valid")

    # --- Check: Schema check ---
    schema_ok, schema_output = check_schema(data)
    if schema_ok:
        output.append("✅ Schema and types match")
    else:
        output.extend(schema_output)
        output.append("❌ Schema check failed")
        return False, output

    # --- Check: 'name' field must not be empty ---
    name_value = data.get("name", "")
    if not isinstance(name_value, str) or not name_value.strip():
        output.append("❌ Invalid 'name': field is empty or missing")
        is_valid = False
    else:
        output.append(f"✅ Name is valid: '{name_value.strip()}'")

    # --- Check: 'logo' must point to a valid image URL ---
    logo = data.get("logo")
    logo_ok, logo_output = check_logo(logo)
    if logo_ok:
        output.append("✅ Logo is valid")
    else:
        output.extend(logo_output)
        output.append(f"❌ Logo {logo} check failed")
        is_valid = False

    # --- Check: on-chain keys must match payload keys
    secp_chain, bls_chain = get_validator_keys(validator_id, network)
    if secp_chain != secp_local:
        output.append(f"❌ SECP mismatch:\n   local={secp_local}\n   chain={secp_chain}")
        is_valid = False
    else:
        output.append("✅ SECP key matches on-chain value")
    if bls_chain != bls_local:
        output.append(f"❌ BLS mismatch:\n   local={bls_local}\n   chain={bls_chain}")
        is_valid = False
    else:
        output.append("✅ BLS key matches on-chain value")

    # --- Check: filename must match "<secp>.json"
    expected_filename = f"{secp_local}.json"
    if basename != expected_filename:
        output.append(f"❌ Filename mismatch: expected '{expected_filename}', got '{basename}'")
        is_valid = False
    else:
        output.append("✅ Filename matches secp key")

    if is_valid:
        output.append("\n🎉 Validation successful!")
    return is_valid, output


def get_all_filenames(network):
    network_folder = os.path.join(BASE_DIR, network)
    filenames = sorted(os.listdir(network_folder))
    return [x for x in filenames if x.endswith('.json')]


def main():
    parser = argparse.ArgumentParser(description='Validate a validator JSON file')
    parser.add_argument('--filenames', '-f', type=str, nargs='+')
    parser.add_argument('--network', '-n', type=str, default='mainnet')
    parser.add_argument('--verbose', '-v', action='store_true')
    args = parser.parse_args()
    network = args.network
    verbose = args.verbose

    if args.filenames is None:
        filenames = get_all_filenames(network)
    else:
        filenames = args.filenames
        filenames = [f + '.json' if not f.endswith('.json') else f for f in filenames]

    problems = []
    outputs = []
    
    for filename in filenames:
        print('checking %s' % filename)
        is_valid, output = check_filename(network, filename)
        if not is_valid:
            problems.append(filename)
        if not is_valid or verbose:
            outputs.append('\n'.join(output))

    print('\n\n'.join(outputs))

    if len(problems) > 0:
        raise Exception(f"❌ Validation failed for {len(problems)} files: {' '.join(problems)}")
    else:
        print("✅ Validation successful!")



if __name__ == "__main__":
    main()
