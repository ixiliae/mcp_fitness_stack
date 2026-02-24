import webbrowser
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
import os

CLIENT_ID = os.environ.get("STRAVA_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("STRAVA_CLIENT_SECRET", "")
REDIRECT_URI = "http://localhost:8080/callback"

auth_code = None

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        auth_code = params.get("code", [None])[0]
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK - tu peux fermer cette fenetre")

# Ouvre le navigateur pour l'autorisation
url = (f"https://www.strava.com/oauth/authorize?client_id={CLIENT_ID}"
       f"&redirect_uri={REDIRECT_URI}&response_type=code"
       f"&scope=activity:read_all")
webbrowser.open(url)

# Attend le callback
server = HTTPServer(("localhost", 8080), CallbackHandler)
server.handle_request()  # une seule requête puis on stoppe

# Échange le code contre les tokens
resp = requests.post("https://www.strava.com/oauth/token", data={
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "code": auth_code,
    "grant_type": "authorization_code",
})
tokens = resp.json()
print("Access token :", tokens["access_token"])
print("Refresh token:", tokens["refresh_token"])  # ← sauvegarde celui-ci !
