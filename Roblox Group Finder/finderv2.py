import requests
import random
import time
import json
import threading
from queue import Queue

WEBHOOK_URL = "https://discord.com/api/webhooks/1253153723262435360/z3F_dLecFPjs21Wi4N5JH-aBzPjy1bqJuSeUf5xv1mCWGSQ9PQjhDaenBzWdNxDgndBX"

# Function to check if a proxy is working
def is_proxy_working(proxy):
    proxy_dict = {
        "http": proxy,
        "https": proxy,
    }
    try:
        response = requests.get("https://httpbin.org/ip", proxies=proxy_dict, timeout=10)
        if response.status_code == 200:
            print(f"Working proxy: {proxy}")
            return True
    except requests.exceptions.RequestException:
        print(f"Bad proxy: {proxy}")
    return False

# Function to validate proxies
def validate_proxies(proxies):
    valid_proxies = []
    for proxy in proxies:
        if is_proxy_working(proxy):
            valid_proxies.append(proxy)
    return valid_proxies

# Function to search for ownerless Roblox groups
def search_ownerless_groups(queue, proxies):
    while True:
        group_id = queue.get()
        success = False
        for _ in range(3):  # Retry up to 3 times with different proxies
            proxy = random.choice(proxies)
            proxy_dict = {
                "http": proxy,
                "https": proxy,
            }
            try:
                response = requests.get(f"https://groups.roblox.com/v1/groups/{group_id}", proxies=proxy_dict, timeout=30)
                if response.status_code == 200:
                    group_data = response.json()
                    if not group_data.get('owner') and group_data.get('publicEntryAllowed'):
                        message = {
                            "content": f"[ORGF][Valid] https://www.roblox.com/groups/group.aspx?gid={group_id} | Name: {group_data['name']} | Members: {group_data['memberCount']}"
                        }
                        requests.post(WEBHOOK_URL, headers={"Content-Type": "application/json"}, data=json.dumps(message), proxies=proxy_dict)
                        print(f"[ORGF][Valid] https://www.roblox.com/groups/group.aspx?gid={group_id} | Name: {group_data['name']} | Members: {group_data['memberCount']}")
                    else:
                        print(f"[ORGF][Invalid] https://www.roblox.com/groups/group.aspx?gid={group_id} | Name: {group_data['name']} | Members: {group_data['memberCount']}")
                    success = True
                    break
                elif response.status_code == 429:
                    print("Rate limited. Waiting for 60 seconds.")
                    time.sleep(60)
                    break
                else:
                    print(f"[ORGF][Invalid] https://www.roblox.com/groups/group.aspx?gid={group_id}")
            except requests.exceptions.RequestException as e:
                print(f"Proxy error: {proxy} - {e}")
        if not success:
            print(f"Failed to process group {group_id} after several attempts.")
        queue.task_done()
        time.sleep(random.uniform(1, 3))  # Random delay between 1 and 3 seconds

def load_proxies(file_path):
    with open(file_path, 'r') as file:
        proxies = [line.strip() for line in file if line.strip()]
    return proxies

def main():
    num_threads = int(input("Enter the number of threads (Recommended: 16-36): "))
    proxies = load_proxies('proxies.txt')

    if not proxies:
        print("No proxies loaded. Please check your proxies.txt file.")
        return

    print("Validating proxies...")
    valid_proxies = validate_proxies(proxies)

    if not valid_proxies:
        print("No valid proxies found. Please check your proxies.txt file.")
        return

    queue = Queue()
    threads = []

    for _ in range(num_threads):
        t = threading.Thread(target=search_ownerless_groups, args=(queue, valid_proxies))
        t.daemon = True
        t.start()
        threads.append(t)

    while True:
        for _ in range(10):  # Add 10 new tasks to the queue at a time
            queue.put(random.randint(1, 1150000))

        queue.join()

if __name__ == "__main__":
    main()
