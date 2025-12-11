# TED University AI Agent 🎓

A Local RAG (Retrieval-Augmented Generation) agent that answers questions about TED University regulations, courses, and internships.

## 🏗 Architecture
This project uses a custom ETL pipeline to scrape, clean, and vectorise university data, running 100% locally using Ollama and ChromaDB.

1.  **Crawler (`map_links.py`)**: Maps the university domain, filtering out news/noise.
2.  **Ingest (`mass_ingest.py`)**: Downloads HTML & PDFs.
3.  **Cleaner (`cleaner.py`)**: Fixes PDF line-breaks, merges split words, and removes navigation menus.
4.  **Vector Store (`reset_brain.py`)**: Embeds text using `all-MiniLM-L6-v2` into ChromaDB.
5.  **Agent (`rag.py`)**: Uses **Gemma 2 (2B)** via Ollama to answer student questions.

## 🚀 How to Run

### 1. Prerequisites
* Python 3.10+
* [Ollama](https://ollama.com/) installed.
* Pull the model: `ollama pull gemma2:2b`

### 2. Installation
```bash
git clone [https://github.com/demirciberk/uni_bot.git](https://github.com/demirciberk/uni_bot.git)
cd uni_bot
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

pip install -r requirements.txt 

### 3. Build the Brain
(Optional: The data is already included in `tedu_clean_data_final.txt`. You can skip scraping and just build the DB.)

```bash
python reset_brain.py
```
4. Chat with the Agent
```Bash

python rag.py
Type exit to quit.
```

🛠 Re-Scraping Data (Optional)
If you want to update the data yourself from scratch:

python map_links.py (Finds URLs)

python mass_ingest.py (Downloads Content)

python cleaner.py (Refines Data)

python reset_brain.py (Updates Database)

⚙️ Configuration & Troubleshooting
Missing Course Info? The retrieval limit (k) in rag.py is set to 15 (or 20). This ensures the AI reads enough chunks to find specific details like "CMPE 114" that might be buried deep in curriculum lists. If the agent says "I don't know," try increasing k.

Model Mismatch Errors Ensure the model name in rag.py (e.g., gemma3:4b or gemma2:2b) matches exactly what you installed.

Check your installed models: ollama list

Pull the correct model: ollama pull gemma3:4b
