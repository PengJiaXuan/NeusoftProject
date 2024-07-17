<template>
  <div class="player">
    <div class="left-panel">
      <div class="album-cover-container" @mouseover="showPlayButton = true" @mouseleave="showPlayButton = false">
        <img src="/1.png" alt="Album Cover" class="album-cover">
        <div v-if="showPlayButton" class="play-button" @click="togglePlayPause">
          <img :src="isPlaying ? '/pause-btn.png' : '/play-btn.png'" alt="Play/Pause Button" class="play-button-image">
        </div>
      </div>
      <div class="album-info">
        <h1>Yoga</h1>
        <p>LagoonWest • 1999 • {{ songCount }}首歌曲, {{ totalDuration }}</p>
      </div>
    </div>
    <div class="right-panel">
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
import { ref, computed } from 'vue';
import { useStore } from '../stores/yourStore';

const props = defineProps({
  songs: Array
});

const store = useStore();
const audioPlayer = ref(null);
const showPlayButton = ref(false);
const isPlaying = computed(() => store.isPlaying);

const playFirstSong = () => {
  if (props.songs.length > 0) {
    playSong(props.songs[0]);
  }
};

const togglePlayPause = () => {
  if (isPlaying.value) {
    audioPlayer.value.pause();
    store.setPlaying(false);
  } else {
    if (audioPlayer.value.src) {
      audioPlayer.value.play();
    } else {
      playFirstSong();
    }
    store.setPlaying(true);
  }
};

const playSong = (song) => {
  store.setCurrentSong(song);
  if (audioPlayer.value) {
    audioPlayer.value.src = song.url;
    audioPlayer.value.play();
    store.setPlaying(true);
  }
};

// 计算歌曲数量和总时长
const songCount = computed(() => props.songs.length);

const totalDuration = computed(() => {
  let totalSeconds = 0;
  props.songs.forEach(song => {
    const parts = song.duration.split(':');
    const minutes = parseInt(parts[0]);
    const seconds = parseInt(parts[1]);
    totalSeconds += (minutes * 60) + seconds;
  });

  const totalMinutes = Math.floor(totalSeconds / 60);
  const remainingSeconds = totalSeconds % 60;

  return `${totalMinutes}分钟${remainingSeconds}秒`;
});
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
  width: 50px; /* 根据需要调整大小 */
  height: 50px; /* 根据需要调整大小 */
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  background-color: transparent; /* 确保按钮背景透明 */
}

.play-button-image {
  width: 100%;
  height: 100%;
  background-color: transparent; /* 确保按钮背景透明 */
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
