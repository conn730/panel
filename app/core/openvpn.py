# CUSTOM: not upstream. See CONTRIBUTING-custom.md.
#
# Mirrors app/core/wireguard.py's shape (a dict subclass, not a formal
# AbstractCore subclass — matching the existing non-inheriting convention
# CoreManager.CORE_CLASSES relies on) so it plugs into the same registry.
# The dict this wraps IS the JSON the node's backend/openvpn.NewConfig
# parses — keep the two in sync if either changes.
from __future__ import annotations

import json
import re
from copy import deepcopy
from ipaddress import ip_network
from pathlib import PosixPath

import commentjson

from app.models.core import CoreType
from app.models.protocol import ProxyProtocol

_OPENVPN_PROTOCOLS = frozenset((ProxyProtocol.openvpn,))
_DEVICE_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,14}$")  # IFNAMSIZ-safe


class OpenVpnConfig(dict):
    def __init__(
        self,
        config: dict | str | PosixPath | None = None,
        exclude_inbound_tags: set[str] | None = None,
        fallbacks_inbound_tags: set[str] | None = None,
        skip_validation: bool = False,
    ):
        if config is None:
            config = {}
        if isinstance(config, str):
            config = commentjson.loads(config)
        if isinstance(config, dict):
            config = deepcopy(config)

        super().__init__(config)

        self._type = CoreType.openvpn
        self.exclude_inbound_tags = set(exclude_inbound_tags or set())
        self.fallbacks_inbound_tags = set(fallbacks_inbound_tags or set())
        self._inbounds: list[str] = []
        self._inbounds_by_tag: dict[str, dict] = {}

        if skip_validation:
            return

        self._validate()
        self._resolve_inbounds()

    @property
    def type(self) -> str:
        return self._type

    def _validate(self):
        if self.exclude_inbound_tags:
            raise ValueError("exclude_inbound_tags is only supported for xray cores")
        if self.fallbacks_inbound_tags:
            raise ValueError("fallbacks_inbound_tags is only supported for xray cores")

        port = self.get("port", 1194)
        if not isinstance(port, int) or port <= 0 or port > 65535:
            raise ValueError("port must be an integer between 1 and 65535")
        self["port"] = port

        proto = str(self.get("proto") or "udp").strip().lower()
        if proto not in ("udp", "tcp"):
            raise ValueError("proto must be 'udp' or 'tcp'")
        self["proto"] = proto

        subnet = str(self.get("subnet") or "10.9.0.0/24").strip()
        try:
            self["subnet"] = str(ip_network(subnet, strict=False))
        except ValueError as e:
            raise ValueError(f"subnet must be a valid IPv4 CIDR: {e}") from e

        self["dns1"] = str(self.get("dns1") or "1.1.1.1").strip()
        self["dns2"] = str(self.get("dns2") or "1.0.0.1").strip()

        device = str(self.get("device") or "tun-pg-ovpn").strip()
        if not _DEVICE_NAME_RE.fullmatch(device):
            raise ValueError("device must be a short alphanumeric interface name (max 15 chars)")
        self["device"] = device

        mtu = self.get("mtu", 1500)
        if not isinstance(mtu, int) or mtu <= 0:
            raise ValueError("mtu must be a positive integer")
        self["mtu"] = mtu

    def _resolve_inbounds(self):
        device = self["device"]
        metadata = {
            "tag": device,
            "protocol": "openvpn",
            "network": self["proto"],
            "tls": "none",  # OpenVPN's own TLS layer, not xray's stream-settings concept
            "device": device,
            "port": self["port"],
            "subnet": self["subnet"],
        }
        self._inbounds = [device]
        self._inbounds_by_tag = {device: metadata}

    def to_str(self, **json_kwargs) -> str:
        return json.dumps(self, **json_kwargs)

    @property
    def inbounds_by_tag(self) -> dict:
        return self._inbounds_by_tag

    @property
    def inbounds(self) -> list[str]:
        return self._inbounds

    @property
    def protocols(self) -> frozenset[ProxyProtocol]:
        return _OPENVPN_PROTOCOLS

    def to_json(self) -> dict:
        return {
            "type": self.type,
            "config": dict(self),
            "exclude_inbound_tags": [],
            "fallbacks_inbound_tags": [],
            "inbounds": self.inbounds,
            "inbounds_by_tag": self.inbounds_by_tag,
        }

    @classmethod
    def from_json(cls, data: dict) -> OpenVpnConfig:
        instance = cls(config=data.get("config", {}), skip_validation=True)
        if "inbounds" in data:
            instance._inbounds = data["inbounds"]
        if "inbounds_by_tag" in data:
            instance._inbounds_by_tag = data["inbounds_by_tag"]
        return instance

    def copy(self):
        return deepcopy(self)
