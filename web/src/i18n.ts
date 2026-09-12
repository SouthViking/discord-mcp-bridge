import { createI18n } from "vue-i18n";

export type SupportedLocale = "en" | "es";

const messages = {
  en: {
    meta: {
      title: "GuildSpan — Discord for AI assistants",
      description: "GuildSpan connects AI assistants to authorized Discord communities.",
    },
    preferences: {
      language: "Language",
      theme: "Appearance",
      system: "System",
      light: "Light",
      dark: "Dark",
    },
    nav: {
      home: "GuildSpan home",
      primary: "Primary navigation",
      documentation: "Documentation",
      remoteMcp: "Remote MCP",
    },
    footer: {
      independent: "GuildSpan is an independent project and is not affiliated with Discord.",
      security: "Security",
      support: "Support",
    },
    home: {
      eyebrow: "Discord, thoughtfully connected",
      title: "Bring your community into the work",
      lede:
        "GuildSpan gives your AI assistant a secure, structured connection to the Discord communities you authorize—without exposing bot credentials or copying conversations into another platform.",
      copyAddress: "Copy MCP address",
      addressCopied: "Address copied",
      setupServer: "Connect Discord",
      seeHow: "See how it works",
      helper: "Remote MCP · Discord OAuth · No local installation",
      previewLabel: "GuildSpan connection preview",
      avatarAlt: "GuildSpan bot avatar",
      cardDescription: "Connect AI workflows to the right conversations.",
      ready: "Ready for your assistant",
      protected: "Protected by OAuth 2.1",
      flowEyebrow: "A calmer connection flow",
      flowTitle: "Clear at every step",
      connectTitle: "Connect",
      connectText:
        "Authorize GuildSpan from your compatible AI assistant through your existing Discord identity.",
      chooseTitle: "Choose",
      chooseText:
        "Work only with servers that you belong to and that GuildSpan can access.",
      collaborateTitle: "Collaborate",
      collaborateText:
        "Read context and take deliberate actions with permissions enforced server-side.",
      supportEyebrow: "Community supported",
      supportTitle: "Help GuildSpan keep growing",
      supportText:
        "GuildSpan grows thanks to the voluntary support of its community. Every contribution helps us keep improving it and create new possibilities for everyone.",
    },
    connecting: {
      title: "Connecting to GuildSpan",
      lede: "One moment, we’re getting everything ready so you can continue.",
    },
    servers: {
      eyebrow: "Your Discord communities",
      title: "Choose a server",
      lede:
        "Select where you want to use GuildSpan. We’ll guide you through anything that is still needed.",
      signedInAs: "Signed in as",
      accountFallback: "Discord user",
      loadingTitle: "Loading your servers",
      loadingText: "One moment while we check your Discord communities.",
      signInTitle: "Start with Discord",
      signInText:
        "Sign in to see the servers you can connect. GuildSpan never asks for your Discord password.",
      signInAction: "Continue with Discord",
      unavailableTitle: "Setup is not available right now",
      unavailableText:
        "GuildSpan server setup is available when the hosted service is configured.",
      errorTitle: "We couldn’t load your servers",
      errorText: "Please try again in a moment.",
      retry: "Try again",
      install: "Add GuildSpan",
      activate: "Finish setup",
      activating: "Finishing…",
      actionError: "We couldn’t finish this server setup. Please try again.",
      emptyTitle: "No Discord servers found",
      emptyText: "Make sure you are using the right Discord account.",
      back: "Back to GuildSpan",
      switchAccount: "Use another account",
      permissionHint:
        "Only an owner or someone with permission to manage the server can add GuildSpan.",
      statusLabel: {
        authorized: "Ready",
        ready_to_activate: "Almost ready",
        requires_installation: "Bot required",
        administrator_required: "Ask an admin",
        restricted: "Unavailable",
      },
      statusText: {
        authorized: "GuildSpan is connected and ready to use.",
        ready_to_activate: "The bot is already here. Confirm this server to continue.",
        requires_installation: "Add the official GuildSpan bot to this server.",
        administrator_required: "A server administrator needs to connect GuildSpan first.",
        restricted: "This server is not currently available in GuildSpan.",
      },
    },
    success: {
      eyebrow: "Connection complete",
      title: "GuildSpan is ready",
      lede:
        "You can close this window and return to your AI assistant. Your Discord credentials remain protected.",
      connected: "GuildSpan connected",
      detail: "Remote MCP · OAuth 2.1",
      onboardingLede: "{guild} is now connected and ready to use with GuildSpan.",
      onboardingDetail: "Discord server connected",
      done: "Done",
    },
    error: {
      eyebrow: "Connection interrupted",
      title: "We couldn’t finish",
      denied: "The authorization request was declined. Nothing was connected or changed.",
      expired:
        "This connection request expired. Start authentication again from your AI assistant.",
      guild: "GuildSpan could not find an eligible Discord server for this account.",
      admin: "A server administrator needs to connect GuildSpan first.",
      install: "Discord did not complete the bot installation. Please try again.",
      restricted: "This server is not currently enabled for GuildSpan.",
      setup: "Discord server setup is not available in this environment.",
      generic:
        "GuildSpan could not complete the connection. Try again from your AI assistant.",
      safe: "Your Discord account is safe.",
      unchanged: "No message was sent and no server permission was changed.",
      back: "Back to GuildSpan",
    },
    consent: {
      pageTitle: "Connect to GuildSpan",
      brandAlt: "GuildSpan",
      eyebrow: "Secure authorization",
      connect: "Connect",
      toGuildSpan: "to GuildSpan",
      lede:
        "Review this connection before continuing to Discord. You stay in control of every server and action.",
      identityTitle: "See your Discord identity",
      identityDetail: "Used to create and protect your GuildSpan connection.",
      guildsTitle: "See your Discord servers",
      guildsDetail: "Only eligible servers are shown. GuildSpan never joins one silently.",
      verifiedDomain: "Verified client domain: {domain}",
      safeHint: "Only continue if you started this connection from your AI assistant.",
      continue: "Continue to Discord",
      cancel: "Cancel",
      technical: "Technical details",
      application: "Application",
      callback: "Callback",
      scopes: "Scopes",
      clientId: "Client ID",
      none: "None",
      footer: "GuildSpan never asks for your Discord password.",
    },
  },
  es: {
    meta: {
      title: "GuildSpan — Discord para asistentes de IA",
      description: "GuildSpan conecta asistentes de IA con comunidades de Discord autorizadas.",
    },
    preferences: {
      language: "Idioma",
      theme: "Apariencia",
      system: "Sistema",
      light: "Claro",
      dark: "Oscuro",
    },
    nav: {
      home: "Inicio de GuildSpan",
      primary: "Navegación principal",
      documentation: "Documentación",
      remoteMcp: "MCP remoto",
    },
    footer: {
      independent: "GuildSpan es un proyecto independiente y no está afiliado con Discord.",
      security: "Seguridad",
      support: "Soporte",
    },
    home: {
      eyebrow: "Discord, conectado con intención",
      title: "Lleva tu comunidad a tu flujo de trabajo",
      lede:
        "GuildSpan conecta de forma segura y estructurada tu asistente de IA con las comunidades de Discord que autorizas, sin exponer credenciales del bot ni copiar conversaciones a otra plataforma.",
      copyAddress: "Copiar dirección MCP",
      addressCopied: "Dirección copiada",
      setupServer: "Conectar Discord",
      seeHow: "Ver cómo funciona",
      helper: "MCP remoto · OAuth de Discord · Sin instalación local",
      previewLabel: "Vista previa de la conexión con GuildSpan",
      avatarAlt: "Avatar del bot GuildSpan",
      cardDescription: "Conecta flujos de IA con las conversaciones correctas.",
      ready: "Listo para tu asistente",
      protected: "Protegido con OAuth 2.1",
      flowEyebrow: "Una conexión más simple",
      flowTitle: "Claridad en cada paso",
      connectTitle: "Conecta",
      connectText:
        "Autoriza GuildSpan desde tu asistente de IA compatible usando tu identidad de Discord.",
      chooseTitle: "Elige",
      chooseText:
        "Trabaja solo con servidores a los que perteneces y a los que GuildSpan puede acceder.",
      collaborateTitle: "Colabora",
      collaborateText:
        "Consulta contexto y realiza acciones deliberadas con permisos aplicados desde el servidor.",
      supportEyebrow: "Impulsado por la comunidad",
      supportTitle: "Ayuda a que GuildSpan siga creciendo",
      supportText:
        "GuildSpan crece gracias al apoyo voluntario de su comunidad. Cada aporte nos ayuda a seguir mejorándolo y a crear nuevas posibilidades para todos.",
    },
    connecting: {
      title: "Conectando con GuildSpan",
      lede: "Un momento, estamos preparando todo para que puedas continuar.",
    },
    servers: {
      eyebrow: "Tus comunidades de Discord",
      title: "Elige un servidor",
      lede:
        "Selecciona dónde quieres usar GuildSpan. Te guiaremos si todavía falta algún paso.",
      signedInAs: "Conectado como",
      accountFallback: "Usuario de Discord",
      loadingTitle: "Cargando tus servidores",
      loadingText: "Un momento mientras revisamos tus comunidades de Discord.",
      signInTitle: "Comienza con Discord",
      signInText:
        "Inicia sesión para ver los servidores que puedes conectar. GuildSpan nunca te pedirá tu contraseña de Discord.",
      signInAction: "Continuar con Discord",
      unavailableTitle: "La configuración no está disponible ahora",
      unavailableText:
        "Podrás configurar servidores cuando el servicio remoto de GuildSpan esté habilitado.",
      errorTitle: "No pudimos cargar tus servidores",
      errorText: "Inténtalo nuevamente en un momento.",
      retry: "Intentar nuevamente",
      install: "Agregar GuildSpan",
      activate: "Finalizar configuración",
      activating: "Finalizando…",
      actionError: "No pudimos terminar la configuración. Inténtalo nuevamente.",
      emptyTitle: "No encontramos servidores de Discord",
      emptyText: "Comprueba que estás utilizando la cuenta correcta de Discord.",
      back: "Volver a GuildSpan",
      switchAccount: "Usar otra cuenta",
      permissionHint:
        "Solo el propietario o alguien con permiso para gestionar el servidor puede agregar GuildSpan.",
      statusLabel: {
        authorized: "Listo",
        ready_to_activate: "Casi listo",
        requires_installation: "Falta el bot",
        administrator_required: "Pide ayuda a un admin",
        restricted: "No disponible",
      },
      statusText: {
        authorized: "GuildSpan está conectado y listo para usar.",
        ready_to_activate: "El bot ya está dentro. Confirma este servidor para continuar.",
        requires_installation: "Agrega el bot oficial de GuildSpan a este servidor.",
        administrator_required: "Un administrador debe conectar GuildSpan primero.",
        restricted: "Este servidor no está disponible actualmente en GuildSpan.",
      },
    },
    success: {
      eyebrow: "Conexión completada",
      title: "GuildSpan está listo",
      lede:
        "Puedes cerrar esta ventana y volver a tu asistente de IA. Tus credenciales de Discord permanecen protegidas.",
      connected: "GuildSpan conectado",
      detail: "MCP remoto · OAuth 2.1",
      onboardingLede: "{guild} ya está conectado y listo para usar con GuildSpan.",
      onboardingDetail: "Servidor de Discord conectado",
      done: "Listo",
    },
    error: {
      eyebrow: "Conexión interrumpida",
      title: "No pudimos terminar",
      denied: "La autorización fue rechazada. No se conectó ni modificó nada.",
      expired:
        "Esta solicitud de conexión expiró. Inicia la autenticación nuevamente desde tu asistente de IA.",
      guild: "GuildSpan no encontró un servidor de Discord elegible para esta cuenta.",
      admin: "Un administrador del servidor debe conectar GuildSpan primero.",
      install: "Discord no completó la instalación del bot. Inténtalo nuevamente.",
      restricted: "Este servidor no está habilitado actualmente para GuildSpan.",
      setup: "La configuración de servidores no está disponible en este entorno.",
      generic:
        "GuildSpan no pudo completar la conexión. Inténtalo nuevamente desde tu asistente de IA.",
      safe: "Tu cuenta de Discord está segura.",
      unchanged: "No se envió ningún mensaje ni se modificaron permisos del servidor.",
      back: "Volver a GuildSpan",
    },
    consent: {
      pageTitle: "Conectar con GuildSpan",
      brandAlt: "GuildSpan",
      eyebrow: "Autorización segura",
      connect: "Conecta",
      toGuildSpan: "con GuildSpan",
      lede:
        "Revisa esta conexión antes de continuar a Discord. Tú mantienes el control de cada servidor y acción.",
      identityTitle: "Ver tu identidad de Discord",
      identityDetail: "Se utiliza para crear y proteger tu conexión con GuildSpan.",
      guildsTitle: "Ver tus servidores de Discord",
      guildsDetail: "Solo se muestran servidores elegibles. GuildSpan nunca se une sin avisarte.",
      verifiedDomain: "Dominio verificado del cliente: {domain}",
      safeHint: "Continúa solo si iniciaste esta conexión desde tu asistente de IA.",
      continue: "Continuar a Discord",
      cancel: "Cancelar",
      technical: "Detalles técnicos",
      application: "Aplicación",
      callback: "Retorno",
      scopes: "Permisos",
      clientId: "ID del cliente",
      none: "Ninguno",
      footer: "GuildSpan nunca te pedirá tu contraseña de Discord.",
    },
  },
} as const;

export function getInitialLocale(): SupportedLocale {
  const storedLocale = window.localStorage.getItem("guildspan-locale");
  if (storedLocale === "en" || storedLocale === "es") {
    return storedLocale;
  }
  return window.navigator.language.toLowerCase().startsWith("es") ? "es" : "en";
}

export function createGuildSpanI18n() {
  const locale = getInitialLocale();
  document.documentElement.lang = locale;
  return createI18n({
    legacy: false,
    locale,
    fallbackLocale: "en",
    messages,
  });
}
