# Product Requirements Document

## MkDocs Documentation Portal

Version: 1.0  
Status: Draft

---

# 1. Overview

MkDocs Documentation Portal adalah portal dokumentasi berbasis MkDocs Material yang digunakan untuk menyimpan, mengelola, mencari, dan mempublikasikan dokumentasi teknis.

Dokumentasi akan disimpan dalam GitHub Repository dan dipublikasikan menggunakan GitHub Pages.

Sebagian besar dokumentasi bersifat public, tetapi administrator dapat menentukan halaman tertentu sebagai secure page.

Secure page membutuhkan password sebelum isi dokumentasi ditampilkan.

Contoh:

```text
Network
├── MikroTik
├── VyOS 🔒
├── BGP
└── WireGuard
```

Dalam contoh tersebut:

- MikroTik → Public
- VyOS → Protected
- BGP → Public
- WireGuard → Public

Hosting menggunakan URL GitHub Pages tanpa custom domain.

Contoh:

```text
https://username.github.io/documentation/
```

---

# 2. Goals

Project harus menyediakan:

1. Portal dokumentasi teknis yang sederhana.
2. Dokumentasi menggunakan Markdown.
3. Mudah menambahkan dokumentasi baru.
4. Mudah mengubah dokumentasi yang sudah ada.
5. Navigasi dokumentasi berdasarkan kategori.
6. Full-text search.
7. Syntax highlighting.
8. Copy button untuk command dan code.
9. Responsive UI.
10. Dark mode.
11. GitHub Pages deployment.
12. Automatic deployment menggunakan GitHub Actions.
13. Kemampuan melindungi halaman tertentu menggunakan password.
14. Konfigurasi secure page yang sederhana.
15. Session unlock agar user tidak perlu memasukkan password setiap membuka halaman yang sama.

---

# 3. Non-Goals

Versi pertama tidak menyediakan:

- User management.
- Database.
- Backend application.
- Role Based Access Control.
- OAuth.
- LDAP.
- Active Directory.
- SSO.
- Audit login server-side.
- Per-user permissions.
- Server-side authentication.

---

# 4. Important Security Limitation

GitHub Pages merupakan static hosting.

Secure Page pada project ini merupakan client-side access protection.

Artinya proteksi digunakan untuk:

- mencegah user biasa membuka dokumentasi tertentu;
- memberikan barrier akses;
- menyembunyikan konten dari navigasi normal sebelum password benar.

Proteksi ini TIDAK boleh dianggap sebagai perlindungan terhadap attacker yang memiliki kemampuan melakukan inspection terhadap static assets GitHub Pages.

Jangan menyimpan:

```text
password production
private key
SSH private key
API secret
database password
VPN private key
credential pelanggan
authentication token
```

pada portal ini.

Jika di masa depan dibutuhkan keamanan sebenarnya, secure documentation harus dipindahkan ke sistem authentication server-side.

---

# 5. Technology Stack

## Documentation Engine

```text
MkDocs
```

## Theme

```text
Material for MkDocs
```

## Source Format

```text
Markdown
```

## Source Control

```text
GitHub
```

## Hosting

```text
GitHub Pages
```

## Deployment

```text
GitHub Actions
```

## Secure Page

```text
JavaScript Client-Side Authentication
+
Hashed Password Verification
+
Web Crypto API
```

---

# 6. Proposed Repository Structure

```text
documentation/
│
├── docs/
│   ├── index.md
│   │
│   ├── network/
│   │   ├── index.md
│   │   ├── mikrotik.md
│   │   ├── vyos.md
│   │   ├── bgp.md
│   │   └── wireguard.md
│   │
│   ├── dns/
│   │   ├── index.md
│   │   ├── bind9.md
│   │   ├── unbound.md
│   │   └── dnsdist.md
│   │
│   ├── server/
│   │   ├── index.md
│   │   ├── ubuntu.md
│   │   └── esxi.md
│   │
│   ├── monitoring/
│   │   ├── grafana.md
│   │   ├── prtg.md
│   │   └── prometheus.md
│   │
│   ├── assets/
│   │   ├── stylesheets/
│   │   │   └── secure.css
│   │   │
│   │   └── javascripts/
│   │       └── secure-pages.js
│   │
│   └── overrides/
│
├── config/
│   └── secure-pages.json
│
├── scripts/
│   ├── generate-password-hash.py
│   └── validate-secure-pages.py
│
├── .github/
│   └── workflows/
│       └── deploy.yml
│
├── mkdocs.yml
├── requirements.txt
├── PRD.md
├── AGENTS.md
└── TASKS.md
```

---

# 7. Navigation Structure

Initial navigation:

```text
Home

Network
├── MikroTik
├── VyOS 🔒
├── BGP
└── WireGuard

DNS
├── Bind9
├── Unbound
└── dnsdist

Server
├── Ubuntu
└── VMware ESXi

Monitoring
├── Grafana
├── PRTG
└── Prometheus
```

Locked pages harus memiliki icon lock.

Contoh:

```text
VyOS 🔒
```

---

# 8. Public Page

Public page dapat dibuka tanpa authentication.

Example:

```text
/network/mikrotik/
/network/bgp/
/network/wireguard/
```

User langsung melihat isi dokumentasi.

---

# 9. Secure Page

Secure page harus ditentukan melalui konfigurasi.

Contoh:

```json
{
  "secure_pages": [
    {
      "path": "/network/vyos/",
      "title": "VyOS",
      "password_hash": "HASH"
    }
  ]
}
```

Application tidak boleh menyimpan plaintext password dalam konfigurasi.

Password harus dibandingkan menggunakan hash.

---

# 10. Secure Page User Flow

Ketika user membuka:

```text
/network/vyos/
```

system memeriksa apakah halaman merupakan secure page.

Jika public:

```text
Render documentation
```

Jika secure:

```text
Open URL
   │
   ▼
Check unlock session
   │
   ├── Valid
   │      ↓
   │   Display page
   │
   └── Not valid
          ↓
     Display Lock Screen
          ↓
     Enter Password
          ↓
     Hash Password
          ↓
     Compare Hash
          │
     ┌────┴────┐
     │         │
   Match     Invalid
     │         │
     ▼         ▼
 Display    Error
 Page
```

---

# 11. Lock Screen

Secure page harus menampilkan UI seperti:

```text
┌───────────────────────────────────┐
│                                   │
│              🔒                   │
│                                   │
│       Protected Documentation     │
│                                   │
│   This page requires a password   │
│                                   │
│   Password                        │
│   ┌───────────────────────────┐   │
│   │ •••••••••••••••••       │   │
│   └───────────────────────────┘   │
│                                   │
│          [ Unlock ]               │
│                                   │
└───────────────────────────────────┘
```

Requirements:

- Password input type harus `password`.
- Enter harus dapat submit.
- Wrong password menampilkan error.
- Isi dokumentasi tidak ditampilkan oleh UI sebelum unlock.
- Tampilan mengikuti Material for MkDocs.
- Support light mode.
- Support dark mode.
- Mobile responsive.

---

# 12. Unlock Session

Setelah password benar, aplikasi menyimpan unlock state.

Recommended:

```text
sessionStorage
```

Default behavior:

```text
Browser Tab Open
    ↓
Page unlocked

Browser Tab Closed
    ↓
Unlock session removed
```

Tidak menggunakan persistent authentication secara default.

Optional future configuration:

```text
sessionStorage
localStorage
expiration time
```

---

# 13. Multiple Secure Pages

System harus mendukung lebih dari satu secure page.

Example:

```text
Network
├── MikroTik
├── VyOS 🔒
├── BGP
└── WireGuard

Server
├── Ubuntu
├── VMware ESXi 🔒
└── Docker
```

Configuration:

```json
{
  "secure_pages": [
    {
      "path": "/network/vyos/",
      "group": "network-vyos",
      "password_hash": "HASH_1"
    },
    {
      "path": "/server/esxi/",
      "group": "server-esxi",
      "password_hash": "HASH_2"
    }
  ]
}
```

---

# 14. Password Groups

Multiple pages harus dapat menggunakan password yang sama.

Contoh:

```text
Network
├── VyOS 🔒
├── Core Router 🔒
└── Backbone 🔒
```

Configuration:

```text
group = network-internal
```

Jika user sudah membuka satu halaman pada group tersebut, halaman lain dalam group yang sama dapat otomatis unlocked selama session masih aktif.

---

# 15. Markdown Documentation

Documentation harus tetap menggunakan Markdown standar.

Example:

```markdown
# VyOS

## Show Interfaces

```bash
show interfaces
```

## Show BGP

```bash
show protocols bgp
```
```

Tidak diperlukan format khusus untuk menulis secure documentation.

Secure/public status ditentukan dari konfigurasi.

---

# 16. Adding New Documentation

Untuk menambah dokumentasi:

Create:

```text
docs/network/ospf.md
```

Isi:

```markdown
# OSPF

## Overview

OSPF documentation.
```

Kemudian tambahkan ke navigation:

```yaml
nav:
  - Network:
      - MikroTik: network/mikrotik.md
      - VyOS 🔒: network/vyos.md
      - BGP: network/bgp.md
      - OSPF: network/ospf.md
      - WireGuard: network/wireguard.md
```

Commit:

```bash
git add .
git commit -m "docs: add OSPF documentation"
git push
```

GitHub Actions otomatis menjalankan deployment.

---

# 17. Making Page Secure

Admin tidak perlu mengubah isi Markdown.

Contoh halaman:

```text
docs/network/vyos.md
```

Tambahkan halaman tersebut ke:

```text
config/secure-pages.json
```

Example:

```json
{
  "path": "/network/vyos/",
  "group": "vyos",
  "password_hash": "..."
}
```

Setelah deployment berikutnya halaman menjadi locked.

---

# 18. Password Hash Generator

Repository harus menyediakan utility:

```bash
python scripts/generate-password-hash.py
```

Program meminta:

```text
Enter password:
Confirm password:
```

Output:

```text
Password hash:

f01c7...
```

Hash kemudian dapat dimasukkan ke konfigurasi secure page.

Password plaintext tidak dicetak kembali.

---

# 19. Search

Material for MkDocs search harus diaktifkan.

Search harus mendukung:

- Page title.
- Heading.
- Documentation content.
- Commands.
- Configuration terms.

Secure page membutuhkan perhatian khusus.

Target V1:

Secure page boleh muncul sebagai judul dalam navigation, tetapi konten protected sebaiknya tidak ditampilkan secara lengkap pada search preview.

Jika implementasi search tidak memungkinkan filtering secara aman pada static build, limitation harus didokumentasikan.

---

# 20. MkDocs Features

Enable:

```text
navigation.tabs
navigation.sections
navigation.expand
navigation.indexes
navigation.top
search.highlight
search.share
content.code.copy
content.code.annotate
content.tabs.link
toc.follow
```

Markdown extensions:

```text
admonition
attr_list
md_in_html
tables
footnotes
pymdownx.details
pymdownx.superfences
pymdownx.highlight
pymdownx.inlinehilite
pymdownx.tabbed
pymdownx.tasklist
```

---

# 21. GitHub Pages Deployment

Deployment flow:

```text
Developer
   │
   ▼
git push
   │
   ▼
GitHub
   │
   ▼
GitHub Actions
   │
   ├── Install dependencies
   ├── Validate configuration
   ├── Build MkDocs
   └── Deploy
        │
        ▼
GitHub Pages
```

Deployment harus dijalankan pada:

```text
push to main
```

---

# 22. GitHub Pages URL

Default URL:

```text
https://<github-user>.github.io/<repository>/
```

Example:

```text
https://company.github.io/documentation/
```

Tidak diperlukan custom domain.

---

# 23. GitHub Actions

Workflow minimal:

```text
checkout
setup python
install requirements
validate secure pages
mkdocs build
deploy github pages
```

Build harus gagal jika:

- `mkdocs.yml` invalid.
- Secure pages JSON invalid.
- Protected path tidak ditemukan.
- Duplicate secure configuration ditemukan.

---

# 24. Local Development

Developer harus dapat menjalankan:

```bash
pip install -r requirements.txt
mkdocs serve
```

Kemudian akses:

```text
http://127.0.0.1:8000
```

Secure page harus dapat diuji di local development.

---

# 25. Documentation Editing Workflow

Normal update:

```text
git pull
    ↓
Edit .md
    ↓
mkdocs serve
    ↓
Check Result
    ↓
git add
    ↓
git commit
    ↓
git push
    ↓
Auto Deploy
```

---

# 26. Example Documentation Categories

Initial categories:

```text
Network
DNS
Server
Monitoring
Security
Automation
Development
Troubleshooting
SOP
```

---

# 27. Homepage

Homepage harus berisi:

- Documentation portal title.
- Search.
- Quick navigation.
- Most commonly accessed sections.
- Recently relevant categories.
- Link ke GitHub repository jika diinginkan.

Example:

```text
Zensnewri Documentation

Search documentation...

Network
Router, BGP, WireGuard, routing

DNS
Unbound, Bind9, dnsdist, RPZ

Server
Ubuntu, VMware ESXi, Docker

Monitoring
Grafana, PRTG, Prometheus
```

---

# 28. UI Requirements

Theme harus menggunakan Material for MkDocs.

Requirements:

- Clean.
- Technical.
- Minimal.
- Responsive.
- Fast.
- Mobile friendly.
- Light/dark mode.
- Readable code blocks.
- Navigation sidebar.
- Table of contents.
- Search bar.

---

# 29. Secure Page Visual Indicator

Protected documentation harus terlihat berbeda di navigation.

Example:

```text
VyOS 🔒
```

Optional future implementation:

```text
lock icon
badge INTERNAL
badge SECURE
```

---

# 30. Error Handling

Wrong password:

```text
Incorrect password.
```

Empty password:

```text
Password is required.
```

Invalid configuration:

Build harus gagal.

Unknown secure page:

Build harus menghasilkan validation error.

---

# 31. Performance

Target:

- Initial page load < 3 seconds pada koneksi normal.
- Static assets harus cacheable.
- JavaScript secure page dibuat minimal.
- Tidak menggunakan frontend framework besar.
- Tidak menggunakan database.

---

# 32. Browser Support

Minimum:

```text
Chrome
Firefox
Safari
Microsoft Edge
```

Modern browser dengan Web Crypto API.

---

# 33. Future Features

Potential V2:

- Multiple password groups.
- Automatic page metadata.
- Secure badge.
- Expiring unlock session.
- Search filtering.
- Documentation versioning.
- Git revision date.
- Contributors.
- PDF export.
- Page feedback.
- Analytics.
- Mermaid diagram.
- PlantUML.
- GitHub edit button.
- Protected documentation using real server-side authentication.

---

# 34. Acceptance Criteria

Project dianggap selesai jika:

1. MkDocs Material dapat dijalankan secara lokal.
2. Homepage tersedia.
3. Navigation tersedia.
4. Public documentation dapat dibuka tanpa password.
5. Secure page menampilkan lock screen.
6. Wrong password tidak membuka documentation UI.
7. Correct password membuka documentation.
8. Unlock state bertahan selama browser session.
9. Multiple secure pages didukung.
10. Secure page configuration tidak memerlukan perubahan Markdown.
11. Password disimpan sebagai hash, bukan plaintext.
12. Documentation dapat dicari.
13. Code memiliki copy button.
14. Light/dark mode berfungsi.
15. GitHub Actions berhasil build.
16. GitHub Actions berhasil deploy.
17. Site tersedia melalui GitHub Pages.
18. Tidak membutuhkan custom domain.
19. Tambah Markdown baru dapat dilakukan tanpa mengubah application core.
20. Security limitation dijelaskan di README/documentation.

---

# 35. Definition of Done

Version 1 dianggap DONE ketika workflow berikut berhasil:

```text
Create documentation
        ↓
Set public / secure
        ↓
Push to GitHub
        ↓
GitHub Actions build
        ↓
GitHub Pages deployment
        ↓
Open public page
        ↓
No password required

Open secure page
        ↓
Password prompt
        ↓
Correct password
        ↓
Documentation displayed
```
