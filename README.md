# cvat-auto-backup

Automate CVAT project backups — download project exports and optionally push them to a separate GitHub repository.

Features
- Export a CVAT project using the CVAT SDK.
- Download the project backup (ZIP) to a local `SAVE_DIR`.
- Optionally extract the backup and commit it into a different GitHub repository (useful for archive/history tracking).

## Quick start

1. Install requirements:

```bash
python -m pip install -r requirements.txt
```

2. Create a local `.env` (copy `.env.example`) and set required values:

Required variables (minimum):

```ini
CVAT_HOST=http://<cvat-host>:8080
CVAT_USERNAME=your_username
CVAT_PASSWORD=your_password
CVAT_PROJECT_ID=1
SAVE_DIR=./backups
```

Optional Git push (if you want backups committed to another repo):

```ini
# HTTPS URL of the target repository (example):
TARGET_REPO=https://github.com/owner/target-repo.git
TARGET_BRANCH=main
GIT_USERNAME=github_username
GIT_TOKEN=ghp_xxx_your_token
```

Notes on the token:
- Create a fine-grained personal access token with minimal permission: Contents → Read & write for the specific repository.
- Do not commit `.env` or tokens to source control. Keep tokens in a local `.env` or use a secret manager.

## Creating a GitHub personal access token (PAT)
	- Go to github.com → Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token.
	- Give the token a descriptive name (e.g. "cvat-auto-backup:backup-to-target-repo").
	- Set an expiration (e.g. 30 days, 90 days) depending on your security policy.
	- Under "Repository access" choose "Only select repositories" and add the target repository.
	- Under Permissions set "Contents" → "Read & write". This is sufficient to push commits.
	- Generate the token and copy it immediately — GitHub will not show it again.

Security best practices
 - Use a fine-grained token restricted to the single target repository and with the minimal scope (Contents read/write).
 - Prefer short expirations and rotate tokens regularly.
 - Store tokens in a secure place (local `.env` excluded from git, or a secrets manager).
 - If a token is compromised, revoke it immediately and create a new one.

## Usage

Run the CLI (reads `.env` by default):

```bash
python cli.py
```

Or pass arguments directly:

```bash
python cli.py --host http://... --username USER --password PASS --project-id 1 --save-dir ./backups \
	--target-repo https://github.com/owner/target-repo.git --target-branch main --git-username USER --git-token YOUR_TOKEN
```

## Behavior
- If `TARGET_REPO`, `GIT_USERNAME` and `GIT_TOKEN` are provided the script will:
	- create the CVAT backup ZIP,
	- extract it to a temporary directory,
	- clone the target repo (will create the `TARGET_BRANCH` locally if it doesn't exist),
	- copy the extracted backup under `cvat_backup_project_<id>/`, commit with a conventional message, and push.
- Commit messages are generated automatically in the format:
	`chore(backup): add cvat project <id> backup <zip_filename> @ <UTC timestamp>`

## Troubleshooting
- If the target branch doesn't exist, the script will clone the repo and create the branch locally before committing.
- If there are no changes to commit, the script will skip committing/pushing.

## License
MIT
