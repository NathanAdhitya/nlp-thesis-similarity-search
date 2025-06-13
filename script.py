from main.main.search_engine import SearchEngine
import numpy as np

search_engine = SearchEngine()

def search(query, thesis=True):

    if thesis:
        results = search_engine.search_thesis(query=query, top_k=10, option="bgem3")

    else:
        results = search_engine.search_advisor_3(query=query, top_k=10, option="bgem3")

    print(results)
    return convert_to_json_serializable(results)

def convert_to_json_serializable(obj):
    if isinstance(obj, dict):
        return {k: convert_to_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_json_serializable(i) for i in obj]
    elif isinstance(obj, (np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, (np.int32, np.int64)):
        return int(obj)
    else:
        return obj