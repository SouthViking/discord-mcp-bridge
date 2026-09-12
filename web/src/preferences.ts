import { ref, watch } from "vue";

export type ThemeMode = "system" | "light" | "dark";

const THEME_STORAGE_KEY = "guildspan-theme";
const systemTheme = window.matchMedia("(prefers-color-scheme: dark)");

function getInitialTheme(): ThemeMode {
  const storedTheme = window.localStorage.getItem(THEME_STORAGE_KEY);
  if (storedTheme === "light" || storedTheme === "dark" || storedTheme === "system") {
    return storedTheme;
  }
  return "system";
}

export const themeMode = ref<ThemeMode>(getInitialTheme());

function applyTheme(mode: ThemeMode): void {
  const resolvedTheme = mode === "system" ? (systemTheme.matches ? "dark" : "light") : mode;
  document.documentElement.dataset.theme = resolvedTheme;
  document.documentElement.style.colorScheme = resolvedTheme;
}

watch(
  themeMode,
  (mode) => {
    window.localStorage.setItem(THEME_STORAGE_KEY, mode);
    applyTheme(mode);
  },
  { immediate: true },
);

systemTheme.addEventListener("change", () => {
  if (themeMode.value === "system") {
    applyTheme("system");
  }
});

export function setTheme(mode: ThemeMode): void {
  themeMode.value = mode;
}
