import re
import os

# --- CONFIGURATION ---
INPUT_FILE = "tedu_clean_data.txt"
OUTPUT_FILE = "tedu_clean_data_final.txt"

def fix_broken_lines(text):
    """
    CRITICAL FIX: Turns PDF 'hard wrapping' into natural sentences.
    
    Logic:
    1. Temporarily mark real paragraphs (Double Newlines) with a placeholder.
    2. Turn remaining Single Newlines (which are just line breaks) into spaces.
    3. Restore the paragraph breaks.
    """
    # 1. Protect real paragraphs
    text = text.replace('\n\n', '<<PARAGRAPH_BREAK>>')
    
    # 2. Unwrap lines (replace single \n with space)
    text = text.replace('\n', ' ')
    
    # 3. Restore paragraphs
    text = text.replace('<<PARAGRAPH_BREAK>>', '\n\n')
    
    # 4. Clean up any double spaces created by this process
    text = re.sub(r' +', ' ', text)
    
    return text.strip()

def fix_merged_words(text):
    """
    Fixes 'word.Nextword' -> 'word. Nextword'
    Also handles Turkish characters (e.g., 'yılmaz.Bilgisayar' -> 'yılmaz. Bilgisayar')
    """
    # Pattern: Lowercase letter (English or Turkish) followed immediately by Uppercase
    return re.sub(r'([a-zçğıöşü])([A-ZÇĞİÖŞÜ])', r'\1 \2', text)

def clean_junk(text):
    """
    Removes repetitive menus, footers, and server error messages.
    """
    junk_patterns = [
        r"Skip to main content",
        r"What are you looking for\?.*",  # Removes the search menu
        r"MyTEDU Portal.*",              # Removes footer links
        r"Copyright ©.*",
        r"Follow the Tedu Computer Engineering:.*",
        r"Access denied.*",
        r"You are not authorized.*",
        r"Ankara - Turkeyinfo@tedu.edu.tr.*",
        r"Page not found.*",
        r"Apache2 Ubuntu Default Page.*",
        r"Welcome to nginx.*"
    ]
    
    for pattern in junk_patterns:
        # re.DOTALL is crucial: it lets '.' match newlines, so we cut multi-line footers
        text = re.sub(pattern, "", text, flags=re.DOTALL | re.IGNORECASE)
        
    return text

def process_file():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found. Run mass_ingest.py first.")
        return

    print(f"Reading {INPUT_FILE}...")
    with open(INPUT_FILE, "r", encoding="utf-8", errors="ignore") as f:
        raw_data = f.read()

    # Split into pages based on the separator
    # We use a capture group () so we keep the separator line in the list
    parts = re.split(r'(--- .*?_SOURCE: .*? ---)', raw_data)
    
    cleaned_data = []
    dropped_count = 0
    
    # Iterate through parts: [Header, Content, Header, Content...]
    # We start at index 1 because index 0 is usually empty string before first header
    for i in range(1, len(parts), 2):
        header = parts[i]
        content = parts[i+1] if i+1 < len(parts) else ""
        
        # --- THE CLEANING PIPELINE ---
        
        # 1. Remove Junk first (so we don't fix sentences inside junk)
        content = clean_junk(content)
        
        # 2. Fix the "PDF Line Cut" issue (Unwrap lines)
        content = fix_broken_lines(content)
        
        # 3. Fix "word.Word" typos (Merged words)
        content = fix_merged_words(content)
        
        # 4. Collapse extra whitespace one last time
        content = re.sub(r'\s+', ' ', content).strip()
        
        # 5. FILTER: If page is empty or too short, skip it
        if len(content) < 50:
            dropped_count += 1
            continue
            
        # Reconstruct the entry
        cleaned_data.append(f"{header}\n{content}\n\n")

    print(f"--- REPORT ---")
    print(f"Total Pages Processed: {(len(parts)-1)//2}")
    print(f"Junk Pages Dropped:    {dropped_count}")
    print(f"Valid Pages Kept:      {len(cleaned_data)}")
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("".join(cleaned_data))
        
    print(f"Saved clean data to:   {OUTPUT_FILE}")
    print("Next Step: Run 'reset_brain.py' (or store.py) to load this new data.")

if __name__ == "__main__":
    process_file()