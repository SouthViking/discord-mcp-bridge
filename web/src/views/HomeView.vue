<script setup lang="ts">
import { ref } from "vue";
import { useI18n } from "vue-i18n";
import BmcButton from "../components/BmcButton.vue";

const endpoint = "https://guildspan-mcp-production.up.railway.app/mcp";
const copied = ref(false);
const { t } = useI18n();

async function copyEndpoint() {
  await navigator.clipboard.writeText(endpoint);
  copied.value = true;
  window.setTimeout(() => (copied.value = false), 1800);
}
</script>

<template>
  <section class="hero section-wrap">
    <div class="hero-copy">
      <span class="eyebrow"><i></i> {{ t("home.eyebrow") }}</span>
      <h1>{{ t("home.title") }}</h1>
      <p class="hero-lede">{{ t("home.lede") }}</p>
      <div class="hero-actions">
        <a class="button button-primary" href="/servers">{{ t("home.setupServer") }}</a>
        <button class="button button-secondary" type="button" @click="copyEndpoint">
          {{ copied ? t("home.addressCopied") : t("home.copyAddress") }}
        </button>
      </div>
      <p class="helper-text">
        {{ t("home.helper") }}
        <span aria-hidden="true">·</span>
        <a class="helper-link" href="#how-it-works">{{ t("home.seeHow") }}</a>
      </p>
    </div>

    <div class="connection-card" :aria-label="t('home.previewLabel')">
      <div class="profile-banner"></div>
      <div class="profile-content">
        <img class="profile-avatar" src="/brand/icon.png" :alt="t('home.avatarAlt')" />
        <span class="app-badge">APP</span>
        <h2>GuildSpan</h2>
        <p>{{ t("home.cardDescription") }}</p>
        <div class="connection-state">
          <span class="connection-icon">✓</span>
          <div>
            <strong>{{ t("home.ready") }}</strong>
            <small>{{ t("home.protected") }}</small>
          </div>
        </div>
      </div>
    </div>
  </section>

  <section id="how-it-works" class="section-wrap trust-section">
    <div class="section-heading">
      <span class="eyebrow">{{ t("home.flowEyebrow") }}</span>
      <h2>{{ t("home.flowTitle") }}</h2>
    </div>
    <div class="feature-grid">
      <article>
        <span>01</span>
        <h3>{{ t("home.connectTitle") }}</h3>
        <p>{{ t("home.connectText") }}</p>
      </article>
      <article>
        <span>02</span>
        <h3>{{ t("home.chooseTitle") }}</h3>
        <p>{{ t("home.chooseText") }}</p>
      </article>
      <article>
        <span>03</span>
        <h3>{{ t("home.collaborateTitle") }}</h3>
        <p>{{ t("home.collaborateText") }}</p>
      </article>
    </div>
  </section>

  <section class="section-wrap support-section" aria-labelledby="support-title">
    <div class="support-copy">
      <span class="eyebrow"><i></i> {{ t("home.supportEyebrow") }}</span>
      <h2 id="support-title">{{ t("home.supportTitle") }}</h2>
      <p>{{ t("home.supportText") }}</p>
    </div>
    <BmcButton />
  </section>
</template>
