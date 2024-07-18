// src/stores/yourStore.js
import { createStore } from 'vuex';

const store = createStore({
  state: {
    currentSong: null,
    isPlaying: false,
    currentSongIndex: 0,
  },
  mutations: {
    setCurrentSong(state, song) {
      state.currentSong = song;
    },
    setIsPlaying(state, isPlaying) {
      state.isPlaying = isPlaying;
    },
    setCurrentSongIndex(state, index) {
      state.currentSongIndex = index;
    }
  },
  getters: {
    currentSong: (state) => state.currentSong,
    isPlaying: (state) => state.isPlaying,
    currentSongIndex: (state) => state.currentSongIndex,
  }
});

export default store;
