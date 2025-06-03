# nlp-thesis-similarity-search

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
