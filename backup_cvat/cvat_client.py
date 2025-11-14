import os
import shutil
import subprocess
import tempfile
import time
import zipfile

import requests
from cvat_sdk.api_client import ApiClient, Configuration, apis


class CVATClient:
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password
        self.configuration = Configuration(
            host=self.host, username=self.username, password=self.password
        )

    def backup_project(self, project_id, save_dir):
        os.makedirs(save_dir, exist_ok=True)

        with ApiClient(self.configuration) as api_client:
            projects_api = apis.ProjectsApi(api_client)
            requests_api = apis.RequestsApi(api_client)

            # Start export
            response, _ = projects_api.create_backup_export(int(project_id))
            request_id = response.get("rq_id")
            print(f"✅ Export started. Request ID: {request_id}")

            # Poll until finished
            while True:
                response, _ = requests_api.retrieve(request_id)
                status = response.get("status")
                print(f"⏳ Export status: {status}")
                if status.to_str() == "finished":
                    print("✅ Export completed.")
                    break
                elif status.to_str() == "failed":
                    raise RuntimeError("❌ Export failed.")
                time.sleep(3)

            # Download ZIP
            result_url = response.get("result_url")
            zip_filename = f"project_{project_id}_backup.zip"
            zip_path = os.path.join(save_dir, zip_filename)

            print(f"⬇️ Downloading backup from: {result_url}")
            session = requests.Session()
            session.auth = (self.username, self.password)
            download_response = session.get(result_url, stream=True)
            download_response.raise_for_status()

            with open(zip_path, "wb") as f:
                for chunk in download_response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"🎉 Backup saved successfully at: {zip_path}")
            return zip_path

    def backup_and_push(
        self, project_id, save_dir, target_repo, target_branch, git_username, git_token
    ):
        """Create backup zip, unzip it, and commit contents to target repo.

        Authentication is done by embedding the token into the clone URL. The token and username
        must be provided by the caller and are not stored in the current repository.
        """
        zip_path = self.backup_project(project_id, save_dir)

        # Create a temp directory to extract the zip and clone the repo
        with tempfile.TemporaryDirectory() as tmpdir:
            extract_dir = os.path.join(tmpdir, "extracted")
            os.makedirs(extract_dir, exist_ok=True)

            # Extract backup
            with zipfile.ZipFile(zip_path, "r") as z:
                z.extractall(extract_dir)

            # Prepare authenticated repo URL
            # Support URLs like https://github.com/owner/repo.git
            if target_repo.startswith("https://"):
                # insert credentials: https://username:token@github.com/owner/repo.git
                auth_repo = target_repo.replace(
                    "https://", f"https://{git_username}:{git_token}@"
                )
            else:
                raise ValueError(
                    "Only https target_repo URLs are supported for authenticated push"
                )

            clone_dir = os.path.join(tmpdir, "repo")
            # Try cloning the desired branch. If the branch doesn't exist (or repo is empty),
            # fall back to cloning the default branch and then checkout/create the target branch.
            try:
                subprocess.check_call(
                    ["git", "clone", "--branch", target_branch, auth_repo, clone_dir]
                )
            except subprocess.CalledProcessError:
                print(
                    f"⚠️ Remote branch {target_branch} not found — cloning default branch and creating {target_branch} locally."
                )
                subprocess.check_call(["git", "clone", auth_repo, clone_dir])
                # Try to checkout the branch; if it doesn't exist locally, create it
                try:
                    subprocess.check_call(
                        ["git", "-C", clone_dir, "checkout", target_branch]
                    )
                except subprocess.CalledProcessError:
                    subprocess.check_call(
                        ["git", "-C", clone_dir, "checkout", "-b", target_branch]
                    )

            # Copy extracted files into clone_dir. We'll place them under a directory named by project id to avoid overwriting unrelated content.
            dest_subdir = os.path.join(clone_dir, f"cvat_backup_project_{project_id}")
            if os.path.exists(dest_subdir):
                shutil.rmtree(dest_subdir)
            shutil.copytree(extract_dir, dest_subdir)

            # Generate conventional commit message: chore(backup): add cvat project <id> backup <timestamp>
            from datetime import datetime, timezone

            ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            zip_name = os.path.basename(zip_path)
            commit_message = (
                f"chore(backup): add cvat project {project_id} backup {zip_name} @ {ts}"
            )

            # Commit and push
            # Set git author if not set
            subprocess.check_call(["git", "-C", clone_dir, "add", "."])
            # If there are no changes, git commit will fail; handle that gracefully
            try:
                subprocess.check_call(
                    ["git", "-C", clone_dir, "commit", "-m", commit_message]
                )
            except subprocess.CalledProcessError:
                print("ℹ️ No changes to commit; skipping commit and push.")
                return
            # Push back to origin. Token is in the remote URL used at clone time.
            subprocess.check_call(
                ["git", "-C", clone_dir, "push", "origin", target_branch]
            )

            print(
                f"✅ Backup contents committed and pushed to {target_repo} (branch: {target_branch})"
            )
