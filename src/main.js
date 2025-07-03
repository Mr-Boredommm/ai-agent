import './assets/main.css'
import 'element-plus/dist/index.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import router from './router'
import chat from './chat.vue'

const app = createApp(chat)

app.use(createPinia())
app.use(router)

app.mount('#app')

