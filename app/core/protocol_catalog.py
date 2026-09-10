# CUSTOM: not upstream. See CONTRIBUTING-custom.md.
#
# The full VPN-protocol catalog this fork intends to reach — matching the
# service list vpn-ui already shows per-server today — with a flag for which
# ones actually have a working node backend + panel core class wired up yet.
# The dashboard's "add a core" flow is expected to list every entry here and
# grey out (or otherwise mark unavailable) the ones with implemented=False,
# rather than only offering what CoreManager.CORE_CLASSES currently has.
#
# core_type is the CoreType enum value to use once implemented=True; it's
# None for anything not wired up yet, so the catalog entry exists (for
# display) without pointing at a CoreType member that doesn't have a class
# registered in CoreManager.CORE_CLASSES.
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CatalogEntry:
    key: str  # stable machine key, independent of display name / CoreType
    display_name: str
    implemented: bool
    core_type: str | None  # CoreType.value once implemented, else None
    note: str = ""


PROTOCOL_CATALOG: tuple[CatalogEntry, ...] = (
    CatalogEntry("xray", "Xray", True, "xray"),
    CatalogEntry("anytls", "AnyTLS", True, "xray", "served via the xray core, not a separate CoreType"),
    CatalogEntry("tuic", "TUIC", True, "xray", "served via the xray core, not a separate CoreType"),
    CatalogEntry("naiveproxy", "NaiveProxy", True, "xray", "served via the xray core, not a separate CoreType"),
    CatalogEntry("wireguard", "WireGuard", True, "wg"),
    CatalogEntry(
        "openvpn",
        "OpenVPN",
        True,
        "openvpn",
        "v1: single transport, username/password auth — see backend/openvpn package doc",
    ),
    CatalogEntry("l2tp", "L2TP", False, None),
    CatalogEntry("ipsec", "IPsec", False, None),
    CatalogEntry("pptp", "PPTP", False, None),
    CatalogEntry("openconnect", "OpenConnect (Cisco)", False, None),
    CatalogEntry("sstp", "SSTP", False, None),
    CatalogEntry("ikev2", "IKEv2", False, None),
    CatalogEntry("amneziawg", "AmneziaWG", False, None),
    CatalogEntry("gre", "GRE", False, None),
    CatalogEntry("mtproto_proxy", "MTProto Proxy", False, None, "distinct from the CoreType.mtproto slot upstream reserved"),
    CatalogEntry("ssh", "SSH", False, None),
    CatalogEntry("radius", "RADIUS", False, None),
)


def catalog_as_dicts() -> list[dict]:
    return [
        {
            "key": e.key,
            "display_name": e.display_name,
            "implemented": e.implemented,
            "core_type": e.core_type,
            "note": e.note,
        }
        for e in PROTOCOL_CATALOG
    ]
