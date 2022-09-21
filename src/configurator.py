import os
import re
import sys
from typing import Optional

import owncloud
import pandas as pd
import qdarkstyle
from loguru import logger
from PySide6.QtCore import Qt, Slot, QThreadPool
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QDialog, QFileDialog
from dotenv import load_dotenv
from requests.exceptions import ConnectionError

from dialog import Ui_Dialog

__version__ = 0.5

try:
    from ctypes import windll  # noqa. Only exists on Windows
    myappid = f'fontys.configurator.{__version__}'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

HTTP_RESPONSES = {100: "Continue",
                  101: "Switching Protocols",
                  102: "Processing",
                  103: "Early Hits",
                  400: "Bad Request",
                  401: "Unauthorized",
                  402: "Payment Required",
                  403: "Forbidden",
                  404: "Not Found",
                  405: "Not Allowed",
                  406: "Not Acceptable",
                  407: "Authentication Required",
                  408: "Timeout",
                  409: "Conflict",
                  410: "Gone",
                  }  # not all responses, but these are most common for this application

PERMISSION_LEVELS = {"Read": 1,
                     "Read/write": 2,
                     "Create": 4,
                     "Delete": 8,
                     "Share": 16,
                     "All permissions": 31}

DEFAULT_PERMISSION = 31

logger.add("configurator_logs.log")


def load_directories(path: str) -> list[str]:
    """Reads directory structure file and parses input."""
    df: pd.DataFrame = pd.read_excel(path, header=None)  # noqa
    df = df.fillna("")

    for idx, col in enumerate(df):
        df[col] = df[col].str.strip()  # progress sometimes adds spaces at the end of an email
        df[col] += "/"
        if idx:  # skip the first column
            df[col] = df.iloc[:, idx - 1] + df[col]
        df[col] = df[col].str.replace(r"\/{2,}", "/", regex=True)

    directories = [df[col].unique().tolist() for col in df]
    directories = [item for directory in directories for item in directory]  # flattened and in hierarchical order
    return list(dict.fromkeys(directories))  # deduplicate between columns while preserving order


def is_email(string: str) -> bool:
    """Fairly naive check to test if something is an email adres."""
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", string))


class Configurator(Ui_Dialog, QDialog):
    def __init__(self):
        super(Configurator, self).__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon(":/icons/configurator_logo.ico"))
        self.setWindowTitle(f"Configurator - v{__version__}")
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)

        self.owncloud_client = None
        self.directories: list[str] = []
        self.thread_manager = QThreadPool()

        self.display("Starting automatic folder configurator script. Please login to Fontys Research Drive with your"
                     " username and WebDAV password.", append=False)

        self.load_credentials()
        self.setup_connections()

    @property
    def username(self) -> str:
        return self.line_username.text()

    @username.setter
    def username(self, string: str):
        self.line_username.setText(string)

    @property
    def password(self) -> str:
        return self.line_password.text()

    @password.setter
    def password(self, string: str):
        self.line_password.setText(string)

    @property
    def url(self) -> str:
        return self.line_url.text()

    @url.setter
    def url(self, string: str):
        self.line_url.setText(string)

    @property
    def permission_level(self) -> int:
        return PERMISSION_LEVELS.get(self.box_permission.currentText(), DEFAULT_PERMISSION)

    def load_credentials(self):
        """Try to find a .env file with an Owncloud username and password."""
        load_dotenv()
        self.username = os.getenv("OWNCLOUD_USERNAME", "")
        self.password = os.getenv("WEBDAV_PASSWORD", "")
        self.url = os.getenv("WEBDAV_URL", "")

    def setup_connections(self):
        """Connect all button signals to their respective slots."""
        self.btn_login.clicked.connect(self.login)
        self.btn_save.clicked.connect(self.save_credentials)
        self.btn_load.clicked.connect(self.load)
        self.btn_doit.clicked.connect(self.doit_threaded)

    @Slot()
    def login(self):
        """Attempt to login to Owncloud with the credentials in the text fields."""
        self.btn_login.setEnabled(False)
        self.display(f"\nSetting up Owncloud connection to {self.url}...")

        self.owncloud_client = owncloud.Client(self.url)
        try:
            self.owncloud_client.login(self.username, self.password)
        except owncloud.HTTPResponseError as e:
            code = e.status_code
            self.display(f"<p style='color:red'>Login returned the following HTTP error {code} "
                         f"({HTTP_RESPONSES.get(code, '')})<p>")
            self.display("Please try again...")
            self.btn_login.setEnabled(True)
            return
        except ConnectionError:
            self.display("<p style='color:red'>Connection error, please check the url and your internet!</p>")
            self.btn_login.setEnabled(True)
            return

        self.display(f"Connection established! You are logged in as {self.username}.")
        self.display(f"\nPlease provide a folder configuration spreadsheet file.")
        
        self.line_username.setEnabled(False)
        self.line_password.setEnabled(False)
        self.line_url.setEnabled(False)
        self.btn_save.setEnabled(True)
        self.btn_load.setEnabled(True)

    @Slot()
    def save_credentials(self):
        """Export credentials to a .env file in the working directory."""
        with open(".env", "w") as file:
            file.write(f"OWNCLOUD_USERNAME='{self.username}'\n")
            file.write(f"WEBDAV_PASSWORD='{self.password}'\n")
            file.write(f"WEBDAV_URL='{self.url}'\n")
        self.display("\nSaved url, username, and password to <b>.env</b> in your working directory. Make sure to keep "
                     "this file safe!\n")
        self.btn_save.setEnabled(False)

    @Slot()
    def load(self):
        """Load spreadsheet file with directory structure."""
        self.btn_load.setEnabled(False)

        filename = QFileDialog.getOpenFileName(filter="Spreadsheets(*.ods *.xlsx)")[0]  # noqa
        if not filename:
            self.btn_load.setEnabled(True)
            return

        self.display(f"\nLoading directory structure from '{os.path.basename(filename)}'...")
        try:
            self.directories = load_directories(filename)
        except Exception:  # noqa
            self.display("<p style='color:red'>Could not parse file, please check the contents...<p>")
            self.btn_load.setEnabled(True)
            return
        self.display("Loaded path structure!")

        contains_emails = False
        self.display("\nThe following directories/shares will be created:")
        for directory in self.directories:
            email_adres = self._get_email(directory)
            self.display(directory)
            if email_adres is not None:
                contains_emails = True
                self.display(f"&nbsp;>>> {email_adres}", append=False)

        if contains_emails:
            self.display("\nIf you agree to create these directories and share them, click <b>doit</b>!\n")
        else:
            self.display("\nIf you agree to create these directories, click <b>doit</b>!\n")

        self.btn_load.setEnabled(True)
        self.btn_doit.setEnabled(True)

    @Slot()
    def doit_threaded(self):
        """Disable buttons and make folders+shares in a new thread so the UI doesn't freeze"""
        self.btn_doit.setEnabled(False)
        self.btn_load.setEnabled(False)
        self.box_permission.setEnabled(False)

        self.thread_manager.start(self._doit)

        self.btn_doit.setEnabled(True)
        self.btn_load.setEnabled(True)
        self.box_permission.setEnabled(True)

    def _doit(self):
        """Create directories and make shares."""
        permission_level = self.permission_level
        email = None
        for directory in self.directories:
            try:  # owncloud package does not support the webDAV check command, so we'll have to yolo it
                self.display(f"Creating '{directory}'...")
                self.owncloud_client.mkdir(directory)
                self.display("&nbsp;Done!", append=False)
            except owncloud.HTTPResponseError as e:
                code = e.status_code
                self.display(f"<p style='color:red'>&nbsp;Failed with HTTP error {code} "
                             f"({HTTP_RESPONSES.get(code, '...')}), possibly already exists.</p>", append=False)
                logger.warning(f"Failed to create directory: {directory}")
            try:  # make the shares
                email = self._get_email(directory)
                if email is not None:
                    self.display(f">>> Sharing with {email}...")
                    self.owncloud_client.share_file_with_user(directory, email, perms=permission_level)
                    self.display("&nbsp;Done!", append=False)
            except Exception:  # noqa
                self.display("<p style='color:red'>&nbsp;Sharing failed...</p>", append=False)
                logger.warning(f"Failed to make share for: {email}")
        self.display("<br><b>Finished!</b>")

    def display(self, html: str, append: bool = True):
        """Display an HTML message in the text browser."""
        if append:
            self.text_browser.insertHtml("<br>" + html.replace("\n", "<br><br>"))
        else:
            self.text_browser.insertHtml(html)
        self.text_browser.ensureCursorVisible()  # scroll all the way to the bottom

    @staticmethod
    def _get_email(string: str) -> Optional[str]:
        """Extract email from path. Assumes the recipient is the last element."""
        if "/" not in string:
            return
        leafs = string.split("/")

        if not len(leafs) >= 2:
            return

        leaf = leafs[-2]
        if is_email(leaf):
            return leaf

    def closeEvent(self, _) -> None:
        """Quit the Python proces after the user clicks exit."""
        sys.exit()


def main():
    # create the application and the main window
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyside6'))

    # create the application form
    form = Configurator()
    form.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
