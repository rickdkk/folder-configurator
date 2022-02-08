import os
import re
import sys
from typing import Optional

import owncloud
import qdarkstyle
import pandas as pd
from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication, QDialog, QFileDialog
from dotenv import load_dotenv

from dialog import Ui_Dialog

FRD_URL = 'https://fontys.data.surfsara.nl/'

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


def load_directories(path: str) -> list:
    """Reads directory structure file and parses input."""
    df: pd.DataFrame = pd.read_excel(path, header=None)
    df = df.fillna("")

    for idx, col in enumerate(df):
        if not idx:
            continue
        previous = df.iloc[:, idx - 1]
        if not all(previous.str.endswith("/")):
            previous += "/"
        df[col] = previous + df[col]

    if not all(df.iloc[:, -1].str.endswith("/")):
        df.iloc[:, -1] += "/"

    for col in df:
        df[col] = df[col].str.replace(r"\/{2,}", "/", regex=True)  # remove duplicate slashes

    directories = [df[col].unique().tolist() for col in df]
    directories = [item for directory in directories for item in directory]  # flattened and in hierarchical order
    return directories


def is_email(string: str) -> bool:
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", string))


class Form(Ui_Dialog, QDialog):
    def __init__(self, app):
        super(Form, self).__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon(self.resource_path("configurator_logo.ico")))
        self.setWindowTitle("Configurator")
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)

        self.owncloud_client = owncloud.Client(FRD_URL)
        self.directories = None
        self.app = app  # needs to be aware of its app so we can force redraws of the UI

        self.display("Starting automatic folder configurator script. Please login to Fontys Research Drive with your"
                     " username and WebDAV password.", append=False)

        self.read_environment()
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

    def read_environment(self):
        load_dotenv()
        self.username = os.getenv("OWNCLOUD_USERNAME", "")
        self.password = os.getenv("WEBDAV_PASSWORD", "")

    def setup_connections(self):
        self.btn_login.clicked.connect(self.login)
        self.btn_save.clicked.connect(self.save)
        self.btn_load.clicked.connect(self.load)
        self.btn_doit.clicked.connect(self.doit)

    def login(self):
        self.btn_login.setEnabled(False)
        self.display(f"\nSetting up owncloud connection to {FRD_URL}...")

        try:
            self.owncloud_client.login(self.username, self.password)
        except owncloud.HTTPResponseError as e:
            code = e.status_code
            self.display(f"<p style='color:red'>Login returned the following HTTP error {code} "
                         f"({HTTP_RESPONSES.get(code, '')})<p>")
            self.display("Please try again...")
            self.btn_login.setEnabled(True)
            return

        self.display(f"Connection established! You are logged in as {self.username}.")
        self.display(f"\nPlease provide a folder configuration spreadsheet file.")
        self.line_username.setEnabled(False)
        self.line_password.setEnabled(False)
        self.btn_save.setEnabled(True)
        self.btn_load.setEnabled(True)

    def save(self):
        with open(".env", "w") as file:
            file.write(f"OWNCLOUD_USERNAME='{self.username}'\n")
            file.write(f"WEBDAV_PASSWORD='{self.password}'\n")
        self.display("\nSaved username and password to .env\n")
        self.btn_save.setEnabled(False)

    def load(self):
        self.btn_load.setEnabled(False)

        filename = QFileDialog.getOpenFileName(filter="Spreadsheets(*.ods *.xlsx)")[0]
        if not filename:
            return

        self.display(f"\nLoading directory structure from '{os.path.basename(filename)}'...")
        try:
            self.directories = load_directories(filename)
        except Exception:  # noqa
            self.display("<p style='color:red'>Could not parse file, please check the contents...<p>")
            return
        self.display("Loaded path structure!")

        self.display("\nThe following directories will be created:")
        for directory in self.directories:
            self.display(directory)
        self.display("\nIf you agree to create these directories click <b>doit</b>!")

        self.btn_load.setEnabled(True)
        self.btn_doit.setEnabled(True)

    def doit(self):
        self.btn_doit.setEnabled(False)
        self.btn_load.setEnabled(False)
        self.btn_save.setEnabled(False)

        for directory in self.directories:
            try:  # owncloud package does not support the webDAV check command, so we'll have to yolo it
                self.display(f"Creating '{directory}'...")
                self.owncloud_client.mkdir(directory)
                self.display(" Done!", append=False)
            except owncloud.HTTPResponseError as e:
                code = e.status_code
                self.display(f"<p style='color:red'>Failed with HTTP error {code} ({HTTP_RESPONSES.get(code, '')}),"
                             f" possibly already exists.</p>", append=False)
        self.display("<br><b>Finished!</b>")

        self.btn_doit.setEnabled(True)
        self.btn_load.setEnabled(True)
        self.btn_save.setEnabled(True)

    def display(self, text: str, append: bool = True):
        if append:
            self.text_browser.insertHtml("<br>" + text.replace("\n", "<br><br>"))
        else:
            self.text_browser.insertHtml(text)
        self.text_browser.ensureCursorVisible()  # scroll all the way to the bottom
        self.app.processEvents()  # make sure to redraw UI, note that this also processes events (duh)

    @staticmethod
    def _get_email(string: str) -> Optional[str]:
        return

    @staticmethod
    def resource_path(relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS  # noqa
        except AttributeError:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)


def main():
    # create the application and the main window
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyside2'))

    # create the application form
    form = Form(app)
    form.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
