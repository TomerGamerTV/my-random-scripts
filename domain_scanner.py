import os
import sys
import time
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET


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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        self.output_file = "mariushosting_links.txt"
        self.image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.pdf',
                                 '.zip', '.exe', '.bin', '.tar', '.gz', '.mp3', '.mp4')

        # Load existing progress
        if os.path.exists(self.output_file):
            with open(self.output_file, 'r') as f:
                self.visited_urls = {line.strip()
                                     for line in f if line.strip()}

    def is_internal(self, url):
        parsed = urlparse(url)
        return parsed.netloc == self.base_domain or parsed.netloc == ''

    def normalize_url(self, url):
        # Skip images and binary files
        if any(url.lower().endswith(ext) for ext in self.image_extensions):
            return None
        if url.lower().startswith('mailto:'):
            return None
        if url.startswith('//'):
            url = f"{self.scheme}:{url}"
        return urljoin(self.base_url, url).split('#')[0].split('?')[0]

    def parse_sitemap(self, sitemap_url):
        try:
            response = requests.get(
                sitemap_url, headers=self.headers, timeout=15)
            response.raise_for_status()
            root = ET.fromstring(response.content)
            namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

            if root.tag == '{http://www.sitemaps.org/schemas/sitemap/0.9}sitemapindex':
                for sitemap in root.findall('ns:sitemap', namespaces):
                    loc = sitemap.find('ns:loc', namespaces).text
                    self.parse_sitemap(loc)
            else:
                for url in root.findall('ns:url', namespaces):
                    loc = url.find('ns:loc', namespaces).text
                    if loc and self.is_internal(loc):
                        normalized = self.normalize_url(loc)
                        if normalized and normalized not in self.visited_urls:
                            self.internal_urls.add(normalized)
                            self.queue.append(normalized)
        except Exception as e:
            print(f"⚠️ Sitemap error: {str(e)[:100]}")

    def extract_links(self, html, base_url):
        try:
            soup = BeautifulSoup(html, 'lxml')
            for link in soup.find_all('a', href=True):
                raw_url = link['href'].strip()
                if not raw_url or raw_url.lower().startswith(('javascript:', 'mailto:', 'tel:')):
                    continue

                normalized = self.normalize_url(raw_url)
                if not normalized or normalized in self.visited_urls:
                    continue

                if self.is_internal(normalized):
                    final_url = urljoin(base_url, normalized)
                    final_url = final_url.split('#')[0].split('?')[0]

                    if final_url not in self.internal_urls:
                        self.internal_urls.add(final_url)
                        self.queue.append(final_url)
        except Exception as e:
            print(f"⚠️ Parsing error: {str(e)[:100]}")

    def verify_completion(self):
        unvisited = self.internal_urls - self.visited_urls
        if unvisited:
            print(f"\n⚠️ Partial completion: {len(self.visited_urls)}/"
                  f"{len(self.internal_urls)} URLs scanned")
            print("Remaining URLs might require authentication or have errors")
            return False
        return True

    def crawl(self):
        # Initial parse of sitemap
        self.parse_sitemap(f"{self.base_url}/sitemap.xml")

        # Main crawling loop
        while self.queue:
            url = self.queue.pop(0)
            if url in self.visited_urls:
                continue

            print(f"🌐 Scanning: {url}")

            try:
                response = requests.get(url, headers=self.headers, timeout=15)
                if response.status_code == 200:
                    self.extract_links(response.text, url)

                # Mark as visited and save to file
                self.visited_urls.add(url)
                with open(self.output_file, 'a') as f:
                    f.write(url + '\n')

            except Exception as e:
                print(f"⚠️ Connection error: {str(e)[:100]}")

            time.sleep(0.5)  # Reduced delay for faster scanning

        # Final verification
        if self.verify_completion():
            print(f"\n✅ True completion! All {
                  len(self.visited_urls)} URLs scanned")
        else:
            print(f"\n⏳ Completed scanning with {
                  len(self.visited_urls)} URLs processed")


if __name__ == "__main__":
    target_url = "https://mariushosting.com/"
    scanner = DomainScanner(target_url)

    try:
        scanner.crawl()
        print(f"Results saved to {scanner.output_file}")
    except KeyboardInterrupt:
        print("\n🛑 Scan interrupted! Current progress saved.")
