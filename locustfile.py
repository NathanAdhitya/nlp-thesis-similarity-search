import time
from locust import HttpUser, User, task, between, tag, TaskSet




def create_task(model: str):
    search_query: str = "Computer Networking"
    top_k: int = 100
    
    @tag(model, "author_search")
    @task
    def author_search(self):
        self.client.get(
            f"/search/author/{search_query}?topK={top_k}&model={model}"
        )

    @tag(model, "paper_search")
    @task
    def paper_search(self):
        self.client.get(
            f"/search/paper/{search_query}?topK={top_k}&model={model}"
        )
        
    return author_search, paper_search

class DefaultUser(HttpUser):
    models = [
        "bgem3",
        "allminilm",
        "indobert"
    ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for model in self.models:
            tasks = create_task(model)
            for task in tasks:
                self.tasks.append(task)