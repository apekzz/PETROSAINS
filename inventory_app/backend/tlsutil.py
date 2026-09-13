"""Local CA + HTTPS cert + iPhone configuration profile."""

from __future__ import annotations

import base64
import os
import subprocess
import sys
import uuid

from config import BASE_DIR, get_lan_ip

CERT_DIR = os.path.join(BASE_DIR, "certs")
CA_KEY = os.path.join(CERT_DIR, "ca.key")
CA_CRT = os.path.join(CERT_DIR, "ca.crt")
CERT_FILE = os.path.join(CERT_DIR, "oneshot.crt")
KEY_FILE = os.path.join(CERT_DIR, "oneshot.key")
CHAIN_FILE = os.path.join(CERT_DIR, "oneshot-chain.pem")
PROFILE_FILE = os.path.join(CERT_DIR, "oneshot.mobileconfig")
IP_STAMP = os.path.join(CERT_DIR, "lan_ip.txt")
STAMP_TAG = "ca-v3"


def _run(args):
    subprocess.run(args, check=True, capture_output=True, text=True)


def _write_ca_config(path):
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(
            "[req]\n"
            "distinguished_name = req_distinguished_name\n"
            "x509_extensions = v3_ca\n"
            "prompt = no\n"
            "[req_distinguished_name]\n"
            "CN = OneShot Local CA\n"
            "[v3_ca]\n"
            "subjectKeyIdentifier = hash\n"
            "authorityKeyIdentifier = keyid:always,issuer\n"
            "basicConstraints = critical,CA:true\n"
            "keyUsage = critical,digitalSignature,cRLSign,keyCertSign\n"
        )


def _write_server_config(path, lan_ip):
    alt = ["DNS.1 = localhost", "DNS.2 = oneshot.local", "IP.1 = 127.0.0.1"]
    if lan_ip:
        alt.append(f"IP.2 = {lan_ip}")
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(
            "[req]\n"
            "distinguished_name = req_distinguished_name\n"
            "req_extensions = v3_req\n"
            "prompt = no\n"
            "[req_distinguished_name]\n"
            "CN = oneshot.local\n"
            "[v3_req]\n"
            "basicConstraints = CA:FALSE\n"
            "keyUsage = digitalSignature,keyEncipherment\n"
            "extendedKeyUsage = serverAuth\n"
            "subjectAltName = @alt_names\n"
            "[alt_names]\n"
            + "\n".join(alt)
            + "\n"
        )


def _write_mobileconfig():
    der = subprocess.check_output(
        ["openssl", "x509", "-in", CA_CRT, "-outform", "DER"]
    )
    payload = base64.b64encode(der).decode("ascii")
    ca_uuid = str(uuid.uuid4()).upper()
    profile_uuid = str(uuid.uuid4()).upper()
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>PayloadContent</key>
  <array>
    <dict>
      <key>PayloadCertificateFileName</key>
      <string>OneShotLocalCA.cer</string>
      <key>PayloadContent</key>
      <data>{payload}</data>
      <key>PayloadDescription</key>
      <string>Trust OneShot on this Wi-Fi so Safari can use the camera.</string>
      <key>PayloadDisplayName</key>
      <string>OneShot Local CA</string>
      <key>PayloadIdentifier</key>
      <string>com.oneshot.inventory.ca</string>
      <key>PayloadType</key>
      <string>com.apple.security.root</string>
      <key>PayloadUUID</key>
      <string>{ca_uuid}</string>
      <key>PayloadVersion</key>
      <integer>1</integer>
    </dict>
  </array>
  <key>PayloadDescription</key>
  <string>Install once, then enable trust in Certificate Trust Settings.</string>
  <key>PayloadDisplayName</key>
  <string>OneShot Inventory</string>
  <key>PayloadIdentifier</key>
  <string>com.oneshot.inventory.profile</string>
  <key>PayloadRemovalDisallowed</key>
  <false/>
  <key>PayloadType</key>
  <string>Configuration</string>
  <key>PayloadUUID</key>
  <string>{profile_uuid}</string>
  <key>PayloadVersion</key>
  <integer>1</integer>
</dict>
</plist>
"""
    with open(PROFILE_FILE, "w", encoding="utf-8") as handle:
        handle.write(xml)


def ensure_tls_files():
    """Return (server_cert, server_key) or (None, None)."""
    os.makedirs(CERT_DIR, exist_ok=True)
    lan_ip = get_lan_ip() or ""
    stamp = f"{lan_ip}|{STAMP_TAG}"
    previous = ""
    if os.path.isfile(IP_STAMP):
        previous = open(IP_STAMP, encoding="utf-8").read().strip()
    need_new = (
        previous != stamp
        or not os.path.isfile(CA_CRT)
        or not os.path.isfile(CERT_FILE)
        or not os.path.isfile(KEY_FILE)
        or not os.path.isfile(PROFILE_FILE)
        or not os.path.isfile(CHAIN_FILE)
    )
    if not need_new:
        return CHAIN_FILE if os.path.isfile(CHAIN_FILE) else CERT_FILE, KEY_FILE

    ca_cfg = os.path.join(CERT_DIR, "ca.cnf")
    server_cfg = os.path.join(CERT_DIR, "server.cnf")
    csr = os.path.join(CERT_DIR, "oneshot.csr")
    _write_ca_config(ca_cfg)
    _write_server_config(server_cfg, lan_ip)
    try:
        _run(["openssl", "genrsa", "-out", CA_KEY, "2048"])
        _run([
            "openssl", "req", "-x509", "-new", "-nodes",
            "-key", CA_KEY, "-sha256", "-days", "3650",
            "-out", CA_CRT, "-config", ca_cfg, "-extensions", "v3_ca",
        ])
        _run(["openssl", "genrsa", "-out", KEY_FILE, "2048"])
        _run([
            "openssl", "req", "-new", "-key", KEY_FILE,
            "-out", csr, "-config", server_cfg,
        ])
        _run([
            "openssl", "x509", "-req", "-in", csr,
            "-CA", CA_CRT, "-CAkey", CA_KEY, "-CAcreateserial",
            "-out", CERT_FILE, "-days", "825", "-sha256",
            "-extfile", server_cfg, "-extensions", "v3_req",
        ])
        _write_mobileconfig()
        with open(CHAIN_FILE, "w", encoding="utf-8") as handle:
            handle.write(open(CERT_FILE, encoding="utf-8").read().rstrip() + "\n")
            handle.write(open(CA_CRT, encoding="utf-8").read().rstrip() + "\n")
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        print("[TLS] Could not create HTTPS certificate:", exc)
        return None, None
    with open(IP_STAMP, "w", encoding="utf-8") as handle:
        handle.write(stamp)
    print(f"[TLS] Wrote CA + server cert for oneshot.local / {lan_ip or 'localhost'}")
    return CHAIN_FILE, KEY_FILE


def start_mdns(https_port: int, http_port: int):
    """Advertise oneshot.local on the LAN so iPhone does not use the raw IP."""
    if sys.platform != "darwin":
        return []
    lan_ip = get_lan_ip()
    if not lan_ip:
        return []
    procs = []
    for args in (
        ["dns-sd", "-P", "OneShot", "_https._tcp", "local", str(https_port), "oneshot.local", lan_ip],
        ["dns-sd", "-P", "OneShotHTTP", "_http._tcp", "local", str(http_port), "oneshot.local", lan_ip],
    ):
        try:
            procs.append(subprocess.Popen(
                args,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            ))
        except FileNotFoundError:
            return []
    print(f"[TLS] Advertised oneshot.local → {lan_ip}")
    return procs
