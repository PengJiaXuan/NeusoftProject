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
        <p>{{ artistName }} • 1999 • {{ totalSongs }}首歌曲, {{ totalDuration }}</p>
      </div>
    </div>
    <div class="right-panel">
      <ul>
        <li class="legend">
          <span>曲目编号</span>
          <span>曲名</span>
          <span>艺术家</span>
          <span>时长</span>
          <span>播放次数</span>
        </li>
        <li v-for="(song, index) in songs" :key="song.id" @click="playSong(song)">
          <span class="track-number">{{ index + 1 }}</span>
          <span class="track-name">{{ song.name }}</span>
          <span class="track-artist">LagoonWest</span>
          <span class="track-duration">{{ song.duration }}</span>
          <span class="time-played">{{ song.timePlayed }}</span>
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
const isPlaying = ref(false);

const totalSongs = props.songs.length;
const totalDuration = props.songs.reduce((acc, song) => {
  const [minutes, seconds] = song.duration.split(':').map(Number);
  return acc + minutes * 60 + seconds;
}, 0);
const formattedTotalDuration = `${Math.floor(totalDuration / 60)}分钟${totalDuration % 60}秒`;

const playFirstSong = () => {
  if (props.songs.length > 0) {
    playSong(props.songs[0]);
  }
};

const togglePlayPause = () => {
  if (isPlaying.value) {
    audioPlayer.value.pause();
  } else {
    if (audioPlayer.value.src) {
      audioPlayer.value.play();
    } else {
      playFirstSong();
    }
  }
  isPlaying.value = !isPlaying.value;
};

const playSong = (song) => {
  store.setCurrentSong(song);
  if (audioPlayer.value) {
    audioPlayer.value.src = song.url;
    audioPlayer.value.play();
    isPlaying.value = true;
  }
  song.timePlayed += 1;
};

const artistName = "LagoonWest";
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
  width: 50px; 
  height: 50px; 
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  background-color: transparent; 
}

.play-button-image {
  width: 100%;
  height: 100%;
  background-color: transparent;
}

.album-info {
  text-align: center;
  margin-top: 1rem;
}


li.legend {
  background-color: var(--button-background-dark);
  color: var(--background-light);
  cursor: default;
}

li.legend:hover {
  background-color: var(--button-background-dark); 
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
  grid-template-columns: 1fr 4fr 2fr 1fr 1fr;
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

.track-number, .track-name, .track-artist, .track-duration, .time-played {
  text-align: left;
}

.track-number, .track-duration, .time-played {
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
