# Format release-notes.txt (untuk user, non-teknis)

File ini ada di `changelogs/X.Y.Z/release-notes.txt` — satu per folder versi,
berdampingan dengan `CHANGELOG.md` (teknis, lihat `changelog-format.md`).
Tujuannya untuk ditempel langsung ke "What's new" di Play Store, App Store,
atau catatan rilis publik lainnya. Pembacanya adalah pengguna aplikasi, bukan
developer.

## Format

- Plain text murni. **Tidak ada** markdown: tanpa `#` heading, tanpa `**bold**`,
  tanpa bullet `-`/`*` ala markdown.
- Kalau perlu daftar poin, pakai simbol bullet biasa (`•`) atau cukup satu
  baris per poin tanpa simbol apa pun — pilih yang paling wajar untuk platform
  target.
- Tidak perlu mencantumkan nomor versi atau tanggal di dalam isi (itu sudah
  terwakili oleh nama foldernya) — kecuali user memang minta ditambahkan.
- Jaga tetap ringkas. Play Store menampilkan "What's new" dengan baik pada
  kisaran ±500 karakter; App Store lebih longgar tapi ringkas tetap lebih
  enak dibaca. Kalau daftar perubahan panjang, pilih yang paling terasa oleh
  user, bukan semuanya.

## Aturan bahasa

- Tulis dari sudut pandang manfaat/pengalaman user, bukan implementasi:
  - Teknis (jangan): `Refactor endpoint /export untuk perbaiki N+1 query`
  - Untuk user (benar): `Export data sekarang jauh lebih cepat`
  - Teknis (jangan): `Fix null pointer exception saat upload file besar`
  - Untuk user (benar): `Perbaikan bug yang membuat aplikasi crash saat upload file besar`
- Hindari istilah: API, endpoint, query, refactor, null/exception, dependency,
  regression, backend/frontend, database, config, CI/CD, commit, hash, dsb.
- Perubahan yang murni internal dan tidak terasa oleh user (refactor tanpa
  perubahan perilaku, bump dependency, perubahan CI, config server) —
  **tidak usah dimasukkan** ke release notes sama sekali.
- Boleh ramah dan sedikit promosional (wajar untuk store listing), tapi tetap
  jujur — jangan melebih-lebihkan fitur yang sebenarnya kecil.
- Tulis dalam bahasa yang sama dengan bahasa utama aplikasi/user (ikuti bahasa
  yang dipakai user saat minta rilis ini, kalau tidak disebutkan pakai Bahasa
  Indonesia).

## Contoh isi

```text
Ada yang baru di versi ini:

• Tampilan dark mode di halaman pengaturan
• Sekarang kamu bisa export riwayat transaksi ke CSV
• Perbaikan bug yang membuat aplikasi crash saat upload file besar

Terima kasih sudah menggunakan aplikasi ini!
```

Contoh yang lebih singkat (gaya Play Store minimalis):

```text
- Dark mode untuk halaman pengaturan
- Export riwayat transaksi ke CSV
- Perbaikan bug crash saat upload file besar
```

## Kalau daftar commit tidak jelas dampaknya ke user

Kalau dari `git log` tidak jelas apakah suatu perubahan terasa oleh user atau
murni internal, jangan menebak — tanyakan singkat ke user, atau default-nya
tidak dimasukkan ke release-notes.txt (lebih aman dilewatkan daripada
mengarang klaim fitur yang tidak akurat).
