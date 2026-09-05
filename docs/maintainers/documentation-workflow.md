# Tutorial Mengelola Dokumentasi

Panduan ini menjelaskan alur lengkap untuk menambah atau mengubah dokumentasi, menguji perubahan, mengirimkannya ke GitHub, dan memastikan situs berhasil dipublikasikan.

## Struktur proyek

Semua dokumen Markdown harus berada di dalam `docs/`.

```text
docs/
├── index.md
├── network/
│   ├── index.md
│   ├── mikrotik.md
│   └── vyos.md
├── server/
└── assets/
    └── images/
```

Gunakan aturan nama berikut:

- huruf kecil;
- gunakan tanda hubung untuk beberapa kata;
- gunakan ekstensi `.md`;
- simpan dokumen di kategori yang sesuai.

Contoh yang benar: `docs/network/wireguard-site-to-site.md`.

## Format halaman

Setiap halaman harus dimulai dengan satu judul tingkat pertama (`#`). Gunakan judul bertingkat secara berurutan dan jangan melewati tingkat judul.

````markdown
# Judul Halaman

Ringkasan singkat mengenai tujuan dokumen.

## Prasyarat

- Perangkat atau sistem yang dibutuhkan
- Hak akses yang dibutuhkan
- Informasi penting sebelum konfigurasi

## Konfigurasi

Jelaskan langkah secara berurutan.

```bash
show interfaces
```

## Verifikasi

Jelaskan cara memastikan konfigurasi bekerja.

```bash
show configuration
```

## Troubleshooting

Tuliskan gejala, penyebab umum, dan solusi.
````

Gunakan penanda bahasa pada blok kode, misalnya `bash`, `yaml`, `json`, `python`, `javascript`, `sql`, atau `ini`. Hal ini membuat syntax highlighting dan tombol salin bekerja dengan baik.

### Tautan, tabel, dan catatan

Gunakan tautan relatif untuk halaman internal:

```markdown
Lihat juga [Panduan BGP](bgp.md).
```

Contoh tabel:

```markdown
| Parameter | Nilai | Keterangan |
| --- | --- | --- |
| ASN | 65001 | ASN lokal |
```

Contoh catatan Material:

```markdown
!!! warning "Perhatian"
    Pastikan perubahan sudah ditinjau sebelum diterapkan ke produksi.
```

### Menambahkan gambar

Simpan gambar di bawah `docs/assets/images/`, lalu gunakan jalur relatif dari dokumen.

```markdown
![Diagram jaringan](../assets/images/diagram-jaringan.png)
```

Gunakan nama file deskriptif, ukuran yang wajar, dan teks alternatif yang menjelaskan isi gambar.

## Menggunakan script pengelola

Untuk pekerjaan harian, gunakan script berikut dari root proyek:

```bash
./scripts/docs.sh help
```

Perintah yang tersedia:

```text
list                         daftar seluruh dokumen
add <path> [judul]           buat dokumen dari template
edit <path>                  edit dokumen
delete <path>                hapus dokumen dengan konfirmasi
nav                          edit navigasi
protect <path> <group>       lindungi dokumen
unprotect <path>             jadikan dokumen publik
hash                         buat hash password
status                       lihat perubahan Git
check                        validasi, unit test, dan strict build
serve                        jalankan preview lokal
publish [pesan commit]       check, commit, dan push
```

Contoh alur paling umum:

```bash
./scripts/docs.sh add network/ospf "Konfigurasi OSPF"
./scripts/docs.sh nav
./scripts/docs.sh serve
./scripts/docs.sh publish "docs: add OSPF guide"
```

Perintah `publish` menampilkan seluruh perubahan dan hanya melanjutkan setelah
Anda mengetik `PUBLISH`. Semua perubahan yang ditampilkan akan masuk ke commit,
jadi selalu baca hasil `git status` dengan teliti.

## Menambah halaman baru

Contoh berikut menambahkan halaman OSPF ke kategori Network.

1. Buat `docs/network/ospf.md`.
2. Isi halaman menggunakan format standar di atas.
3. Tambahkan halaman ke bagian `nav` dalam `mkdocs.yml`:

    ```yaml
    nav:
      - Network:
          - Overview: network/index.md
          - MikroTik: network/mikrotik.md
          - OSPF: network/ospf.md
    ```

4. Jalankan pratinjau lokal dan periksa navigasinya.

Indentasi YAML harus menggunakan spasi, bukan tab. Halaman yang tidak dimasukkan ke `nav` dapat memicu peringatan pada build ketat.

Cara singkat menggunakan script:

```bash
./scripts/docs.sh add network/ospf "Konfigurasi OSPF"
./scripts/docs.sh nav
```

## Membuat halaman publik

Secara default, halaman baru bersifat publik selama jalurnya tidak terdaftar di `config/secure-pages.json`. Halaman publik akan terbuka langsung dan isi halamannya dapat masuk ke hasil pencarian.

## Membuat halaman terlindungi

Fitur ini adalah gerbang akses di sisi browser pada hosting statis, bukan autentikasi server.

### 1. Buat hash kata sandi

Jalankan utilitas berikut dari root proyek:

```bash
python3 scripts/generate-password-hash.py
```

Masukkan kata sandi saat diminta. Utilitas hanya menampilkan hash SHA-256; jangan menulis kata sandi asli ke dalam file proyek atau perintah shell.

### 2. Tambahkan konfigurasi

Tambahkan entri ke `config/secure-pages.json`:

```json
{
  "secure_pages": [
    {
      "path": "/network/ospf/",
      "group": "network-internal",
      "password_hash": "HASH_SHA_256_DARI_UTILITAS"
    }
  ]
}
```

Nilai `path` mengikuti URL hasil MkDocs, bukan nama berkas. Konfigurasi tetap terpisah dari isi Markdown.

### 3. Beri indikator navigasi

Tambahkan simbol kunci pada label halaman di `mkdocs.yml`:

```yaml
- OSPF 🔒: network/ospf.md
```

### 4. Validasi

```bash
python3 scripts/validate-secure-pages.py
```

Validator akan menolak JSON rusak, hash atau grup kosong, jalur duplikat, konfigurasi yang bertentangan, dan jalur yang tidak memiliki dokumen.

## Cara kerja grup kata sandi

Halaman dengan nilai `group` yang sama menggunakan status buka yang sama selama sesi tab browser. Setelah satu halaman berhasil dibuka, halaman lain dalam grup tersebut ikut terbuka. Grup yang berbeda tetap terkunci secara independen.

Status disimpan di `sessionStorage`. Memuat ulang halaman mempertahankan status, tetapi sesi atau tab browser baru meminta kata sandi lagi.

## Mengubah kata sandi

1. Jalankan `python3 scripts/generate-password-hash.py`.
2. Ganti hanya nilai `password_hash` pada entri yang sesuai.
3. Jalankan validator dan pengujian.
4. Commit dan push perubahan.

Pengguna yang sudah membuka grup dalam sesi aktif mungkin perlu membuka tab atau sesi baru untuk menguji hash yang baru.

## Menghapus perlindungan

1. Hapus entri halaman dari `config/secure-pages.json`.
2. Hapus simbol `🔒` pada label navigasi.
3. Jalankan validator dan build ketat.
4. Periksa indeks pencarian karena isi halaman sekarang akan bersifat publik.

Cara singkat:

```bash
./scripts/docs.sh unprotect network/ospf
```

## Mengedit dan menghapus halaman

Edit halaman:

```bash
./scripts/docs.sh edit network/ospf
```

Hapus halaman:

```bash
./scripts/docs.sh delete network/ospf
```

Penghapusan membutuhkan konfirmasi. Script juga membersihkan item navigasi,
konfigurasi secure, dan tautan Markdown yang menuju halaman tersebut. Perintah
yang sama dapat dijalankan ulang jika file sudah telanjur dihapus tetapi masih
ada referensi yang tertinggal.

Setelah menghapus beberapa halaman, cukup jalankan publish:

```bash
./scripts/docs.sh delete network/mikrotik
./scripts/docs.sh delete network/bgp
./scripts/docs.sh publish "docs: remove unused network pages"
```

Tinjau daftar perubahan yang ditampilkan sebelum mengetik `PUBLISH`. Script
akan menjalankan validator, unit test, dan strict build sebelum commit dan push.

## Menyiapkan lingkungan lokal

Direkomendasikan menggunakan virtual environment agar paket proyek tidak bercampur dengan Python sistem.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

Jika virtual environment sudah dibuat, cukup aktifkan kembali:

```bash
source .venv/bin/activate
```

## Pratinjau lokal

```bash
mkdocs serve
```

Buka alamat yang ditampilkan di terminal, biasanya `http://127.0.0.1:8000/`. Periksa:

- judul, isi, tautan, gambar, dan blok kode;
- posisi halaman pada navigasi;
- tampilan desktop dan mobile;
- mode terang dan gelap;
- halaman publik dapat dibuka langsung;
- halaman terlindungi menampilkan formulir kunci.

Hentikan server dengan ++ctrl+c++.

## Pemeriksaan sebelum push

Jalankan dari root proyek:

```bash
python3 scripts/validate-secure-pages.py
python3 -m unittest discover -s tests -v
mkdocs build --strict
```

Atau gunakan satu perintah:

```bash
./scripts/docs.sh check
```

Build ketat harus selesai tanpa error. Folder `site/` adalah hasil build lokal dan tidak perlu di-commit.

Periksa perubahan sebelum membuat commit:

```bash
git status
git diff
```

## Push langsung ke GitHub

Cara otomatis yang direkomendasikan:

```bash
./scripts/docs.sh publish "docs: jelaskan perubahan"
```

Script menjalankan seluruh pemeriksaan, menampilkan file yang berubah, meminta
konfirmasi eksplisit, membuat commit, lalu melakukan push ke branch aktif.
Deployment produksi hanya dipicu jika branch tersebut adalah `main`.

Untuk menjalankan Git secara manual, ikuti langkah berikut.

Sinkronkan branch lokal terlebih dahulu:

```bash
git pull --rebase origin main
```

Tambahkan hanya file yang memang ingin dikirim. Contoh:

```bash
git add docs/network/ospf.md mkdocs.yml
git status
git commit -m "docs: add OSPF guide"
git push origin main
```

Prefix commit yang disarankan:

- `docs:` untuk isi dokumentasi;
- `feat:` untuk fitur baru;
- `fix:` untuk perbaikan;
- `security:` untuk perubahan terkait gerbang akses;
- `chore:` untuk pemeliharaan.

Jangan gunakan `git add .` tanpa memeriksa `git status`, agar file lokal atau rahasia tidak ikut ter-commit.

## Alur pull request

Untuk perubahan yang perlu ditinjau:

```bash
git switch -c docs/tambah-panduan-ospf
git add docs/network/ospf.md mkdocs.yml
git commit -m "docs: add OSPF guide"
git push -u origin docs/tambah-panduan-ospf
```

Setelah itu, buka repository GitHub dan buat pull request menuju `main`. Deployment produksi berjalan setelah perubahan masuk ke `main`.

## Proses publish

Push ke `main` memicu workflow `.github/workflows/deploy.yml`. GitHub Actions akan:

1. mengambil isi repository;
2. menyiapkan Python;
3. memasang `requirements.txt`;
4. memvalidasi konfigurasi halaman terlindungi;
5. menjalankan `mkdocs build --strict`;
6. mengunggah hasil build;
7. melakukan deployment ke GitHub Pages.

Pantau tab **Actions** pada GitHub sampai workflow berwarna hijau. Setelah berhasil, buka:

```text
https://zaenferdiansyah.github.io/docsnewri/
```

Periksa halaman yang baru dipublikasikan melalui navigasi dan URL langsung. Jika perubahan belum terlihat, tunggu sebentar lalu lakukan hard refresh.

Jika workflow gagal, buka job **Build documentation**, baca langkah pertama yang gagal, perbaiki di lokal, kemudian commit dan push perbaikannya.

## Edit langsung dari halaman

Setiap halaman memiliki tombol edit yang menuju berkas terkait di branch `main` pada GitHub. Setelah mengedit melalui GitHub, buat commit atau pull request. Gunakan alur ini untuk perubahan kecil; perubahan besar tetap sebaiknya diuji secara lokal.

## Batas keamanan

GitHub Pages adalah hosting statis. Perlindungan halaman di proyek ini hanya gerbang akses client-side dan tidak boleh dipakai untuk menyimpan informasi yang sangat sensitif.

Jangan pernah menyimpan:

- private key;
- password produksi;
- API secret;
- kredensial database;
- VPN private key;
- authentication token;
- kredensial pelanggan.

File hasil build tetap dapat diambil dari hosting statis oleh pengguna yang mengetahui lokasinya. Gunakan sistem autentikasi server dan penyimpanan privat jika membutuhkan kerahasiaan sebenarnya.
