import sys
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# --- 1. SETUP DATABASE ---
print("Loading local vector database...")
embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Optional: Fix for sqlite3 on some systems
if not sys.platform.startswith('win'):
    try:
        __import__('pysqlite3')
        import sys
        sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
    except ImportError:
        pass

db = Chroma(persist_directory="./chroma_db", embedding_function=embedding_function)
retriever = db.as_retriever(search_kwargs={"k": 10})

# --- 2. SETUP LLM ---
print("Initializing Local LLM (Gemma 3 4B)...")
llm = ChatOllama(
    model="gemma3:4b",
    temperature=0
)

# --- 3. DEFINE HELPERS ---
# We need a function to turn the list of Documents into a single string for the prompt
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# --- 4. BUILD THE CHAIN (LCEL) ---
# This is the modern "Pipe" syntax (|)
template = """You are a helpful assistant for TED University students.
Answer the question based ONLY on the following context:

{context}

Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# --- 5. INTERACTIVE LOOP ---
print("\n--- TEDU LOCAL AI AGENT (Pure LCEL) READY ---")
print("Type 'exit' to quit.\n")

while True:
    query = input("Ask a question: ")
    if query.lower() == "exit":
        break
    
    print("Thinking...")
    try:
        # In this specific LCEL structure, we just pass the string directly
        result = rag_chain.invoke(query)
        
        print(f"\nAnswer: {result}")
        print("-" * 50)
        
    except Exception as e:
        print(f"Error: {e}")