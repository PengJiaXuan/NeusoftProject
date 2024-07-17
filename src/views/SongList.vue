<template>
  <div class="player">
    <div class="left-panel">
      <div class="album-cover-container" @mouseover="showPlayButton = true" @mouseleave="showPlayButton = false">
        <img src="/1.png" alt="Album Cover" class="album-cover">
        <div v-if="showPlayButton" class="play-button" @click="playFirstSong">
          <img src="/path/to/play-button.png" alt="Play Button">
        </div>
      </div>
      <div class="album-info">
        <h1>Yoga</h1>
        <p>LagoonWest • 1999 • 8首歌曲, 50分钟29秒</p>
      </div>
    </div>
    <div class="right-panel">
      <div class="album">专辑: Lagoon West</div>
      <ul>
        <li v-for="(song, index) in songs" :key="song.id" @click="playSong(song)">
          <span class="track-number">{{ index + 1 }}</span>
          <span class="track-name">{{ song.name }}</span>
          <span class="track-artist">LagoonWest</span>
          <span class="track-duration">{{ song.duration }}</span>
        </li>
      </ul>
      <audio ref="audioPlayer" class="audio-player"></audio>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useStore } from '../stores/yourStore';

const props = defineProps({
  songs: Array
});

const store = useStore();
const audioPlayer = ref(null);
const showPlayButton = ref(false);

const playFirstSong = () => {
  if (props.songs.length > 0) {
    playSong(props.songs[0]);
  }
};

const playSong = (song) => {
  store.setCurrentSong(song);
  if (audioPlayer.value) {
    audioPlayer.value.src = song.url;
    audioPlayer.value.play();
  }
};
</script>

<style scoped>
.player {
  display: flex;
  flex-direction: column;
  align-items: center;
  background-color: var(--button-background-dark);
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  max-width: 900px;
  margin: 0 auto;
}

.left-panel {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 2rem;
}

.album-cover-container {
  position: relative;
}

.album-cover {
  max-width: 100%;
  max-height: 300px;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.play-button {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 60px;
  height: 60px;
  background-color: rgba(0, 0, 0, 0.5);
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
}

.play-button img {
  width: 50%;
  height: 50%;
}

.album-info {
  text-align: center;
  margin-top: 1rem;
}

.album-info h1 {
  font-size: 2.5rem;
  margin: 0;
}

.album-info p {
  font-size: 1rem;
  margin: 0.5rem 0 0 0;
  color: rgba(255, 255, 255, 0.7);
}

.right-panel {
  width: 100%;
}

.album {
  font-size: 1.2em;
  margin: 20px 0 10px;
  text-align: left;
}

ul {
  list-style: none;
  padding: 0;
}

li {
  display: grid;
  grid-template-columns: 1fr 4fr 2fr 1fr;
  gap: 10px;
  align-items: center;
  padding: 10px;
  margin: 5px 0;
  background-color: var(--button-background-light);
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}

li:hover {
  background-color: var(--hover-color);
  color: var(--background-light);
}

.track-number, .track-name, .track-artist, .track-duration {
  text-align: left;
}

.track-number, .track-duration {
  text-align: center;
  color: #666;
}

.track-name {
  font-weight: bold;
}

.audio-player {
  display: none;
}
</style>
