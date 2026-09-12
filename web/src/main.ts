import { createApp } from "vue";
import App from "./App.vue";
import { createGuildSpanI18n } from "./i18n";
import router from "./router";
import "./styles.css";

createApp(App).use(router).use(createGuildSpanI18n()).mount("#app");
