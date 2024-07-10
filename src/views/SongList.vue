<template>
  <div>
    <ul>
      <li v-for="song in songs" :key="song.id" @click="playSong(song)">
        {{ song.name }}
      </li>
    </ul>
    <!-- 音频播放器元素 -->
    <audio ref="audioPlayer" controls></audio>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useStore } from '../stores/yourStore';
import { songs } from '../mock/data';

const store = useStore();
const audioPlayer = ref(null);

const songList = ref(songs);

const playSong = (song) => {
  try {
    store.setCurrentSong(song);
    if (audioPlayer.value) {
      audioPlayer.value.src = song.url;
      audioPlayer.value.play();
    }
  } catch (err) {
    console.error('Error setting current song:', err);
  }
};
</script>

<style>
/* 样式调整，可以根据需要修改 */
ul {
  list-style-type: none;
  padding: 0;
}

li {
  cursor: pointer;
  margin: 5px 0;
}
</style>
