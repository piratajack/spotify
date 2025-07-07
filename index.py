#app.py

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, render_template
import os


app = Flask(__name__)
# --- Clases de tu lógica de negocio (Song, User, Playlist, etc.) ---

# Clase Song
class Song:
    def __init__(self, title, artist, duration, genre):
        self.title = title
        self.artist = artist
        self.duration = duration
        self.genre = genre

    def to_dict(self):
        return {
            "title": self.title,
            "artist": self.artist,
            "duration": self.duration,
            "genre": self.genre
        }

# Clase User
class User:
    def __init__(self, username, is_premium=False):
        self.username = username
        self.is_premium = is_premium

    def upgrade_to_premium(self):
        self.is_premium = True

    def to_dict(self):
        return {
            "username": self.username,
            "is_premium": self.is_premium
        }

# Clases de Nodos
class Node:
    def __init__(self, song):
        self.song = song
        self.next = None

class DoublyNode(Node):
    def __init__(self, song):
        super().__init__(song)
        self.prev = None

# Clase Base Playlist
class Playlist:
    def __init__(self):
        self.current_item = None
        self.size = 0

    def add_item(self, song):
        raise NotImplementedError

    def remove_item(self):
        raise NotImplementedError

    def get_current_item(self):
        if self.current_item:
            return self.current_item.song
        return None

    def next_item(self):
        raise NotImplementedError

    def previous_item(self):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    def get_all_songs(self):
        # Método auxiliar para obtener todas las canciones como una lista de diccionarios
        songs = []
        if not self.current_item:
            return songs
        
        # Implementación genérica, cada subclase podría optimizarla
        temp_current = self.current_item # Guardar el actual para restaurarlo
        self.current_item = self.head # Empezar desde el inicio (asumiendo head en Simple/Doubly)

        if isinstance(self, (SimpleLinkedList, DoublyLinkedList)):
            current = self.head
            while current:
                songs.append(current.song.to_dict())
                current = current.next
        elif isinstance(self, (CircularLinkedList, CircularDoublyLinkedList)):
            if self.head:
                current = self.head
                while True:
                    songs.append(current.song.to_dict())
                    current = current.next
                    if current == self.head:
                        break
        
        self.current_item = temp_current # Restaurar el actual
        return songs

# Implementaciones de Playlists 
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
        self.size -= 1
        return removed_song

    def next_item(self):
        if not self.head: return None
        if self.current_item and self.current_item.next:
            self.current_item = self.current_item.next
        else:
            self.current_item = self.head
        return self.get_current_item()

    def previous_item(self):
        # Las listas simples no tienen previous_item eficiente
        return None

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
        if not self.head: return None

        removed_song = self.current_item.song
        next_item = self.current_item.next
        prev_item = self.current_item.prev

        if prev_item: prev_item.next = next_item
        else: self.head = next_item

        if next_item: next_item.prev = prev_item
        else: self.tail = prev_item

        if self.head is None:
            self.tail = None
            self.current_item = None
        elif next_item: self.current_item = next_item
        elif prev_item: self.current_item = prev_item
        else: self.current_item = None
        
        self.size -= 1
        return removed_song

    def next_item(self):
        if not self.head: return None
        if self.current_item and self.current_item.next:
            self.current_item = self.current_item.next
        else:
            self.current_item = self.head
        return self.get_current_item()

    def previous_item(self):
        if not self.head: return None
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
        if not self.head: return None

        removed_song = None
        if self.size == 1:
            removed_song = self.head.song
            self.head = None
            self.current_item = None
        else:
            prev_node = None
            current = self.head
            while current != self.current_item:
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
        if not self.head: return None
        self.current_item = self.current_item.next
        return self.get_current_item()

    def previous_item(self):
        # Necesita recorrer la lista para encontrar el anterior
        if not self.head: return None
        if self.size == 1: return self.get_current_item() # Solo hay uno
        
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
        if not self.head: return songs
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
        if not self.head: return None

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
        if not self.head: return None
        self.current_item = self.current_item.next
        return self.get_current_item()

    def previous_item(self):
        if not self.head: return None
        self.current_item = self.current_item.prev
        return self.get_current_item()

    def reset(self):
        self.head = None
        self.current_item = None
        self.size = 0

    def get_all_songs(self):
        songs = []
        if not self.head: return songs
        current = self.head
        while True:
            songs.append(current.song.to_dict())
            current = current.next
            if current == self.head:
                break
        return songs

# Clase PlaylistManager 
class PlaylistManager:
    def __init__(self, user):
        self.user = user
        self.current_playlist_type = "simple" # Almacena el tipo de playlist actual como string
        self.playlists = {
            "simple": SimpleLinkedList(),
            "double": DoublyLinkedList(),
            "circular_simple": CircularLinkedList(),
            "circular_double": CircularDoublyLinkedList()
        }
        self.current_playlist = self.playlists[self.current_playlist_type] # La instancia de la playlist actual

    def select_playlist_type(self, new_type):
        if self.user.is_premium or new_type == "simple":
            if new_type in self.playlists:
                self.current_playlist_type = new_type
                self.current_playlist = self.playlists[new_type]
                return True
        return False

    def get_playlist_data(self):
        current_song_data = self.current_playlist.get_current_item()
        return {
            "type": self.current_playlist_type,
            "songs": self.current_playlist.get_all_songs(),
            "current_song": current_song_data.to_dict() if current_song_data else None,
            "can_go_previous": isinstance(self.current_playlist, (DoublyLinkedList, CircularDoublyLinkedList))
        }

# --- Configuración de Flask ---
app = Flask(__name__)


# Simulación de sesión de usuario y manager (en una app real usarías sesiones o bases de datos)
user_data = User("version", is_premium=False)
manager = PlaylistManager(user_data)

@app.route('/')
def index():
    return render_template('sitio/index.html')


@app.route('/api/user_info', methods=['GET'])
def get_user_info():
    return jsonify(manager.user.to_dict())

@app.route('/api/upgrade_premium', methods=['POST'])
def upgrade_premium():
    manager.user.upgrade_to_premium()
    return jsonify({"message": "Usuario actualizado a Premium", "user": manager.user.to_dict()})


@app.route('/api/playlist_type', methods=['GET', 'POST'])
def handle_playlist_type():
    if request.method == 'GET':
        return jsonify(manager.get_playlist_data())
    elif request.method == 'POST':
        data = request.json
        new_type = data.get('type')
        if new_type and manager.select_playlist_type(new_type):
            return jsonify({"message": f"Tipo de playlist cambiado a {new_type}", "playlist": manager.get_playlist_data()})
        else:
            return jsonify({"error": "Tipo de playlist inválido o sin permisos"}, 400)

@app.route('/api/add_song', methods=['POST'])
def add_song():
    data = request.json
    try:
        song = Song(data['title'], data['artist'], data['duration'], data['genre'])
        manager.current_playlist.add_item(song)
        return jsonify({"message": "Canción añadida", "playlist": manager.get_playlist_data()})
    except KeyError:
        return jsonify({"error": "Datos de canción incompletos"}, 400)

@app.route('/api/next_song', methods=['POST'])
def next_song():
    song = manager.current_playlist.next_item()
    if song:
        return jsonify({"message": "Siguiente canción", "current_song": song.to_dict()})
    return jsonify({"message": "No hay siguiente canción"})

@app.route('/api/previous_song', methods=['POST'])
def previous_song():
    song = manager.current_playlist.previous_item()
    if song:
        return jsonify({"message": "Canción anterior", "current_song": song.to_dict()})
    return jsonify({"message": "No se puede ir a la canción anterior en este tipo de playlist"})

@app.route('/api/remove_song', methods=['POST'])
def remove_song():
    removed_song = manager.current_playlist.remove_item()
    if removed_song:
        return jsonify({"message": f"Canción '{removed_song.title}' eliminada", "playlist": manager.get_playlist_data()})
    return jsonify({"message": "No se pudo eliminar la canción"})

@app.route('/api/reset_playlist', methods=['POST'])
def reset_playlist():
    manager.current_playlist.reset()
    return jsonify({"message": "Playlist reseteada", "playlist": manager.get_playlist_data()})

if __name__ == '__main__':
    #  canciones de prueba
    manager.current_playlist.add_item(Song("Bohemian Rhapsody", "Queen", "5:55", "Rock"))
    manager.current_playlist.add_item(Song("Stairway to Heaven", "Led Zeppelin", "8:02", "Rock"))
    manager.current_playlist.add_item(Song("Billie Jean", "Michael Jackson", "4:54", "Pop"))
    manager.current_playlist.add_item(Song("Hotel California", "Eagles", "6:30", "Rock"))

    app.run(debug=True) 