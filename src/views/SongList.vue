<template>
  <div class="player">
    <div class="left-panel">
      <img :src="currentCover" alt="Album Cover" class="album-cover" v-if="currentCover">
      <audio ref="audioPlayer" controls class="audio-player"></audio>
    </div>
    <div class="right-panel">
      <div class="album">专辑: Lagoon West</div>
      <ul>
        <li v-for="(song, index) in songs" :key="song.id" @click="playSong(song)">
          <span>{{ index + 1 }}. {{ song.name }}</span> 
          <span class="duration">{{ song.duration }}</span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useStore } from '../stores/yourStore';
import { parseBlob } from 'music-metadata-browser';

const props = defineProps({
  songs: Array
});

const store = useStore();
const audioPlayer = ref(null);
const currentCover = ref(null);

const playSong = async (song) => {
  try {
    store.setCurrentSong(song);
    if (audioPlayer.value) {
      audioPlayer.value.src = song.url;
      audioPlayer.value.play();
      await fetchCover(song.url);
    }
  } catch (err) {
    console.error('Error setting current song:', err);
  }
};

const fetchCover = async (url) => {
  try {
    console.log(`Fetching cover for URL: ${url}`);
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const blob = await response.blob();
    console.log('Blob fetched:', blob);
    const metadata = await parseBlob(blob);
    console.log('Metadata parsed:', metadata);
    const picture = metadata.common.picture && metadata.common.picture[0];
    if (picture) {
      const base64String = arrayBufferToBase64(picture.data);
      currentCover.value = `data:${picture.format};base64,${base64String}`;
      console.log('Cover extracted:', currentCover.value);
    } else {
      currentCover.value = null;
      console.log('No cover found in metadata');
    }
  } catch (error) {
    console.error('Error reading metadata:', error);
    currentCover.value = null;
  }
};

const arrayBufferToBase64 = (buffer) => {
  let binary = '';
  const bytes = new Uint8Array(buffer);
  const len = bytes.byteLength;
  for (let i = 0; i < len; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return window.btoa(binary);
};
</script>

<style>
.player {
  display: flex;
  background-color: var(--background-dark);
  color: rgba(255, 255, 255, 0.87);
  font-family: Inter, system-ui, Avenir, Helvetica, Arial, sans-serif;
  height: 100vh;
  overflow: hidden;
}

.left-panel {
  flex: 1;
  padding: 20px;
  text-align: center;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.album-cover {
  max-width: 100%;
  max-height: 70%;
  border-radius: 10px;
}

.audio-player {
  margin-top: 20px;
  width: 100%;
}

.right-panel {
  flex: 2;
  padding: 20px;
  overflow-y: auto;
}

.album {
  font-size: 1.2em;
  margin: 20px 0 10px;
}

ul {
  list-style: none;
  padding: 0;
}

li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  cursor: pointer;
  transition: background-color 0.2s;
}

li:hover {
  background-color: var(--button-background-dark);
}

.duration {
  font-size: 0.9em;
  color: #ccc;
}
</style>
