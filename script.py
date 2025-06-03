import mysql.connector
from sentence_transformers import SentenceTransformer
from main.sql_FAISS.thesis_search_engine import SearchEngine

# from main.sql_FAISS.search_utils import get_embedding, print_formatted_results

database = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
)
cursor = database.cursor()
cursor.execute("USE nlp_thesis_similarity")

model = SentenceTransformer("all-MiniLM-L6-v2")

search_manager = SearchEngine(model=model, cursor=cursor)

# Load the search engine (first time will load from database)
try:
    search_engine = search_manager.load(use_title=True, use_abstract=True)
    print("\nSearch engine ready for queries!")
except Exception as e:
    print(f"Error initializing search engine: {e}")

def search(query):
    results = search_manager.quick_search(query, top_k=100)
    print(results)