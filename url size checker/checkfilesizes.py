def get_file_size(url):
    try:
        response = requests.head(url)
        return int(response.headers['Content-Length'])
    except requests.exceptions.RequestException:
        response = requests.get(url, headers={'Range': 'bytes=0-0'}, stream=True)
        return int(response.headers['Content-Length'])

# Database setup
db = sqlite3.connect('links.db')
cursor = db.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS links  
                  (link text PRIMARY KEY, size integer)""")

total_size = 0

# Open links file  
with open('links.txt') as f:
    lines = f.readlines()

# Try to open the progress file and get the last processed line
try:
    with open('progress.txt', 'r') as f:
        start = int(f.read().strip())
except FileNotFoundError:
    start = 0

# Link processing loop
for i in range(start, len(lines)):
    link = lines[i].strip()
    ext = link.split('.')[-1]

    if ext.lower() in VIDEO_EXTENSIONS:
        cursor.execute("SELECT * FROM links WHERE link=?", (link,))
        if not cursor.fetchone():
            time.sleep(1)
            size = get_file_size(link)
            total_size += size
            cursor.execute("INSERT INTO links VALUES (?,?)", (link, size))
            print(f"Processed {link} - Size: {size}")

    # Write the current line number to the progress file
    with open('progress.txt', 'w') as f:
        f.write(str(i))

# Close db after loop   
db.commit()
print(f"Total size: {total_size}")

import pyperclip
pyperclip.copy(f"Total size: {total_size}")

db.close()
