import argparse
import os

from dotenv import load_dotenv

load_dotenv()


def get_config():
    parser = argparse.ArgumentParser(description="CVAT Project Backup Script")

    parser.add_argument("--host", default=os.getenv("CVAT_HOST"), help="CVAT host URL")
    parser.add_argument(
        "--username", default=os.getenv("CVAT_USERNAME"), help="CVAT username"
    )
    parser.add_argument(
        "--password", default=os.getenv("CVAT_PASSWORD"), help="CVAT password"
    )
    parser.add_argument(
        "--project-id",
        type=int,
        default=os.getenv("CVAT_PROJECT_ID"),
        help="Project ID to backup",
    )
    parser.add_argument(
        "--save-dir", default=os.getenv("SAVE_DIR"), help="Directory to save backup"
    )
    parser.add_argument(
        "--target-repo",
        default=os.getenv("TARGET_REPO"),
        help="Git URL of target repository to commit backup into",
    )
    parser.add_argument(
        "--target-branch",
        default=os.getenv("TARGET_BRANCH", "main"),
        help="Branch of the target repository",
    )
    parser.add_argument(
        "--git-username",
        default=os.getenv("GIT_USERNAME"),
        help="Username for git authentication (used with token)",
    )
    parser.add_argument(
        "--git-token",
        default=os.getenv("GIT_TOKEN"),
        help="Personal access token for git authentication",
    )
    # commit message will be generated automatically; do not accept from user

    namespace = parser.parse_args()

    try:
        assert namespace.host is not None, "CVAT_HOST must be set"
        assert namespace.username is not None, "CVAT_USERNAME must be set"
        assert namespace.password is not None, "CVAT_PASSWORD must be set"
        assert namespace.project_id is not None, "CVAT_PROJECT_ID must be set"
        assert namespace.save_dir is not None, "SAVE_DIR must be set"
        # If one of the git credentials is provided, require target repo and token/username
        if namespace.target_repo or namespace.git_token or namespace.git_username:
            assert (
                namespace.target_repo is not None
            ), "TARGET_REPO must be set when pushing backups to a repo"
            assert (
                namespace.git_token is not None
            ), "GIT_TOKEN must be set when pushing backups to a repo"
            assert (
                namespace.git_username is not None
            ), "GIT_USERNAME must be set when pushing backups to a repo"
    except AssertionError as e:
        parser.error(str(e))

    return namespace
