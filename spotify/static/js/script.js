// Definir onSpotifyWebPlaybackSDKReady globalmente
console.log("Definiendo onSpotifyWebPlaybackSDKReady");
window.onSpotifyWebPlaybackSDKReady = () => {
    console.log("Spotify Web Playback SDK listo");
    spotifyPlayer = new Spotify.Player({
        name: 'Spotify 2.0',
        getOAuthToken: cb => {
            fetch('/api/get_access_token')
                .then(response => response.json())
                .then(data => cb(data.access_token))
                .catch(error => console.error('Error al obtener token:', error));
        },
        volume: 0.5
    });

    spotifyPlayer.addListener('ready', ({ device_id }) => {
        console.log('Dispositivo listo con ID:', device_id);
        sessionStorage.setItem('device_id', device_id);
    });

    spotifyPlayer.addListener('not_ready', ({ device_id }) => {
        console.log('Dispositivo no listo:', device_id);
        sessionStorage.removeItem('device_id');
    });

    spotifyPlayer.addListener('player_state_changed', state => {
        if (state && state.paused) {
            playPauseBtn.textContent = '▶️ Play';
        } else {
            playPauseBtn.textContent = '⏸️ Pause';
        }
    });

    spotifyPlayer.connect();
};

document.addEventListener('DOMContentLoaded', () => {
    console.log("¡Script.js cargado y DOM listo!");

    let currentCustomPlaylist = { songs: [], current_song_index: -1 };
    let spotifyUserProfile = null;
    let spotifyPlayer = null;

    const welcomeMessage = document.getElementById('welcome-message');
    const usernameDisplay = document.getElementById('username-display');
    const premiumStatus = document.getElementById('premium-status');
    const upgradeBtn = document.getElementById('upgrade-btn');
    const aboutBtn = document.getElementById('about-btn');
    const searchBtn = document.getElementById('search-btn');
    const searchSectionBtn = document.getElementById('search-section-btn');
    const searchInput = document.getElementById('search-input');
    const searchInputSection = document.getElementById('search-input-section');
    const searchResults = document.getElementById('search-results');
    const addSongBtn = document.getElementById('add-song-btn');
    const removeSongBtn = document.getElementById('remove-song-btn');
    const resetPlaylistBtn = document.getElementById('reset-playlist-btn');
    const prevBtn = document.getElementById('prev-btn');
    const playPauseBtn = document.getElementById('play-pause-btn');
    const nextBtn = document.getElementById('next-btn');
    const songsList = document.getElementById('songs-list');
    const currentSongInfo = document.getElementById('current-song-info');
    const currentPlaylistType = document.getElementById('current-playlist-type');
    const addSongModal = document.getElementById('addSongModal');
    const closeModalBtn = document.querySelector('.close-button');
    const addSongForm = document.getElementById('add-song-form');
    const songTitleInput = document.getElementById('songTitle');
    const songArtistInput = document.getElementById('songArtist');
    const songDurationInput = document.getElementById('songDuration');
    const songGenreInput = document.getElementById('songGenre');
    const songFileInput = document.getElementById('songFile');
    const audioPlayer = document.getElementById('audio-player');
    const volumeControl = document.getElementById('volume-control');
    const menuButtons = document.querySelectorAll('#main-menu button');
    const playlistTypeButtons = document.querySelectorAll('#playlist-types button');

    function formatDuration(seconds) {
        const minutes = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${minutes}:${secs.toString().padStart(2, '0')}`;
    }

    function showMessage(message, type = 'info') {
        const messageContainer = document.getElementById('message-container');
        if (!messageContainer) return;
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type}`;
        alertDiv.textContent = message;
        messageContainer.appendChild(alertDiv);
        setTimeout(() => alertDiv.remove(), 5000);
    }

    function updateUI() {
        console.log("Actualizando UI...");
        const userDataElement = document.getElementById('user-data');
        if (welcomeMessage) welcomeMessage.textContent = '';
        if (usernameDisplay) usernameDisplay.textContent = '';
        if (premiumStatus) premiumStatus.textContent = '';

        if (userDataElement && userDataElement.textContent) {
            try {
                spotifyUserProfile = JSON.parse(userDataElement.textContent);
                console.log("Perfil de usuario de Spotify:", spotifyUserProfile);
                if (welcomeMessage) welcomeMessage.textContent = `Hola, ${spotifyUserProfile.display_name || spotifyUserProfile.id}!`;
                if (usernameDisplay) usernameDisplay.textContent = spotifyUserProfile.display_name || spotifyUserProfile.id;
                if (upgradeBtn) upgradeBtn.style.display = 'inline';
                if (aboutBtn) aboutBtn.style.display = 'inline';
            } catch (e) {
                console.error("Error al parsear user-data:", e);
                if (upgradeBtn) upgradeBtn.style.display = 'none';
                if (aboutBtn) aboutBtn.style.display = 'none';
            }
        }

        fetchPlaylistData().then(() => {
            console.log("fetchPlaylistData completado, llamando a fetchUserPlaylists...");
            fetchUserPlaylists();
        });
        fetch('/api/user_info')
            .then(response => response.json())
            .then(data => {
                if (premiumStatus) {
                    premiumStatus.textContent = data.is_premium ? 'Premium' : 'Gratis';
                    if (upgradeBtn && !data.is_premium) {
                        upgradeBtn.style.display = 'inline';
                    }
                }
            })
            .catch(error => {
                showMessage('Error al cargar info de usuario.', 'danger');
                console.error('Error en user_info:', error);
            });
    }

    async function fetchPlaylistData() {
        try {
            console.log("Solicitando /api/get_playlist...");
            const response = await fetch('/api/get_playlist');
            if (response.status === 401) {
                showMessage('Sesión expirada. Inicia sesión nuevamente.', 'danger');
                window.location.href = '/login';
                return;
            }
            const data = await response.json();
            console.log("Respuesta de /api/get_playlist:", data);
            if (response.ok) {
                currentCustomPlaylist = data;
                if (!currentCustomPlaylist.songs || !Array.isArray(currentCustomPlaylist.songs)) {
                    console.warn("currentCustomPlaylist.songs no es un array, inicializando como vacío");
                    currentCustomPlaylist.songs = [];
                }
                renderCustomPlaylist();
                updatePlaybackControls();
                if (currentPlaylistType) {
                    currentPlaylistType.textContent = `Tipo de Playlist: ${currentCustomPlaylist.strategy_name || 'simple'}`;
                }
            } else {
                showMessage(`Error al cargar playlist: ${data.error || 'Desconocido'}`, 'danger');
            }
        } catch (error) {
            showMessage('Error de red al cargar playlist.', 'danger');
            console.error('Error en fetchPlaylistData:', error);
        }
    }

    async function fetchUserPlaylists() {
        console.log("Iniciando carga de playlists de Spotify...");
        try {
            const response = await fetch('/api/get_user_playlists');
            console.log("Respuesta de /api/get_user_playlists:", response);
            const data = await response.json();
            console.log("Datos de playlists:", data);
            if (response.ok) {
                renderPlaylists(data.playlists || []);
            } else {
                showMessage(`Error al cargar playlists: ${data.error || 'Desconocido'}`, 'danger');
            }
        } catch (error) {
            showMessage('Error de red al cargar playlists.', 'danger');
            console.error('Error en fetchUserPlaylists:', error);
        }
    }

    function renderPlaylists(playlists) {
        const librarySection = document.getElementById('your-library-section');
        if (!librarySection) {
            console.error("No se encontró #your-library-section");
            return;
        }
        librarySection.innerHTML = '<h2>Tus Playlists</h2>';
        const ul = document.createElement('ul');
        ul.className = 'list-group';
        if (playlists.length === 0) {
            ul.innerHTML = '<li class="list-group-item">No se encontraron playlists.</li>';
        } else {
            playlists.forEach(playlist => {
                const li = document.createElement('li');
                li.className = 'list-group-item';
                li.textContent = playlist.name;
                li.style.cursor = 'pointer';
                li.addEventListener('click', () => fetchPlaylistTracks(playlist.id));
                ul.appendChild(li);
            });
        }
        librarySection.appendChild(ul);
    }

    async function fetchPlaylistTracks(playlistId) {
        try {
            console.log("Cargando canciones de la playlist:", playlistId);
            const response = await fetch(`/api/get_playlist_tracks?playlist_id=${playlistId}`);
            const data = await response.json();
            console.log("Respuesta de /api/get_playlist_tracks:", data);
            if (response.ok) {
                currentCustomPlaylist.songs = data.tracks || [];
                currentCustomPlaylist.current_song_index = -1;
                renderCustomPlaylist();
                showMessage('Playlist cargada correctamente.', 'success');
            } else {
                showMessage(`Error al cargar canciones: ${data.error || 'Desconocido'}`, 'danger');
            }
        } catch (error) {
            showMessage('Error de red al cargar canciones.', 'danger');
            console.error('Error en fetchPlaylistTracks:', error);
        }
    }

    function renderCustomPlaylist() {
        if (!songsList) {
            console.error("No se encontró #songs-list");
            return;
        }
        songsList.innerHTML = '';

        if (!currentCustomPlaylist.songs || currentCustomPlaylist.songs.length === 0) {
            songsList.innerHTML = '<li>No hay canciones en la playlist.</li>';
            currentSongInfo.textContent = 'Nada reproduciéndose.';
            return;
        }

        currentCustomPlaylist.songs.forEach((song, index) => {
            const listItem = document.createElement('li');
            listItem.className = 'list-group-item d-flex justify-content-between align-items-center';
            listItem.textContent = `${song.title} - ${song.artist} (${formatDuration(song.duration)})`;
            if (index === currentCustomPlaylist.current_song_index) {
                listItem.classList.add('active');
            }
            listItem.addEventListener('click', () => {
                currentCustomPlaylist.current_song_index = index;
                currentCustomPlaylist.current_song = song;
                renderCustomPlaylist();
                updateCurrentSongDisplay();
            });
            songsList.appendChild(listItem);
        });

        updateCurrentSongDisplay();
    }

    function updateCurrentSongDisplay() {
        if (currentSongInfo && currentCustomPlaylist.current_song && currentCustomPlaylist.current_song.file_path) {
            currentSongInfo.textContent = `Reproduciendo: ${currentCustomPlaylist.current_song.title} - ${currentCustomPlaylist.current_song.artist} (${formatDuration(currentCustomPlaylist.current_song.duration)})`;
            if (audioPlayer) {
                audioPlayer.src = currentCustomPlaylist.current_song.file_path;
                audioPlayer.play().catch(e => console.error("Error al reproducir:", e));
                playPauseBtn.textContent = '⏸️ Pause';
            }
        } else if (currentSongInfo && currentCustomPlaylist.current_song && currentCustomPlaylist.current_song.uri) {
            currentSongInfo.textContent = `Reproduciendo (Spotify): ${currentCustomPlaylist.current_song.title} - ${currentCustomPlaylist.current_song.artist} (${formatDuration(currentCustomPlaylist.current_song.duration)})`;
            if (spotifyPlayer && currentCustomPlaylist.current_song.uri) {
                playSpotifyTrack(currentCustomPlaylist.current_song.uri);
            }
        } else {
            currentSongInfo.textContent = 'Nada reproduciéndose.';
            if (audioPlayer) {
                audioPlayer.pause();
                audioPlayer.src = '';
                playPauseBtn.textContent = '▶️ Play';
            }
        }
    }

    function updatePlaybackControls() {
        if (prevBtn) {
            prevBtn.disabled = !currentCustomPlaylist.can_go_previous;
        }
        if (nextBtn) {
            nextBtn.disabled = !currentCustomPlaylist.songs || currentCustomPlaylist.songs.length === 0 ||
                             (currentCustomPlaylist.current_song_index >= currentCustomPlaylist.songs.length - 1 &&
                              currentCustomPlaylist.strategy_name === 'simple');
        }
    }

    async function addSong(event) {
        event.preventDefault();
        const title = songTitleInput.value;
        const artist = songArtistInput.value;
        const file = songFileInput.files[0];
        const duration = songDurationInput.value || '3:00';
        const genre = songGenreInput.value || 'Desconocido';

        if (!title || !artist || !file) {
            showMessage('Completa todos los campos y selecciona un archivo.', 'warning');
            return;
        }

        const formData = new FormData();
        formData.append('title', title);
        formData.append('artist', artist);
        formData.append('file', file);
        formData.append('duration', parseDuration(duration));
        formData.append('genre', genre);

        try {
            const response = await fetch('/api/add_song', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();

            if (response.ok) {
                showMessage(data.message, 'success');
                songTitleInput.value = '';
                songArtistInput.value = '';
                songDurationInput.value = '';
                songGenreInput.value = '';
                songFileInput.value = '';
                addSongModal.style.display = 'none';
                fetchPlaylistData();
            } else {
                showMessage(`Error al añadir canción: ${data.error || 'Desconocido'}`, 'danger');
            }
        } catch (error) {
            showMessage('Error de red al añadir canción.', 'danger');
            console.error('Error al añadir canción:', error);
        }
    }

    function parseDuration(durationStr) {
        const [minutes, seconds] = durationStr.split(':').map(Number);
        return (minutes * 60) + (seconds || 0);
    }

    async function removeSong() {
        try {
            const response = await fetch('/api/remove_song', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            const data = await response.json();

            if (response.ok) {
                showMessage(data.message, 'success');
                fetchPlaylistData();
            } else {
                showMessage(`Error al eliminar canción: ${data.error || 'Desconocido'}`, 'danger');
            }
        } catch (error) {
            showMessage('Error de red al eliminar canción.', 'danger');
            console.error('Error al eliminar:', error);
        }
    }

    async function resetPlaylist() {
        try {
            const response = await fetch('/api/reset_playlist', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            const data = await response.json();

            if (response.ok) {
                showMessage(data.message, 'success');
                fetchPlaylistData();
            } else {
                showMessage(`Error al resetear playlist: ${data.error || 'Desconocido'}`, 'danger');
            }
        } catch (error) {
            showMessage('Error de red al resetear playlist.', 'danger');
            console.error('Error al resetear:', error);
        }
    }

    async function playSong() {
        if (!currentCustomPlaylist.current_song) {
            showMessage('No hay canción seleccionada.', 'warning');
            return;
        }
        if (currentCustomPlaylist.current_song.file_path) {
            try {
                audioPlayer.src = currentCustomPlaylist.current_song.file_path;
                audioPlayer.play();
                playPauseBtn.textContent = '⏸️ Pause';
                showMessage('Reproduciendo canción local.', 'success');
            } catch (error) {
                showMessage('Error al reproducir canción local.', 'danger');
                console.error('Error al reproducir:', error);
            }
        } else if (currentCustomPlaylist.current_song.uri) {
            try {
                await playSpotifyTrack(currentCustomPlaylist.current_song.uri);
                playPauseBtn.textContent = '⏸️ Pause';
                showMessage('Reproduciendo canción de Spotify.', 'success');
            } catch (error) {
                showMessage('Error al reproducir canción de Spotify.', 'danger');
                console.error('Error al reproducir Spotify:', error);
            }
        }
    }

    async function pauseSong() {
        try {
            if (currentCustomPlaylist.current_song && currentCustomPlaylist.current_song.file_path) {
                audioPlayer.pause();
                playPauseBtn.textContent = '▶️ Play';
                showMessage('Canción pausada.', 'success');
            } else if (currentCustomPlaylist.current_song && currentCustomPlaylist.current_song.uri) {
                await spotifyPlayer.pause();
                playPauseBtn.textContent = '▶️ Play';
                showMessage('Canción de Spotify pausada.', 'success');
            }
        } catch (error) {
            showMessage('Error al pausar canción.', 'danger');
            console.error('Error al pausar:', error);
        }
    }

    async function prevSong() {
        try {
            const response = await fetch('/api/previous_song', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            const data = await response.json();

            if (response.ok) {
                showMessage(data.message, 'success');
                currentCustomPlaylist = { ...currentCustomPlaylist, current_song: data.current_song, current_song_index: currentCustomPlaylist.current_song_index - 1 };
                updateCurrentSongDisplay();
                updatePlaybackControls();
                renderCustomPlaylist();
            } else {
                showMessage(`Error al ir a la canción anterior: ${data.error || 'Desconocido'}`, 'danger');
            }
        } catch (error) {
            showMessage('Error de red al ir a la canción anterior.', 'danger');
            console.error('Error al ir a la canción anterior:', error);
        }
    }

    async function nextSong() {
        try {
            const response = await fetch('/api/next_song', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            const data = await response.json();

            if (response.ok) {
                showMessage(data.message, 'success');
                currentCustomPlaylist = { ...currentCustomPlaylist, current_song: data.current_song, current_song_index: currentCustomPlaylist.current_song_index + 1 };
                updateCurrentSongDisplay();
                updatePlaybackControls();
                renderCustomPlaylist();
            } else {
                showMessage(`Error al ir a la canción siguiente: ${data.error || 'Desconocido'}`, 'danger');
            }
        } catch (error) {
            showMessage('Error de red al ir a la canción siguiente.', 'danger');
            console.error('Error al ir a la canción siguiente:', error);
        }
    }

    async function searchSongs(event) {
        event.preventDefault();
        const query = event.target.querySelector('input').value;
        if (!query) return;

        try {
            const response = await fetch(`/api/search_spotify_tracks?query=${encodeURIComponent(query)}`);
            const data = await response.json();

            if (response.ok) {
                renderSearchResults(data.tracks || []);
            } else {
                showMessage(`Error al buscar canciones: ${data.error || 'Desconocido'}`, 'danger');
            }
        } catch (error) {
            showMessage('Error de red al buscar canciones.', 'danger');
            console.error('Error en searchSongs:', error);
        }
    }

    function renderSearchResults(tracks) {
        if (!searchResults) return;
        searchResults.innerHTML = '';
        if (tracks.length === 0) {
            searchResults.innerHTML = '<p>No se encontraron resultados.</p>';
            return;
        }

        const ul = document.createElement('ul');
        ul.className = 'list-group';
        tracks.forEach(track => {
            const li = document.createElement('li');
            li.className = 'list-group-item d-flex justify-content-between align-items-center';
            li.textContent = `${track.title} - ${track.artist} (${formatDuration(track.duration)})`;
            const addBtn = document.createElement('button');
            addBtn.className = 'btn btn-success btn-sm ml-2';
            addBtn.textContent = 'Añadir a playlist';
            addBtn.onclick = async () => {
                try {
                    const response = await fetch('/api/add_song', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            title: track.title,
                            artist: track.artist,
                            duration: track.duration,
                            genre: track.genre,
                            uri: track.uri,
                            file_path: null
                        })
                    });
                    const data = await response.json();
                    if (response.ok) {
                        showMessage(data.message, 'success');
                        fetchPlaylistData();
                    } else {
                        showMessage(`Error al añadir canción: ${data.error || 'Desconocido'}`, 'danger');
                    }
                } catch (error) {
                    showMessage('Error de red al añadir canción.', 'danger');
                    console.error('Error al añadir:', error);
                }
            };
            li.appendChild(addBtn);
            ul.appendChild(li);
        });
        searchResults.appendChild(ul);
    }

    async function setStrategy(event) {
        const strategyName = event.target.getAttribute('data-type');
        try {
            const response = await fetch('/api/playlist_type', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ type: strategyName })
            });
            const data = await response.json();

            if (response.ok) {
                showMessage(data.message, 'success');
                currentCustomPlaylist = data.playlist;
                renderCustomPlaylist();
                updatePlaybackControls();
                if (currentPlaylistType) {
                    currentPlaylistType.textContent = `Tipo de Playlist: ${currentCustomPlaylist.strategy_name || 'simple'}`;
                }
            } else {
                showMessage(`Error al cambiar estrategia: ${data.error || 'Desconocido'}`, 'danger');
            }
        } catch (error) {
            showMessage('Error de red al cambiar estrategia.', 'danger');
            console.error('Error en setStrategy:', error);
        }
    }

    async function upgradePremium() {
        try {
            const response = await fetch('/api/upgrade_premium', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            const data = await response.json();
            if (response.ok) {
                showMessage(data.message, 'success');
                updateUI();
            } else {
                showMessage(`Error al actualizar a Premium: ${data.error || 'Desconocido'}`, 'danger');
            }
        } catch (error) {
            showMessage('Error de red al actualizar a Premium.', 'danger');
            console.error('Error al actualizar:', error);
        }
    }

    async function playSpotifyTrack(uri) {
        if (!spotifyPlayer || !sessionStorage.getItem('device_id')) {
            showMessage('El reproductor de Spotify no está listo o no hay dispositivo activo.', 'warning');
            return;
        }
        try {
            const response = await fetch('/api/play_track', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ uri, device_id: sessionStorage.getItem('device_id') })
            });
            const data = await response.json();
            if (response.ok) {
                showMessage(data.message, 'success');
            } else {
                showMessage(`Error al reproducir en Spotify: ${data.error || 'Desconocido'}`, 'danger');
            }
        } catch (error) {
            showMessage('Error de red al reproducir en Spotify.', 'danger');
            console.error('Error al reproducir en Spotify:', error);
        }
    }

    // Manejo de secciones
    menuButtons.forEach(button => {
        button.addEventListener('click', () => {
            const section = button.getAttribute('data-section');
            document.querySelectorAll('.content-section').forEach(s => s.classList.add('hidden'));
            document.getElementById(`${section}-section`).classList.remove('hidden');
            menuButtons.forEach(b => b.classList.remove('active'));
            button.classList.add('active');
        });
    });

    // Manejo de tipos de playlist
    playlistTypeButtons.forEach(button => {
        button.addEventListener('click', setStrategy);
    });

    // Manejo de eventos
    if (addSongBtn) {
        addSongBtn.addEventListener('click', () => {
            addSongModal.style.display = 'block';
        });
    }
    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', () => {
            addSongModal.style.display = 'none';
        });
    }
    if (addSongForm) {
        addSongForm.addEventListener('submit', addSong);
    }
    if (removeSongBtn) {
        removeSongBtn.addEventListener('click', removeSong);
    }
    if (resetPlaylistBtn) {
        resetPlaylistBtn.addEventListener('click', resetPlaylist);
    }
    if (prevBtn) {
        prevBtn.addEventListener('click', prevSong);
    }
    if (nextBtn) {
        nextBtn.addEventListener('click', nextSong);
    }
    if (playPauseBtn) {
        playPauseBtn.addEventListener('click', () => {
            if ((audioPlayer && !audioPlayer.paused) || (spotifyPlayer && playPauseBtn.textContent === '⏸️ Pause')) {
                pauseSong();
            } else {
                playSong();
            }
        });
    }
    if (searchBtn) {
        searchBtn.addEventListener('click', searchSongs);
    }
    if (searchSectionBtn) {
        searchSectionBtn.addEventListener('click', searchSongs);
    }
    if (upgradeBtn) {
        upgradeBtn.addEventListener('click', upgradePremium);
    }
    if (audioPlayer && volumeControl) {
        audioPlayer.volume = volumeControl.value;
        volumeControl.addEventListener('input', (event) => {
            audioPlayer.volume = event.target.value;
            if (spotifyPlayer) {
                spotifyPlayer.setVolume(event.target.value);
            }
        });
    }
    if (audioPlayer) {
        audioPlayer.addEventListener('ended', () => {
            console.log("Canción terminada. Pasando a la siguiente...");
            nextSong();
        });
    }

    updateUI();
});