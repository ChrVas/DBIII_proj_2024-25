import os
import subprocess
from datetime import datetime
from db_config import DB_CONFIG


def create_backup():
    backup_dir = os.path.join(os.path.dirname(
        os.path.dirname(__file__)), 'backups')
    os.makedirs(backup_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(
        backup_dir, f'mye030_project_backup_{timestamp}.sql')

    mysqldump_cmd = [
        'mysqldump',
        '-h', DB_CONFIG['host'],
        '-u', DB_CONFIG['user'],
        f'--password={DB_CONFIG["password"]}',
        '--databases', f'{DB_CONFIG["database"]}',
        '--add-drop-database',
        '--events',
        '--routines',
        '--triggers',
        '--complete-insert',
        '--single-transaction',
        f'--result-file={backup_file}'
    ]

    subprocess.run(mysqldump_cmd, check=True)
    print("Backup completed")


if __name__ == "__main__":
    create_backup()
