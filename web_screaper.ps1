# Define the starting URL and sitemap URL
$domain = "https://mariushosting.com"
$sitemapUrl = "https://mariushosting.com/sitemap.xml"
$outputFile = "Links.txt"

# HashSet to store visited links
$visitedLinks = @{}

# Function to fetch links from a webpage
function Get-LinksFromPage {
    param (
        [string]$url
    )

    try {
        $html = Invoke-WebRequest -Uri $url -UseBasicParsing
        $links = ($html.Links | Where-Object { $_.href -like "$domain*" }).href
        return $links
    }
    catch {
        Write-Warning "Failed to fetch or parse $url"
        return @()
    }
}

# Function to fetch links from a sitemap
function Get-LinksFromSitemap {
    param (
        [string]$sitemapUrl
    )

    try {
        # Use headers to mimic a browser
        $headers = @{
            "User-Agent" = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36"
        }
        $response = Invoke-WebRequest -Uri $sitemapUrl -UseBasicParsing -Headers $headers
        $xml = $response.Content | ConvertFrom-Xml
        if ($xml.urlset.url) {
            return $xml.urlset.url.loc
        }
        else {
            Write-Warning "Sitemap does not contain any links"
            return @()
        }
    }
    catch {
        Write-Warning "Failed to fetch or parse sitemap at $sitemapUrl"
        return @()
    }
}

# Recursive function to scan the domain
function Search-Domain {
    param (
        [string]$url
    )

    if ($visitedLinks.ContainsKey($url)) {
        return
    }

    $visitedLinks[$url] = $true
    $links = Get-LinksFromPage -url $url
    foreach ($link in $links) {
        Search-Domain -url $link
    }
}

# Main script execution
Write-Host "Starting scan of $domain..." -ForegroundColor Green

$initialLinks = Get-LinksFromSitemap -sitemapUrl $sitemapUrl

if ($initialLinks.Count -gt 0) {
    Write-Host "Sitemap found. Starting scan with links from sitemap..."
    foreach ($link in $initialLinks) {
        Scan-Domain -url $link
    }
}
else {
    Write-Host "Sitemap not found or empty. Starting scan from homepage..."
    Search-Domain -url $domain
}

$visitedLinks.Keys | Set-Content -Path $outputFile

Write-Host "Scan completed. Links saved to $outputFile" -ForegroundColor Green
