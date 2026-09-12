<script setup lang="ts">
import { useI18n } from "vue-i18n";
import type { SupportedLocale } from "../i18n";
import { setTheme, themeMode, type ThemeMode } from "../preferences";

const { locale, t } = useI18n();
const localeOptions: SupportedLocale[] = ["en", "es"];

function setLocale(nextLocale: SupportedLocale): void {
  locale.value = nextLocale;
  window.localStorage.setItem("guildspan-locale", nextLocale);
  document.documentElement.lang = nextLocale;
}

const themeOptions: Array<{ mode: ThemeMode; icon: string }> = [
  { mode: "system", icon: "◐" },
  { mode: "light", icon: "☀" },
  { mode: "dark", icon: "☾" },
];
</script>

<template>
  <div class="preference-controls">
    <div class="preference-group" role="group" :aria-label="t('preferences.language')">
      <button
        v-for="option in localeOptions"
        :key="option"
        type="button"
        class="preference-button language-option"
        :class="{ active: locale === option }"
        :aria-pressed="locale === option"
        @click="setLocale(option)"
      >
        {{ option.toUpperCase() }}
      </button>
    </div>
    <div class="preference-group" role="group" :aria-label="t('preferences.theme')">
      <button
        v-for="option in themeOptions"
        :key="option.mode"
        type="button"
        class="preference-button theme-option"
        :class="{ active: themeMode === option.mode }"
        :aria-label="t(`preferences.${option.mode}`)"
        :title="t(`preferences.${option.mode}`)"
        :aria-pressed="themeMode === option.mode"
        @click="setTheme(option.mode)"
      >
        <span aria-hidden="true">{{ option.icon }}</span>
        <span class="preference-text">{{ t(`preferences.${option.mode}`) }}</span>
      </button>
    </div>
  </div>
</template>
