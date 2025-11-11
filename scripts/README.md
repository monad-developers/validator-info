# Scripts

## validate.py

This `validate.py` is used to verify the information for validators.

### Setup

```bash
python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Usage

```bash
source .venv/bin/activate
./validate.py ../testnet/0209ca34a0469e8bfc88de9e05953bb26cd518401c4382491793f3318c7c25c033.json
```

## generate_validators_json.py

The `generate_validators_json.py` script generates consolidated JSON files containing all validators from the mainnet and testnet directories.

### Usage

```bash
python3 scripts/generate_validators_json.py
```

### Output

The script generates two JSON files in the project root:

- `mainnet_validators.json` - All mainnet validators
- `testnet_validators.json` - All testnet validators

### Format

Each JSON file maps validator SECP keys to their names:

```json
{
  "secp_key_1": "Validator Name 1",
  "secp_key_2": "Validator Name 2"
}
```

If a validator's `name` field is empty or missing, the SECP key is used as the name value.
