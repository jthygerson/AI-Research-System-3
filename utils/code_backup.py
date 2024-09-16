# utils/code_backup.py

import shutil
import os
import datetime

def backup_code(source_dir, backup_dir):
    """
    Backs up the code to the backup directory with a timestamp.
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(backup_dir, f'backup_{timestamp}')
    try:
        # Ignore certain directories and files
        shutil.copytree(
            source_dir, backup_path, dirs_exist_ok=True,
            ignore=shutil.ignore_patterns(
                '*.pyc', '__pycache__', 'logs', 'reports', 'code_backups', '*.log', '*.txt', '.git', '.idea', 'venv', '*.md'
            )
        )
        return backup_path
    except Exception as e:
        print(f"Error backing up code: {e}")
        return None

def restore_code(backup_path, source_dir):
    """
    Restores the code from the backup directory.
    """
    try:
        # Remove current code except backup and logs
        for item in os.listdir(source_dir):
            if item not in ['code_backups', 'logs', 'reports', 'venv', 'requirements.txt', 'readme.txt']:
                item_path = os.path.join(source_dir, item)
                if os.path.isfile(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
        # Copy backup code to source directory
        for item in os.listdir(backup_path):
            s = os.path.join(backup_path, item)
            d = os.path.join(source_dir, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)
    except Exception as e:
        print(f"Error restoring code: {e}")
