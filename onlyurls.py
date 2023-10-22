import re
import pyperclip

text = ""  # Paste your URLs here

# Remove some characters
clean_text = re.sub(r'[@!*]', '', text)

# Remove empty lines and extra spaces
clean_text = re.sub(r'\n\s*\n', '\n', clean_text)
clean_text = "\n".join([line for line in clean_text.split('\n') if line.strip() != ''])

# Extract lines containing URLs
url_lines = [line for line in clean_text.split('\n') if re.search(r'\.\w+', line)]

urls = []
for url_line in url_lines:
    urls.extend(re.findall(r'(?<=\|\|)([^$|^]+)', url_line))

# Copy URLs to clipboard
pyperclip.copy('\n'.join(url.strip() for url in urls))

print("URLs have been copied to clipboard.")