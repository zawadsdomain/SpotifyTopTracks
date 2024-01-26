
from flask import Flask, render_template, request

from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json

app = Flask(__name__)


@app.route("/", methods=["POST", "GET"])
def home():
    return render_template("index.html")

@app.route("/search", methods=["POST", "GET"])
def search():
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    artist_name = request.form.get('artist_name')
    token = get_token(client_id=client_id, client_secret=client_secret)
    result = search_for_artist(token, artist_name)

    if result:
        artist_id = result['id']
        songs = get_songs_by_artist(token, artist_id)
        return render_template('result.html', songs=songs)

    return render_template('no_result.html')
    
def get_token(client_id, client_secret): 
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"} 
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def search_for_artist(token, artist_name): 
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = "?q={}&type=artist&limit=1".format(artist_name)
    
    query_url = url + query

    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["artists"]["items"]

    if len(json_result) == 0:
        print("No artist with this name exists...")
        return None

    return json_result[0]

def get_songs_by_artist(token, artist_id):
    url = "https://api.spotify.com/v1/artists/{}/top-tracks?country=US".format(artist_id)
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["tracks"]
    return json_result

    
if __name__ == "__main__":
    app.run(debug=True)