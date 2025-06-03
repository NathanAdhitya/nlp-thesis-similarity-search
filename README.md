# nlp-thesis-similarity-search

## How to run
1. **Clone the repository** or **download the ZIP** file.
2. In the root directory, run `python app.py` to start the Flask API server.  
   Wait a few seconds for the server to fully start — check the terminal output to confirm it's running.
3. Navigate to the `ui` folder:

   ```bash
   cd ui
   npm install
   npm run dev

## Endpoint
### 1. Search

**URL**: `/search/:query`

**Method**: `GET`

**Description**: Search Based on Query

**Response**:

- Status: `200 - Ok`
- Body:

```json
{
  "message": "Data retrieved successfully",
  "data": {
    "topPapers": [
      {
        "title": "Paper Title A",
        "score": "0.58",
        "author": "Author A",
        "abstract": "This is abstract. This is abstract. This is abstract. This is abstract. This is abstract. " 
          "This is abstract. This is abstract. This is abstract. This is abstract. This is abstract. " 
          "This is abstract. This is abstract. This is abstract. This is abstract. This is abstract."
      },
      {
        "title": "Paper Title A",
        "score": "0.58",
        "author": "Author A",
        "abstract": "This is abstract. This is abstract. This is abstract. This is abstract. This is abstract. " 
          "This is abstract. This is abstract. This is abstract. This is abstract. This is abstract. " 
          "This is abstract. This is abstract. This is abstract. This is abstract. This is abstract."
      }  
    ],
    "topAuthors": [
      {
        "name": "Author A",
        "score": "0.56",
        "thesis": [
          {
            "title": "Paper Title A",
            "score": "0.58",
            "author": "Author A",
            "abstract": "This is abstract. This is abstract. This is abstract. This is abstract. This is abstract. " 
              "This is abstract. This is abstract. This is abstract. This is abstract. This is abstract. " 
              "This is abstract. This is abstract. This is abstract. This is abstract. This is abstract."
          },
          {
            "title": "Paper Title A",
            "score": "0.58",
            "author": "Author A",
            "abstract": "This is abstract. This is abstract. This is abstract. This is abstract. This is abstract. " 
              "This is abstract. This is abstract. This is abstract. This is abstract. This is abstract. " 
              "This is abstract. This is abstract. This is abstract. This is abstract. This is abstract."
          }
        ]
      }
    ]
  }
}
```
