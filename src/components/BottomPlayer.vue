<template>
  <div class="bottom-player">
    <div class="left-section">
      <img :src="currentSong?.cover || '/1.png'" alt="Album Cover" class="album-cover">
      <div class="song-info">
        <div class="song-name">{{ currentSong?.name || 'Song Name' }}</div>
        <div class="song-artist">{{ currentSong?.artist || 'Artist' }}</div>
      </div>
    </div>
    <div class="center-section">
      <div class="controls">
        <button @click="prevSong">&#9664;&#9664;</button>
        <button @click="togglePlayPause">
          <img :src="isPlaying ? '/pause-btn.png' : '/play-btn.png'" alt="Play/Pause Button" class="control-button-image">
        </button>
        <button @click="nextSong">&#9654;&#9654;</button>
      </div>
      <div class="progress">
        <span class="current-time">{{ formatTime(currentTime) }}</span>
        <input type="range" min="0" :max="duration" v-model="currentTime" @input="seek">
        <span class="duration">{{ formatTime(duration) }}</span>
      </div>
    </div>
    <div class="right-section">
      <input type="range" min="0" max="100" v-model="volume" @input="setVolume">
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import { useStore } from '../stores/yourStore';

const store = useStore();
const audioPlayer = ref(new Audio());
const isPlaying = ref(false);
const currentTime = ref(0);
const duration = ref(0);
const volume = ref(100);

const currentSong = store.currentSong;

watch(currentSong, (newSong) => {
  if (audioPlayer.value) {
    audioPlayer.value.src = newSong.url;
    audioPlayer.value.play();
    isPlaying.value = true;
    duration.value = audioPlayer.value.duration;
  }
});

watch(isPlaying, (newVal) => {
  if (audioPlayer.value) {
    if (newVal) {
      audioPlayer.value.play();
    } else {
      audioPlayer.value.pause();
    }
  }
});

watch(currentTime, (newTime) => {
  if (audioPlayer.value) {
    audioPlayer.value.currentTime = newTime;
  }
});

const togglePlayPause = () => {
  isPlaying.value = !isPlaying.value;
};

const prevSong = () => {
  // 实现上一首歌曲逻辑
};

const nextSong = () => {
  // 实现下一首歌曲逻辑
};

const seek = (event) => {
  currentTime.value = event.target.value;
};

const setVolume = (event) => {
  volume.value = event.target.value;
  if (audioPlayer.value) {
    audioPlayer.value.volume = volume.value / 100;
  }
};

const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
};
</script>

<style scoped>
.bottom-player {
  position: fixed;
  bottom: 0;
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #000;
  padding: 10px 20px;
  box-shadow: 0 -2px 5px rgba(0, 0, 0, 0.5);
  z-index: 1000;
}

.left-section {
  display: flex;
  align-items: center;
}

.album-cover {
  width: 50px;
  height: 50px;
  border-radius: 4px;
  margin-right: 10px;
}

.song-info {
  display: flex;
  flex-direction: column;
}

.song-name {
  font-size: 16px;
  font-weight: bold;
  color: #fff;
}

.song-artist {
  font-size: 14px;
  color: #ccc;
}

.center-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  margin: 0 20px;
}

.controls {
  display: flex;
  align-items: center;
}

.controls button {
  background: none;
  border: none;
  color: #fff;
  font-size: 18px;
  margin: 0 10px;
  cursor: pointer;
}

.control-button-image {
  width: 24px;
  height: 24px;
}

.progress {
  display: flex;
  align-items: center;
  width: 100%;
}

.progress input[type="range"] {
  flex: 1;
  margin: 0 10px;
}

.current-time, .duration {
  font-size: 12px;
  color: #fff;
}

.right-section {
  display: flex;
  align-items: center;
}

.right-section input[type="range"] {
  width: 100px;
  margin: 0 10px;
}
</style>
