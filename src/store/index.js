import { createPinia, defineStore } from 'pinia';

export const useStore = defineStore('main', {
  state: () => ({
    currentSong: null,
  }),
  actions: {
    setCurrentSong(song) {
      this.currentSong = song;
    },
  }
});

const pinia = createPinia();
export default pinia;
