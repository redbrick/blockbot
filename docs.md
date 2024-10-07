# API Docs

* [hikari](https://docs.hikari-py.dev/en/stable/reference/hikari/)
* [hikari-arc](https://arc.hypergonial.com/api_reference/)
* [hikari-miru](https://miru.hypergonial.com/api_reference/)

# Usage Guides

## hikari

* [Getting Started](https://hg.cursed.solutions/#getting-started) - first steps of using `hikari`
* [Events](https://hg.cursed.solutions/01.events/) - understanding receiving events from Discord with `hikari`

## hikari-arc

* [Getting Started](https://arc.hypergonial.com/getting_started/) - first steps of using `hikari-arc`
* [Guides](https://arc.hypergonial.com/guides/) - various guides on aspects of `hikari-arc`

## hikari-miru

* [Getting Started](https://miru.hypergonial.com/getting_started/) - first steps of using `hikari-miru`
* [Guides](https://miru.hypergonial.com/guides/) - various guides on aspects of `hikari-miru`

# What's the difference between `hikari`, `hikari-arc` and `hikari-miru`?

* `hikari` -  the Discord API Wrapper. Can be used to:
    * [add roles to server members](https://docs.hikari-py.dev/en/stable/reference/hikari/api/rest/#hikari.api.rest.RESTClient.add_role_to_member)
    * [create threads](https://docs.hikari-py.dev/en/stable/reference/hikari/api/rest/#hikari.api.rest.RESTClient.create_thread)
    * [send individual messages](https://docs.hikari-py.dev/en/stable/reference/hikari/api/rest/#hikari.api.rest.RESTClient.create_message)
    * [fetch guild (server) information](https://docs.hikari-py.dev/en/stable/reference/hikari/api/rest/#hikari.api.rest.RESTClient.fetch_guild)
    * update member roles ([add role](https://docs.hikari-py.dev/en/stable/reference/hikari/api/rest/#hikari.api.rest.RESTClient.add_role_to_member), [remove role](https://docs.hikari-py.dev/en/stable/reference/hikari/api/rest/#hikari.api.rest.RESTClient.remove_role_from_member), [edit roles](https://docs.hikari-py.dev/en/stable/reference/hikari/api/rest/#hikari.api.rest.RESTClient.edit_member))
    * listen for events from Discord, like [message edits](https://docs.hikari-py.dev/en/stable/reference/hikari/events/message_events/#hikari.events.message_events.MessageUpdateEvent)
* `hikari-arc` - the command handler. Can be used to:
    * create application commands ([slash](https://arc.hypergonial.com/guides/options/#declaring-options), [message & user commands](https://arc.hypergonial.com/guides/context_menu/))
    * respond to command interactions 
* `hikari-miru` - the component handler. Can be used to:
    * create message components (buttons, select menus & modals)
    * respond to component interactions (button clicks, select menu selections & modal submissions)

# Why use a `hikari.GatewayBot` instead of a `hikari.RESTBot`?

**TL;DR:** `RESTBot`s do not receive events required for some blockbot features (e.g. starboard), so `GatewayBot` must be used instead.

`GatewayBot`s connect to Discord via a websocket, and Discord sends events (including interactions) through this websocket. `RESTBot`s run a web server which Discord sends only interactions to (not events) via HTTP requests. These events are required for specific blockbot features, like starboard (which uses reaction create/remove events).

**Further reading:** <https://arc.hypergonial.com/getting_started/#difference-between-gatewaybot-restbot>

# What's the difference between `hikari.GatewayBot`, `arc.GatewayClient` and `miru.Client`?

* `hikari.GatewayBot` is the actual Discord bot. It:
    * manages the websocket connection to Discord
    * sends HTTP requests to the Discord REST API
    * caches information received in events sent by Discord.
* `arc.GatewayClient` adds additional functionality to `hikari.GatewayBot` for:
    * splitting the bot across multiple files using [extensions](https://arc.hypergonial.com/guides/plugins_extensions/#extensions)
    * grouping commands using [plugins](https://arc.hypergonial.com/guides/plugins_extensions/#plugins)
    * easily creating and managing commands and [command groups](https://arc.hypergonial.com/guides/command_groups/)
    * accessing objects globally (in any extension, plugin or command) using [dependency injection](https://arc.hypergonial.com/guides/dependency_injection/) (e.g. a database connection)
* `miru.Client` adds additional functionality to `hikari.GatewayBot` for:
    * creating message components using [views](https://miru.hypergonial.com/getting_started/#first-steps)
    * creating [modals](https://miru.hypergonial.com/guides/modals/)
    * creating [navigators](https://miru.hypergonial.com/guides/navigators/) and [menus](https://miru.hypergonial.com/guides/menus/) using views

# Do's and Don'ts

* Always try to get data from the cache before fetching it from the API.

