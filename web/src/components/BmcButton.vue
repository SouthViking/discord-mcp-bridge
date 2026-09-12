<script setup lang="ts">
import { onBeforeUnmount, onMounted, useTemplateRef } from "vue";

const container = useTemplateRef<HTMLDivElement>("container");
const buttonColor = "#A99DD0";
const buttonInk = "#242A34";
const coffeeColor = "#FFFFFF";

type BmcButtonRenderer = (
  text: string,
  slug: string,
  color: string,
  emoji: string,
  font: string,
  fontColor: string,
  outlineColor: string,
  coffeeColor: string,
) => string;

declare global {
  interface Window {
    bmcBtnWidget?: BmcButtonRenderer;
  }
}

function renderOfficialButton(): void {
  if (!container.value || !window.bmcBtnWidget) {
    return;
  }

  const buttonMarkup = window.bmcBtnWidget(
    "Buy me a coffee",
    "southviking",
    buttonColor,
    "",
    "Cookie",
    buttonInk,
    buttonInk,
    coffeeColor,
  );
  container.value.replaceChildren();
  container.value.insertAdjacentHTML("afterbegin", buttonMarkup);
}

function createOfficialButton(): void {
  if (!container.value) {
    return;
  }

  if (window.bmcBtnWidget) {
    renderOfficialButton();
    return;
  }

  const script = document.createElement("script");
  script.type = "text/javascript";
  script.src = "https://cdnjs.buymeacoffee.com/1.0.0/button.prod.min.js";
  script.dataset.name = "bmc-button";
  script.dataset.slug = "southviking";
  script.dataset.color = buttonColor;
  script.dataset.emoji = "";
  script.dataset.font = "Cookie";
  script.dataset.text = "Buy me a coffee";
  script.dataset.outlineColor = buttonInk;
  script.dataset.fontColor = buttonInk;
  script.dataset.coffeeColor = coffeeColor;
  script.addEventListener("load", renderOfficialButton, { once: true });
  container.value.appendChild(script);
}

onMounted(createOfficialButton);

onBeforeUnmount(() => {
  container.value?.replaceChildren();
});
</script>

<template>
  <div ref="container" class="bmc-button-slot"></div>
</template>
