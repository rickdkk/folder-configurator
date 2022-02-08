import os

import owncloud
import pandas as pd
from dotenv import load_dotenv

FRD_URL = 'https://fontys.data.surfsara.nl/'


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


def main():
    # %% log in
    print("Starting automatic folder configurator script.\nYou can exit at any time by pressing (ctrl+C)\n")
    load_dotenv()
    username = os.getenv("OWNCLOUD_USERNAME", "")
    if not username:
        username = input("Please enter your owncloud username: ")

    password = os.getenv("WEBDAV_PASSWORD", "")
    if not password:
        password = input("Please enter your webDAV password for FRD: ")

    print(f"Setting up owncloud connection to {FRD_URL}...")
    oc = owncloud.Client(FRD_URL)
    oc.login(username, password)
    print(f"Connection established! You are logged in as {username}.")

    # %% read the directory structure
    path = ""
    while not os.path.isfile(path):
        path = input("\nPlease provide the name of the file containing the directory structure: ")

    print(f"\nLoading directory structure from '{path}'...")
    directories = load_directories(path)
    print("Loaded path structure!")

    print("\nThe following directories will be created:")
    for directory in directories:
        print(directory)

    response = ""
    while response not in ["yes", "no"]:
        response = input("\nConfirm (yes/no): ")
        print()

    if response == "no":
        print("Quitting program...")
        quit()

    # %% create directories on owncloud
    for directory in directories:
        try:  # owncloud package does not support the webDAV check command, so we'll just need to catch the exceptions
            print(f"Creating '{directory}'...", end=" ", flush=True)
            oc.mkdir(directory)
            print("Done!")
        except owncloud.HTTPResponseError:
            print(f"Operation failed, possibly already exists.")

    print("All operations complete!")


if __name__ == "__main__":
    main()
