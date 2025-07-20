# app.py
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from .models import Song
from .playlist_manager import PlaylistManager
from .linked_lists import Node, SimpleLinkedList, DoublyLinkedList, CircularLinkedList, CircularDoublyLinkedList
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import os

# Carga las variables de entorno desde el archivo .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configuración para carga de archivos
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'mp3', 'wav'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- Variables de Spotify ---
CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")
SPOTIFY_SCOPE = 'user-read-private user-read-email streaming user-modify-playback-state playlist-read-private playlist-read-collaborative'


if not all([CLIENT_ID, CLIENT_SECRET, REDIRECT_URI]):
    raise EnvironmentError("Faltan variables de entorno: SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI.")

SCOPES = "user-read-private user-read-email user-library-read playlist-read-private user-top-read user-read-playback-state user-modify-playback-state user-read-currently-playing streaming app-remote-control"
oauth_manager = SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope=SCOPES)

AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1/'

# --- Clases ---
class Song:
    def __init__(self, title, artist, duration, genre, file_path=None):
        self.title = title
        self.artist = artist
        self.duration = duration
        self.genre = genre
        self.file_path = file_path

    def to_dict(self):
        return {
            "title": self.title,
            "artist": self.artist,
            "duration": self.duration,
            "genre": self.genre,
            "file_path": self.file_path
        }

class User:
    def __init__(self, username, is_premium=False):
        self.username = username
        self.is_premium = is_premium

    def upgrade_to_premium(self):
        self.is_premium = True

    def to_dict(self):
        return {"username": self.username, "is_premium": self.is_premium}

class Node:
    def __init__(self, song):
        self.song = song
        self.next = None

class DoublyNode(Node):
    def __init__(self, song):
        super().__init__(song)
        self.prev = None

class Playlist:
    def __init__(self):
        self.current_item = None
        self.size = 0

    def add_item(self, song):
        raise NotImplementedError

    def remove_item(self):
        raise NotImplementedError

    def get_current_item(self):
        return self.current_item.song if self.current_item else None

    def next_item(self):
        raise NotImplementedError

    def previous_item(self):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    def get_all_songs(self):
        songs = []
        if not self.current_item:
            return songs
        if hasattr(self, 'head') and self.head:
            if isinstance(self, (SimpleLinkedList, DoublyLinkedList)):
                current = self.head
                while current:
                    songs.append(current.song.to_dict())
                    current = current.next
            elif isinstance(self, (CircularLinkedList, CircularDoublyLinkedList)):
                current = self.head
                while True:
                    songs.append(current.song.to_dict())
                    current = current.next
                    if current == self.head:
                        break
        return songs

class SimpleLinkedList(Playlist):
    def __init__(self):
        super().__init__()
        self.head = None
        self.tail = None

    def add_item(self, song):
        new_node = Node(song)
        if not self.head:
            self.head = new_node
            self.tail = new_node
            self.current_item = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node
        self.size += 1

    def remove_item(self):
        if not self.head:
            return None
        removed_song = None
        if self.current_item == self.head:
            removed_song = self.head.song
            self.head = self.head.next
            if not self.head:
                self.tail = None
                self.current_item = None
            else:
                self.current_item = self.head
        else:
            prev_node = self.head
            while prev_node and prev_node.next != self.current_item:
                prev_node = prev_node.next
            if prev_node:
                removed_song = self.current_item.song
                prev_node.next = self.current_item.next
                if self.current_item == self.tail:
                    self.tail = prev_node
                self.current_item = prev_node.next if prev_node.next else self.head
            else:
                return None
        self.size -= 1
        return removed_song

    def next_item(self):
        if not self.head:
            return None
        if self.current_item and self.current_item.next:
            self.current_item = self.current_item.next
        else:
            self.current_item = self.head
        return self.get_current_item()

    def previous_item(self):
        if not self.head or self.current_item == self.head:
            return None
        prev = self.head
        while prev and prev.next != self.current_item:
            prev = prev.next
        self.current_item = prev
        return self.get_current_item()

    def reset(self):
        self.head = None
        self.tail = None
        self.current_item = None
        self.size = 0

    def get_all_songs(self):
        songs = []
        current = self.head
        while current:
            songs.append(current.song.to_dict())
            current = current.next
        return songs

class DoublyLinkedList(Playlist):
    def __init__(self):
        super().__init__()
        self.head = None
        self.tail = None

    def add_item(self, song):
        new_node = DoublyNode(song)
        if not self.head:
            self.head = new_node
            self.tail = new_node
            self.current_item = new_node
        else:
            self.tail.next = new_node
            new_node.prev = self.tail
            self.tail = new_node
        self.size += 1

    def remove_item(self):
        if not self.head:
            return None
        removed_song = self.current_item.song
        next_item = self.current_item.next
        prev_item = self.current_item.prev
        if prev_item:
            prev_item.next = next_item
        else:
            self.head = next_item
        if next_item:
            next_item.prev = prev_item
        else:
            self.tail = prev_item
        if self.head is None:
            self.tail = None
            self.current_item = None
        elif next_item:
            self.current_item = next_item
        elif prev_item:
            self.current_item = prev_item
        else:
            self.current_item = None
        self.size -= 1
        return removed_song

    def next_item(self):
        if not self.head:
            return None
        if self.current_item and self.current_item.next:
            self.current_item = self.current_item.next
        else:
            self.current_item = self.head
        return self.get_current_item()

    def previous_item(self):
        if not self.head:
            return None
        if self.current_item and self.current_item.prev:
            self.current_item = self.current_item.prev
        else:
            self.current_item = self.tail
        return self.get_current_item()

    def reset(self):
        self.head = None
        self.tail = None
        self.current_item = None
        self.size = 0

    def get_all_songs(self):
        songs = []
        current = self.head
        while current:
            songs.append(current.song.to_dict())
            current = current.next
        return songs

class CircularLinkedList(Playlist):
    def __init__(self):
        super().__init__()
        self.head = None

    def add_item(self, song):
        new_node = Node(song)
        if not self.head:
            self.head = new_node
            new_node.next = self.head
            self.current_item = new_node
        else:
            current = self.head
            while current.next != self.head:
                current = current.next
            current.next = new_node
            new_node.next = self.head
        self.size += 1

    def remove_item(self):
        if not self.head:
            return None
        removed_song = None
        if self.size == 1:
            removed_song = self.head.song
            self.head = None
            self.current_item = None
        else:
            prev_node = None
            current = self.head
            while True:
                if current == self.current_item:
                    break
                prev_node = current
                current = current.next
            removed_song = self.current_item.song
            if prev_node:
                prev_node.next = self.current_item.next
                if self.current_item == self.head:
                    self.head = self.current_item.next
                self.current_item = self.current_item.next
            else:
                temp = self.head
                while temp.next != self.head:
                    temp = temp.next
                temp.next = self.head.next
                self.head = self.head.next
                self.current_item = self.head
        self.size -= 1
        return removed_song

    def next_item(self):
        if not self.head:
            return None
        self.current_item = self.current_item.next
        return self.get_current_item()

    def previous_item(self):
        if not self.head:
            return None
        if self.size == 1:
            return self.get_current_item()
        prev_node = self.head
        while prev_node.next != self.current_item:
            prev_node = prev_node.next
        self.current_item = prev_node
        return self.get_current_item()

    def reset(self):
        self.head = None
        self.current_item = None
        self.size = 0

    def get_all_songs(self):
        songs = []
        if not self.head:
            return songs
        current = self.head
        while True:
            songs.append(current.song.to_dict())
            current = current.next
            if current == self.head:
                break
        return songs

class CircularDoublyLinkedList(Playlist):
    def __init__(self):
        super().__init__()
        self.head = None

    def add_item(self, song):
        new_node = DoublyNode(song)
        if not self.head:
            self.head = new_node
            new_node.next = self.head
            new_node.prev = self.head
            self.current_item = new_node
        else:
            tail = self.head.prev
            tail.next = new_node
            new_node.prev = tail
            new_node.next = self.head
            self.head.prev = new_node
        self.size += 1

    def remove_item(self):
        if not self.head:
            return None
        removed_song = self.current_item.song
        if self.size == 1:
            self.head = None
            self.current_item = None
        else:
            next_node = self.current_item.next
            prev_node = self.current_item.prev
            prev_node.next = next_node
            next_node.prev = prev_node
            if self.current_item == self.head:
                self.head = next_node
            self.current_item = next_node
        self.size -= 1
        return removed_song

    def next_item(self):
        if not self.head:
            return None
        self.current_item = self.current_item.next
        return self.get_current_item()

    def previous_item(self):
        if not self.head:
            return None
        self.current_item = self.current_item.prev
        return self.get_current_item()

    def reset(self):
        self.head = None
        self.current_item = None
        self.size = 0

    def get_all_songs(self):
        songs = []
        if not self.head:
            return songs
        current = self.head
        while True:
            songs.append(current.song.to_dict())
            current = current.next
            if current == self.head:
                break
        return songs

# Instancias globales
# Instancia global
global_user = User("SpotifyUserDemo", is_premium=False)
global_playlist_manager = PlaylistManager(playlist_type='simple')

# Middleware para verificar token
@app.before_request
def check_token_expiration():
    if request.path in ['/', '/login', '/callback'] or request.path.startswith('/static/'):
        return
    if 'access_token' not in session:
        return redirect(url_for('show_login_page'))
    expires_at = session.get('token_obtained_at', 0) + session.get('expires_in', 0) - 60
    if time.time() > expires_at:
        if 'refresh_token' in session:
            refresh_token_data = {
                'grant_type': 'refresh_token',
                'refresh_token': session['refresh_token'],
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET
            }
            response = requests.post(TOKEN_URL, data=refresh_token_data)
            new_token_info = response.json()
            if response.status_code == 200 and 'access_token' in new_token_info:
                session['access_token'] = new_token_info['access_token']
                session['expires_in'] = new_token_info['expires_in']
                session['token_obtained_at'] = int(time.time())
                if 'refresh_token' in new_token_info:
                    session['refresh_token'] = new_token_info['refresh_token']
            else:
                session.clear()
                return redirect(url_for('show_login_page'))
        else:
            session.clear()
            return redirect(url_for('show_login_page'))

# Rutas de autenticación
@app.route('/')
def show_login_page():
    return render_template('login.html', logged_in='access_token' in session)

@app.route('/login')
def login():
    scopes = 'user-read-private user-read-email playlist-read-private playlist-modify-public playlist-modify-private user-modify-playback-state user-read-playback-state'
    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'scope': scopes,
        'show_dialog': 'true'
    }
    return redirect(f"{AUTH_URL}?{'&'.join([f'{k}={v}' for k,v in params.items()])}")

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return "Error: No se recibió el código de autorización.", 400
    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    response = requests.post(TOKEN_URL, data=token_data)
    token_info = response.json()
    if 'access_token' not in token_info:
        print(f"Error al obtener tokens: {token_info.get('error_description', token_info.get('error', 'Desconocido'))}")
        return f"Error al obtener tokens: {token_info.get('error_description', token_info.get('error', 'Desconocido'))}", 400
    session['access_token'] = token_info['access_token']
    session['refresh_token'] = token_info.get('refresh_token')
    session['expires_in'] = token_info['expires_in']
    session['token_obtained_at'] = int(time.time())
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    if 'access_token' not in session:
        return redirect(url_for('show_login_page'))
    headers = {'Authorization': f"Bearer {session['access_token']}"}
    user_profile_response = requests.get(API_BASE_URL + 'me', headers=headers)
    print(f"Estado de la respuesta de Spotify: {user_profile_response.status_code}")
    print(f"Contenido RAW: {user_profile_response.text}")
    if user_profile_response.status_code == 200:
        user_profile = user_profile_response.json()
        session['spotify_user_id'] = user_profile['id']
        return render_template('dashboard.html', user_profile=user_profile)
    else:
        print(f"Error al obtener perfil: {user_profile_response.status_code} - {user_profile_response.text}")
        session.pop('access_token', None)
        session.pop('refresh_token', None)
        return redirect(url_for('login'))

# Rutas de la API
@app.route('/api/search_tracks', methods=['GET'])
def search_tracks():
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "No search query provided"}), 400
    sp = spotipy.Spotify(auth=session.get('access_token'))
    try:
        results = sp.search(q=query, type='track', limit=10)
        return jsonify(results)
    except spotipy.SpotifyException as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/play_track', methods=['POST'])
def play_track():
    headers = {
        'Authorization': f"Bearer {session['access_token']}",
        'Content-Type': 'application/json'
    }
    track_uri = request.json.get('uri')
    if not track_uri:
        return jsonify({'error': 'Missing track URI', 'message': 'Track URI is required.'}), 400
    play_data = {"uris": [track_uri]}
    devices_response = requests.get(f"{API_BASE_URL}me/player/devices", headers=headers)
    active_device_id = None
    if devices_response.status_code == 200:
        devices = devices_response.json().get('devices', [])
        for device in devices:
            if device['is_active']:
                active_device_id = device['id']
                break
    if not active_device_id:
        return jsonify({'error': 'No active device found', 'message': 'Abre Spotify y asegúrate de que un dispositivo esté activo.'}), 400
    response = requests.put(f"{API_BASE_URL}me/player/play?device_id={active_device_id}", headers=headers, json=play_data)
    if response.status_code == 204:
        return jsonify({'message': 'Reproduciendo'}), 200
    else:
        return jsonify(response.json()), response.status_code

@app.route('/api/user_info', methods=['GET'])
def get_custom_user_info():
    return jsonify(global_user.to_dict())

@app.route('/api/upgrade_premium', methods=['POST'])
def upgrade_premium():
    global_user.upgrade_to_premium()
    return jsonify({"message": "Usuario actualizado a Premium", "user": global_user.to_dict()})

@app.route('/api/playlist_type', methods=['GET', 'POST'])
def handle_playlist_type():
    if request.method == 'POST':
        data = request.get_json()
        if data is None:
            return jsonify({"success": False, "message": "No JSON data provided"}), 400
        playlist_type = data.get('type')
        if playlist_type:
            global_playlist_manager.set_strategy(playlist_type)
            return jsonify({"success": True, "message": f"Playlist type set to {playlist_type}"})
        return jsonify({"success": False, "message": "No playlist type provided"}), 400
    elif request.method == 'GET':
        current_type = global_playlist_manager.get_current_strategy_name()
        if current_type:
            return jsonify({"success": True, "type": current_type})
        return jsonify({"success": False, "message": "Playlist type not set yet"}), 200

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/add_song', methods=['POST'])
def add_song_api():
    try:
        title = request.form.get('title')
        artist = request.form.get('artist')
        duration = request.form.get('duration', 180)  # Duración en segundos
        genre = request.form.get('genre', 'Desconocido')
        file = request.files.get('file')
        if not all([title, artist, file]):
            return jsonify({"error": "Faltan datos: título, artista o archivo."}), 400
        if not allowed_file(file.filename):
            return jsonify({"error": "Formato de archivo no permitido. Usa mp3 o wav."}), 400
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        song = Song(title=title, artist=artist, duration=int(duration), genre=genre, file_path=f"/{file_path}")
        global_playlist_manager.add_song(song)
        return jsonify({"message": "Canción añadida a la playlist personalizada", "playlist": global_playlist_manager.to_dict()})
    except Exception as e:
        return jsonify({"error": f"Error al añadir canción: {str(e)}"}), 500
    


@app.route('/api/next_song', methods=['POST'])
def next_song_api():
    song = global_playlist_manager.current_playlist.next_item()
    if song:
        return jsonify({"message": "Siguiente canción", "current_song": song.to_dict()})
    return jsonify({"message": "No hay siguiente canción", "current_song": None})

@app.route('/api/previous_song', methods=['POST'])
def previous_song_api():
    song = global_playlist_manager.current_playlist.previous_item()
    if song:
        return jsonify({"message": "Canción anterior", "current_song": song.to_dict()})
    return jsonify({"message": "No se puede ir a la canción anterior", "current_song": None})

@app.route('/api/remove_song', methods=['POST'])
def remove_song_api():
    removed_song = global_playlist_manager.current_playlist.remove_item()
    if removed_song:
        return jsonify({"message": f"Canción '{removed_song.title}' eliminada", "playlist": global_playlist_manager.get_playlist_data()})
    return jsonify({"message": "No se pudo eliminar la canción"})

@app.route('/api/reset_playlist', methods=['POST'])
def reset_playlist_api():
    global_playlist_manager.current_playlist.reset()
    return jsonify({"message": "Playlist reseteada", "playlist": global_playlist_manager.get_playlist_data()})


@app.route('/api/get_playlist', methods=['GET'])
def get_playlist_route():
    print("Solicitando playlist...")
    if global_playlist_manager:
        playlist_data = global_playlist_manager.to_dict()
        if 'songs' not in playlist_data or not isinstance(playlist_data['songs'], list):
            playlist_data['songs'] = []
        print("Datos de la playlist:", playlist_data)
        return jsonify(playlist_data)
    print("Playlist manager no inicializado")
    return jsonify({
        "songs": [],
        "current_song_index": -1,
        "current_song": None,
        "strategy_name": "simple",
        "can_go_previous": False
    })

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message": "Sesión cerrada exitosamente"})

if __name__ == '__main__':
    song1 = Song("Canción 1", "Artista 1", 180, "Pop")
    song2 = Song("Canción 2", "Artista 2", 200, "Rock")
    global_playlist_manager.current_playlist.add_item(song1)
    global_playlist_manager.current_playlist.add_item(song2)
    app.run(host='0.0.0.0', port=5000, debug=True)
