import { reactive, computed } from 'vue';

export const useStore = () => {
  const state = reactive({
    currentSong: null,
    isPlaying: false,
    songs: []
  });

  const setCurrentSong = (song) => {
    state.currentSong = song;
  };

  const setIsPlaying = (isPlaying) => {
    state.isPlaying = isPlaying;
  };

  const setSongs = (songs) => {
    state.songs = songs;
  };

  return {
    state,
    setCurrentSong,
    setIsPlaying,
    setSongs,
    currentSong: computed(() => state.currentSong),
    isPlaying: computed(() => state.isPlaying),
    songs: computed(() => state.songs)
  };
};
