import base64
import json

from app.auth.graph_auth import GraphAuth


token = GraphAuth.get_access_token()

payload = token.split(".")[1]

payload += "=" * (-len(payload) % 4)

decoded = json.loads(base64.urlsafe_b64decode(payload))

print(json.dumps(decoded, indent=4))