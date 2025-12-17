import pandas as pd
from data_pipeline.processing import cleanup_sqlite


def test_create_database(tmp_path, monkeypatch):
    monkeypatch.setattr(cleanup_sqlite, "os", cleanup_sqlite.os)
    monkeypatch.setattr(cleanup_sqlite.os.path, "exists", lambda p: False)
    monkeypatch.setattr(cleanup_sqlite, "sqlite3", cleanup_sqlite.sqlite3)

    conn, cursor = cleanup_sqlite.create_database()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [t[0] for t in cursor.fetchall()]
    assert set(tables).issuperset(
        {"users", "publications", "publication_user_mapping"})
    conn.close()


def test_load_users(tmp_path, monkeypatch):
    df = pd.DataFrame([
        {"dewey_id": 1, "scholar_id": "s1", "name": "Alice",
            "original_names": "A. Smith", "interests": "AI", "url_picture": "pic1.jpg"},
        {"dewey_id": 2, "scholar_id": "s2", "name": "Bob",
            "original_names": "B. Doe", "interests": "ML", "url_picture": "pic2.jpg"}
    ])
    monkeypatch.setattr(cleanup_sqlite.pd, "read_csv", lambda _: df)
    conn, cursor = cleanup_sqlite.create_database()

    cleanup_sqlite.load_users(cursor, conn)

    cursor.execute("SELECT COUNT(*) FROM users")
    assert cursor.fetchone()[0] == 2

    conn.close()


def test_load_dewey_publications(tmp_path, monkeypatch):
    df = pd.DataFrame([
        {"dewey_thesis_id": "123", "year": 2020, "title": "Paper1",
         "abstract": "Abstract1", "dewey_ids": "1;2"},
        {"dewey_thesis_id": "124", "year": 2021, "title": "Paper2",
         "abstract": "Abstract2", "dewey_ids": ""}
    ])
    monkeypatch.setattr(cleanup_sqlite.pd, "read_csv", lambda _: df)
    conn, cursor = cleanup_sqlite.create_database()

    cleanup_sqlite.load_dewey_publications(cursor, conn)

    cursor.execute("SELECT COUNT(*) FROM publications")
    pub_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM publication_user_mapping")
    map_count = cursor.fetchone()[0]

    assert pub_count == 2
    assert map_count > 0

    conn.close()


def test_load_scholar_publications(tmp_path, monkeypatch):
    authors_df = pd.DataFrame([
        {"dewey_id": 1, "scholar_id": "s1"},
        {"dewey_id": 2, "scholar_id": "s2"}
    ])
    publications_df = pd.DataFrame([
        {"year": 2022, "title": "Scholar Paper", "abstract": "Test",
         "url": "url1", "scholar_ids": "s1;s3"}
    ])

    def fake_read_csv(path):
        path = str(path)
        if "merged_authors" in path:
            return authors_df
        if "cleaned_publications" in path:
            return publications_df
        raise ValueError("Unexpected path: " + path)
    monkeypatch.setattr(cleanup_sqlite.pd, "read_csv", fake_read_csv)
    conn, cursor = cleanup_sqlite.create_database()

    cleanup_sqlite.load_scholar_publications(cursor, conn)

    cursor.execute("SELECT COUNT(*) FROM publications")
    pub_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM publication_user_mapping")
    map_count = cursor.fetchone()[0]

    assert pub_count == 1
    assert map_count == 1

    conn.close()
