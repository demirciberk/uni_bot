import shutil
import os
import sys
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# --- CONFIGURATION ---
DB_FOLDER = "./chroma_db"
DATA_FILE = "./tedu_clean_data_final.txt"

def reset_and_rebuild():
    # 1. DELETE OLD BRAIN (The crucial step you missed)
    if os.path.exists(DB_FOLDER):
        print(f"Deleting old database at {DB_FOLDER}...")
        try:
            shutil.rmtree(DB_FOLDER)
            print("Deleted.")
        except Exception as e:
            print(f"Error deleting folder: {e}")
            print("Please manually delete the 'chroma_db' folder and run this again.")
            return

    # 2. LOAD CLEAN DATA
    print(f"Loading data from {DATA_FILE}...")
    if not os.path.exists(DATA_FILE):
        print(f"Error: {DATA_FILE} not found!")
        return

    loader = TextLoader(DATA_FILE, encoding="utf-8")
    documents = loader.load()

    # 3. CHUNK DATA (Using your tuned hyperparameters)
    print("Splitting text...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Generated {len(chunks)} clean chunks.")

    # 4. CREATE NEW BRAIN
    print("Building new Vector Database...")
    embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # This creates the fresh DB since we deleted the folder
    db = Chroma.from_documents(
        documents=chunks, 
        embedding=embedding_function, 
        persist_directory=DB_FOLDER
    )
    print("SUCCESS! Brain rebuilt.")

if __name__ == "__main__":
    reset_and_rebuild()