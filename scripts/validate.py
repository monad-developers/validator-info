#!/usr/bin/env python3
import json
import os
import sys

import requests
from staking_sdk_py.callGetters import call_getter
from web3 import Web3


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
    for key, example_value in example.items():
        if key not in test_data:
            print(f"❌ Missing field: '{key}'")
            ok = False
            continue
        test_value = test_data[key]
        if type(test_value) is not type(example_value):
            print(
                f"❌ Type mismatch for '{key}': expected {type(example_value).__name__}, got {type(test_value).__name__}"
            )
            ok = False
    # Extra keys not in example
    for key in test_data.keys():
        if key not in example:
            print(f"⚠️ Extra field not in schema: '{key}'")
    return ok


def check_logo(logo_url):
    ok = True
    if not isinstance(logo_url, str) or not logo_url.strip():
        print("❌ Invalid 'logo': field is missing or empty")
        ok = False
    if not logo_url.startswith("https://"):
        print("❌ Invalid 'logo': must start with https://")
        ok = False

    try:
        resp = requests.get(logo_url, timeout=10, stream=True)
        content_type = resp.headers.get("Content-Type", "")
        if resp.status_code != 200:
            print(f"❌ Logo URL returned HTTP {resp.status_code}")
            ok = False
        if not content_type.startswith("image/"):
            print(f"❌ Logo URL is not an image (Content-Type: {content_type})")
            ok = False
    except Exception as e:
        print(f"❌ Failed to fetch logo: {e}")
        ok = False
    return ok


def main():
    if len(sys.argv) < 2:
        print("Usage: validate.py <file_path>")
        sys.exit(1)

    file = sys.argv[1]
    basename = os.path.basename(file)
    directory = os.path.dirname(os.path.abspath(file))

    data = {}

    # --- Check 0: ensure JSON is loadable ---
    try:
        with open(file, "r") as f:
            content = f.read()
        data = json.loads(content)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON format: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to read file: {e}")
        sys.exit(1)

    network = os.path.basename(directory)
    validator_id = data.get("id")
    secp_local = data.get("secp")
    bls_local = data.get("bls")

    print(f"\n🌐 Network: {network}")
    print(f"🆔 Validator ID: {validator_id}")
    print(f"🔑 SECP: {secp_local}")
    print(f"🔑 BLS : {bls_local}\n")
    print("✅ JSON is valid")

    # --- Check: Schema check ---
    if not check_schema(data):
        print("❌ Schema check failed")
        sys.exit(1)
    else:
        print("✅ Schema and types match")

    # --- Check: 'name' field must not be empty ---
    name_value = data.get("name", "")
    if not isinstance(name_value, str) or not name_value.strip():
        print("❌ Invalid 'name': field is empty or missing")
        sys.exit(1)
    else:
        print(f"✅ Name is valid: '{name_value.strip()}'")

    # --- Check: 'logo' must point to a valid image URL ---
    logo = data.get("logo")
    if check_logo(logo):
        print("✅ Logo is valid")
    else:
        print(f"❌ Logo {logo} check failed")
        sys.exit(1)

    # --- Check: on-chain keys must match payload keys
    secp_chain, bls_chain = get_validator_keys(validator_id, network)
    if secp_chain != secp_local:
        print(f"❌ SECP mismatch:\n   local={secp_local}\n   chain={secp_chain}")
        sys.exit(1)
    else:
        print("✅ SECP key matches on-chain value")
    if bls_chain != bls_local:
        print(f"❌ BLS mismatch:\n   local={bls_local}\n   chain={bls_chain}")
        sys.exit(1)
    else:
        print("✅ BLS key matches on-chain value")

    # --- Check: filename must match "<secp>.json"
    expected_filename = f"{secp_local}.json"
    if basename != expected_filename:
        print(f"❌ Filename mismatch: expected '{expected_filename}', got '{basename}'")
        sys.exit(1)
    else:
        print("✅ Filename matches secp key")

    print("\n🎉 Validation successful!")


if __name__ == "__main__":
    main()
