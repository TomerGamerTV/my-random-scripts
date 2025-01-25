import os
import sys
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from blessings import Terminal

# Constants
EMBY_API_BASE = "/emby"
AUTH_ENDPOINT = "/Users/AuthenticateByName"
ITEMS_ENDPOINT = "/Items"

term = Terminal()


def authenticate(emby_url, username, password):
    auth_url = urljoin(emby_url, EMBY_API_BASE + AUTH_ENDPOINT)
    data = {
        "Username": username,
        "Password": password
    }

    try:
        response = requests.post(auth_url, json=data)
        response.raise_for_status()
        return response.json()["AccessToken"]
    except requests.exceptions.RequestException as e:
        print(f"Error authenticating: {e}")
        sys.exit(1)


def get_items(emby_url, access_token, parent_id=None):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    items_url = urljoin(emby_url, EMBY_API_BASE + ITEMS_ENDPOINT)
    params = {"ParentId": parent_id} if parent_id else {}

    try:
        response = requests.get(items_url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()["Items"]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching items: {e}")
        sys.exit(1)


def build_tree(items):
    tree = []
    for item in items:
        tree.append({
            "id": item["Id"],
            "name": item["Name"],
            "children": [],
            "type": item.get("Type", "")
        })

        if item.get("Children"):
            children = get_items(emby_url, access_token, parent_id=item["Id"])
            tree[-1]["children"] = build_tree(children)

    return tree


def print_tree(tree, level=0):
    for node in tree:
        print(f"{'  ' * level}{node['name']}")
        print_tree(node["children"], level + 1)


def select_folder_with_arrows(tree):
    selected_index = 0
    while True:
        os.system('clear')
        print("Use arrow keys to navigate, Enter to select")

        for i, node in enumerate(tree):
            prefix = "→ " if i == selected_index else "   "
            print(f"{prefix}{node['name']}")

        key = sys.stdin.read(1)
        if key == '\x1b':
            next_key = sys.stdin.read(2)
            if next_key == '[A':  # Up arrow
                selected_index = max(0, selected_index - 1)
            elif next_key == '[B':  # Down arrow
                selected_index = min(len(tree) - 1, selected_index + 1)
        elif key == '\n':
            return tree[selected_index]


def download_folder(emby_url, access_token, folder_id, output_path):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    items_url = urljoin(emby_url, EMBY_API_BASE + ITEMS_ENDPOINT)
    params = {"ParentId": folder_id}

    try:
        response = requests.get(items_url, headers=headers, params=params)
        response.raise_for_status()

        for item in response.json()["Items"]:
            download_item(emby_url, access_token, item["Id"], output_path)
    except requests.exceptions.RequestException as e:
        print(f"Error downloading folder: {e}")
        sys.exit(1)


def download_item(emby_url, access_token, item_id, output_path):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    download_url = urljoin(emby_url, EMBY_API_BASE +
                           f"/Items/{item_id}/Download")

    try:
        response = requests.get(download_url, headers=headers, stream=True)
        response.raise_for_status()

        file_path = Path(output_path) / item["Name"]
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")
        sys.exit(1)


def main():
    global emby_url, access_token

    # Get user input
    emby_url = input("Enter Emby server URL: ")
    username = input("Enter username: ")
    password = input("Enter password: ")

    # Authenticate
    access_token = authenticate(emby_url, username, password)

    # Fetch and build tree
    root_items = get_items(emby_url, access_token)
    tree = build_tree(root_items)

    # Select folder
    selected_folder = select_folder_with_arrows(tree)
    print(f"Selected folder: {selected_folder['name']}")

    # Download folder contents
    output_path = input("Enter output directory (relative path): ")
    download_folder(emby_url, access_token, selected_folder["id"], output_path)


if __name__ == "__main__":
    main()
