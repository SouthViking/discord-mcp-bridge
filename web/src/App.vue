<script setup lang="ts">
import { watchEffect } from "vue";
import { RouterLink, RouterView } from "vue-router";
import { useI18n } from "vue-i18n";
import PreferenceControls from "./components/PreferenceControls.vue";

const { t } = useI18n();

watchEffect(() => {
  document.title = t("meta.title");
  document
    .querySelector<HTMLMetaElement>('meta[name="description"]')
    ?.setAttribute("content", t("meta.description"));
});
</script>

<template>
  <div class="site-shell">
    <header class="site-header">
      <RouterLink class="brand-lockup" to="/" :aria-label="t('nav.home')">
        <img src="/brand/icon.png" alt="" />
        <span>GuildSpan</span>
      </RouterLink>
      <nav :aria-label="t('nav.primary')">
        <a href="https://github.com/SouthViking/guildspan-mcp" target="_blank" rel="noreferrer">
          {{ t("nav.documentation") }}
        </a>
        <span class="status-pill"><i></i> {{ t("nav.remoteMcp") }}</span>
        <PreferenceControls />
      </nav>
    </header>

    <main>
      <RouterView />
    </main>

    <footer class="site-footer">
      <p>{{ t("footer.independent") }}</p>
      <div>
        <a href="https://github.com/SouthViking/guildspan-mcp/blob/main/SECURITY.md" target="_blank" rel="noreferrer">{{ t("footer.security") }}</a>
        <a href="https://github.com/SouthViking/guildspan-mcp" target="_blank" rel="noreferrer">{{ t("footer.support") }}</a>
      </div>
    </footer>
  </div>
</template>
