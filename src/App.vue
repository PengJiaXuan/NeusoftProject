<template>
  <div id="App">
    <SongList :songs="songsRef" />
    <BottomPlayer />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import SongList from './views/SongList.vue';
import BottomPlayer from './components/BottomPlayer.vue';
import { songs } from './mock/data';

const songsRef = ref(songs);
</script>

<style>
#App {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

.loading-indicator {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  font-size: 1.5em;
}

.SongList-empty {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}

#error-message {
  color: red;
  margin-top: 20px;
}
</style>
