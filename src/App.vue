<template>
  <div id="App">
    <SongList :songsDisc1="songsDisc1" :songsDisc2="songsDisc2" />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import SongList from './views/SongList.vue';
import { songsDisc1, songsDisc2 } from './mock/data';

const songsDisc1Ref = ref(songsDisc1);
const songsDisc2Ref = ref(songsDisc2);
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
