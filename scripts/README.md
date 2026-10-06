# Scripts

## validate.py

Validates a single validator JSON file against the schema, on-chain keys, and logo URL.

### Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r scripts/requirements.txt
```

### Usage

```bash
# Validate a single file
python scripts/validate.py mainnet/<secp>.json

# With a custom RPC URL
MAINNET_RPC_URL=<url> python scripts/validate.py mainnet/<secp>.json
TESTNET_RPC_URL=<url> python scripts/validate.py testnet/<secp>.json
```

## validate_many.py

Runs `validate.py` on multiple validator files in parallel.

### Usage

```bash
# Validate all validators across all networks
python scripts/validate_many.py

# Validate a specific network only
python scripts/validate_many.py --network mainnet
python scripts/validate_many.py --network testnet

# Validate specific files by path (compatible with CI file lists)
python scripts/validate_many.py mainnet/<secp>.json testnet/<secp>.json

# Increase parallelism (default: 10)
python scripts/validate_many.py --network mainnet --workers 20

# Show output for passing validators too
python scripts/validate_many.py --network mainnet --verbose
```

Failed validator output is printed at the end, after all files have been checked.

## generate_validators_json.py

Generates consolidated JSON and CSV files containing all validators from the mainnet and testnet directories.

### Usage

```bash
python3 scripts/generate_validators_json.py
```

### Output

The script generates four files in the current directory:

**JSON files:**

- `mainnet_validators.json` - All mainnet validators
- `testnet_validators.json` - All testnet validators

**CSV files:**

- `mainnet_validators.csv` - All mainnet validators
- `testnet_validators.csv` - All testnet validators

### Format

**JSON format** - Maps validator SECP keys to their names:

```json
{
  "secp_key_1": "Validator Name 1",
  "secp_key_2": "Validator Name 2"
}
```

**CSV format** - Two columns with SECP keys and names:

```csv
secp,name
secp_key_1,Validator Name 1
secp_key_2,Validator Name 2
```

If a validator's `name` field is empty or missing, the SECP key is used as the name value.
