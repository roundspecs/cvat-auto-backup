import os
import time
import requests
from cvat_sdk.api_client import Configuration, ApiClient, apis

class CVATClient:
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password
        self.configuration = Configuration(host=self.host, username=self.username, password=self.password)

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
