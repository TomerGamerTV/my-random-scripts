import requests
import time
import pyperclip
import os
import json
import threading
from queue import Queue

# Function to calculate the file size without downloading it


def get_file_size(url, proxies):
    try:
        response = requests.head(url, allow_redirects=True, proxies=proxies)
        content_length = response.headers.get('content-length')
        if content_length:
            return int(content_length)
    except requests.exceptions.RequestException:
        return None
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
        try:
            with open('state.json', 'r') as file:
                state = json.load(file)
                return state['processed_links'], state['link_sizes'], state['total_size']
        except json.JSONDecodeError:
            print('Error: The state.json file is corrupted. Please fix or delete it before running the script again.')
            exit(1)  # Exit the script with an error code
    return [], [], 0

# Function to process a link


def process_link(link, proxies):
    global total_size  # Declare total_size as global
    global num_files  # Declare num_files as global
    link = link.strip()
    size = 0
    if link not in processed_links:
        size = get_file_size(link, proxies)
        if size is None:  # If a request fails, assume it's due to rate limiting
            print('Rate limit exceeded, waiting for 60 seconds...')
            time.sleep(60)  # Wait for 60 seconds
            size = get_file_size(link, proxies)  # Try again
            if size is None:  # If the request still fails, skip this link
                print(f'Failed to get the size of {link}, skipping...')
                return
        total_size += size
        link_sizes.append(size)
        processed_links.append(link)
        num_files += 1  # Increment the total number of video files

# Function to print the progress


def print_progress():
    while True:
        # Clear previous output and print updated statistics
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f'Processing file {num_files}/{len(links)}')
        print(f'Total number of supported video files: {num_files}')
        print(
            f'Total size of supported video files: {format_size(total_size)}')
        time.sleep(1)  # Update the progress every second


# Supported video file types
supported_file_types = ['.mp4', '.mov', '.avi', '.webm']

# Read the links from a text file and filter out non-video files
links = []
with open('links.txt', 'r') as file:
    links = [link for link in file.readlines() if any(
        file_type in link for file_type in supported_file_types)]

# Read the proxies from a text file
proxies = []
if os.path.exists('proxies.txt'):
    with open('proxies.txt', 'r') as file:
        proxies = [{'http': proxy.strip(), 'https': proxy.strip()}
                   for proxy in file.readlines()]

# Variables for total size and cooldown
cooldown = 0.5  # Set the default cooldown time in seconds

# Load the previously processed links and sizes if available
processed_links, link_sizes, total_size = load_state()

# Initialize the total number of video files
num_files = len(processed_links)

# Create a queue for the links
link_queue = Queue()
for link in links:
    link_queue.put(link)

# Function for the worker threads to execute


def worker():
    try:
        while not link_queue.empty():
            link = link_queue.get()
            process_link(link, proxies)
            link_queue.task_done()
    except KeyboardInterrupt:
        return


# Create and start the worker threads
num_threads = 10  # Number of worker threads
for _ in range(num_threads):
    threading.Thread(target=worker, daemon=True).start()

# Start the progress printing thread
threading.Thread(target=print_progress, daemon=True).start()

# Wait for all links in the queue to be processed
link_queue.join()

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
