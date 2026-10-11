"""Ganti merek source moonlight-qt menjadi aplikasi stream CloudPC, dengan perubahan sesedikit mungkin.

    python apply_branding.py <folder source moonlight-qt> [--branding branding.json]

Yang diubah HANYA tampilan merek: nama aplikasi/organisasi, judul jendela stream, nama di mixer volume,
properti file .exe, ikon, teks "Moonlight" di UI (QML), dan cek update otomatis dimatikan (tombol update
mengarah ke unduhan Moonlight resmi). Logika streaming dan teks log TIDAK disentuh: aplikasi CloudPC membaca
log stream (`cloudpc_client.moonlight.parse_stream_log`) dan mencari jendela kelas `SDL_app`.

Setiap penggantian wajib ketemu. Kalau upstream mengubah baris yang dicari, skrip berhenti dengan error
supaya tidak ada build yang diam-diam masih bermerek Moonlight. Perbaiki pola di REPLACEMENTS lalu ulangi.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent

# (file relatif ke root source, teks lama, teks baru). {product} dll. diisi dari branding.json.
REPLACEMENTS = [
    ("app/main.cpp", 'QCoreApplication::setOrganizationName("Moonlight Game Streaming Project");',
     'QCoreApplication::setOrganizationName("{company}");'),
    ("app/main.cpp", 'QCoreApplication::setOrganizationDomain("moonlight-stream.com");',
     'QCoreApplication::setOrganizationDomain("{domain}");'),
    ("app/main.cpp", 'QCoreApplication::setApplicationName("Moonlight");',
     'QCoreApplication::setApplicationName("{product}");'),
    ("app/main.cpp", 'SDL_SetHint(SDL_HINT_AUDIO_DEVICE_APP_NAME, "Moonlight");',
     'SDL_SetHint(SDL_HINT_AUDIO_DEVICE_APP_NAME, "{product}");'),
    ("app/main.cpp", 'SDL_SetHint(SDL_HINT_APP_NAME, "Moonlight");',
     'SDL_SetHint(SDL_HINT_APP_NAME, "{product}");'),
    # Judul jendela stream: "vm1 - Moonlight" -> nama produk saja (nama host internal tidak perlu dilihat user).
    ("app/streaming/session.cpp", 'QString(m_Computer->name + " - Moonlight").toStdString();',
     'QString("{product}").toStdString();'),
    # Properti file .exe (Task Manager, Properties > Details).
    ("app/app.pro", "QMAKE_TARGET_COMPANY = Moonlight Game Streaming Project", "QMAKE_TARGET_COMPANY = {company}"),
    ("app/app.pro", "QMAKE_TARGET_DESCRIPTION = Moonlight Game Streaming Client",
     "QMAKE_TARGET_DESCRIPTION = {description}"),
    ("app/app.pro", "QMAKE_TARGET_PRODUCT = Moonlight", "QMAKE_TARGET_PRODUCT = {product}"),
    ("app/gui/main.qml", "AutoUpdateChecker.start()",
     "// AutoUpdateChecker.start() -- dimatikan di build {product}: pembaruan dikirim lewat aplikasi {product}"),
]

# Ikon: file upstream ditimpa dengan nama yang sama supaya .pro/.qrc tidak perlu diubah.
ICONS = [("assets/icon.ico", "app/moonlight.ico"), ("assets/icon.svg", "app/res/moonlight.svg")]

# Teks terjemahan yang terlihat user: qsTr("...") di QML dan tr("...") di C++.
_TR = {".qml": re.compile(r'(qsTr\(")((?:[^"\\]|\\.)*)"'), ".cpp": re.compile(r'(\btr\(")((?:[^"\\]|\\.)*)"')}


def _read(path: Path) -> str:
    with open(path, encoding="utf-8", newline="") as fh:  # newline="" menjaga CRLF/LF asli
        return fh.read()


def _write(path: Path, text: str) -> None:
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)


def apply(src: Path, brand: dict) -> list[str]:
    log: list[str] = []
    for rel, old, new in REPLACEMENTS:
        path = src / rel
        text = _read(path)
        if old not in text:
            raise SystemExit(f"GAGAL: pola tidak ditemukan di {rel}:\n  {old}\n"
                             "Upstream berubah; sesuaikan REPLACEMENTS di apply_branding.py.")
        _write(path, text.replace(old, new.format(**brand)))
        log.append(f"{rel}: {old.strip()[:60]}")

    # Teks "Moonlight" yang terlihat user (hanya isi qsTr/tr, bukan log, nama tipe, import, atau komentar).
    total = 0
    for path in sorted(p for p in (src / "app").rglob("*") if p.suffix in _TR):
        text = _read(path)
        count = 0

        def _sub(m: re.Match) -> str:
            nonlocal count
            inner, n = re.subn(r"\bMoonlight\b", brand["product"], m[2])
            count += n
            return f'{m[1]}{inner}"'

        new_text = _TR[path.suffix].sub(_sub, text)
        if count:
            _write(path, new_text)
            total += count
            log.append(f"{path.relative_to(src).as_posix()}: {count} teks UI")
    if not total:
        raise SystemExit("GAGAL: tidak ada teks 'Moonlight' di qsTr()/tr(); struktur UI upstream berubah?")

    for asset, rel in ICONS:
        target = src / rel
        if not target.is_file():
            raise SystemExit(f"GAGAL: file ikon upstream tidak ada: {rel}")
        shutil.copyfile(HERE / asset, target)
        log.append(f"{rel}: ikon diganti")
    return log


def write_notice(src: Path, brand: dict, log: list[str]) -> Path:
    """Pemberitahuan modifikasi (wajib GPLv3 pasal 5a), ikut di source dan di paket aplikasi."""
    notice = src / "CLOUDPC_MODIFICATIONS.txt"
    lines = [
        f"{brand['description']} adalah versi modifikasi dari Moonlight (moonlight-qt) {brand['upstream_tag']}",
        f"<{brand['upstream_repo']}>, dilisensikan di bawah GNU GPL versi 3 (lihat LICENSE).",
        "",
        f"Dimodifikasi pada {date.today().isoformat()} oleh {brand['company']}: hanya penggantian merek",
        "(nama, ikon, judul jendela, teks UI) dan cek update otomatis dimatikan. Logika streaming tidak diubah.",
        "Moonlight adalah merek milik pemiliknya; produk ini tidak berafiliasi dengan proyek Moonlight.",
        "",
        "File yang diubah:",
        *[f"  - {x}" for x in log],
    ]
    notice.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return notice


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("src", type=Path, help="folder source moonlight-qt (hasil checkout tag upstream)")
    ap.add_argument("--branding", type=Path, default=HERE / "branding.json")
    args = ap.parse_args(argv)
    brand = json.loads(args.branding.read_text(encoding="utf-8"))
    if (args.src / "CLOUDPC_MODIFICATIONS.txt").exists():
        raise SystemExit("GAGAL: source ini sudah pernah diganti mereknya. Mulai dari checkout upstream yang bersih.")
    log = apply(args.src, brand)
    notice = write_notice(args.src, brand, log)
    print("\n".join(log))
    print(f"Selesai: {len(log)} perubahan, catatan di {notice}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
