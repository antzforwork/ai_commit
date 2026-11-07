# Format CHANGELOG.md (teknis) per-versi

File ini ada di `changelogs/X.Y.Z/CHANGELOG.md` — satu folder baru per
kenaikan versi, berisi file ini DAN `release-notes.txt` (lihat
`store-notes-format.md`). Formatnya mengikuti gaya
[Keep a Changelog](https://keepachangelog.com/), disederhanakan. File ini
untuk konsumsi developer/internal — boleh teknis, beda dengan
`release-notes.txt` yang harus awam.

## Template

```markdown
# vX.Y.Z — YYYY-MM-DD

## Added
- ...

## Changed
- ...

## Fixed
- ...
```

Aturan:
- Judul (`# vX.Y.Z — tanggal`) wajib ada, tanggal pakai format ISO (`YYYY-MM-DD`), ambil dari tanggal saat bump dijalankan.
- Section (`Added`/`Changed`/`Fixed`) yang tidak ada isinya, dihapus saja — jangan ditulis kosong.
- Kalau tidak ada histori commit yang jelas kategorinya (repo baru, atau tidak ada tag sebelumnya), boleh pakai satu section generik:

```markdown
# vX.Y.Z — YYYY-MM-DD

## Changes
- <ringkasan singkat perubahan, satu baris per commit/perubahan>
```

- Setiap baris changelog idealnya berasal dari pesan commit yang sudah dirapikan (bukan hash mentah), contoh:
  - Commit: `fix: handle null response from payment API`
  - Changelog: `- Fixed: handle null response from payment API`
- Jangan mengarang detail yang tidak ada di commit message atau diff. Kalau pesan commit-nya tidak jelas (mis. "wip", "update"), lebih baik tanyakan singkat ke user maksud perubahan itu daripada menebak.

## Contoh isi lengkap

```markdown
# v1.5.0 — 2026-08-08

## Added
- Added dark mode toggle on settings page
- Added CSV export for transaction history

## Fixed
- Fixed crash when uploading files larger than 10MB

## Changed
- Bumped minimum Node.js version to 20
```
