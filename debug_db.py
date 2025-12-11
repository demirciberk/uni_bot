from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# 1. Load Database
embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
db = Chroma(persist_directory="./chroma_db", embedding_function=embedding_function)

# 2. Ask the missing question
query = input("\nEnter the question the AI fails to answer: ")

# 3. Retrieve raw documents
results = db.similarity_search(query, k=20)

print("\n--- DATABASE RAW CONTENT ---")
for i, doc in enumerate(results):
    print(f"\n[RESULT {i+1}]")
    print(doc.page_content)
    print("-" * 40)

print("\nDIAGNOSIS:")
print("1. If you see the answer above: The Database works, but the LLM is confused.")
print("2. If you DO NOT see the answer: The text was never scraped or chunked correctly.")