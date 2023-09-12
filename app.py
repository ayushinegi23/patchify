from dotenv import load_dotenv
from flask import Flask, request, url_for, session, redirect, render_template
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import os

load_dotenv()

CLIENT_ID= os.getenv("CLIENT_ID")
CLIENT_SECRET= os.getenv("CLIENT_SECRET")

app = Flask(__name__)

app.secret_key = "randomKey"
app.config['SESSION_COOKIE_NAME'] = 'Cookie Monster'
TOKEN_INFO= "token_info"


@app.route('/')
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


@app.route('/redirect')
def redirectPage():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for('getTopTracks', _external=True))

@app.route('/getTopTracks')

def getTopTracks():
    try: 
        global token_info
        token_info = get_token()
    except:
        print("User Not Logged In")
        redirect("/")

    sp = spotipy.Spotify(auth=token_info['access_token'])

    LIMIT = 9

    top_songs_data = sp.current_user_top_tracks(limit=LIMIT, offset=0, time_range='medium_term')
    
    top_songs_list = []
    for x in range(LIMIT):
        top_songs_list.append(str(top_songs_data['items'][x]['album']['images'][0]['url']))


    return render_template('top_tracks.html', top_songs_list=top_songs_list) 
    #return top_songs_data
    
    

def get_token():
    global token_info
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        raise "exception"
    
    now = int(time.time())
    expired = token_info['expired_at'] - now < 60

    if expired:
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])

    return token_info


def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=url_for('redirectPage', _external=True),
        scope ="user-library-read user-top-read"
        )