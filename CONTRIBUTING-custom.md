# This fork's own conventions

This file only applies to `conn730/panel` (and its siblings `conn730/node`
and `conn730/node_bridge_py`) — it is not part of upstream PasarGuard and
should never be merged upstream.

## Why this file exists

We add protocols upstream PasarGuard doesn't have (OpenVPN first, then
L2TP/PPTP/etc.) while still pulling in upstream's own updates regularly.
Every rule below exists to keep that merge cheap.

## Rules for anything we add here

1. **New code goes in new files/modules.** A new protocol's core-config
   class gets its own `app/core/<protocol>.py`. Never grow an existing
   upstream file to add our functionality — a new file can never conflict
   with an upstream change to a file it doesn't touch; an edited shared file
   can.

2. **Touching an existing upstream file is sometimes unavoidable**
   (registering a new `CoreType` in `CoreManager.CORE_CLASSES`, or adding a
   protocol's branch in `_serialize_user_for_node`). Keep that touch to the
   smallest possible diff, and mark it:
   ```python
   # CUSTOM: not upstream. See CONTRIBUTING-custom.md.
   ```
   so `grep -rn "CUSTOM: not upstream" .` always finds every place upstream
   and our fork share a file.

3. **Reserve a high number range for our own enum values.** `ProxyProtocol`
   values we add start at `7` (`openvpn = 7`), matching field `7` on the
   node/bridge `Proxy` protobuf message — not whatever the next sequential
   number happens to be, so a future upstream addition never collides with
   ours on merge. Same rule applies on the node and node_bridge_py forks'
   `BackendType` (`OPENVPN = 1000`).

4. **Merge upstream often, not eventually.** Small, regular merges
   (`git fetch upstream && git merge upstream/main`, weekly-ish) stay
   resolvable. A merge left for months turns into the `vpn-ui` vs. `3x-ui`
   situation this fork exists to avoid — two codebases that no longer share
   enough history to merge at all. Tag every successful merge
   (`git tag sync-YYYY-MM-DD`) so there's always a known-good point to fall
   back to.

5. **Prefer upstreaming the hook, not the feature.** If a limitation in
   upstream is what's forcing a bigger touch than rule 2 allows for, consider
   proposing that flexibility as a PR to `PasarGuard/panel` (or
   `PasarGuard/node_bridge_py`) itself instead of working around it here. A
   hook upstream maintains needs no re-applying after every sync; a
   workaround we maintain does.

## The three-repo shape

A protocol only actually works end to end across all three forks:

| Repo | What it needs |
|---|---|
| `conn730/node` | A `backend.Backend` implementation (`backend/<protocol>/`) and a `BackendType` value in `common/service.proto`. |
| `conn730/node_bridge_py` | The **same** message/field added to its own independent copy of `common/service.proto` (this package does not import node's proto — it's a separately generated client library), plus a `create_proxy()` kwarg in `PasarGuardNodeBridge/utils.py`. Easy to forget; nothing fails loudly if you do — the panel just silently never sends that protocol's credentials to the node. |
| `conn730/panel` (this repo) | A `CoreType` + `app/core/<protocol>.py` class (the *server config* side), **and separately** a `ProxyTable` settings class in `app/models/proxy.py` plus a branch in `app/node/user.py`'s `_serialize_user_for_node` (the *per-user credential* side). These two sides are independent — it's possible to fully wire one and forget the other, which is exactly what happened on the first OpenVPN pass here. |

`pyproject.toml`'s `[tool.uv.sources]` points `pasarguard-node-bridge` at our
`node_bridge_py` fork instead of the PyPI release, since upstream has no
protocol fields beyond what shipped in 0.9.x. Run `uv lock` after changing
either the pin or the fork it points to.

## Current custom additions

| Area | What | Where |
|---|---|---|
| Core config | OpenVPN core class (mirrors `WireGuardConfig`'s shape) | `app/core/openvpn.py`, `CoreType.openvpn` in `app/db/models.py`, `CoreManager.CORE_CLASSES` in `app/core/manager.py`, migration `a1b2c3d4e5f6_add_openvpn_core_type.py` |
| Protocol catalog | Lists all planned protocols (implemented + not yet) for the future "add core" UI | `app/core/protocol_catalog.py`, `GET /api/core/catalog` in `app/routers/core.py` |
| User credentials | Per-user OpenVPN username/password, generated like Trojan/Hysteria's password | `OpenVPNSettings` + `ProxyTable.openvpn` in `app/models/proxy.py`, `ProxyProtocol.openvpn = 7` in `app/models/protocol.py` |
| Node sync | Sends the above to the node over the (forked) bridge | `_serialize_user_for_node`'s openvpn branch in `app/node/user.py` |

Known follow-ups, roughly in the order we'll tackle them: the React
dashboard UI for creating/managing an OpenVPN core and viewing the catalog
(everything above is API-only today), then the next protocol (L2TP).
