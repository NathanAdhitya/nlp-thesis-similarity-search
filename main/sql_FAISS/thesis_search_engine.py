import numpy as np
import faiss
import json
import mysql.connector
from typing import List, Dict, Any, Optional, Tuple, Union
from sentence_transformers import SentenceTransformer
from main.sql_FAISS.search_utils import get_embedding, print_formatted_results

class ThesisSimilaritySearch:
    def __init__(self, model, use_title=False, use_abstract=True):
        """
        Initialize the similarity search engine
        
        Args:
            model: The SentenceTransformer model to use for encoding queries
            use_title: Whether to use title embeddings for similarity search
            use_abstract: Whether to use abstract embeddings for similarity search
        """
        self.model = model
        self.use_title = use_title
        self.use_abstract = use_abstract
        
        # Model name is used in column names
        self.model_name = model._modules['0'].auto_model.config.name_or_path
        
        # These will be populated when load_index is called
        self.index = None
        self.paper_ids = []
        self.paper_metadata = {}
    
    def load_index(self, cursor, limit=None):
        """
        Load embeddings from database and build FAISS index
        
        Args:
            cursor: MySQL database cursor
            limit: Optional limit on number of papers to load
        """
        # Determine which embedding column to use
        if self.use_abstract and not self.use_title:
            embedding_column = f"abstract_embeddings_{self.model_name[22:]}"  # Remove 'sentence-transformers/' prefix
            print(f"Using abstract embeddings ({embedding_column[22:]})")
        elif self.use_title and not self.use_abstract:
            embedding_column = f"title_embeddings_{self.model_name[22:]}"  # Remove 'sentence-transformers/' prefix
            print(f"Using title embeddings ({embedding_column[22:]})")
        else:
            # Default to abstract if both or neither are specified
            embedding_column = f"abstract_embeddings_{self.model_name[22:]}"  # Remove 'sentence-transformers/' prefix
            print(f"Using abstract embeddings ({embedding_column[22:]})")
        
        # Build query with limit if provided
        query = f"""
        SELECT id, title, abstract, `{embedding_column}`
        FROM dewey_papers 
        WHERE `{embedding_column}` IS NOT NULL
        """
        if limit:
            query += f" LIMIT {limit}"
            
        # Execute query
        cursor.execute(query)
        papers = cursor.fetchall()
        
        if not papers:
            raise ValueError(f"No papers found with {embedding_column} not null")
            
        print(f"Loaded {len(papers)} papers with embeddings")
        
        # Extract data for index building
        self.paper_ids = []
        self.paper_metadata = {}
        embeddings = []
        
        for paper in papers:
            paper_id = paper[0]
            title = paper[1]
            abstract = paper[2]
            embedding_json = paper[3]
            
            # Skip papers with null embeddings
            if embedding_json is None:
                continue
                
            # Parse JSON embedding if it's a string
            if isinstance(embedding_json, str):
                try:
                    embedding = json.loads(embedding_json)
                except json.JSONDecodeError:
                    print(f"Error decoding embedding for paper {paper_id}")
                    continue
            else:
                embedding = embedding_json
                
            # Add to our collections
            self.paper_ids.append(paper_id)
            self.paper_metadata[paper_id] = {
                'id': paper_id,
                'title': title,
                'abstract': abstract,
                'authors': [],     # Initialize empty authors list to be filled later
                'contributors': []  # Initialize empty contributors list to be filled later
            }
            embeddings.append(embedding)
        
        # Fetch authors and contributors for all papers
        self._fetch_authors(cursor)
        self._fetch_contributors(cursor)
        
        # Convert embeddings to numpy array
        embeddings_array = np.array(embeddings).astype('float32')
        
        # Create and build the FAISS index
        dimension = embeddings_array.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings_array)
        
        print(f"Built FAISS index with {self.index.ntotal} vectors of dimension {dimension}")
        return self.index
    
    def _fetch_authors(self, cursor):
        """
        Fetch authors for all papers in paper_metadata
        
        Args:
            cursor: MySQL database cursor
        """
        if not self.paper_ids:
            return
            
        # Format paper IDs for SQL IN clause
        paper_ids_str = ", ".join([f"'{pid}'" for pid in self.paper_ids])
        
        # Query to get authors for all papers in one go
        query = f"""
        SELECT pc.paper_id, c.name 
        FROM paper_creators pc
        JOIN creators c ON pc.creator_id = c.id
        WHERE pc.paper_id IN ({paper_ids_str})
        ORDER BY pc.paper_id, c.name
        """
        
        cursor.execute(query)
        author_results = cursor.fetchall()
        
        # Group authors by paper_id
        for paper_id, author_name in author_results:
            if paper_id in self.paper_metadata:
                self.paper_metadata[paper_id]['authors'].append(author_name)
        
        # Count papers with authors
        papers_with_authors = sum(1 for pid in self.paper_ids if self.paper_metadata[pid]['authors'])
        print(f"Found authors for {papers_with_authors} out of {len(self.paper_ids)} papers")
        
    def _fetch_contributors(self, cursor):
        """
        Fetch contributors for all papers in paper_metadata
        
        Args:
            cursor: MySQL database cursor
        """
        if not self.paper_ids:
            return
            
        # Format paper IDs for SQL IN clause
        paper_ids_str = ", ".join([f"'{pid}'" for pid in self.paper_ids])
        
        # Query to get contributors for all papers in one go
        query = f"""
        SELECT pc.paper_id, c.name, pc.role
        FROM paper_contributors pc
        JOIN contributors c ON pc.contributor_id = c.id
        WHERE pc.paper_id IN ({paper_ids_str})
        ORDER BY pc.paper_id, pc.role, c.name
        """
        
        cursor.execute(query)
        contributor_results = cursor.fetchall()
        
        # Group contributors by paper_id
        for paper_id, contributor_name, role in contributor_results:
            if paper_id in self.paper_metadata:
                self.paper_metadata[paper_id]['contributors'].append({
                    'name': contributor_name,
                    'role': role
                })
        
        # Count papers with contributors
        papers_with_contributors = sum(1 for pid in self.paper_ids if self.paper_metadata[pid]['contributors'])
        print(f"Found contributors for {papers_with_contributors} out of {len(self.paper_ids)} papers")
    
    def search(self, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar papers using the provided query text
        
        Args:
            query_text: The text query to search for
            top_k: Number of results to return
            
        Returns:
            List of dictionaries containing search results with metadata and similarity scores
        """
        if self.index is None:
            raise ValueError("Index not built. Call load_index first.")
            
        # Convert query to embedding
        query_embedding = np.array(get_embedding(query_text, self.model)).reshape(1, -1).astype('float32')
        
        # Search the index
        distances, indices = self.index.search(query_embedding, top_k)
        
        # Format results
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.paper_ids):
                paper_id = self.paper_ids[idx]
                metadata = self.paper_metadata[paper_id]
                
                # Calculate similarity score (convert distance to similarity)
                similarity = 1 / (1 + distances[0][i])

                results.append({
                    'id': paper_id,
                    'title': metadata['title'],
                    'abstract': metadata['abstract'],
                    'authors': metadata['authors'],
                    'contributors': metadata['contributors'],
                    'similarity_score': similarity,
                    'distance': float(distances[0][i])
                })
        
        return results


class SearchEngine:
    """
    Manager class for the ThesisSimilaritySearch engine that handles:
    - Loading and caching the search engine instance
    - Reloading with different parameters
    - Quick searches using the cached instance
    """
    
    def __init__(self, model: SentenceTransformer, cursor):
        """
        Initialize the search engine manager
        
        Args:
            model: The SentenceTransformer model to use
            cursor: MySQL database cursor
        """
        self.model = model
        self.cursor = cursor
        self.search_engine = None
    
    def load(self, use_title=True, use_abstract=False, limit=None, force_reload=False):
        """
        Load or return the cached search engine instance
        
        Args:
            use_title: Whether to use title embeddings
            use_abstract: Whether to use abstract embeddings
            limit: Optional limit on number of papers to load
            force_reload: Whether to force reload the index even if already loaded
            
        Returns:
            ThesisSimilaritySearch instance with loaded index
        """
        # Check if we already have a loaded search engine and we're not forcing a reload
        if self.search_engine is not None and not force_reload:
            print("Using cached search engine instance...")
            return self.search_engine
        
        # Create a new search engine instance
        print("Creating new search engine instance...")
        search_engine = ThesisSimilaritySearch(model=self.model, use_title=use_title, use_abstract=use_abstract)
        
        # Load the index
        try:
            search_engine.load_index(self.cursor, limit=limit)
            # Cache the loaded search engine
            self.search_engine = search_engine
            return self.search_engine
        except Exception as e:
            print(f"Error loading search engine: {e}")
            return None
    
    def reload(self, use_title=True, use_abstract=False, limit=None):
        """
        Force reload the search engine with different parameters
        
        Args:
            use_title: Whether to use title embeddings
            use_abstract: Whether to use abstract embeddings
            limit: Optional limit on number of papers to load
            
        Returns:
            ThesisSimilaritySearch instance with reloaded index
        """
        print("Forcing reload of search engine...")
        
        # Set the search engine to None to ensure we reload
        self.search_engine = None
        
        # Call load with force_reload=True
        return self.load(
            use_title=use_title, 
            use_abstract=use_abstract, 
            limit=limit, 
            force_reload=True
        )
    
    def quick_search(self, query, top_k=5, show_abstract=True, show_authors=True,
                    show_contributors=True, show_metrics=True):
        """
        Perform a quick search using the cached search engine
        
        Args:
            query: The search query
            top_k: Number of results to return
            show_abstract: Whether to display abstracts
            show_authors: Whether to display author information
            show_contributors: Whether to display contributor information
            show_metrics: Whether to display similarity score and distance
            
        Returns:
            List of search results
        """
        # Check if we have a cached search engine
        if self.search_engine is None:
            print("No cached search engine found. Loading index first...")
            self.load()
            if self.search_engine is None:
                print("Failed to load search engine.")
                return []
        
        # Perform the search
        print(f"Searching for: '{query}'")
        results = self.search_engine.search(query, top_k=top_k)
        
        # Display results
        print_formatted_results(results, 
                               show_authors=show_authors, 
                               show_contributors=show_contributors, 
                               show_abstract=show_abstract,
                               show_metrics=show_metrics)
        
        return results
    
    def search_by_people_and_topic(self, query, author_name=None, contributor_name=None, 
                                  contributor_role=None, top_k=10):
        """
        Search for papers by topic and filter by people (authors or contributors)
        
        Args:
            query: The search query for topic
            author_name: Optional author name to filter by (case-insensitive partial match)
            contributor_name: Optional contributor name to filter by (case-insensitive partial match)
            contributor_role: Optional contributor role to filter by (case-insensitive partial match)
            top_k: Number of results to return
            
        Returns:
            Filtered list of search results
        """
        # Check if we have a cached search engine
        if self.search_engine is None:
            print("No cached search engine found. Loading index first...")
            self.load()
            if self.search_engine is None:
                print("Failed to load search engine.")
                return []
        
        # Get more results than needed since we'll be filtering
        expanded_top_k = min(top_k * 5, 100)  # Get more results but cap at 100
        print(f"Searching for: '{query}' with people filters")
        results = self.search_engine.search(query, top_k=expanded_top_k)
        
        # Filter by authors if specified
        if author_name:
            author_name = author_name.lower()
            results = [r for r in results if any(author_name in author.lower() for author in r['authors'])]
        
        # Filter by contributors if specified
        if contributor_name or contributor_role:
            filtered_results = []
            for r in results:
                if 'contributors' in r and r['contributors']:
                    for contributor in r['contributors']:
                        name_match = True
                        role_match = True
                        
                        if contributor_name:
                            name_match = contributor_name.lower() in contributor['name'].lower()
                        
                        if contributor_role:
                            role_match = contributor_role.lower() in contributor['role'].lower()
                        
                        if name_match and role_match:
                            filtered_results.append(r)
                            break
            results = filtered_results
        
        # Return only up to top_k results
        return results[:top_k]
