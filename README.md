# validator-info

This repository serves as a standard directory for validators to publish their information.

To contribute:

1. Fork this repository.
1. Add a new JSON file named `<SECP_KEY>.json`.
1. Ensure the file follows the format shown in the [example file](example/000000000000000000000000000000000000000000000000000000000000000000.json).
1. Open a pull request (PR) with your changes.
1. Make sure the branch is (re)based on `main` branch.
1. Verify the Github checks are passing.
1. Share the PR link in the designated Discord channel for review.

⚠️ Note: PRs that are not shared via Discord will not be reviewed.

## Schema

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | integer | yes | Validator ID on-chain |
| `name` | string | yes | Display name |
| `secp` | string | yes | SECP public key (66-char hex); must match filename |
| `bls` | string | yes | BLS public key (96-char hex) |
| `website` | string | yes | Validator website URL |
| `description` | string | yes | Short description of the validator |
| `x` | string | yes | X (Twitter) profile URL |
| `logo` | string | no | HTTPS URL to a logo image |
| `registration_date` | string | yes | Date of on-chain registration (`YYYY-MM-DD`) |
| `decommissioned` | boolean | yes | `true` if the validator is no longer active |
| `vdp` | boolean | yes | `true` if the validator participates in the Validator Delegation Program |
