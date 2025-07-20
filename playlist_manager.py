# playlist_manager.py
from .models import Song
from .linked_lists import SimpleLinkedList, DoublyLinkedList, CircularLinkedList, CircularDoublyLinkedList
from .playback_strategies import ShuffleStrategy

class PlaylistManager:
    def __init__(self, playlist_type='simple'):
        self.strategy_name = playlist_type
        self.current_playlist = self._get_playlist(playlist_type)
        self.current_song_index = -1
        self.is_shuffled = False

    def set_strategy(self, new_playlist_type):
        """Cambia el tipo de lista de reproducción."""
        if self.strategy_name != new_playlist_type:
            current_songs = self.current_playlist.get_all_songs()
            was_shuffled = self.is_shuffled
            self.strategy_name = new_playlist_type
            self.current_playlist = self._get_playlist(new_playlist_type)
            for song_data in current_songs:
                song = Song(**song_data)
                self.current_playlist.add_item(song)
            self.current_song_index = 0 if current_songs else -1
            self.is_shuffled = False
            if new_playlist_type == 'shuffle' or (was_shuffled and new_playlist_type != 'shuffle'):
                self._apply_shuffle()

    def _get_playlist(self, playlist_type):
        """Devuelve la instancia de la lista de reproducción según el tipo."""
        if playlist_type == 'simple':
            return SimpleLinkedList()
        elif playlist_type == 'doubly':
            return DoublyLinkedList()
        elif playlist_type == 'circular':
            return CircularLinkedList()
        elif playlist_type == 'circular_doubly':
            return CircularDoublyLinkedList()
        elif playlist_type == 'shuffle':
            return SimpleLinkedList()  # Usamos SimpleLinkedList para shuffle
        else:
            raise ValueError(f"Tipo de playlist desconocido: {playlist_type}")

    def _apply_shuffle(self):
        """Aplica la estrategia de reproducción aleatoria."""
        if self.strategy_name == 'shuffle':
            strategy = ShuffleStrategy()
            strategy.apply(self)
            self.is_shuffled = True
        else:
            self.is_shuffled = False

    def get_current_strategy_name(self):
        """Retorna el nombre del tipo de lista actual."""
        return self.strategy_name

    def add_song(self, song_data):
        """Añade una canción a la lista de reproducción."""
        if isinstance(song_data, dict):
            song = Song(**song_data)
        elif isinstance(song_data, Song):
            song = song_data
        else:
            raise ValueError("Datos de la canción inválidos. Debe ser un diccionario o un objeto Song.")
        
        self.current_playlist.add_item(song)
        if self.current_song_index == -1:
            self.current_song_index = 0
        if self.is_shuffled:
            self._apply_shuffle()

    def remove_current_song(self):
        """Elimina la canción actual de la lista."""
        removed_song = self.current_playlist.remove_item()
        if removed_song:
            if self.current_playlist.size == 0:
                self.current_song_index = -1
            elif self.current_song_index >= self.current_playlist.size:
                self.current_song_index = self.current_playlist.size - 1
            if self.is_shuffled:
                self._apply_shuffle()
        return removed_song

    def next_song(self):
        """Avanza a la siguiente canción."""
        song = self.current_playlist.next_item()
        if song:
            self.current_song_index = min(self.current_song_index + 1, self.current_playlist.size - 1)
        return song

    def previous_song(self):
        """Retrocede a la canción anterior."""
        song = self.current_playlist.previous_item()
        if song and self.current_song_index > 0:
            self.current_song_index -= 1
        return song

    def get_current_song(self):
        """Retorna la canción actual."""
        return self.current_playlist.get_current_item()

    def get_playlist_data(self):
        """Retorna los datos de la lista para la API."""
        return self.to_dict()

    def to_dict(self):
        """Retorna una representación de la playlist como diccionario."""
        return {
            "songs": self.current_playlist.get_all_songs(),
            "current_song_index": self.current_song_index,
            "current_song": self.get_current_song().to_dict() if self.get_current_song() else None,
            "strategy_name": self.strategy_name,
            "can_go_previous": self.current_song_index > 0 or self.strategy_name in ['circular', 'circular_doubly', 'shuffle']
        }