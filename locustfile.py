import time
from locust import HttpUser, task, between

class DefaultUser(HttpUser):
    search_query = "Computer Networking"
    model = "bgem3"
    top_k = 100

    @task
    def author_search(self):
        self.client.get(f"/search/author/{self.search_query}?topK={self.top_k}&model={self.model}")

    @task
    def paper_search(self):
        self.client.get(f"/search/paper/{self.search_query}?topK={self.top_k}&model={self.model}")
