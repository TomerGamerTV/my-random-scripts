"""
Domain Scanner with Tree Visualization
"""
import time
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, urljoin
from collections import defaultdict
import requests
from bs4 import BeautifulSoup
from rich.live import Live
from rich.tree import Tree
from rich.console import Console
from rich.panel import Panel
from rich.box import ROUNDED

console = Console()


class DomainScanner:
    """Web domain scanner with interactive tree visualization"""

    def __init__(self, base_url):
        self.base_url = base_url
        parsed_base = urlparse(base_url)
        self.base_domain = parsed_base.netloc
        self.scheme = parsed_base.scheme
        self.visited = set()
        self.url_tree = defaultdict(list)
        self.max_depth = 0
        self.start_time = time.time()
        self.output_file = "scan_results.txt"
        self.current_url = ""  # Add this line to initialize the attribute

        # Initialize output file
        with open(self.output_file, "w", encoding="utf-8") as f:
            f.write("")

        # Tree visualization state
        self.tree_root = Tree(
            f"🌳 [bold green]{self.base_domain}[/]",
            style="bright_black",
            guide_style="bright_white"
        )
        self.path_map = {self.base_url: self.tree_root}

    def display_summary(self):
        """Show final statistics"""
        elapsed = time.time() - self.start_time
        summary_table = Panel(
            f"[bold]Scan Summary:[/]\n\n"
            f"🌐 Total URLs Found: [bold cyan]{len(self.visited)}[/]\n"
            f"📏 Max Depth Reached: [bold yellow]{self.max_depth}[/]\n"
            f"⏱️ Elapsed Time: [bold magenta]{elapsed:.1f} seconds[/]\n"
            f"💾 Results Saved To: [bold green]{self.output_file}[/]",
            title="[bold]Scan Complete[/]",
            border_style="bright_green",
            box=ROUNDED
        )
        console.print(summary_table)

    def build_tree_path(self, url):
        """Create hierarchical tree structure from URL path"""
        parsed = urlparse(url)
        path_parts = [p for p in parsed.path.split('/') if p]
        current_node = self.tree_root
        full_path = self.base_url

        for i, part in enumerate(path_parts):
            full_path = f"{full_path.rstrip('/')}/{part}"
            if full_path not in self.path_map:
                display_text = part or "(root)"
                node = current_node.add(
                    f"📂 [link {full_path}]{display_text}[/]")
                self.path_map[full_path] = node
                self.max_depth = max(self.max_depth, i+1)
            current_node = self.path_map[full_path]
        return current_node

    def update_display(self):
        """Create dynamic interface layout"""
        elapsed = time.time() - self.start_time
        stats_content = (
            f"[bold cyan]Total URLs:[/] {len(self.visited)}\n"
            f"[bold yellow]Max Depth:[/] {self.max_depth}\n"
            f"[bold magenta]Elapsed:[/] {elapsed:.1f}s\n"
            f"[bold green]Current:[/] {self.current_url}"
        )
        return Panel(
            self.tree_root,
            title="[bold white]Domain Structure[/]",
            subtitle=f"[dim]Navigating {self.base_domain}\n\n{stats_content}",
            border_style="bright_blue",
            width=console.width,
            box=ROUNDED
        )

    def save_results(self):
        """Save discovered URLs to file"""
        with open(self.output_file, "a", encoding="utf-8") as f:
            for url in self.visited:
                f.write(f"{url}\n")

    def parse_sitemap(self, sitemap_url):
        """Parse XML sitemap with proper error handling"""
        try:
            response = requests.get(sitemap_url, timeout=10)
            root = ET.fromstring(response.content)
            namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            sitemap_tag = '{http://www.sitemaps.org/schemas/sitemap/0.9}sitemapindex'

            if root.tag == sitemap_tag:
                for sitemap in root.findall('ns:sitemap', namespaces):
                    loc = sitemap.find('ns:loc', namespaces).text
                    self.parse_sitemap(loc)
            else:
                for url in root.findall('ns:url', namespaces):
                    loc = url.find('ns:loc', namespaces).text
                    if loc and self.base_domain in loc:
                        self.url_tree[self.base_url].append(loc)
                        self.visited.add(loc)
        except (requests.exceptions.RequestException, ET.ParseError) as error:
            console.print(f"[yellow]⚠️ Sitemap error: {str(error)[:50]}[/]")

    # Add this missing method for URL normalization
    def normalize_url(self, url):
        """Sanitize and format URLs"""
        if url.startswith('//'):
            url = f"{self.scheme}:{url}"
        return urljoin(self.base_url, url).split('#')[0].split('?')[0]

    def process_url(self, url):  # ✅ Proper indentation (no extra spaces before def)
        """Process individual URL"""
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'lxml')
                for link in soup.find_all('a', href=True):
                    raw_url = link['href'].strip()
                    normalized = self.normalize_url(raw_url)
                    if normalized and normalized not in self.visited:
                        self.url_tree[url].append(normalized)
                        self.visited.add(normalized)
        except requests.exceptions.RequestException as e:
            console.print(f"[yellow]⚠️ Connection error: {str(e)[:50]}[/]")

    def crawl(self):
        """Main crawling process with live visualization"""  # Add indentation here
        try:
            with Live(self.update_display(), console=console, screen=True,
                      refresh_per_second=10) as live:
                self.parse_sitemap(f"{self.base_url}/sitemap.xml")

                while self.url_tree:
                    parent_url, children = self.url_tree.popitem()
                    parent_node = self.build_tree_path(parent_url)

                    for child in children:
                        self.current_url = child
                        self.visited.add(child)
                        
                        parsed_child = urlparse(child)
                        leaf_text = parsed_child.path.split('/')[-1] or parsed_child.netloc
                        parent_node.add(f"🪶 [link {child}]{leaf_text}[/]")
                        live.update(self.update_display())
                        
                        self.process_url(child)
                        time.sleep(0.15)

                self.save_results()
        except KeyboardInterrupt:
            self.save_results()
            console.print("\n[bold red]🛑 Scan interrupted! Saving progress...[/]")
        finally:
            self.display_summary()


if __name__ == "__main__":
    scanner = DomainScanner("https://mariushosting.com/")
    scanner.crawl()
