<template>
  <div>
    <audio ref="audio" controls @timeupdate="updateTime">
      <source :src="currentSong?.url" type="audio/mpeg">
    </audio>
    <div>
      <button @click="play">Play</button>
      <button @click="pause">Pause</button>
      <div>
        <span>{{ currentTime }}</span> / <span>{{ duration }}</span>
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
</script>

<style scoped>
/* 添加一些基本样式 */
</style>

