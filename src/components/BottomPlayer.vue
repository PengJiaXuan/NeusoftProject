<template>
  <div class="bottom-player">
    <div class="left-section">
      <img :src="currentSong?.cover || '/1.png'" alt="Album Cover" class="album-cover">
      <div class="song-info">
        <div class="song-name">{{ currentSong?.name || 'Song Name' }}</div>
      </div>
    </div>
    <div class="center-section">
      <div class="controls">
        <button @click="prevSong">&#9664;&#9664;</button>
        <button @click="togglePlayPause">
          <img :src="isPlaying ? '/bottompause-btn.png' : '/bottomplay-btn.png'" alt="Play/Pause Button" class="control-button-image">
        </button>
        <button @click="nextSong">&#9654;&#9654;</button>
      </div>
      <div class="progress">
        <span class="current-time">{{ formatTime(currentTime) }}</span>
        <input type="range" min="0" :max="duration" v-model="currentTime" @input="seek" class="progress-bar">
        <span class="duration">{{ formatTime(duration) }}</span>
      </div>
      <div class="playback-speed">
        <label for="speed">Speed:</label>
        <select id="speed" v-model="playbackRate" @change="setPlaybackRate">
          <option value="0.5">0.5x</option>
          <option value="1">1x</option>
          <option value="1.5">1.5x</option>
          <option value="2">2x</option>
        </select>
      </div>
    </div>
    <div class="right-section">
      <input type="range" min="0" max="100" v-model="volume" @input="setVolume" class="volume-control">
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed, onMounted } from 'vue';
import { useStore } from '../stores/yourStore';
import { songs } from '../mock/data';

const store = useStore();
const audioPlayer = ref(new Audio());
const isPlaying = ref(false);
const currentTime = ref(0);
const duration = ref(0);
const volume = ref(100);
const playbackRate = ref(1);
const currentSongIndex = ref(0);

const currentSong = computed(() => songs[currentSongIndex.value]);

watch(currentSong, (newSong) => {
  if (audioPlayer.value) {
    audioPlayer.value.src = newSong.url;
    audioPlayer.value.load();
    audioPlayer.value.onloadedmetadata = () => {
      duration.value = audioPlayer.value.duration;
      audioPlayer.value.play();
      isPlaying.value = true;
    };
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

watch(playbackRate, (newRate) => {
  if (audioPlayer.value) {
    audioPlayer.value.playbackRate = newRate;
  }
});

const togglePlayPause = () => {
  if (!isPlaying.value && !audioPlayer.value.src) {
    playSong(0);
  } else {
    isPlaying.value = !isPlaying.value;
  }
};

const playSong = (index) => {
  currentSongIndex.value = index;
  if (audioPlayer.value) {
    audioPlayer.value.src = songs[currentSongIndex.value].url;
    audioPlayer.value.load();
    audioPlayer.value.onloadedmetadata = () => {
      duration.value = audioPlayer.value.duration;
      audioPlayer.value.play();
      isPlaying.value = true;
    };
  }
};

const prevSong = () => {
  if (currentSongIndex.value > 0) {
    playSong(currentSongIndex.value - 1);
  }
};

const nextSong = () => {
  if (currentSongIndex.value < songs.length - 1) {
    playSong(currentSongIndex.value + 1);
  }
};

const seek = (event) => {
  currentTime.value = event.target.value;
  audioPlayer.value.currentTime = currentTime.value;
};

const setVolume = (event) => {
  volume.value = event.target.value;
  if (audioPlayer.value) {
    audioPlayer.value.volume = volume.value / 100;
  }
};

const setPlaybackRate = (event) => {
  playbackRate.value = event.target.value;
  if (audioPlayer.value) {
    audioPlayer.value.playbackRate = playbackRate.value;
  }
};

const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
};

onMounted(() => {
  audioPlayer.value.ontimeupdate = () => {
    currentTime.value = audioPlayer.value.currentTime;
  };
});
</script>

<style scoped>
.bottom-player {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #000;
  padding: 10px 20px;
  box-shadow: 0 -2px 5px rgba(0, 0, 0, 0.5);
  z-index: 1000;
  border-radius: 10px 10px 0 0;
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
  justify-content: center;
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

.progress-bar {
  flex: 1;
  margin: 0 10px;
  max-width: 1300px;
}

.current-time, .duration {
  font-size: 12px;
  color: #fff;
}

.right-section {
  display: flex;
  align-items: center;
}

.volume-control {
  width: 100px;
  margin-right: 30px;
}

.playback-speed {
  margin-top: 10px;
  color: #fff;
}

.playback-speed label {
  margin-right: 5px;
}

.playback-speed select {
  background: #333;
  color: #fff;
  border: 1px solid #444;
  border-radius: 4px;
  padding: 2px 5px;
}
</style>
