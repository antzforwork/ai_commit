---
name: semantic-version-release
description: Menaikkan (bump) versi aplikasi/website mengikuti Semantic Versioning (major.minor.patch), lalu membuat changelog teknis DAN release notes non-teknis untuk user (Play Store/App Store) dalam satu folder per versi (mis. changelogs/2.1.0/), dan mem-push hasilnya ke git. WAJIB gunakan skill ini setiap kali user minta "naikkan versi", "bump version", "rilis versi baru", "release patch/minor/major", "update version aplikasi/website", "buatkan release notes/what's new", atau menyebut kata "changelog" terkait rilis versi — bahkan jika mereka tidak menyebut kata "semver" secara eksplisit.
---

# Semver Release

Skill ini menjalankan alur rilis versi end-to-end: deteksi versi saat ini →
bump sesuai semver → tulis changelog teknis + release notes untuk user,
dikelompokkan per-versi dalam satu folder → commit → push ke git.

## Kapan trigger

Gunakan skill ini ketika user minta hal-hal seperti:
- "naikkan versi jadi minor/major/patch"
- "bump version dong"
- "rilis versi baru, buatkan changelog-nya"
- "update version.json terus push"

Jangan gunakan untuk sekadar membaca/menampilkan versi saat ini tanpa mengubah apa pun — itu cukup dijawab langsung tanpa alur di bawah.

## Alur kerja (jalankan berurutan)

### 1. Pastikan berada di repo git yang bersih

```bash
git rev-parse --is-inside-work-tree
git status --porcelain
```

- Jika bukan repo git → beri tahu user, hentikan.
- Jika ada perubahan uncommitted yang TIDAK terkait rilis (kode yang belum selesai, dsb.) → tanyakan ke user apakah mau di-commit dulu terpisah, atau ikut masuk ke commit rilis. Jangan asumsikan sendiri.

### 2. Deteksi versi saat ini

```bash
python3 <path-skill-ini>/scripts/bump_version.py detect --path .
```

Script ini mendeteksi salah satu dari: `package.json`, `package-lock.json`,
`pyproject.toml`, `Cargo.toml`, `composer.json`, `gradle.properties`,
`VERSION`, `version.txt`, `setup.py`, `setup.cfg`.

- Kalau `error: no_version_file_found` → tanyakan ke user file mana yang jadi sumber kebenaran versi (atau tawarkan bikin file `VERSION` baru mulai dari `0.1.0`).
- Kalau `inconsistent: true` (versi beda-beda antar file, mis. monorepo) → tampilkan daftar file+versinya ke user, minta konfirmasi versi target sebelum lanjut. Jangan menebak mana yang benar.

### 3. Tentukan jenis bump

Jika user sudah bilang eksplisit (mis. "naikkan minor") → langsung pakai itu.

Jika user cuma bilang "naikkan versi" tanpa detail, gunakan heuristik dari histori commit sejak tag terakhir untuk **menyarankan** jenis bump, lalu tetap konfirmasi ke user sebelum eksekusi:

```bash
git describe --tags --abbrev=0 2>/dev/null   # tag terakhir, kalau ada
git log <tag-terakhir>..HEAD --oneline
```

Heuristik (mengikuti Conventional Commits bila dipakai di repo):
- Ada `BREAKING CHANGE` / `!:` di commit → **major**
- Ada `feat:` tanpa breaking change → **minor**
- Hanya `fix:`, `chore:`, `docs:`, dll → **patch**
- Kalau repo tidak pakai conventional commits, cukup tanya user langsung: major/minor/patch.

### 4. Jalankan bump

```bash
python3 <path-skill-ini>/scripts/bump_version.py bump --type <major|minor|patch> --path .
```

Simpan `old_version` dan `new_version` dari output JSON-nya — dipakai di langkah changelog & commit message.

### 5. Buat folder changelog per versi (2 file: teknis + untuk user)

Setiap kenaikan versi menghasilkan **satu folder baru**, bukan satu file:

```
changelogs/
└── NEW_VERSION/          # nama folder = angka versi saja, tanpa prefix "v" (contoh: 2.1.0)
    ├── CHANGELOG.md       # teknis, untuk developer/internal
    └── release-notes.txt  # non-teknis, untuk dipublish ke Play Store / App Store / user akhir
```

```bash
mkdir -p changelogs/NEW_VERSION
```

Jangan pernah menimpa/menggabung ke folder versi yang sudah ada — selalu folder baru per kenaikan versi.

Sumber isi untuk KEDUA file: daftar commit sejak tag/rilis terakhir
(`git log <tag-lama>..HEAD --oneline`). Jangan mengarang perubahan yang tidak ada di git log — kalau pesan commit tidak jelas maksudnya, tanyakan singkat ke user daripada menebak.

**a) `CHANGELOG.md` (teknis)** — ikuti format di `references/changelog-format.md`:
kelompokkan jadi Added/Changed/Fixed berdasarkan prefix commit (`feat`→Added, `fix`→Fixed, sisanya→Changed) bila repo pakai Conventional Commits; kalau tidak ada pola, tulis apa adanya sebagai daftar perubahan.

**b) `release-notes.txt` (non-teknis, untuk publik)** — ikuti format & aturan bahasa di `references/store-notes-format.md`. Poin penting:
- Plain text biasa (bukan markdown), tanpa heading `#`, tanpa bullet `-`/`*` bergaya markdown — cukup baris per baris atau tanda "•" kalau perlu daftar.
- Bahasa awam, fokus ke manfaat/pengalaman user ("Sekarang kamu bisa export data ke Excel"), BUKAN istilah teknis ("refactor endpoint /export", "fix null pointer", "optimize query").
- Setiap poin teknis dari CHANGELOG.md diterjemahkan ke dampaknya bagi user; perubahan yang murni internal (refactor, chore, dependency bump, config, CI) yang tidak berdampak ke user **tidak usah dimasukkan** ke release-notes.txt.
- Ringkas — usahakan muat dalam batas umum Play Store "What's new" (sekitar 500 karakter); App Store lebih longgar tapi tetap ringkas.

Setelah kedua file dibuat, tampilkan isinya ke user sebelum lanjut commit — terutama `release-notes.txt`, karena ini akan tampil ke publik dan sebaiknya dikonfirmasi dulu.

### 6. Commit & tag

```bash
git add <file-versi-yang-diupdate> changelogs/NEW_VERSION/
git commit -m "chore(release): vNEW_VERSION"
git tag vNEW_VERSION
```

### 7. Push — konfirmasi dulu ke user

Push ke remote itu tindakan yang memengaruhi orang lain (mengubah histori bersama), jadi **selalu konfirmasi singkat sebelum push**, sebutkan: branch tujuan, remote, dan bahwa tag ikut ter-push. Contoh konfirmasi:

> Siap push `vNEW_VERSION` (branch `<branch>`, remote `origin`) beserta tag-nya. Lanjut?

Setelah user setuju:

```bash
git push origin <branch>
git push origin vNEW_VERSION
```

Jika user sudah pernah bilang secara eksplisit di awal permintaan ("langsung push aja tanpa nanya lagi") untuk sesi ini, boleh lewati konfirmasi ulang setiap kali — tapi tetap laporkan hasil push (sukses/gagal) di akhir.

### 8. Ringkasan akhir

Laporkan ke user secara singkat: versi lama → versi baru, file yang diupdate, path folder changelog (`changelogs/NEW_VERSION/`) beserta isinya (CHANGELOG.md & release-notes.txt), status commit/tag/push.

## Hal yang perlu diperhatikan

- **Jangan pernah menimpa folder changelog versi sebelumnya** — selalu folder baru per versi.
- **`release-notes.txt` ditujukan untuk publik** — jangan bocorkan detail internal (nama file/endpoint, nomor tiket internal, nama library, dll). Kalau ragu apakah satu perubahan layak masuk ke situ, tanyakan ke user.
- **Jangan push langsung ke `main`/`master` tanpa konfirmasi** kalau repo tampaknya dipakai bersama tim (banyak kontributor di `git log`, ada branch protection, dst.) — tanyakan dulu kalau ragu.
- Kalau `git push` gagal (mis. perlu `--force`, ada konflik, autentikasi gagal) — jangan otomatis pakai `--force`. Laporkan errornya ke user dan minta arahan.
- Jika project pakai monorepo dengan banyak versi independen, jalankan alur ini per-package sesuai konfirmasi user di langkah 2.

## Referensi

- `references/changelog-format.md` — format & contoh isi `CHANGELOG.md` (teknis) per-versi.
- `references/store-notes-format.md` — format, aturan bahasa, & contoh isi `release-notes.txt` (non-teknis, untuk Play Store/App Store/user akhir) per-versi.
