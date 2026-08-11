from app.auth.graph_auth import GraphAuth

token = GraphAuth.get_access_token()

print(token)