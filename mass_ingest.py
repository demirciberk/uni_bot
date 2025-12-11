import requests
from bs4 import BeautifulSoup
import io
from pypdf import PdfReader
import time
import re

# --- CONFIGURATION ---
INPUT_MAP_FILE = "tedu_url_map_clean.txt"
OUTPUT_DATA_FILE = "tedu_final_data.txt"

def clean_text(text):
    """Reduces multiple spaces/newlines to single ones."""
    return re.sub(r'\s+', ' ', text).strip()

def extract_pdf(content):
    try:
        reader = PdfReader(io.BytesIO(content))
        text = ""
        for page in reader.pages:
            t = page.extract_text()
            if t: text += t + " "
        return clean_text(text)
    except:
        return ""

def extract_html(content):
    try:
        soup = BeautifulSoup(content, 'html.parser')
        # Kill junk
        for x in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
            x.decompose()
        return clean_text(soup.get_text())
    except:
        return ""

# --- MAIN EXECUTION ---
print("Reading URL map...")
with open(INPUT_MAP_FILE, "r", encoding="utf-8") as f:
    urls = [line.strip() for line in f if line.strip()]

print(f"Loaded {len(urls)} URLs to process.")
print("Starting Mass Ingestion (This may take a while)...")

all_data = []

# Loop through the list
for i, url in enumerate(urls):
    try:
        # Progress Log every 10 items
        if i % 10 == 0:
            print(f"Processing [{i}/{len(urls)}] - {url}")

        headers = {'User-Agent': 'TEDU_Student_Project_Bot/1.0'}
        # 5 second timeout so we don't get stuck on one page
        response = requests.get(url, headers=headers, timeout=5)

        content_type = response.headers.get("Content-Type", "").lower()
        extracted_text = ""

        if "application/pdf" in content_type:
            extracted_text = extract_pdf(response.content)
            source_tag = f"PDF_SOURCE: {url}"
            
        elif "text/html" in content_type:
            extracted_text = extract_html(response.content)
            source_tag = f"WEB_SOURCE: {url}"

        # Only save if we found actual words (skip empty pages)
        if len(extracted_text) > 200:
            entry = f"--- {source_tag} ---\n{extracted_text}\n\n"
            all_data.append(entry)
            
        # Be polite to the server
        time.sleep(0.2)

    except Exception as e:
        print(f"Failed: {url} ({e})")

# Save to file
print(f"\nSaving {len(all_data)} pages to {OUTPUT_DATA_FILE}...")
with open(OUTPUT_DATA_FILE, "w", encoding="utf-8") as f:
    f.write("".join(all_data))

print("DONE! You are ready to run store.py.")