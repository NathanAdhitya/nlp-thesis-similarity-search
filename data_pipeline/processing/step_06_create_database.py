"""
Database creation and population script for Semantica.

This module creates the SQLite database schema and populates it with data from
the processed CSV files (merged_authors.csv, cleaned_dewey.csv, cleaned_publications.csv).
"""

import sqlite3
import os
import sys
from typing import Tuple
import pandas as pd


def create_database() -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
    """
    Create the SQLite database with the required schema.
    
    Returns:
        Tuple of (connection, cursor) for the created database.
    """
    try:
        from data_pipeline.processing.path_utils import get_database_file
    except ImportError:
        from path_utils import get_database_file
    
    # Database path
    db_path = str(get_database_file())
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Create connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        scholar_id TEXT,
        name TEXT,
        original_names TEXT,
        interests TEXT,
        url_picture TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS publications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        year INTEGER,
        title TEXT,
        abstract TEXT,
        url TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS publication_user_mapping (
        publication_id INTEGER,
        user_id TEXT,
        FOREIGN KEY (publication_id) REFERENCES publications(id),
        FOREIGN KEY (user_id) REFERENCES users(id),
        PRIMARY KEY (publication_id, user_id)
    )
    ''')
    
    return conn, cursor


def load_users(cursor: sqlite3.Cursor, conn: sqlite3.Connection) -> None:
    """
    Load user data from merged_authors.csv into the users table.
    
    Args:
        cursor: Database cursor.
        conn: Database connection.
    """
    try:
        from data_pipeline.processing.path_utils import get_merged_authors_file
    except ImportError:
        from path_utils import get_merged_authors_file
    
    # Load merged_authors.csv
    authors_df = pd.read_csv(str(get_merged_authors_file()))
    
    # Insert users data
    for _, row in authors_df.iterrows():
        cursor.execute('''
        INSERT OR REPLACE INTO users (id, scholar_id, name, original_names, interests, url_picture)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (row['dewey_id'], row['scholar_id'], row['name'], row['original_names'], 
              row['interests'], row['url_picture']))
    
    conn.commit()
    print(f"Inserted {len(authors_df)} users")


def load_dewey_publications(cursor: sqlite3.Cursor, conn: sqlite3.Connection) -> None:
    """
    Load Dewey thesis publications from cleaned_dewey.csv into the publications table.
    
    Args:
        cursor: Database cursor.
        conn: Database connection.
    """
    try:
        from data_pipeline.processing.path_utils import get_cleaned_dewey_file
    except ImportError:
        from path_utils import get_cleaned_dewey_file
    
    # Load cleaned_dewey.csv
    dewey_df = pd.read_csv(str(get_cleaned_dewey_file()))
    
    for _, row in dewey_df.iterrows():
        # Convert dewey_thesis_id to URL
        url = f"https://dewey.petra.ac.id/digital/view/{row['dewey_thesis_id']}"
        
        # Insert publication
        cursor.execute('''
        INSERT INTO publications (year, title, abstract, url)
        VALUES (?, ?, ?, ?)
        ''', (row['year'], row['title'], row['abstract'], url))
        
        publication_id = cursor.lastrowid
        
        # Handle dewey_ids mapping
        if pd.notna(row['dewey_ids']):
            dewey_ids = [did.strip() for did in str(row['dewey_ids']).split(';')]
            for dewey_id in dewey_ids:
                if dewey_id:  # Skip empty strings
                    cursor.execute('''
                    INSERT OR IGNORE INTO publication_user_mapping (publication_id, user_id)
                    VALUES (?, ?)
                    ''', (publication_id, dewey_id))
    
    conn.commit()
    print(f"Inserted {len(dewey_df)} Dewey publications")


def load_scholar_publications(cursor: sqlite3.Cursor, conn: sqlite3.Connection) -> None:
    """
    Load Google Scholar publications from cleaned_publications.csv into the publications table.
    
    Args:
        cursor: Database cursor.
        conn: Database connection.
    """
    try:
        from data_pipeline.processing.path_utils import get_cleaned_publications_file, get_merged_authors_file
    except ImportError:
        from path_utils import get_cleaned_publications_file, get_merged_authors_file
    
    # Load cleaned_publications.csv
    publications_df = pd.read_csv(str(get_cleaned_publications_file()))
    
    # Create mapping from scholar_id to dewey_id
    authors_df = pd.read_csv(str(get_merged_authors_file()))
    scholar_to_dewey = dict(zip(authors_df['scholar_id'], authors_df['dewey_id']))
    
    for _, row in publications_df.iterrows():
        # Insert publication
        cursor.execute('''
        INSERT INTO publications (year, title, abstract, url)
        VALUES (?, ?, ?, ?)
        ''', (row['year'], row['title'], row['abstract'], row['url']))
        
        publication_id = cursor.lastrowid
        
        # Handle scholar_ids mapping
        if pd.notna(row['scholar_ids']):
            scholar_ids = [sid.strip() for sid in str(row['scholar_ids']).split(';')]
            for scholar_id in scholar_ids:
                if scholar_id in scholar_to_dewey:
                    dewey_id = scholar_to_dewey[scholar_id]
                    cursor.execute('''
                    INSERT OR IGNORE INTO publication_user_mapping (publication_id, user_id)
                    VALUES (?, ?)
                    ''', (publication_id, dewey_id))
    
    conn.commit()
    print(f"Inserted {len(publications_df)} Scholar publications")


def main() -> None:
    """Main function to create database and load all data."""
    try:
        # Create database and tables
        conn, cursor = create_database()
        
        # Load data
        load_users(cursor, conn)
        load_dewey_publications(cursor, conn)
        load_scholar_publications(cursor, conn)
        
        # Print summary
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM publications")
        pub_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM publication_user_mapping")
        mapping_count = cursor.fetchone()[0]
        
        print(f"\nDatabase created successfully!")
        print(f"Users: {user_count}")
        print(f"Publications: {pub_count}")
        print(f"Mappings: {mapping_count}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        from data_pipeline.processing.path_utils import get_database_file
    except ImportError:
        from path_utils import get_database_file
    import os
    
    # Skip if database already exists
    db_path = str(get_database_file())
    if os.path.exists(db_path):
        print(f"[SKIP] Database already exists: {db_path}")
        print("Delete the database to regenerate or run processing manually.")
        exit(0)
    
    main()

