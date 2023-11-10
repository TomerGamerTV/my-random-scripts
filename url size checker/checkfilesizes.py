import requests
import time
import pyperclip
import os
import json

# Function to calculate the file size without downloading it


def get_file_size(url):
    try:
        response = requests.head(url, allow_redirects=True)
        content_length = response.headers.get('content-length')
        if content_length:
            return int(content_length)
    except requests.exceptions.RequestException:
        pass
    return 0

# Function to convert size to human-readable format


def format_size(size):
    units = ['bytes', 'KB', 'MB', 'GB', 'TB']
    i = 0
    while size >= 1024 and i < len(units)-1:
        size /= 1024
        i += 1
    return f'{size:.2f} {units[i]}'

# Function to update the links file with the processed links and their sizes


def update_links_file(links, sizes):
    with open('links.txt', 'w') as file:
        for i, link in enumerate(links):
            file.write(f'{link.strip()} - Size: {sizes[i]}\n')

# Function to save the state of the program


def save_state(processed_links, link_sizes, total_size):
    state = {
        'processed_links': processed_links,
        'link_sizes': link_sizes,
        'total_size': total_size
    }
    with open('state.json', 'w') as file:
        json.dump(state, file)

# Function to load the state of the program


def load_state():
    if os.path.exists('state.json'):
        with open('state.json', 'r') as file:
            state = json.load(file)
            return state['processed_links'], state['link_sizes'], state['total_size']
    return [], [], 0


# Supported video file types
supported_file_types = ['.mp4', '.mov', '.avi', '.webm']

# Read the links from a text file and filter out non-video files
links = []
with open('links.txt', 'r') as file:
    links = [link for link in file.readlines() if any(
        file_type in link for file_type in supported_file_types)]

# Variables for total size and cooldown
cooldown = 1  # Set the cooldown time in seconds

# Load the previously processed links and sizes if available
processed_links, link_sizes, total_size = load_state()

# Iterate through the links and calculate the sizes
num_files = len(processed_links)  # Initialize the total number of video files
for i, link in enumerate(links):
    link = link.strip()
    size = 0
    if link not in processed_links:
        num_files += 1  # Increment the total number of video files
        size = get_file_size(link)
        total_size += size
        link_sizes.append(size)
        processed_links.append(link)

        # Clear previous output and print updated statistics
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f'Processing file {num_files}/{len(links)}')
        print(f'Current file: {link} - Size: {format_size(size)}')
        print(f'Total number of supported video files: {num_files}')
        print(
            f'Total size of supported video files: {format_size(total_size)}')

        time.sleep(cooldown)  # Cooldown to avoid overwhelming the server

        # Save the state of the program
        save_state(processed_links, link_sizes, total_size)

# Update the links and sizes files with the processed links and sizes
update_links_file(processed_links, link_sizes)

# Print final statistics
os.system('cls' if os.name == 'nt' else 'clear')
print(f'Processing complete!')
print(f'Total number of supported video files: {num_files}')
print(f'Total size of supported video files: {format_size(total_size)}')

try:
    pyperclip.copy(str(total_size))
    print('Total size copied to clipboard.')
except pyperclip.PyperclipException:
    print('Failed to copy to clipboard.')
