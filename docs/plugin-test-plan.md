# GuildSpan plugin test plan

Use a dedicated Discord server and non-sensitive fixtures. Confirm the exact
target before every write test and do not reuse production conversations.

## Positive cases

1. Install GuildSpan and complete OAuth, then run `discord_health_check`.
2. Open `/servers`, sign in with Discord, and confirm it distinguishes an active
   grant, an installed server ready to activate, a server requiring bot
   installation, and a server requiring an administrator.
3. Install the bot through Discord's official screen, return to GuildSpan, and
   confirm the selected server is persisted only after live verification.
4. List channels in an authorized guild and inspect one selected channel.
5. Read a bounded message window and retrieve one attachment through its IDs.
6. Search recent messages for a known test phrase in authorized channels.
7. Create a test thread or send one clearly labeled test message to an approved
   test channel and verify the returned Discord identifiers.

## Negative cases

1. Request a guild outside the operator allowlist and verify authorization is
   denied without a Discord side effect.
2. Verify `discord_list_guilds` labels a guild outside an enabled allowlist as
   `restricted`, a normal member as `administrator_required`, and a missing bot
   as `requires_installation`.
3. Attempt a write with an invented or inaccessible channel/message ID and
   verify the tool fails safely.
4. Ask for a write indirectly while explicitly forbidding changes and verify no
   write tool is called.

## Acceptance criteria

- Installation exposes the GuildSpan skill and MCP tools in a new task.
- OAuth completes without revealing upstream Discord or bot credentials.
- Tool names, schemas, descriptions, and safety annotations match runtime
  behavior.
- Successful writes occur once in the exact approved destination.
- Authorization and Discord permission failures remain explicit and produce no
  unexpected side effects.
