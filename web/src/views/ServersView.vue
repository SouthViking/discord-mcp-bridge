<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";

type GuildStatus =
  | "authorized"
  | "ready_to_activate"
  | "requires_installation"
  | "administrator_required"
  | "restricted";

interface DiscordUser {
  id: string;
  username: string | null;
  display_name: string | null;
  avatar_url: string | null;
}

interface DiscordGuild {
  id: string;
  name: string;
  icon_url: string | null;
  owner: boolean;
  status: GuildStatus;
  bot_accessible: boolean;
}

interface GuildResponse {
  status: string;
  user?: DiscordUser;
  csrf_token?: string;
  guilds?: DiscordGuild[];
}

type PageState = "loading" | "signed_out" | "ready" | "unavailable" | "error";

const { t } = useI18n();
const pageState = ref<PageState>("loading");
const user = ref<DiscordUser | null>(null);
const guilds = ref<DiscordGuild[]>([]);
const csrfToken = ref("");
const activeGuildId = ref<string | null>(null);
const actionError = ref("");

const userName = computed(
  () => user.value?.display_name || user.value?.username || t("servers.accountFallback"),
);

function guildInitial(name: string): string {
  return name.trim().charAt(0).toUpperCase() || "G";
}

function installUrl(guildId: string): string {
  return `/onboarding/install?guild_id=${encodeURIComponent(guildId)}`;
}

async function loadGuilds(): Promise<void> {
  pageState.value = "loading";
  try {
    const response = await fetch("/api/onboarding/guilds", {
      credentials: "same-origin",
      headers: { Accept: "application/json" },
    });
    if (response.status === 401) {
      pageState.value = "signed_out";
      return;
    }
    if (response.status === 503) {
      pageState.value = "unavailable";
      return;
    }
    if (!response.ok) {
      throw new Error("guild discovery failed");
    }
    const payload = (await response.json()) as GuildResponse;
    user.value = payload.user ?? null;
    guilds.value = payload.guilds ?? [];
    csrfToken.value = payload.csrf_token ?? "";
    pageState.value = "ready";
  } catch {
    pageState.value = "error";
  }
}

async function activateGuild(guild: DiscordGuild): Promise<void> {
  activeGuildId.value = guild.id;
  actionError.value = "";
  try {
    const response = await fetch(
      `/api/onboarding/guilds/${encodeURIComponent(guild.id)}/activate`,
      {
        method: "POST",
        credentials: "same-origin",
        headers: {
          Accept: "application/json",
          "X-GuildSpan-CSRF": csrfToken.value,
        },
      },
    );
    const payload = (await response.json()) as { redirect?: string };
    if (!response.ok || !payload.redirect) {
      throw new Error("guild activation failed");
    }
    window.location.assign(payload.redirect);
  } catch {
    actionError.value = t("servers.actionError");
    activeGuildId.value = null;
  }
}

onMounted(loadGuilds);
</script>

<template>
  <section class="servers-page section-wrap">
    <div class="server-picker">
      <template v-if="pageState === 'loading'">
        <div class="server-message">
          <div class="orb-loader" aria-hidden="true"><span></span></div>
          <h1>{{ t("servers.loadingTitle") }}</h1>
          <p>{{ t("servers.loadingText") }}</p>
        </div>
      </template>

      <template v-else-if="pageState === 'signed_out'">
        <div class="server-message">
          <img class="server-message-icon" src="/brand/icon.png" alt="" />
          <h1>{{ t("servers.signInTitle") }}</h1>
          <p>{{ t("servers.signInText") }}</p>
          <a class="button button-primary" href="/onboarding/start">
            {{ t("servers.signInAction") }}
          </a>
        </div>
      </template>

      <template v-else-if="pageState === 'unavailable'">
        <div class="server-message">
          <img class="server-message-icon" src="/brand/icon.png" alt="" />
          <h1>{{ t("servers.unavailableTitle") }}</h1>
          <p>{{ t("servers.unavailableText") }}</p>
          <a class="button button-secondary" href="/">{{ t("servers.back") }}</a>
        </div>
      </template>

      <template v-else-if="pageState === 'error'">
        <div class="server-message">
          <div class="state-icon error" aria-hidden="true">!</div>
          <h1>{{ t("servers.errorTitle") }}</h1>
          <p>{{ t("servers.errorText") }}</p>
          <button class="button button-primary" type="button" @click="loadGuilds">
            {{ t("servers.retry") }}
          </button>
        </div>
      </template>

      <template v-else>
        <div class="server-picker-heading">
          <div>
            <span class="eyebrow">{{ t("servers.eyebrow") }}</span>
            <h1>{{ t("servers.title") }}</h1>
            <p>{{ t("servers.lede") }}</p>
          </div>
          <div class="discord-account">
            <img v-if="user?.avatar_url" :src="user.avatar_url" alt="" />
            <span v-else>{{ guildInitial(userName) }}</span>
            <div>
              <small>{{ t("servers.signedInAs") }}</small>
              <strong>{{ userName }}</strong>
            </div>
          </div>
        </div>

        <p v-if="actionError" class="inline-error" role="alert">{{ actionError }}</p>

        <div v-if="guilds.length" class="guild-list">
          <article v-for="guild in guilds" :key="guild.id" class="guild-row">
            <img v-if="guild.icon_url" :src="guild.icon_url" alt="" />
            <span v-else class="guild-fallback">{{ guildInitial(guild.name) }}</span>
            <div class="guild-copy">
              <h2>{{ guild.name }}</h2>
              <p>{{ t(`servers.statusText.${guild.status}`) }}</p>
            </div>
            <span :class="['guild-status', `is-${guild.status}`]">
              {{ t(`servers.statusLabel.${guild.status}`) }}
            </span>
            <a
              v-if="guild.status === 'requires_installation'"
              class="button button-primary guild-action"
              :href="installUrl(guild.id)"
            >
              {{ t("servers.install") }}
            </a>
            <button
              v-else-if="guild.status === 'ready_to_activate'"
              class="button button-primary guild-action"
              type="button"
              :disabled="activeGuildId === guild.id"
              @click="activateGuild(guild)"
            >
              {{
                activeGuildId === guild.id
                  ? t("servers.activating")
                  : t("servers.activate")
              }}
            </button>
            <span v-else-if="guild.status === 'authorized'" class="guild-ready-mark">✓</span>
          </article>
        </div>

        <div v-else class="empty-guilds">
          <strong>{{ t("servers.emptyTitle") }}</strong>
          <p>{{ t("servers.emptyText") }}</p>
        </div>

        <div class="server-picker-footer">
          <div class="server-picker-links">
            <a href="/">{{ t("servers.back") }}</a>
            <a href="/onboarding/logout">{{ t("servers.switchAccount") }}</a>
          </div>
          <span>{{ t("servers.permissionHint") }}</span>
        </div>
      </template>
    </div>
  </section>
</template>
