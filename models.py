# models.py
class Song:
    def __init__(self, title, artist, duration, genre="Unknown", uri=None, file_path=None):
        self.uri = uri  # Para canciones de Spotify (opcional)
        self.title = title
        self.artist = artist
        self.duration = duration  # Duración en segundos (entero) para consistencia
        self.genre = genre
        self.file_path = file_path  # Para canciones locales (opcional)

    def to_dict(self):
        return {
            "uri": self.uri,
            "title": self.title,
            "artist": self.artist,
            "duration": self.duration,
            "genre": self.genre,
            "file_path": self.file_path
        }

    def __eq__(self, other):
        if not isinstance(other, Song):
            return NotImplemented
        # Considera que dos canciones son iguales si tienen la misma URI (Spotify) o file_path (local)
        return (self.uri and other.uri and self.uri == other.uri) or \
               (self.file_path and other.file_path and self.file_path == other.file_path)

    def __hash__(self):
        # Usa uri o file_path para el hash, según esté disponible
        return hash(self.uri or self.file_path or (self.title, self.artist))

    def __repr__(self):
        return f"Song(title='{self.title}', artist='{self.artist}', uri='{self.uri}', file_path='{self.file_path}')"