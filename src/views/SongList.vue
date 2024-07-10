<template>
  <div>
    <h1>Song List</h1>
    <ul>
      <li v-for="song in songs" :key="song.id">
        {{ song.name }}
        <button @click="playSong(song)">Play</button>
      </li>
    </ul>
    <AudioPlayer />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useStore } from '../stores/yourStore';
import { songs } from '../mock/data';
import { useStore } from '../store';
import AudioPlayer from '../components/AudioPlayer.vue';

const store = useStore();

const playSong = (song) => {
  store.setCurrentSong(song);
};
</script>
