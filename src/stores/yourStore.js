import { defineStore } from 'pinia';

export const useStore = defineStore('yourStore', {
  state: () => ({
    currentSong: null,
  }),
  actions: {
    setCurrentSong(song) {
      this.currentSong = song;
    },
  },
});
