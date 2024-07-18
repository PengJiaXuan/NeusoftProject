// src/main.js
import { createApp } from 'vue';
import App from './App.vue';
import store from './stores/yourStore'; 
import './styles/style.css'; 
import { Buffer } from 'buffer';

window.Buffer = Buffer;

const app = createApp(App);

app.use(store); 

app.mount('#app');
