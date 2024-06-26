import json
import requests
import time
# Load JSON file
with open('file location.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

webhook_url = 'webhook'  # Replace with your actual webhook URL
cooldown = 5  # Cooldown in seconds, adjust as necessary

for message in data['messages']:
    content = message['content']
    author = message['author']['name']
    avatar_url = message['author']['avatarUrl']

    payload = {
        "username": author,
        "avatar_url": avatar_url,
        "content": content
    }

    response = requests.post(webhook_url, json=payload)

    if response.status_code == 204:
        print(f"Message from {author} sent successfully.")
    else:
        print(f"Failed to send message from {author}: {response.status_code}")

    time.sleep(cooldown)  # Wait for the cooldown period before sending the next message
