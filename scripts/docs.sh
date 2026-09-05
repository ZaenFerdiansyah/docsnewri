#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
DOCS_DIR="$PROJECT_ROOT/docs"
SECURE_CONFIG="$PROJECT_ROOT/config/secure-pages.json"

cd "$PROJECT_ROOT"

die() {
    printf 'Error: %s\n' "$*" >&2
    exit 1
}

info() {
    printf '%s\n' "$*"
}

confirm() {
    local prompt="$1"
    local answer
    read -r -p "$prompt [y/N] " answer
    [[ "$answer" == "y" || "$answer" == "Y" ]]
}

python_bin() {
    if [[ -x "$PROJECT_ROOT/.venv/bin/python" ]]; then
        printf '%s\n' "$PROJECT_ROOT/.venv/bin/python"
    else
        command -v python3 || die "Python 3 tidak ditemukan."
    fi
}

normalize_doc_path() {
    local value="${1#./}"
    value="${value#docs/}"
    value="${value%.md}"

    [[ "$value" =~ ^[a-z0-9]+(-[a-z0-9]+)*(/[a-z0-9]+(-[a-z0-9]+)*)+$ ]] ||
        die "Gunakan path seperti network/ospf atau docs/network/ospf.md."

    case "$value" in
        assets/* | overrides/*)
            die "Path assets/ dan overrides/ bukan halaman dokumentasi."
            ;;
    esac

    printf '%s.md\n' "$value"
}

page_url_from_doc() {
    local relative="${1%.md}"
    if [[ "${relative##*/}" == "index" ]]; then
        relative="${relative%/index}"
    fi
    printf '/%s/\n' "$relative"
}

choose_editor() {
    if [[ -n "${EDITOR:-}" ]]; then
        printf '%s\n' "$EDITOR"
    elif command -v nano >/dev/null 2>&1; then
        printf 'nano\n'
    elif command -v vi >/dev/null 2>&1; then
        printf 'vi\n'
    else
        die "Editor tidak ditemukan. Atur variabel EDITOR, misalnya: export EDITOR=nano"
    fi
}

open_editor() {
    local editor
    editor="$(choose_editor)"
    "$editor" "$@"
}

require_git() {
    command -v git >/dev/null 2>&1 || die "Git tidak ditemukan."
    git rev-parse --is-inside-work-tree >/dev/null 2>&1 ||
        die "Direktori ini bukan Git repository."
}

show_help() {
    cat <<'EOF'
Pengelola dokumentasi MkDocs

Pemakaian:
  ./scripts/docs.sh <perintah> [argumen]

Perintah:
  help                         Tampilkan bantuan
  list [kata]                  Daftar halaman; opsional filter pencarian
  add <path> [judul]           Buat halaman dari template lalu buka editor
  edit <path>                  Edit halaman
  delete <path>                Hapus halaman beserta semua referensinya
  nav                          Edit navigasi di mkdocs.yml
  protect <path> <group>       Lindungi halaman dengan password/group
  unprotect <path>             Jadikan halaman publik
  hash                         Buat hash password tanpa menyimpan plaintext
  status                       Tampilkan status dan ringkasan perubahan Git
  check                        Validator, unit test, dan strict build
  serve                        Jalankan preview lokal
  publish [pesan commit]       Check, commit seluruh perubahan terkonfirmasi,
                               lalu push branch aktif ke origin

Contoh:
  ./scripts/docs.sh add network/ospf "Konfigurasi OSPF"
  ./scripts/docs.sh edit network/ospf
  ./scripts/docs.sh protect network/ospf network-internal
  ./scripts/docs.sh unprotect network/ospf
  ./scripts/docs.sh delete network/ospf
  ./scripts/docs.sh check
  ./scripts/docs.sh publish "docs: add OSPF guide"

Catatan:
  Setelah add, jalankan './scripts/docs.sh nav' untuk menambahkan halaman ke
  sidebar. Perintah publish hanya deploy produksi jika branch aktif adalah main.
EOF
}

list_docs() {
    local filter="${1:-}"
    local found=0
    while IFS= read -r file; do
        if [[ -z "$filter" || "$file" == *"$filter"* ]]; then
            printf '%s\n' "${file#docs/}"
            found=1
        fi
    done < <(find docs -type f -name '*.md' -not -path 'docs/overrides/*' | sort)
    [[ "$found" -eq 1 ]] || die "Dokumen tidak ditemukan."
}

add_doc() {
    [[ -n "${1:-}" ]] || die "Path wajib diisi."
    local relative title target
    relative="$(normalize_doc_path "$1")"
    title="${2:-}"
    target="$DOCS_DIR/$relative"
    [[ ! -e "$target" ]] || die "Dokumen sudah ada: docs/$relative"

    if [[ -z "$title" ]]; then
        read -r -p "Judul halaman: " title
    fi
    [[ -n "$title" ]] || die "Judul tidak boleh kosong."

    mkdir -p -- "$(dirname -- "$target")"
    {
        printf '# %s\n\n' "$title"
        printf 'Ringkasan singkat mengenai tujuan dokumen.\n\n'
        printf '## Prasyarat\n\n'
        printf -- '- Tambahkan prasyarat di sini.\n\n'
        printf '## Konfigurasi\n\n'
        printf 'Jelaskan langkah konfigurasi secara berurutan.\n\n'
        printf '## Verifikasi\n\n'
        printf 'Jelaskan cara memverifikasi hasil konfigurasi.\n\n'
        printf '## Troubleshooting\n\n'
        printf 'Tuliskan masalah umum dan solusinya.\n'
    } >"$target"

    info "Dibuat: docs/$relative"
    info "Setelah selesai, tambahkan ke navigasi dengan: ./scripts/docs.sh nav"
    open_editor "$target"
}

edit_doc() {
    [[ -n "${1:-}" ]] || die "Path wajib diisi."
    local relative target
    relative="$(normalize_doc_path "$1")"
    target="$DOCS_DIR/$relative"
    [[ -f "$target" ]] || die "Dokumen tidak ditemukan: docs/$relative"
    open_editor "$target"
}

remove_secure_entry() {
    local page_url="$1"
    "$(python_bin)" - "$SECURE_CONFIG" "$page_url" <<'PY'
import json
import sys
from pathlib import Path

config_path = Path(sys.argv[1])
page_url = sys.argv[2]
data = json.loads(config_path.read_text(encoding="utf-8"))
original = data.get("secure_pages", [])
filtered = [page for page in original if page.get("path") != page_url]
if len(filtered) != len(original):
    data["secure_pages"] = filtered
    config_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Konfigurasi secure dihapus: {page_url}")
PY
}

remove_nav_entry() {
    local relative="$1"
    "$(python_bin)" - "$PROJECT_ROOT/mkdocs.yml" "$relative" <<'PY'
import re
import sys
from pathlib import Path

config_path = Path(sys.argv[1])
relative = sys.argv[2]
lines = config_path.read_text(encoding="utf-8").splitlines(keepends=True)
pattern = re.compile(r":\s*" + re.escape(relative) + r"\s*$")
filtered = [line for line in lines if not pattern.search(line.rstrip("\n"))]
if len(filtered) != len(lines):
    config_path.write_text("".join(filtered), encoding="utf-8")
    print(f"Navigasi dihapus: {relative}")
PY
}

remove_markdown_links() {
    local relative="$1"
    "$(python_bin)" - "$DOCS_DIR" "$relative" <<'PY'
import re
import sys
from pathlib import Path
from urllib.parse import unquote

docs_dir = Path(sys.argv[1]).resolve()
relative = Path(sys.argv[2])
target = (docs_dir / relative).resolve()
link_pattern = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")

for source in sorted(docs_dir.rglob("*.md")):
    if source.resolve() == target or "overrides" in source.parts:
        continue

    original_lines = source.read_text(encoding="utf-8").splitlines(keepends=True)
    filtered_lines = []
    removed = 0

    for line in original_lines:
        targets_page = False
        for match in link_pattern.finditer(line):
            destination = match.group(1).strip()
            if destination.startswith("<") and ">" in destination:
                destination = destination[1 : destination.index(">")]
            else:
                destination = destination.split(maxsplit=1)[0]

            destination = unquote(destination.split("#", 1)[0].split("?", 1)[0])
            if not destination or "://" in destination or destination.startswith(("mailto:", "/")):
                continue

            linked_file = (source.parent / destination).resolve()
            if linked_file == target:
                targets_page = True
                break

        if targets_page:
            removed += 1
        else:
            filtered_lines.append(line)

    if removed:
        source.write_text("".join(filtered_lines), encoding="utf-8")
        display = source.relative_to(docs_dir)
        print(f"Tautan dibersihkan: docs/{display} ({removed} baris)")
PY
}

delete_doc() {
    [[ -n "${1:-}" ]] || die "Path wajib diisi."
    local relative target page_url
    relative="$(normalize_doc_path "$1")"
    target="$DOCS_DIR/$relative"

    if [[ -f "$target" ]]; then
        info "Dokumen yang akan dihapus: docs/$relative"
    else
        info "File sudah tidak ada; referensi akan tetap dibersihkan: docs/$relative"
    fi
    confirm "Hapus halaman dan seluruh referensinya?" || die "Dibatalkan."

    page_url="$(page_url_from_doc "$relative")"
    remove_secure_entry "$page_url"
    remove_nav_entry "$relative"
    remove_markdown_links "$relative"

    if [[ -f "$target" ]] &&
        git rev-parse --is-inside-work-tree >/dev/null 2>&1 &&
        git ls-files --error-unmatch "docs/$relative" >/dev/null 2>&1; then
        git rm -- "docs/$relative"
        info "File dihapus melalui Git. Sebelum commit dapat dipulihkan dengan:"
        info "  git restore --staged docs/$relative"
        info "  git restore docs/$relative"
    elif [[ -f "$target" ]]; then
        rm -- "$target"
        info "File lokal yang belum dilacak Git telah dihapus."
    else
        info "Tidak ada file yang perlu dihapus; pembersihan referensi selesai."
    fi

    info "Berikutnya jalankan: ./scripts/docs.sh publish \"docs: remove $relative\""
}

protect_doc() {
    [[ -n "${1:-}" && -n "${2:-}" ]] ||
        die "Gunakan: ./scripts/docs.sh protect <path> <group>"
    local relative target page_url group
    relative="$(normalize_doc_path "$1")"
    target="$DOCS_DIR/$relative"
    group="$2"
    [[ -f "$target" ]] || die "Dokumen tidak ditemukan: docs/$relative"
    [[ "$group" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]] ||
        die "Group hanya boleh berisi huruf kecil, angka, dan tanda hubung."
    page_url="$(page_url_from_doc "$relative")"

    "$(python_bin)" - "$SECURE_CONFIG" "$page_url" "$group" <<'PY'
import getpass
import hashlib
import json
import sys
from pathlib import Path

config_path = Path(sys.argv[1])
page_url = sys.argv[2]
group = sys.argv[3]
data = json.loads(config_path.read_text(encoding="utf-8"))
pages = data.setdefault("secure_pages", [])

if any(page.get("path") == page_url for page in pages):
    raise SystemExit(f"Error: halaman sudah dilindungi: {page_url}")

group_hashes = {
    page["password_hash"]
    for page in pages
    if page.get("group") == group and page.get("password_hash")
}
if len(group_hashes) > 1:
    raise SystemExit(f"Error: group {group!r} memiliki hash yang bertentangan.")

if group_hashes:
    password_hash = group_hashes.pop()
    print(f"Menggunakan password group yang sudah ada: {group}")
else:
    password = getpass.getpass("Password baru: ")
    confirmation = getpass.getpass("Konfirmasi password: ")
    if not password:
        raise SystemExit("Error: password tidak boleh kosong.")
    if password != confirmation:
        raise SystemExit("Error: konfirmasi password tidak sama.")
    password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()

pages.append(
    {"path": page_url, "group": group, "password_hash": password_hash}
)
config_path.write_text(
    json.dumps(data, indent=2, ensure_ascii=False) + "\n",
    encoding="utf-8",
)
print(f"Halaman dilindungi: {page_url} (group: {group})")
PY

    info "Tambahkan simbol 🔒 pada label halaman melalui: ./scripts/docs.sh nav"
    "$(python_bin)" scripts/validate-secure-pages.py
}

unprotect_doc() {
    [[ -n "${1:-}" ]] || die "Path wajib diisi."
    local relative target page_url
    relative="$(normalize_doc_path "$1")"
    target="$DOCS_DIR/$relative"
    [[ -f "$target" ]] || die "Dokumen tidak ditemukan: docs/$relative"
    page_url="$(page_url_from_doc "$relative")"

    confirm "Jadikan $page_url sebagai halaman publik?" || die "Dibatalkan."
    remove_secure_entry "$page_url"
    info "Hapus simbol 🔒 dari navigasi melalui: ./scripts/docs.sh nav"
    "$(python_bin)" scripts/validate-secure-pages.py
}

git_status() {
    require_git
    git status --short
    git diff --stat
}

run_check() {
    local python
    python="$(python_bin)"
    "$python" scripts/validate-secure-pages.py
    "$python" -m unittest discover -s tests -v
    "$python" -m mkdocs build --strict
}

serve_docs() {
    "$(python_bin)" -m mkdocs serve
}

publish_changes() {
    require_git
    local message="${1:-}"
    local branch
    branch="$(git branch --show-current)"
    [[ -n "$branch" ]] || die "Tidak dapat publish dari detached HEAD."
    git remote get-url origin >/dev/null 2>&1 || die "Remote origin tidak tersedia."

    run_check
    info
    info "Perubahan yang akan dipublish:"
    git status --short
    [[ -n "$(git status --porcelain)" ]] || die "Tidak ada perubahan untuk dipublish."

    info
    info "Peringatan: semua perubahan di atas akan dimasukkan ke commit."
    local approval
    read -r -p "Ketik PUBLISH untuk melanjutkan: " approval
    [[ "$approval" == "PUBLISH" ]] || die "Publish dibatalkan."

    if [[ -z "$message" ]]; then
        read -r -p "Pesan commit: " message
    fi
    [[ -n "$message" ]] || die "Pesan commit tidak boleh kosong."

    git add -A
    git diff --cached --check
    git commit -m "$message"
    git push origin "$branch"

    info "Push berhasil ke origin/$branch."
    if [[ "$branch" == "main" ]]; then
        info "GitHub Actions akan membangun dan mempublikasikan GitHub Pages."
        info "Pantau: https://github.com/ZaenFerdiansyah/docsnewri/actions"
    else
        info "Branch ini tidak memicu deployment produksi. Buat pull request ke main."
    fi
}

command_name="${1:-help}"
shift || true

case "$command_name" in
    help | -h | --help) show_help ;;
    list) list_docs "${1:-}" ;;
    add) add_doc "${1:-}" "${2:-}" ;;
    edit) edit_doc "${1:-}" ;;
    delete | remove | rm) delete_doc "${1:-}" ;;
    nav) open_editor "$PROJECT_ROOT/mkdocs.yml" ;;
    protect) protect_doc "${1:-}" "${2:-}" ;;
    unprotect) unprotect_doc "${1:-}" ;;
    hash) "$(python_bin)" scripts/generate-password-hash.py ;;
    status) git_status ;;
    check) run_check ;;
    serve) serve_docs ;;
    publish) publish_changes "${1:-}" ;;
    *) die "Perintah tidak dikenal: $command_name. Jalankan './scripts/docs.sh help'." ;;
esac
