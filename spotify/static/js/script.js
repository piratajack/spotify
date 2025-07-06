// static/js/script.js

document.addEventListener('DOMContentLoaded', () => {
    // --- Elementos del DOM ---
    const usernameDisplay = document.getElementById('username-display');
    const premiumStatus = document.getElementById('premium-status');
    const upgradeBtn = document.getElementById('upgrade-btn');

    // Menú principal y secciones de contenido
    const mainMenuButtons = document.querySelectorAll('#main-menu button');
    const contentSections = document.querySelectorAll('.content-section');

    // Tipos de playlist
    const playlistTypeButtons = document.querySelectorAll('#playlist-types button');

    // Controles de la playlist (en la sección de gestión)
    const currentPlaylistTypeDisplay = document.getElementById('current-playlist-type');
    const addSongBtn = document.getElementById('add-song-btn');
    const removeSongBtn = document.getElementById('remove-song-btn');
    const resetPlaylistBtn = document.getElementById('reset-playlist-btn');
    const currentSongInfo = document.getElementById('current-song-info');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const songsList = document.getElementById('songs-list');

    // Modal para añadir canción
    const addSongModal = document.getElementById('addSongModal');
    const closeModalButton = document.querySelector('.close-button');
    const songTitleInput = document.getElementById('songTitle');
    const songArtistInput = document.getElementById('songArtist');
    const songDurationInput = document.getElementById('songDuration');
    const songGenreInput = document.getElementById('songGenre');
    const submitAddSongButton = document.getElementById('submitAddSong');


    // --- Funciones para interactuar con el Backend (Flask) ---

    /**
     * Obtiene y muestra la información del usuario (nombre, estado premium).
     */
    async function fetchUserInfo() {
        try {
            const response = await fetch('/api/user_info');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            usernameDisplay.textContent = data.username;
            premiumStatus.textContent = data.is_premium ? 'Premium' : 'Gratuito';

            // Muestra u oculta el botón de upgrade a Premium
            if (!data.is_premium) {
                upgradeBtn.style.display = 'inline-block';
            } else {
                upgradeBtn.style.display = 'none';
            }
            // Actualiza el estado de los botones de tipo de playlist según si es Premium
            updatePlaylistTypeButtons(data.is_premium);
        } catch (error) {
            console.error('Error al obtener la información del usuario:', error);
            alert('No se pudo cargar la información del usuario.');
        }
    }

    /**
     * Envía una solicitud para que el usuario actual se convierta en Premium.
     */
    async function upgradeToPremium() {
        try {
            const response = await fetch('/api/upgrade_premium', { method: 'POST' });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            alert(data.message);
            await fetchUserInfo(); // Refresca la información del usuario
            await fetchPlaylistData(); // Refresca la playlist actual (por si cambia el tipo)
        } catch (error) {
            console.error('Error al actualizar a premium:', error);
            alert('Hubo un error al intentar actualizar a premium.');
        }
    }

    /**
     * Obtiene y muestra los datos de la playlist actual (tipo, canciones, canción actual).
     */
    async function fetchPlaylistData() {
        try {
            const response = await fetch('/api/playlist_type');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            // Muestra el tipo de playlist actual
            currentPlaylistTypeDisplay.textContent = `Playlist Actual: ${data.type.replace('_', ' ').replace('simple', 'Simple Enlazada').replace('double', 'Doble Enlazada').replace('circular_simple', 'Circular Simple').replace('circular_double', 'Circular Doble')}`;

            // Actualiza la lista de canciones en el DOM
            updateSongsList(data.songs, data.current_song);
            
            // Habilita/deshabilita el botón 'Anterior' según la estructura de la playlist
            prevBtn.disabled = !data.can_go_previous;

            // Muestra la canción que se está reproduciendo actualmente
            if (data.current_song) {
                currentSongInfo.textContent = `${data.current_song.title} - ${data.current_song.artist} (${data.current_song.duration})`;
            } else {
                currentSongInfo.textContent = 'No hay canción reproduciéndose.';
            }

        } catch (error) {
            console.error('Error al obtener los datos de la playlist:', error);
            // alert('No se pudo cargar la playlist. Inténtalo de nuevo.');
        }
    }

    /**
     * Cambia el tipo de playlist actual en el backend.
     * @param {string} type - El nuevo tipo de playlist (ej. 'simple', 'double').
     */
    async function selectPlaylistType(type) {
        try {
            const response = await fetch('/api/playlist_type', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ type: type })
            });
            const data = await response.json();
            if (response.ok) {
                alert(data.message);
                await fetchPlaylistData(); // Refresca la playlist después de cambiar el tipo
            } else {
                alert(`Error: ${data.error}`);
            }
        } catch (error) {
            console.error('Error al seleccionar el tipo de playlist:', error);
            alert('Hubo un error al intentar cambiar el tipo de playlist.');
        }
    }

    /**
     * Añade una nueva canción a la playlist actual.
     * @param {object} songData - Objeto con los datos de la canción (title, artist, duration, genre).
     */
    async function addSong(songData) {
        try {
            const response = await fetch('/api/add_song', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(songData)
            });
            const data = await response.json();
            if (response.ok) {
                alert(data.message);
                await fetchPlaylistData(); // Refresca la playlist
                addSongModal.style.display = 'none'; // Cierra el modal
            } else {
                alert(`Error: ${data.error}`);
            }
        } catch (error) {
            console.error('Error al añadir canción:', error);
            alert('Hubo un error al intentar añadir la canción.');
        }
    }

    /**
     * Pasa a la siguiente canción en la playlist.
     */
    async function nextSong() {
        try {
            const response = await fetch('/api/next_song', { method: 'POST' });
            const data = await response.json();
            if (response.ok && data.current_song) {
                currentSongInfo.textContent = `${data.current_song.title} - ${data.current_song.artist} (${data.current_song.duration})`;
                await fetchPlaylistData(); // Re-renderiza para mostrar el marcador de canción actual
            } else {
                alert(data.message);
            }
        } catch (error) {
            console.error('Error al reproducir la siguiente canción:', error);
            alert('Hubo un error al intentar ir a la siguiente canción.');
        }
    }

    /**
     * Pasa a la canción anterior en la playlist (si la estructura lo permite).
     */
    async function previousSong() {
        try {
            const response = await fetch('/api/previous_song', { method: 'POST' });
            const data = await response.json();
            if (response.ok && data.current_song) {
                currentSongInfo.textContent = `${data.current_song.title} - ${data.current_song.artist} (${data.current_song.duration})`;
                await fetchPlaylistData(); // Re-renderiza para mostrar el marcador de canción actual
            } else {
                alert(data.message);
            }
        } catch (error) {
            console.error('Error al reproducir la canción anterior:', error);
            alert('Hubo un error al intentar ir a la canción anterior.');
        }
    }

    /**
     * Elimina la canción actual de la playlist.
     */
    async function removeSong() {
        if (!confirm('¿Estás seguro de que quieres eliminar la canción actual?')) {
            return;
        }
        try {
            const response = await fetch('/api/remove_song', { method: 'POST' });
            const data = await response.json();
            alert(data.message);
            await fetchPlaylistData(); // Refresca la playlist
        } catch (error) {
            console.error('Error al eliminar la canción:', error);
            alert('Hubo un error al intentar eliminar la canción.');
        }
    }

    /**
     * Resetea la playlist actual (elimina todas las canciones).
     */
    async function resetPlaylist() {
        if (!confirm('¿Estás seguro de que quieres resetear la playlist? Esto eliminará todas las canciones.')) {
            return;
        }
        try {
            const response = await fetch('/api/reset_playlist', { method: 'POST' });
            const data = await response.json();
            alert(data.message);
            await fetchPlaylistData(); // Refresca la playlist
        } catch (error) {
            console.error('Error al resetear la playlist:', error);
            alert('Hubo un error al intentar resetear la playlist.');
        }
    }

    // --- Funciones para actualizar el DOM (Interfaz de Usuario) ---

    /**
     * Actualiza la lista de canciones mostrada en el DOM.
     * @param {Array<object>} songs - Lista de objetos de canciones.
     * @param {object} currentSong - Objeto de la canción actual (puede ser null).
     */
    function updateSongsList(songs, currentSong) {
        songsList.innerHTML = ''; // Limpia la lista existente
        if (songs.length === 0) {
            songsList.innerHTML = '<li class="empty-list-message">No hay canciones en esta playlist.</li>';
            return;
        }
        songs.forEach((song, index) => {
            const li = document.createElement('li');
            li.className = 'song-item';
            // Añade la clase 'current-song' si es la canción que se está reproduciendo
            if (currentSong && song.title === currentSong.title && song.artist === currentSong.artist && song.duration === currentSong.duration) {
                li.classList.add('current-song');
            }
            li.innerHTML = `
                <span class="song-number">${index + 1}.</span>
                <span class="song-title">${song.title}</span> -
                <span class="song-artist">${song.artist}</span>
                <span class="song-duration">(${song.duration})</span>
            `;
            songsList.appendChild(li);
        });
    }

    /**
     * Actualiza el estado (habilitado/deshabilitado) de los botones de tipo de playlist.
     * @param {boolean} isPremium - True si el usuario es Premium, False de lo contrario.
     */
    function updatePlaylistTypeButtons(isPremium) {
        playlistTypeButtons.forEach(button => {
            const type = button.dataset.type;
            if (type !== 'simple' && !isPremium) {
                button.disabled = true; // Deshabilita botones para tipos premium si no es premium
                button.classList.add('disabled-premium');
            } else {
                button.disabled = false;
                button.classList.remove('disabled-premium');
            }
        });
    }

    /**
     * Muestra una sección específica del contenido principal y oculta las demás.
     * También actualiza el estado 'active' de los botones del menú.
     * @param {string} sectionId - El ID de la sección a mostrar (ej. 'home-section').
     */
    function showSection(sectionId) {
        contentSections.forEach(section => {
            section.classList.remove('active');
            section.classList.add('hidden'); // Asegura que esté oculta
        });
        // Muestra la sección deseada
        document.getElementById(sectionId).classList.add('active');
        document.getElementById(sectionId).classList.remove('hidden');

        // Actualiza el estado 'active' en los botones del menú principal
        mainMenuButtons.forEach(button => {
            // El dataset.section es 'home', 'search', 'your-library', 'playlists-manager'
            // El sectionId es 'home-section', 'search-section', etc.
            if (`${button.dataset.section}-section` === sectionId) {
                button.classList.add('active');
            } else {
                button.classList.remove('active');
            }
        });
    }


    // --- Event Listeners Globales ---

    // Botón para actualizar a Premium
    upgradeBtn.addEventListener('click', upgradeToPremium);

    // Event listeners para los botones de tipo de playlist en la barra lateral
    playlistTypeButtons.forEach(button => {
        button.addEventListener('click', () => {
            selectPlaylistType(button.dataset.type);
        });
    });

    // Event listeners para los botones del menú principal (navegación)
    mainMenuButtons.forEach(button => {
        button.addEventListener('click', () => {
            const sectionToShow = `${button.dataset.section}-section`;
            showSection(sectionToShow);
            // Si se va a la sección de gestión de playlists, refresca sus datos
            if (button.dataset.section === 'playlists-manager') {
                fetchPlaylistData();
            }
        });
    });

    // --- Event Listeners para el Modal de Añadir Canción ---
    addSongBtn.addEventListener('click', () => {
        addSongModal.style.display = 'flex'; // Usar flex para centrar
        // Limpiar campos del formulario al abrir
        songTitleInput.value = '';
        songArtistInput.value = '';
        songDurationInput.value = '';
        songGenreInput.value = '';
    });

    closeModalButton.addEventListener('click', () => {
        addSongModal.style.display = 'none';
    });

    // Cierra el modal si se hace clic fuera del contenido
    window.addEventListener('click', (event) => {
        if (event.target == addSongModal) {
            addSongModal.style.display = 'none';
        }
    });

    submitAddSongButton.addEventListener('click', () => {
        const songData = {
            title: songTitleInput.value.trim(),
            artist: songArtistInput.value.trim(),
            duration: songDurationInput.value.trim(),
            genre: songGenreInput.value.trim()
        };

        // Simple validación de entrada
        if (!songData.title || !songData.artist || !songData.duration) {
            alert('Por favor, completa al menos el título, artista y duración de la canción.');
            return;
        }
        addSong(songData);
    });

    // --- Event Listeners para los Controles del Reproductor y Playlist ---
    nextBtn.addEventListener('click', nextSong);
    prevBtn.addEventListener('click', previousSong);
    removeSongBtn.addEventListener('click', removeSong);
    resetPlaylistBtn.addEventListener('click', resetPlaylist);


    // --- Inicialización de la Aplicación ---
    // Se ejecuta cuando el DOM está completamente cargado
    async function initializeApp() {
        await fetchUserInfo(); // Primero, carga la información del usuario
        await fetchPlaylistData(); // Luego, carga los datos de la playlist actual
        showSection('home-section'); // Muestra la sección de inicio por defecto
    }

    initializeApp(); // Llama a la función de inicialización
});