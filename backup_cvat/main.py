from backup_cvat.config import get_config
from backup_cvat.cvat_client import CVATClient


def main():
    args = get_config()
    client = CVATClient(args.host, args.username, args.password)
    # If git target repo and credentials are provided, create the backup and push it there.
    if (
        getattr(args, "target_repo", None)
        and getattr(args, "git_username", None)
        and getattr(args, "git_token", None)
    ):
        client.backup_and_push(
            args.project_id,
            args.save_dir,
            args.target_repo,
            args.target_branch,
            args.git_username,
            args.git_token,
        )
    else:
        client.backup_project(args.project_id, args.save_dir)


if __name__ == "__main__":
    main()
