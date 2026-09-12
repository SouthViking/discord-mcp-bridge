import { computed, createApp, defineComponent, h, watchEffect } from "vue";
import { useI18n } from "vue-i18n";
import PreferenceControls from "./components/PreferenceControls.vue";
import { createGuildSpanI18n } from "./i18n";
import "./styles.css";

type ConsentConfig = {
  clientName: string;
  clientId: string;
  redirectUri: string;
  scopes: string[];
  txnId: string;
  csrfToken: string;
  isVerified: boolean;
  verifiedDomain: string;
};

function readConfig(): ConsentConfig {
  const root = document.querySelector<HTMLElement>("#guildspan-consent");
  if (!root?.dataset.config) {
    throw new Error("Missing GuildSpan consent configuration");
  }
  return JSON.parse(root.dataset.config) as ConsentConfig;
}

const ConsentApp = defineComponent({
  setup() {
    const config = readConfig();
    const { t } = useI18n();
    watchEffect(() => {
      document.title = t("consent.pageTitle");
    });
    const requestedAccess = computed(() => [
      {
        title: t("consent.identityTitle"),
        detail: t("consent.identityDetail"),
      },
      {
        title: t("consent.guildsTitle"),
        detail: t("consent.guildsDetail"),
      },
    ]);

    return () =>
      h("main", { class: "consent-shell" }, [
        h("div", { class: "consent-toolbar" }, [h(PreferenceControls)]),
        h("section", { class: "consent-card" }, [
          h("div", { class: "consent-brand" }, [
            h("img", { src: "/brand/icon.png", alt: t("consent.brandAlt") }),
            h("span", "GuildSpan"),
          ]),
          h("span", { class: "eyebrow" }, t("consent.eyebrow")),
          h("h1", [
            `${t("consent.connect")} `,
            h("span", config.clientName),
            ` ${t("consent.toGuildSpan")}`,
          ]),
          h("p", { class: "consent-lede" }, t("consent.lede")),
          h(
            "div",
            { class: "permission-list" },
            requestedAccess.value.map((permission) =>
              h("div", { class: "permission-row" }, [
                h("span", { class: "permission-check" }, "✓"),
                h("div", [h("strong", permission.title), h("small", permission.detail)]),
              ]),
            ),
          ),
          config.isVerified
            ? h("div", { class: "verified-note" }, [
                h("span", "✓"),
                h("p", [
                  t("consent.verifiedDomain", { domain: config.verifiedDomain }),
                ]),
              ])
            : h("div", { class: "neutral-note" }, [
                h("span", "i"),
                h("p", t("consent.safeHint")),
              ]),
          h("form", { method: "POST", action: "", class: "consent-form" }, [
            h("input", { type: "hidden", name: "txn_id", value: config.txnId }),
            h("input", { type: "hidden", name: "csrf_token", value: config.csrfToken }),
            h("input", { type: "hidden", name: "submit", value: "true" }),
            h(
              "button",
              { class: "button button-primary", type: "submit", name: "action", value: "approve" },
              t("consent.continue"),
            ),
            h(
              "button",
              { class: "button button-quiet", type: "submit", name: "action", value: "deny" },
              t("consent.cancel"),
            ),
          ]),
          h("details", { class: "technical-details" }, [
            h("summary", t("consent.technical")),
            h("dl", [
              h("div", [h("dt", t("consent.application")), h("dd", config.clientName)]),
              h("div", [h("dt", t("consent.callback")), h("dd", config.redirectUri)]),
              h("div", [
                h("dt", t("consent.scopes")),
                h("dd", config.scopes.join(", ") || t("consent.none")),
              ]),
              h("div", [h("dt", t("consent.clientId")), h("dd", config.clientId)]),
            ]),
          ]),
        ]),
        h("p", { class: "consent-footer" }, t("consent.footer")),
      ]);
  },
});

createApp(ConsentApp).use(createGuildSpanI18n()).mount("#guildspan-consent");
