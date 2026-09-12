<script setup lang="ts">
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute } from "vue-router";

const route = useRoute();
const { t } = useI18n();
const guildName = computed(() =>
  typeof route.query.guild === "string" ? route.query.guild : "",
);
const isOnboarding = computed(
  () => route.query.source === "onboarding" && Boolean(guildName.value),
);
const lede = computed(() =>
  isOnboarding.value
    ? t("success.onboardingLede", { guild: guildName.value })
    : t("success.lede"),
);
const detail = computed(() =>
  isOnboarding.value ? t("success.onboardingDetail") : t("success.detail"),
);
</script>

<template>
  <section class="state-page section-wrap">
    <div class="state-card">
      <div class="state-icon success" aria-hidden="true">✓</div>
      <span class="eyebrow">{{ t("success.eyebrow") }}</span>
      <h1>{{ t("success.title") }}</h1>
      <p>{{ lede }}</p>
      <div class="soft-panel">
        <img src="/brand/icon.png" alt="" />
        <div>
          <strong>{{ t("success.connected") }}</strong>
          <small>{{ detail }}</small>
        </div>
      </div>
      <a class="button button-primary full-width" href="/">{{ t("success.done") }}</a>
    </div>
  </section>
</template>
