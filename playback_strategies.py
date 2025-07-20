# playback_strategies.py
import random

class PlaybackStrategy:
    """Clase base abstracta para estrategias de reproducción."""
    def apply(self, playlist_manager):
        """Aplica la estrategia al administrador de la lista de reproducción."""
        raise NotImplementedError("Subclasses must implement 'apply' method")

class ShuffleStrategy(PlaybackStrategy):
    """Estrategia de reproducción aleatoria."""
    def apply(self, playlist_manager):
        """Genera un orden aleatorio para las canciones de la lista de reproducción."""
        songs = playlist_manager.current_playlist.get_all_songs()
        if not songs:
            return
        
        # Barajar las canciones
        random.shuffle(songs)
        
        # Reconstruir la lista con el orden aleatorio
        new_playlist = type(playlist_manager.current_playlist)()
        for song_data in songs:
            from .models import Song
            song = Song(**song_data)
            new_playlist.add_item(song)
        
        playlist_manager.current_playlist = new_playlist
        playlist_manager.current_song_index = 0
        playlist_manager.is_shuffled = True