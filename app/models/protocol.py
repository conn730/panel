from enum import IntEnum


class ProxyProtocol(IntEnum):
    vmess = 1
    vless = 2
    trojan = 3
    shadowsocks = 4
    wireguard = 5
    hysteria = 6
    # CUSTOM: not upstream. Field 7 is reserved for this fork's own additions
    # going forward (openvpn today) — see CONTRIBUTING-custom.md and the
    # matching `openvpn = 7` field on node's Proxy message.
    openvpn = 7

    @classmethod
    def from_value(cls, value: str) -> ProxyProtocol | None:
        try:
            return _PROXY_PROTOCOL_BY_NAME[value]
        except KeyError:
            return None


_PROXY_PROTOCOL_BY_NAME = {protocol.name: protocol for protocol in ProxyProtocol}
