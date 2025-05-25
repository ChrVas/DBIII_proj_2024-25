# Βασιλάκος Χριστόφορoς - ΑΜ:4861

Click to play presentation video

[![Watch the video](https://img.youtube.com/vi/N7Fw8yDrDzM/0.jpg)](https://www.youtube.com/watch?v=N7Fw8yDrDzM)

## Prerequisites

- Python 3.12+
- MySQL 8.0+
- pip (Python package manager)

You will also need to install the following packages

Ubuntu/Debian
```bash
sudo apt install libgirepository-2.0-dev gcc libcairo2-dev pkg-config python3-dev gir1.2-gtk-4.0
```

For Windows/MacOS/Fedora/ArchLinux/openSUSE check the [PyGObject docs](https://pygobject.gnome.org/getting_started.html)

## Installation (Ubuntu/Debian)

1. Clone the repository:
```bash
git clone https://github.com/ChrVas/DBIII-project-2024_25.git
cd project
```

2. Set up a Python virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  
```

3. Install required packages:
```bash
pip install -r requirements.txt
```
In case you get an error on this step, install pycairo first and then PyGObject

4. Configure Database:
   - Edit `database/db_config.py`:
     ```python
     DB_CONFIG = {
         'host': 'localhost',
         'user': 'your_username',
         'password': 'your_password',
         'database': 'mye030_project'
     }
     ```

5. Initialize Database Schema:
```bash
cd project
mysql -u your_username -p
source schema.sql
```

## Data Import Process

1. Run the ETL process:
```bash
python run_etl.py
```
Make sure to run the run_etl script from the project root directory and that the csv files are inside the data folder.

## Running the Application

1. Start the GUI application:
```bash
python run_gui.py
```
Just like the run_etl script, run this from the project root directory.


## Database Backup/Restore

To backup the database:
```bash
python database/backup_db.py
```

Backups are stored in the `backups/` directory.

To restore from a backup:
```bash
mysql -u your_username -p mye030_project 
source backups/your_backup_file.sql
```
