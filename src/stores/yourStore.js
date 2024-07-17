import { defineStore } from 'pinia';

export const useStore = defineStore('yourStore', {
  state: () => ({
    currentSong: null,
    isPlaying: false,
    currentSongIndex: 0,
  }),
  actions: {
    setCurrentSong(song) {
      this.currentSong = song;
    },
    setPlaying(status) {
      this.isPlaying = status;
    },
    setCurrentSongIndex(index) {
      this.currentSongIndex = index;
      this.currentSong = null;  // Force refresh
      this.currentSong = this.$state.songs[index];
    },
  },
});
