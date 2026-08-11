from app.clients.graph_client import GraphClient

client = GraphClient.get_client()

response = client.get("/users")

print(response.status_code)
print(response.json())