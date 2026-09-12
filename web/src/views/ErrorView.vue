<script setup lang="ts">
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute } from "vue-router";

const route = useRoute();
const { t } = useI18n();
const reason = computed(() => {
  switch (route.query.reason) {
    case "denied":
      return t("error.denied");
    case "expired":
      return t("error.expired");
    case "guild":
      return t("error.guild");
    case "admin":
      return t("error.admin");
    case "install":
      return t("error.install");
    case "restricted":
      return t("error.restricted");
    case "setup":
      return t("error.setup");
    case "oauth":
      return t("error.generic");
    default:
      return t("error.generic");
  }
});
</script>

<template>
  <section class="state-page section-wrap">
    <div class="state-card">
      <div class="state-icon error" aria-hidden="true">!</div>
      <span class="eyebrow">{{ t("error.eyebrow") }}</span>
      <h1>{{ t("error.title") }}</h1>
      <p>{{ reason }}</p>
      <div class="error-help">
        <strong>{{ t("error.safe") }}</strong>
        <span>{{ t("error.unchanged") }}</span>
      </div>
      <a class="button button-primary full-width" href="/">{{ t("error.back") }}</a>
    </div>
  </section>
</template>
