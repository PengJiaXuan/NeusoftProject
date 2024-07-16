import { createApp } from 'vue';
import App from './App.vue';
import { createPinia } from 'pinia';
import './style.css'; 
import { Buffer } from 'buffer';


window.Buffer = Buffer;

const pinia = createPinia();
const app = createApp(App);

app.use(pinia);

app.mount('#app');
