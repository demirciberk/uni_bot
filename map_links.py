import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque

# --- CONFIGURATION ---
SEED_URLS = [
    "https://cmpe.tedu.edu.tr/en",             # Start directly at CMPE
    "https://cmpe.tedu.edu.tr/en/summer-internship", # Force this one in!
    "https://career.tedu.edu.tr/en",
    "https://www.tedu.edu.tr/en",
    "https://www.tedu.edu.tr/en/regulations-and-guidelines",
    "https://www.tedu.edu.tr/en/student-affairs"
]

TARGET_DOMAIN = "tedu.edu.tr"
OUTPUT_FILE = "tedu_url_map_clean.txt" # New filename
MAX_URLS = 1500 

# --- FILTERS ---
IGNORE_YEARS = [str(y) for y in range(2012, 2024)]

# NOISE FILTER: If URL contains these, skip them!
IGNORE_KEYWORDS = [
    "/news", "/events", "/announcements", "/whats-happening-tedu", 
    "/gundemde-neler-var", "/duyurular", "/etkinlikler", 
    "/node/", # Drupal CMS generic nodes are usually junk
    "/agenda/", "/blog"
]

# --- STATE ---
visited = set()
queue = deque(SEED_URLS)
found_urls = []

def is_valid_link(url):
    try:
        parsed = urlparse(url)
        
        # 1. Domain Check
        if parsed.scheme not in ["http", "https"]: return False
        if TARGET_DOMAIN not in parsed.netloc: return False

        # 2. Year Filter
        for year in IGNORE_YEARS:
            if year in url: return False
            
        # 3. NOISE Filter (The Fix)
        for keyword in IGNORE_KEYWORDS:
            if keyword in url.lower():
                return False

        # 4. File Type Check
        junk = ('.jpg', '.png', '.gif', '.css', '.js', '.zip', '.mp4')
        if url.lower().endswith(junk): return False
            
        return True
    except:
        return False

print(f"--- STARTING NOISE-FREE MAP ---")
print("Filtering out news, events, and old dates...")

try:
    while queue and len(visited) < MAX_URLS:
        current_url = queue.popleft()
        
        if current_url in visited: continue
        visited.add(current_url)
        found_urls.append(current_url)
        
        if len(visited) % 20 == 0:
            print(f"Mapped {len(visited)} clean URLs... (Queue: {len(queue)})")
            
        try:
            response = requests.get(current_url, timeout=2)
            if "text/html" in response.headers.get("Content-Type", ""):
                soup = BeautifulSoup(response.content, 'html.parser')
                for link in soup.find_all('a', href=True):
                    full_url = urljoin(current_url, link['href']).split('#')[0].split('?')[0]
                    if is_valid_link(full_url) and full_url not in visited and full_url not in queue:
                        queue.append(full_url)
        except:
            pass

except KeyboardInterrupt:
    print("Stopping early...")

# --- SAVE ---
found_urls.sort()
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(found_urls))

print(f"Saved {len(found_urls)} HIGH QUALITY URLs to {OUTPUT_FILE}")