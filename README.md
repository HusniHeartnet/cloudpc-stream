# CloudPC Stream

Penampil layar (client streaming) aplikasi CloudPC: **moonlight-qt yang diganti mereknya**, dengan perubahan
sesedikit mungkin supaya pembaruan dari upstream mudah diikuti.

Folder ini berisi semua yang dibutuhkan untuk build, dan **isinya dijadikan repo GitHub publik tersendiri**.
Repo publik itu sekaligus memenuhi kewajiban GPLv3: setiap rilis menyertakan zip source lengkap.

| File | Isi |
|---|---|
| `branding.json` | Nama produk, perusahaan, nama `.exe`, dan versi upstream (`upstream_tag`) |
| `apply_branding.py` | Mengganti merek di source upstream; berhenti dengan error kalau ada pola yang tidak ketemu |
| `assets/icon.ico`, `assets/icon.svg` | Ikon (sementara; ganti dengan logo asli, nama file tetap sama) |
| `.github/workflows/build-windows.yml` | Build Windows x64 di GitHub Actions, lalu membuat GitHub Release |

## Apa yang diubah dari Moonlight

Hanya merek. Logika streaming tidak disentuh.

- Nama aplikasi/organisasi, nama di mixer volume Windows, properti file `.exe`
- Judul jendela stream (`"vm1 - Moonlight"` menjadi `"CloudPC"`)
- Teks "Moonlight" di UI (`qsTr()` di QML, `tr()` di C++); teks log TIDAK diubah, karena aplikasi CloudPC
  membaca log stream untuk statistik
- Ikon
- Cek update otomatis dimatikan (tombolnya mengarah ke unduhan Moonlight resmi)
- `Moonlight.exe` diganti nama menjadi `CloudPCStream.exe` setelah build

Daftar persisnya ditulis ke `CLOUDPC_MODIFICATIONS.txt` di source dan di zip aplikasi.

Yang sengaja dibiarkan: tombol Discord/Help di layar utama Moonlight (layar itu tidak dipakai; aplikasi CloudPC
selalu memanggil mode `pair`/`stream`), installer MSI, serta build Mac/Linux/Android.

## Cara build (sekali siapkan, lalu tinggal klik)

1. Buat akun/organisasi GitHub, lalu buat repo **publik** baru, misalnya `cloudpc-stream`. Saat membuat repo,
   pilih lisensi **GNU GPLv3**.
2. Unggah isi folder ini ke repo itu, termasuk folder `.github` (lewat "Add file > Upload files" atau git).
3. Buka tab **Actions** > "Build CloudPC Stream (Windows)" > **Run workflow**. Lama build sekitar 20-40 menit.
4. Hasilnya muncul di **Releases**:
   - `CloudPCStream-x64-v6.2.0.zip`: aplikasinya
   - `CloudPCStream-src-v6.2.0.zip`: source lengkap (wajib GPL, biarkan tetap ada)
5. Di PC build CloudPC: ekstrak zip aplikasi ke `client\vendor\stream\` (sehingga ada
   `client\vendor\stream\CloudPCStream.exe`), lalu jalankan `client\build.ps1` dan `tools\teman\buat-paket-app.ps1`.
   Aplikasi CloudPC otomatis memakai `stream\CloudPCStream.exe`, dan installer tester tidak lagi memasang Moonlight.

## Memperbarui ke versi Moonlight baru

1. Ubah `upstream_tag` di `branding.json` (contoh `v6.3.0`).
2. Samakan `QT_VERSION` dan `aqtsource` di workflow dengan `.github/workflows/build-win-mac.yml` milik upstream
   pada tag tersebut.
3. Run workflow. Kalau langkah "Ganti merek" gagal, artinya upstream mengubah baris yang dicari: sesuaikan
   `REPLACEMENTS` di `apply_branding.py`. Uji lokal dulu dengan `python apply_branding.py <folder source>`
   pada isi `MoonlightSrc-<versi>.tar.gz` dari rilis upstream.
4. Setelah rilis jadi, uji pairing + stream sungguhan, dan pastikan `manage.py report` masih menampilkan
   statistik FPS (berarti format log tidak berubah).

## Kewajiban lisensi (GPLv3), ringkas

- Repo ini publik, dan setiap rilis berisi zip source. Jangan hapus rilis lama yang masih dipakai pengguna.
- Zip aplikasi berisi `LICENSE.txt`, `SOURCE.txt` (alamat source), dan `CLOUDPC_MODIFICATIONS.txt`.
  Aplikasi CloudPC menyebutkannya di tab Akun.
- Jangan memakai nama atau logo Moonlight sebagai merek produk; kami menyebut "berbasis Moonlight" sebagai kredit.
- Aplikasi CloudPC (pywebview) tetap terpisah dan tertutup: ia hanya menjalankan `CloudPCStream.exe` lewat
  command line, tidak menyertakan kode Moonlight di dalamnya.

Ini ringkasan praktis, bukan nasihat hukum.
