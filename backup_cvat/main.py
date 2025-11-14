from backup_cvat.config import get_config
from backup_cvat.cvat_client import CVATClient

def main():
    args = get_config()
    client = CVATClient(args.host, args.username, args.password)
    client.backup_project(args.project_id, args.save_dir)

if __name__ == "__main__":
    main()
