import sqlite3
import sqlite_vec
import concurrent.futures
import os
from typing import List, Dict, Any
from FlagEmbedding import BGEM3FlagModel
from sentence_transformers import SentenceTransformer
from deep_translator import GoogleTranslator
from typing import Optional
import torch
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
DB_PATH = os.path.join(PROJECT_ROOT, 'data', 'cleaned_with_bge_m3.db')

class SearchEngine:
    def __init__(self, device=None) -> None:
        # Determine device
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        
        self.device = device
        
        # Load BGEM3 with explicit device
        self.bgem3 = BGEM3FlagModel('BAAI/bge-m3', use_fp16=True, device=device)
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            allminilm_future = executor.submit(self._load_sentence_transformer, "all-MiniLM-L6-v2")
            indobert_future = executor.submit(self._load_sentence_transformer, 'rahmanfadhil/indobert-finetuned-indonli')
            translator_future = executor.submit(GoogleTranslator, source='auto', target='indonesian')
            
            self.allminilm = allminilm_future.result()
            self.indobert = indobert_future.result()
            self.translator = translator_future.result()
    
    def _load_sentence_transformer(self, model_name):
        model = SentenceTransformer(model_name, device=self.device)
        return model
            
    def search_thesis(self, query: str, top_k: int = 5, option: str = "bgem3") -> List[Dict[str, Any]]:
        """
        Searches for thesis documents based on the provided query.

        Args:
            query (str): The search query.
            top_k (int): The number of top results to return.
            option (str): The model to use for searching ('bgem3', 'allminilm', or 'indobert').

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing the search results.
        """
        # Select embedding model based on option
        model_options = {
            "bgem3": self.bgem3,
            "allminilm": self.allminilm,
            "indobert": self.indobert        
        }
        if option not in model_options:
            raise ValueError("Invalid option. Choose 'bgem3', 'allminilm', or 'indobert'.")
            
        model = model_options[option]
        
        query_embedding = self._encode_query(query, model)
        
        # Perform the search using the query embedding
        results = self._search(query_embedding, top_k, option)
        
        return results
    
    def search_advisor(self, query: str, top_k: int = 10, option: str = "bgem3") -> List[Dict[str, Any]]:
        """
        Searches for advisors/users with expertise related to the provided query.

        Args:
            query (str): The search query.
            top_k (int): The number of top advisors to return.
            option (str): The model to use for searching ('bgem3', 'allminilm', or 'indobert').

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing the top advisors and their related publications.
        """
        # Select embedding model based on option
        model_options = {
            "bgem3": self.bgem3,
            "allminilm": self.allminilm,
            "indobert": self.indobert        
        }
        
        if option not in model_options:
            raise ValueError("Invalid option. Choose 'bgem3', 'allminilm', or 'indobert'.")
            
        model = model_options[option]
        
        # Encode the query using the selected model
        query_embedding = self._encode_query(query, model)
        
        # First, get relevant publications
        publications = self._search(query_embedding, 1000, option)  # Get top 100 publications
        
        if not publications:
            return []
        
        # Compile advisor frequencies
        advisor_data = {}
        
        for pub in publications:
            for author in pub['authors']:
                author = author.strip()
                if not author:
                    continue
                    
                if author not in advisor_data:
                    advisor_data[author] = {
                        'count': 0,
                        'publications': [],
                        'avg_distance': 0.0
                    }
                    
                advisor_data[author]['count'] += 1
                advisor_data[author]['publications'].append({
                    'id': pub['id'],
                    'title': pub['title'],
                    'distance': pub['distance']
                })
                
                # Update average distance
                avg_dist = sum(p['distance'] for p in advisor_data[author]['publications']) / len(advisor_data[author]['publications'])
                advisor_data[author]['avg_distance'] = avg_dist
        
        # Convert to a list and sort by frequency and then by average distance
        advisors = [
            {
                'name': name,
                'publication_count': data['count'],
                'publications': sorted(data['publications'], key=lambda x: x['distance'])[:5],  # Top 5 most relevant publications
                'relevance_score': 1.0 - data['avg_distance']  # Convert distance to similarity score
            }
            for name, data in advisor_data.items()
        ]
        
        # Sort by publication count (descending) and then by relevance (descending)
        advisors.sort(key=lambda x: (x['publication_count'], x['relevance_score']), reverse=True)
        
        # Return top k advisors
        return advisors[:top_k]
    
    def search_advisor_2(self, query: str, top_k: int = 10, option: str = "bgem3") -> List[Dict[str, Any]]:
        """
        Searches for advisors/users with expertise related to the provided query,
        ranking based purely on semantic similarity scores.

        Args:
            query (str): The search query.
            top_k (int): The number of top advisors to return.
            option (str): The model to use for searching ('bgem3', 'allminilm', or 'indobert').

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing the top advisors with percentage-based relevance scores.
        """
        # Select embedding model based on option
        model_options = {
            "bgem3": self.bgem3,
            "allminilm": self.allminilm,
            "indobert": self.indobert        
        }
        
        if option not in model_options:
            raise ValueError("Invalid option. Choose 'bgem3', 'allminilm', or 'indobert'.")
            
        model = model_options[option]
        
        # Encode the query using the selected model
        query_embedding = self._encode_query(query, model)
        
        # Get relevant publications - retrieve more for better statistics
        publications = self._search(query_embedding, 200, option)
        
        if not publications:
            return []
        
        # Compile advisor data with similarity scores
        advisor_data = {}
        
        # Track max value for normalization
        max_similarity_score = 0.0
        for pub in publications:
            # Convert distance to similarity (1.0 = exact match, 0.0 = completely different)
            # Note: We don't use 1-distance since distances may not be in the 0-1 range
            # Instead we use 1/distance which works for any positive distance metric
            for author in pub['authors']:
                author = author.strip()
                if not author:
                    continue
                    
                if author not in advisor_data:
                    advisor_data[author] = {
                        'similarity_score': 0.0,
                        'publications': [],
                        'best_match': None,
                        'best_similarity': 0.0,
                        'publication_count': 0
                    }
                
                # We'll use 1/distance for similarity (higher is better)
                # Add a small epsilon to prevent division by zero
                epsilon = 1e-10
                similarity_value = 1.0 / (pub['distance'] + epsilon)
                
                # Accumulate similarity scores
                advisor_data[author]['similarity_score'] += similarity_value
                max_similarity_score = max(max_similarity_score, advisor_data[author]['similarity_score'])
                
                # Increment publication count (for informational purposes only)
                advisor_data[author]['publication_count'] += 1
                # Store publication with its similarity
                publication_entry = {
                    'id': pub['id'],
                    'title': pub['title'],
                    'similarity': similarity_value,
                    'similarity_percentage': round((similarity_value / (1.0 + similarity_value)) * 100, 1)  # Normalize to 0-100%
                }
                advisor_data[author]['publications'].append(publication_entry)
                
                # Track the best matching publication
                if similarity_value > advisor_data[author]['best_similarity']:
                    advisor_data[author]['best_similarity'] = similarity_value
                    advisor_data[author]['best_match'] = publication_entry
        
        # Normalize and calculate final scores (prevent division by zero)
        max_similarity_score = max(max_similarity_score, 0.01)
        
        # Calculate normalized scores
        advisors = []
        for name, data in advisor_data.items():
            # Normalize similarity score to a percentage
            normalized_score = (data['similarity_score'] / max_similarity_score) * 100
            advisors.append({
                'name': name,
                'relevance_score': round(normalized_score, 1),  # Overall relevance score (0-100%)
                'best_match': data['best_match'],
                'publication_count': data['publication_count'],  # Included for information only
                'best_match_score': round((data['best_similarity'] / (1.0 + data['best_similarity'])) * 100, 1),  # Best single match percentage
                'publications': sorted(data['publications'], key=lambda x: x['similarity'], reverse=True)[:5]  # Top 5 most relevant
            })
        
        # Sort by the relevance score (descending)
        advisors.sort(key=lambda x: x['relevance_score'], reverse=True)
          # Return top k advisors
        return advisors[:top_k]
    
    def search_advisor_3(self, query: str, top_k: int = 10, option: str = "bgem3", count_weight: float = 0.4, program_ids: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Searches for advisors/users with expertise related to the provided query,
        with balanced ranking based on both publication count and semantic similarity.

        Args:
            query (str): The search query.
            top_k (int): The number of top advisors to return.
            option (str): The model to use for searching ('bgem3', 'allminilm', or 'indobert').
            count_weight (float): Weight given to publication count (0.0-1.0). Similarity weight will be (1-count_weight).

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing the top advisors with combined relevance scores.
        """
        # Select embedding model based on option
        model_options = {
            "bgem3": self.bgem3,
            "allminilm": self.allminilm,
            "indobert": self.indobert        
        }
        
        if option not in model_options:
            raise ValueError("Invalid option. Choose 'bgem3', 'allminilm', or 'indobert'.")
            
        model = model_options[option]
        
        # Encode the query using the selected model
        query_embedding = self._encode_query(query, model)
        
        # Get relevant publications - retrieve more for better statistics
        publications = self._search(query_embedding, 1000, option)
        
        if not publications:
            return []

        # Optional: Fetch allowed authors from program_user table
        allowed_authors = None
        if program_ids is not None:
            conn = self._connect_db()
            placeholders = ','.join(['?'] * len(program_ids))
            query = f'''
                SELECT u.name
                FROM users u
                JOIN program_user pu ON pu.user_id = u.id
                WHERE pu.program_id IN ({placeholders})
            '''
            cursor = conn.execute(query, program_ids)
            allowed_authors = set(row[0] for row in cursor.fetchall())
        
        # Compile advisor data with both count and similarity scores
        advisor_data = {}
        
        # Track max values for normalization
        max_similarity_score = 0.0
        max_pub_count = 0
        
        for pub in publications:
            # Calculate similarity from distance
            epsilon = 1e-10
            similarity_value = 1.0 / (pub['distance'] + epsilon)
            
            for author in pub['authors']:
                author = author.strip()
                if not author:
                    continue

                if allowed_authors is not None and author not in allowed_authors:
                    continue
                    
                if author not in advisor_data:
                    advisor_data[author] = {
                        'similarity_score': 0.0,
                        'publications': [],
                        'best_match': None,
                        'best_similarity': 0.0,
                        'publication_count': 0
                    }
                
                # Accumulate similarity scores
                advisor_data[author]['similarity_score'] += similarity_value
                max_similarity_score = max(max_similarity_score, advisor_data[author]['similarity_score'])
                
                # Increment and track publication count
                advisor_data[author]['publication_count'] += 1
                max_pub_count = max(max_pub_count, advisor_data[author]['publication_count'])
                
                # Store publication with its similarity
                publication_entry = {
                    'id': pub['id'],
                    'title': pub['title'],
                    'similarity': similarity_value,
                    'similarity_percentage': round((similarity_value / (1.0 + similarity_value)) * 100, 1), # Normalize to 0-100%
                    'url': pub['url'],
                }
                advisor_data[author]['publications'].append(publication_entry)
                
                # Track the best matching publication
                if similarity_value > advisor_data[author]['best_similarity']:
                    advisor_data[author]['best_similarity'] = similarity_value
                    advisor_data[author]['best_match'] = publication_entry
        
        # Prevent division by zero
        max_similarity_score = max(max_similarity_score, 0.01)
        max_pub_count = max(max_pub_count, 1)
        
        # Weight factors
        similarity_weight = 1.0 - count_weight
        
        # Calculate combined scores
        advisors = []
        for name, data in advisor_data.items():
            # Normalize individual metrics (0-100%)
            normalized_count = (data['publication_count'] / max_pub_count) * 100
            normalized_similarity = (data['similarity_score'] / max_similarity_score) * 100
            
            # Calculate combined score
            combined_score = (
                (normalized_count * count_weight) + 
                (normalized_similarity * similarity_weight)
            )
            
            
            advisors.append({
                'name': name,
                'combined_score': round(combined_score, 1),  # Overall combined score (0-100%)
                'publication_count': data['publication_count'],
                'count_percentage': round(normalized_count, 1),  # Publication count as percentage of max
                'relevance_score': round(normalized_similarity, 1),  # Semantic relevance score
                'best_match': data['best_match'],
                'best_match_score': round((data['best_similarity'] / (1.0 + data['best_similarity'])) * 100, 1),
                'publications': sorted(data['publications'], key=lambda x: x['similarity'], reverse=True),  # Top 5 most relevant
                'url_picture': self._get_author_data(name).get('url_picture', '')
            })
        
        # Sort by the combined score (descending)
        advisors.sort(key=lambda x: x['combined_score'], reverse=True)
        
        # Return top k advisors
        return advisors[:top_k]

    # def _get_advisor_prodi(self, name: str) -> Dict[str, Any]:
    def _get_author_data(self, name: str) -> Dict[str, Any]:
        """
        Retrieves detailed information about an author by their ID.
        
        Args:
            author_id (int): The ID of the author to retrieve.
            program_id (int, optional): The program ID to filter by. Defaults to None.
            
        Returns:
            Dict[str, Any]: A dictionary containing the author's details.
        """
        conn = self._connect_db()

        query = '''
            SELECT *
            FROM users 
            WHERE name LIKE ?
        '''
        
        cursor = conn.execute(query, (name,))
        row = cursor.fetchall()
        
        if row and len(row) == 1:
            row = row[0]  # Get the first (and only) row
            # Get the picture URL, prioritizing url_picture_dewey if available
            url_picture = row[6] if row[6] is not None and row[6] != "" else row[5]
            # Store the author name before potentially modifying url_picture
            author_name = row[2]
            
            # Set custom profile pictures for specific authors
            if author_name == "Liliana":
                url_picture = "https://informatics.petra.ac.id/wp-content/uploads/2023/07/cropped-Liliana-S.T.M.Eng_.-Ph.D-scaled-1.jpg"
            elif author_name == "Gregorius Satiabudhi":
                url_picture = "https://informatics.petra.ac.id/wp-content/uploads/2023/07/cropped-Dr.-Gregorius-Satiabudhi-S.T.-M.T-scaled-1.jpg"
            elif author_name == "Hans Juwiantho S.Kom":
                url_picture = "https://informatics.petra.ac.id/wp-content/uploads/2023/07/cropped-Hans-Juwiantho-S.Kom_.-M.Kom_-scaled-1.jpg"
            
            print(row[4])
            return {
                'id': row[0],
                'scholar_id': row[1],
                'name': author_name,
                'original_names': row[3],
                'interests': row[4],
                'url_picture': url_picture
            }
            
        print(row)
        
        return {}

    def get_all_programs(self) -> List[Dict[str, Any]]:
        """
        Retrieves all programs from the 'programs' table.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries where each dictionary contains
                                  information about a single program.
        """
        conn = self._connect_db()
        query = '''
            SELECT * FROM programs
        '''
        cursor = conn.execute(query)
        rows = cursor.fetchall()

        programs = []
        for row in rows:
            programs.append({
                'id': row[0],
                'name': row[1],
                'url': row[2]
            })

        return programs
    
    def _connect_db(self) -> sqlite3.Connection:
        """
        Connects to the SQLite database.
        
        Returns:
            sqlite3.Connection: A connection to the SQLite database.
        """
        db = sqlite3.connect(DB_PATH, check_same_thread=False)
        db.enable_load_extension(True)
        sqlite_vec.load(db)
        db.enable_load_extension(False)
        return db
    
    def _encode_query(self, query: str, model) -> List[float]:
        """
        Encodes a query string using the specified model.
        
        Args:
            query (str): The query string to encode.
            model: The model to use for encoding.
            
        Returns:
            List[float]: The embedding vector for the query.
        """
        try:
            if model == self.bgem3:
                return self.bgem3.encode([query])['dense_vecs'][0]
            elif model == self.allminilm:
                return self.allminilm.encode(query)
            elif model == self.indobert:
                print("before translation:", query)
                query = self.translator.translate(query) if self.translator else query
                print("after translation:", query)
                return self.indobert.encode(query)
            else:
                raise ValueError(f"Unsupported model: {model}")
        except Exception as e:
            print(f"Error encoding query: {str(e)}")
            # Return a zero vector as fallback (adjust size based on your models)
            return [0.0] * 768
        
    def _search(self, query_embedding: List[float], top_k: int = 5, option: str = "bgem3") -> List[Dict[str, Any]]:
        """
        Searches for similar thesis documents based on the provided query embedding.
        
        Args:
            query_embedding (List[float]): The embedding vector of the query.
            top_k (int): The number of top results to return.
            option (str): The type of model used for the search ('bgem3', 'allminilm', or 'indobert').
            
        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing the search results.
        """
        conn = self._connect_db()
        # Map model types to their corresponding table names
        model_table_map = {
            "bgem3": "publications_vec_bge_m3",
            "allminilm": "publications_vec_all_MiniLM_L6_v2",
            "indobert": "publications_vec_indobert"
        }
        
        if option not in model_table_map:
            raise ValueError(f"Invalid model type: {option}. Choose from 'bgem3', 'allminilm', or 'indobert'.")
        
        table_name = model_table_map[option]
        
        # Perform KNN search to get top matches
        query = f'''
        SELECT publication_id, distance 
        FROM {table_name} 
        WHERE embedding MATCH ? 
        ORDER BY distance 
        LIMIT ?
        '''

        cursor = conn.execute(query, [query_embedding, top_k])

        matches = cursor.fetchall()
        
        if not matches:
            return []
            
        # Get publication details and authors for each match
        publication_ids = [str(match[0]) for match in matches]
        placeholders = ','.join(['?'] * len(publication_ids))
        
        query = f'''
        SELECT p.id, p.title, p.abstract, GROUP_CONCAT(u.name, '; ') as authors, p.url
        FROM publications p
        LEFT JOIN publication_user_mapping pum ON p.id = pum.publication_id
        LEFT JOIN users u ON pum.user_id = u.id
        WHERE p.id IN ({placeholders})
        GROUP BY p.id, p.title, p.abstract, p.url
        ORDER BY CASE p.id {' '.join([f'WHEN {pid} THEN {i}' for i, pid in enumerate(publication_ids)])} END
        '''

        cursor = conn.execute(query, publication_ids)
        result_rows = cursor.fetchall()

        # Format the results as a list of dictionaries
        results = []
        for row in result_rows:
            pub_id, title, abstract, authors, url = row
            distance = next(match[1] for match in matches if match[0] == pub_id)
            
            # Split authors string into a list
            author_list = authors.split('; ') if authors else []
            
            results.append({
                'id': pub_id,
                'title': title,
                'abstract': abstract,
                'authors': author_list,
                'distance': distance,
                'url': url
            })
            
        return results
        
        