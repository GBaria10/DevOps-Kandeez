import os
import sys
import logging
import time
import base64
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import getpass

# Set up logging to show in console and file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("decryption_log.txt"),
        logging.StreamHandler(sys.stdout)
    ]
)


class FileDecryptor:
    def _init_(self):
        self.key = None
        self.encrypted_extension = ".encrypted"
        self.dirs_to_scan = [
            os.path.join(os.path.expanduser("~"), "Documents"),
            os.path.join(os.path.expanduser("~"), "Downloads"),
            os.path.join(os.path.expanduser("~"), "Desktop"),
            os.path.join(os.path.expanduser("~"), "Pictures"),
            os.path.join(os.path.expanduser("~"), "Music"),
            os.path.join(os.path.expanduser("~"), "AppData", "Local"),
            os.path.join(os.path.expanduser("~"), "AppData", "Roaming"),
            os.path.join(os.path.expanduser("~"), "AppData", "LocalLow")
        ]
        self.ransom_note_paths = [
            os.path.join(os.path.expanduser("~"), "Desktop", "README_IMPORTANT.html"),
            os.path.join(os.path.expanduser("~"), "Desktop", "README_IMPORTANT.lnk")
        ]
        self.success_note_path = os.path.join(os.path.expanduser("~"), "Desktop", "DECRYPTION_COMPLETE.txt")

    def set_decryption_key(self, key_input):
        """Set the decryption key from user input."""
        try:
            # Check if the input might be base64 encoded
            try:
                # Try to decode as base64
                self.key = base64.b64decode(key_input)
                logging.info("Using provided key as Base64 encoded key")
            except:
                # If not Base64, hash it to create a key
                self.key = hashlib.sha256(key_input.encode()).digest()
                logging.info("Using provided key after SHA-256 hashing")

            logging.info("Encryption key set")
            return True
        except Exception as e:
            logging.error(f"Error setting decryption key: {e}")
            return False

    def decrypt_file(self, file_path):
        """Decrypt a single file using AES."""
        try:
            # Skip empty files
            if os.path.getsize(file_path) == 0:
                logging.warning(f"Skipping empty file: {file_path}")
                return False

            # Read the encrypted content
            with open(file_path, 'rb') as f:
                encrypted_data = f.read()

            # The first 16 bytes should be the IV
            if len(encrypted_data) <= 16:
                logging.warning(f"File too small to contain IV: {file_path}")
                return False

            iv = encrypted_data[:16]
            ciphertext = encrypted_data[16:]

            # Create cipher
            cipher = Cipher(
                algorithms.AES(self.key),
                modes.CBC(iv),
                backend=default_backend()
            )

            # Decrypt
            decryptor = cipher.decryptor()
            padded_data = decryptor.update(ciphertext) + decryptor.finalize()

            # Unpad the data
            unpadder = padding.PKCS7(128).unpadder()
            try:
                decrypted_data = unpadder.update(padded_data) + unpadder.finalize()
            except Exception as e:
                logging.error(f"Invalid token for file: {file_path} - This file may not be encrypted with this key")
                # Alternative approach: try a different decryption method
                try:
                    # Try with CTR mode instead of CBC (no padding needed)
                    cipher_alt = Cipher(
                        algorithms.AES(self.key),
                        modes.CTR(iv),
                        backend=default_backend()
                    )
                    decryptor_alt = cipher_alt.decryptor()
                    decrypted_data = decryptor_alt.update(ciphertext) + decryptor_alt.finalize()
                    logging.info(f"Decrypted using alternative method: {file_path}")
                except Exception:
                    return False

            # Write decrypted content to original file
            output_path = file_path[:-len(self.encrypted_extension)]
            with open(output_path, 'wb') as f:
                f.write(decrypted_data)

            # Remove the encrypted file
            os.remove(file_path)
            logging.info(f"Successfully decrypted: {file_path}")
            return True

        except Exception as e:
            logging.error(f"Error decrypting {file_path}: {e}")
            return False

    def scan_and_decrypt(self):
        """Scan directories and decrypt encrypted files."""
        total_files = 0
        decrypted_files = 0

        logging.info("Identifying directories to scan...")
        valid_dirs = []
        for dir_path in self.dirs_to_scan:
            if os.path.exists(dir_path) and os.path.isdir(dir_path):
                valid_dirs.append(dir_path)

        logging.info(f"Found {len(valid_dirs)} directories to scan")
        logging.info("Starting decryption of files...")

        for dir_path in valid_dirs:
            logging.info(f"Scanning directory: {dir_path}")
            for root, _, files in os.walk(dir_path):
                for file in files:
                    if file.endswith(self.encrypted_extension):
                        total_files += 1
                        file_path = os.path.join(root, file)
                        if self.decrypt_file(file_path):
                            decrypted_files += 1

        logging.info(
            f"Decryption complete. Processed {total_files} files, successfully decrypted {decrypted_files} files.")
        return decrypted_files

    def remove_ransom_notes(self):
        """Remove ransom notes from the system."""
        logging.info("Removing ransom notes...")
        for note_path in self.ransom_note_paths:
            if os.path.exists(note_path):
                try:
                    os.remove(note_path)
                    logging.info(f"Removed ransom note: {note_path}")
                except Exception as e:
                    logging.error(f"Failed to remove ransom note {note_path}: {e}")

    def create_success_note(self):
        """Create a success note on the desktop."""
        logging.info("Creating success note...")
        try:
            with open(self.success_note_path, 'w') as f:
                f.write("DECRYPTION COMPLETE\n\n")
                f.write("All your files have been decrypted.\n")
                f.write("Your system is now secure again.\n\n")
                f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            logging.info(f"Created success note at: {self.success_note_path}")
        except Exception as e:
            logging.error(f"Failed to create success note: {e}")

    def run_decryption(self):
        """Run the complete decryption process."""
        logging.info("==================================================")
        logging.info("Starting decryption process")
        logging.info("==================================================")

        decrypted_count = self.scan_and_decrypt()
        self.remove_ransom_notes()

        if decrypted_count > 0:
            self.create_success_note()
            logging.info("Decryption process completed successfully")
            return True
        else:
            logging.warning("No files were successfully decrypted")
            return False


if __name__ == "_main_":
    try:
        print("File Decryptor - Starting...\n")

        # Initialize decryptor
        decryptor = FileDecryptor()

        # ===== ADD YOUR DECRYPTION KEY BELOW =====
        # Replace 'YOUR_DECRYPTION_KEY_HERE' with your actual decryption key
        hardcoded_key = "8pXisE1tjtFsDQl7CA40tNUgXSKLV6WsrA6PPZgNMGo="
        # =========================================

        print("Using hardcoded decryption key")

        if not decryptor.set_decryption_key(hardcoded_key):
            print("Failed to set decryption key. Aborting.")
            print("\nPress any key to exit...")
            input()
            sys.exit(1)

        # Run decryption process
        decryptor.run_decryption()

        print("\nDecryption process complete. See log for details.")
        print("Press any key to exit...")
        input()  # Wait for user input before closing
    except Exception as e:
        print(f"Fatal error: {e}")
        print("\nPress any key to exit...")
        input()  # Ensure window stays open on error