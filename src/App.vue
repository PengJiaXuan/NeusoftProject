<template>
  <div id="App">
    <SongList :songs="songs" />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import SongList from './views/SongList.vue';

// 初始化变量
const songs = ref([
  { id: 1, name: 'Alivvve - All We Have', url: 'public/Alivvve - All We Have.mp3' },
  { id: 2, name: 'Bubble Tea and Cigarettes - Room 907', url: 'public/Bubble Tea and Cigarettes - Room 907.mp3' },
  { id: 3, name: 'hozuki - snowfield', url: 'public/hozuki - snowfield.mp3' },
]);

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

