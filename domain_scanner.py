import os
import sys
import time
import signal
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup

class DomainScanner:
    def __init__(self, base_url):
        self.base_url = base_url
        parsed_base = urlparse(base_url)
        self.base_domain = parsed_base.netloc
        self.scheme = parsed_base.scheme
        self.visited_urls = set()
        self.internal_urls = set()
        self.queue = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        self.output_file = "mariushosting_links.txt"
        self.state_file = "scanner_state.txt"

        # Load previous state if exists
        if os.path.exists(self.state_file):
            self.load_state()

        # Load existing URLs from output file
        if os.path.exists(self.output_file):
            with open(self.output_file, 'r') as f:
                self.internal_urls.update(line.strip() for line in f)

    # New state management methods
    def save_state(self):
        with open(self.state_file, 'w') as f:
            f.write('\n'.join([
                ','.join(self.visited_urls),
                ','.join(self.queue)
            ]))

    def load_state(self):
        try:
            with open(self.state_file, 'r') as f:
                data = f.read().split('\n')
                self.visited_urls = set(
                    data[0].split(',')) if data[0] else set()
                self.queue = data[1].split(',') if len(data) > 1 else []
            os.remove(self.state_file)
        except Exception as e:
            print(f"⚠️ State load error: {str(e)[:100]}")

    def is_internal(self, url):
        parsed = urlparse(url)
        return parsed.netloc == self.base_domain or parsed.netloc == ''

    def normalize_url(self, url):
        if url.startswith('//'):
            url = f"{self.scheme}:{url}"
        # New: Explicitly exclude mailto links
        if url.lower().startswith('mailto:'):
            return None
        return urljoin(self.base_url, url).split('#')[0].split('?')[0]

    def parse_sitemap(self, sitemap_url):
        try:
            response = requests.get(
                sitemap_url, headers=self.headers, timeout=15)
            response.raise_for_status()

            root = ET.fromstring(response.content)
            namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
# Add this comment to disable the warning for specific lines
# flake8: noqa: E501
            if root.tag == '{http://www.sitemaps.org/schemas/sitemap/0.9}sitemapindex':
                for sitemap in root.findall('ns:sitemap', namespaces):
                    loc = sitemap.find('ns:loc', namespaces).text
                    self.parse_sitemap(loc)
            else:
                for url in root.findall('ns:url', namespaces):
                    loc = url.find('ns:loc', namespaces).text
                    if loc and self.is_internal(loc):
                        normalized = self.normalize_url(loc)
                        if normalized and normalized not in self.internal_urls:
                            self.internal_urls.add(normalized)
                            self.queue.append(normalized)
                            self._save_url(normalized)
        except Exception as e:
            print(f"⚠️ Sitemap error: {str(e)[:100]}")

    def _save_url(self, url):
        # Check if URL is already in file before writing
        with open(self.output_file, 'a+') as f:
            f.seek(0)
            existing = set(line.strip() for line in f)
            if url not in existing:
                f.write(url + '\n')

    def extract_links(self, html, base_url):
        try:
            soup = BeautifulSoup(html, 'lxml')
            for link in soup.find_all('a', href=True):
                raw_url = link['href'].strip()
                # Skip mailto and other non-http links
                if not raw_url or raw_url.lower().startswith(('javascript:', 'mailto:', 'tel:')):
                    continue

                normalized = self.normalize_url(raw_url)
                if not normalized:
                    continue

                if self.is_internal(normalized):
                    final_url = urljoin(base_url, normalized)
                    final_url = final_url.split('#')[0].split('?')[0]

                    if final_url not in self.internal_urls:
                        self.internal_urls.add(final_url)
                        self.queue.append(final_url)
                        self._save_url(final_url)
        except Exception as e:
            print(f"⚠️ Parsing error: {str(e)[:100]}")

    def crawl(self):
        # Setup interrupt handler
        original_sigint = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, self.exit_gracefully)

        try:
            if not self.queue:  # Only parse sitemap if starting fresh
                self.parse_sitemap(f"{self.base_url}/sitemap.xml")

            while self.queue:
                url = self.queue.pop(0)
                if url in self.visited_urls:
                    continue

                print(f"🌐 Scanning: {url}")

                try:
                    response = requests.get(
                        url, headers=self.headers, timeout=15)
                    if response.status_code == 200:
                        self.extract_links(response.text, url)
                    self.visited_urls.add(url)
                except Exception as e:
                    print(f"⚠️ Connection error: {str(e)[:100]}")

                time.sleep(1)
                self.save_state()  # Save state after each URL

        finally:
            signal.signal(signal.SIGINT, original_sigint)
            if os.path.exists(self.state_file):
                os.remove(self.state_file)

    def exit_gracefully(self, signum, frame):
        print("\n🛑 Capture interrupt signal - Saving state...")
        self.save_state()
        sys.exit(0)


if __name__ == "__main__":
    target_url = "https://mariushosting.com/"
    scanner = DomainScanner(target_url)
    scanner.crawl()
    print(f"\n✅ Scan complete! Saved {
          len(scanner.internal_urls)} URLs to {scanner.output_file}")
