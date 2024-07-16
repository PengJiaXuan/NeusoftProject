<template>
  <div class="player-container">
    <audio ref="audio" controls @timeupdate="updateTime" class="audio-player">
      <source :src="currentSong?.url" type="audio/mpeg">
    </audio>
    <div class="controls">
      <button @click="play" class="control-button">Play</button>
      <button @click="pause" class="control-button">Pause</button>
      <div class="time-display">
        <span>{{ formattedCurrentTime }}</span> / <span>{{ formattedDuration }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue';
import { useStore } from '../store';

const audio = ref(null);
const store = useStore();
const currentSong = computed(() => store.currentSong);
const currentTime = ref(0);
const duration = ref(0);

watch(currentSong, (newSong) => {
  if (newSong && audio.value) {
    audio.value.load();
    audio.value.play();
  }
});

const play = () => {
  audio.value.play();
};

const pause = () => {
  audio.value.pause();
};

const updateTime = () => {
  currentTime.value = audio.value.currentTime;
  duration.value = audio.value.duration;
};

const formattedTime = (time) => {
  const minutes = Math.floor(time / 60).toString().padStart(2, '0');
  const seconds = Math.floor(time % 60).toString().padStart(2, '0');
  return `${minutes}:${seconds}`;
};

const formattedCurrentTime = computed(() => formattedTime(currentTime.value));
const formattedDuration = computed(() => formattedTime(duration.value));
</script>

<style scoped>
.player-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  background-color: var(--background-dark);
  color: rgba(255, 255, 255, 0.87);
  font-family: Inter, system-ui, Avenir, Helvetica, Arial, sans-serif;
  padding: 20px;
  border-radius: 10px;
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
}

.audio-player {
  width: 100%;
  margin-bottom: 20px;
}

.controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.control-button {
  padding: 10px 20px;
  background-color: var(--button-background-dark);
  border: none;
  border-radius: 5px;
  color: white;
  cursor: pointer;
  transition: background-color 0.3s;
}

.control-button:hover {
  background-color: var(--primary-color);
}

.time-display {
  display: flex;
  gap: 5px;
  font-size: 1em;
  font-weight: bold;
}
</style>


