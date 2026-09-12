import { createRouter, createWebHistory } from "vue-router";
import ConnectingView from "./views/ConnectingView.vue";
import ErrorView from "./views/ErrorView.vue";
import HomeView from "./views/HomeView.vue";
import ServersView from "./views/ServersView.vue";
import SuccessView from "./views/SuccessView.vue";

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", name: "home", component: HomeView },
    { path: "/servers", name: "servers", component: ServersView },
    { path: "/connecting", name: "connecting", component: ConnectingView },
    { path: "/success", name: "success", component: SuccessView },
    { path: "/error", name: "error", component: ErrorView },
  ],
  scrollBehavior: () => ({ top: 0 }),
});
