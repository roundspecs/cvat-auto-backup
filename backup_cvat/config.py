import os
from dotenv import load_dotenv
import argparse

load_dotenv()

def get_config():
    parser = argparse.ArgumentParser(description="CVAT Project Backup Script")

    parser.add_argument("--host", default=os.getenv("CVAT_HOST"), help="CVAT host URL")
    parser.add_argument("--username", default=os.getenv("CVAT_USERNAME"), help="CVAT username")
    parser.add_argument("--password", default=os.getenv("CVAT_PASSWORD"), help="CVAT password")
    parser.add_argument("--project-id", type=int, default=os.getenv("CVAT_PROJECT_ID"), help="Project ID to backup")
    parser.add_argument("--save-dir", default=os.getenv("SAVE_DIR"), help="Directory to save backup")

    namespace = parser.parse_args()

    try:
        assert namespace.host is not None, "CVAT_HOST must be set"
        assert namespace.username is not None, "CVAT_USERNAME must be set"
        assert namespace.password is not None, "CVAT_PASSWORD must be set"
        assert namespace.project_id is not None, "CVAT_PROJECT_ID must be set"
        assert namespace.save_dir is not None, "SAVE_DIR must be set"
    except AssertionError as e:
        parser.error(str(e))

    return namespace
