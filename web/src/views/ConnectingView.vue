<script setup lang="ts">
import { useI18n } from "vue-i18n";

const { t } = useI18n();
</script>

<template>
  <section class="state-page section-wrap">
    <div class="state-card">
      <div class="orb-loader" aria-hidden="true"><span></span></div>
      <h1>{{ t("connecting.title") }}</h1>
      <p>{{ t("connecting.lede") }}</p>
    </div>
  </section>
</template>
