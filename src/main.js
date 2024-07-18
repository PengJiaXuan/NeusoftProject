// src/main.js
import { createApp } from 'vue';
import App from './App.vue';
import store from './stores/yourStore'; // Ensure this path is correct
import './styles/style.css'; 
import { Buffer } from 'buffer';

window.Buffer = Buffer;

const app = createApp(App);

app.use(store); // Use Vuex store

app.mount('#app');
