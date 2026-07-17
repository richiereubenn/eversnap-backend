# EverSnap API Documentation

Dokumentasi ini berisi daftar lengkap dan spesifikasi teknis dari seluruh endpoint API yang tersedia pada aplikasi **EverSnap**.

---

## Informasi Umum
* **Base URL**: `/api`
* **Format Request/Response**: `application/json` (kecuali untuk upload foto yang menggunakan `multipart/form-data`)
* **Autentikasi**: Menggunakan JWT Token dengan format header:
  ```http
  Authorization: Bearer <access_token>
  ```

---

## Ringkasan Endpoint (Endpoint Summary)

Berikut adalah daftar ringkas seluruh endpoint yang tersedia:

### 1. Authentication Modul (`/api/auth`)
| Method | Endpoint | Keterangan Singkat | Akses |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/register` | Mendaftarkan akun admin baru | Public |
| `POST` | `/api/auth/login` | Login admin untuk mendapatkan token JWT | Public |
| `POST` | `/api/auth/refresh` | Memperbarui Access Token menggunakan Refresh Token | Admin (Refresh JWT) |
| `GET` | `/api/auth/me` | Mengambil detail profil admin yang sedang login | Admin (Access JWT) |

### 2. Event Modul (`/api/events`)
| Method | Endpoint | Keterangan Singkat | Akses |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/events` | Menampilkan daftar seluruh event milik admin | Admin (Access JWT) |
| `POST` | `/api/events` | Membuat event baru | Admin (Access JWT) |
| `GET` | `/api/events/<event_id>` | Menampilkan detail spesifik dari suatu event | Admin (Access JWT) |
| `PUT` | `/api/events/<event_id>` | Mengubah data event (misal judul, lokasi, dsb) | Admin (Access JWT) |
| `DELETE` | `/api/events/<event_id>` | Menghapus event beserta semua quest di dalamnya | Admin (Access JWT) |
| `GET` | `/api/events/<event_id>/qr` | Mengambil atau membuat gambar QR Code event | Admin (Access JWT) |
| `GET` | `/api/events/<event_id>/dashboard` | Mengambil statistik ringkas (tamu, foto, quest) | Admin (Access JWT) |

### 3. Quest Modul (`/api/events/<event_id>/quests`)
| Method | Endpoint | Keterangan Singkat | Akses |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/events/<event_id>/quests` | Menampilkan semua quest di suatu event | Admin (Access JWT) |
| `POST` | `/api/events/<event_id>/quests` | Membuat quest baru untuk event | Admin (Access JWT) |
| `GET` | `/api/events/<event_id>/quests/<quest_id>` | Menampilkan detail dari suatu quest | Admin (Access JWT) |
| `PUT` | `/api/events/<event_id>/quests/<quest_id>` | Mengubah data detail dari suatu quest | Admin (Access JWT) |
| `DELETE` | `/api/events/<event_id>/quests/<quest_id>` | Menghapus quest dari event | Admin (Access JWT) |
| `PATCH` | `/api/events/<event_id>/quests/<quest_id>/toggle-active` | Mengaktifkan/menonaktifkan status quest | Admin (Access JWT) |
| `PATCH` | `/api/events/<event_id>/quests/reorder` | Mengatur ulang urutan quest | Admin (Access JWT) |

### 4. Guest Modul (`/api/guest`)
| Method | Endpoint | Keterangan Singkat | Akses |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/guest/event/<event_id>/join` | Tamu bergabung ke event via scan QR & isi nama | Public |
| `GET` | `/api/guest/<guest_id>/event` | Tamu melihat detail event & list quest | Public |
| `GET` | `/api/guest/<guest_id>/quests` | Tamu melihat list quest beserta progress miliknya | Public |
| `POST` | `/api/guest/<guest_id>/quests/<quest_id>/photos` | Tamu mengunggah foto untuk menyelesaikan quest | Public |

---
---

## Detail Spesifikasi Endpoint

## 1. Authentication Modul (`/api/auth`)

### 1.1. Register Admin
* **Endpoint**: `POST /api/auth/register`
* **Autentikasi**: Tidak ada (Public)
* **Request Body (JSON)**:
  ```json
  {
    "username": "admin_wedding",
    "email": "admin@eversnap.com",
    "password": "securepassword123"
  }
  ```
* **Response (201 Created)**:
  ```json
  {
    "message": "Account created successfully",
    "user": {
      "id": 1,
      "username": "admin_wedding",
      "email": "admin@eversnap.com"
    }
  }
  ```

### 1.2. Login Admin
* **Endpoint**: `POST /api/auth/login`
* **Autentikasi**: Tidak ada (Public)
* **Request Body (JSON)**:
  ```json
  {
    "email": "admin@eversnap.com",
    "password": "securepassword123"
  }
  ```
* **Response (200 OK)**:
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "refresh_token": "eyJhbGciOi...",
    "user": {
      "id": 1,
      "username": "admin_wedding",
      "email": "admin@eversnap.com"
    }
  }
  ```

### 1.3. Refresh Token
* **Endpoint**: `POST /api/auth/refresh`
* **Autentikasi**: **Wajib menggunakan Refresh Token** (`Authorization: Bearer <refresh_token>`)
* **Response (200 OK)**:
  ```json
  {
    "access_token": "eyJhbGciOi..."
  }
  ```

### 1.4. Detail Admin Aktif (Me)
* **Endpoint**: `GET /api/auth/me`
* **Autentikasi**: **Wajib menggunakan Access Token**
* **Response (200 OK)**:
  ```json
  {
    "id": 1,
    "username": "admin_wedding",
    "email": "admin@eversnap.com"
  }
  ```

---

## 2. Event Modul (`/api/events`)

### 2.1. List Semua Event
* **Endpoint**: `GET /api/events`
* **Autentikasi**: **Wajib (Admin)**
* **Response (200 OK)**:
  ```json
  [
    {
      "id": 1,
      "title": "Andi & Budi Wedding",
      "date": "2026-12-12",
      "location": "Gedung Serbaguna Jakarta",
      "is_started": false,
      "qr_code_path": "qrcodes/event_1.png"
    }
  ]
  ```

### 2.2. Buat Event Baru
* **Endpoint**: `POST /api/events`
* **Autentikasi**: **Wajib (Admin)**
* **Request Body (JSON)**:
  ```json
  {
    "title": "Andi & Budi Wedding",
    "date": "2026-12-12",
    "location": "Gedung Serbaguna Jakarta"
  }
  ```
* **Response (201 Created)**:
  ```json
  {
    "message": "Event created",
    "event": {
      "id": 1,
      "title": "Andi & Budi Wedding",
      "date": "2026-12-12",
      "location": "Gedung Serbaguna Jakarta",
      "is_started": false,
      "qr_code_path": null
    }
  }
  ```

### 2.3. Detail Event
* **Endpoint**: `GET /api/events/<event_id>`
* **Autentikasi**: **Wajib (Admin)**
* **Response (200 OK)**:
  ```json
  {
    "id": 1,
    "title": "Andi & Budi Wedding",
    "date": "2026-12-12",
    "location": "Gedung Serbaguna Jakarta",
    "is_started": false,
    "qr_code_path": "qrcodes/event_1.png"
  }
  ```

### 2.4. Edit Event
* **Endpoint**: `PUT /api/events/<event_id>`
* **Autentikasi**: **Wajib (Admin)**
* **Request Body (JSON)**:
  ```json
  {
    "title": "Andi & Budi Wedding Updated",
    "location": "Bali Beach Resort"
  }
  ```
* **Response (200 OK)**:
  ```json
  {
    "message": "Event updated",
    "event": {
      "id": 1,
      "title": "Andi & Budi Wedding Updated",
      "date": "2026-12-12",
      "location": "Bali Beach Resort",
      "is_started": false
    }
  }
  ```

### 2.5. Hapus Event
* **Endpoint**: `DELETE /api/events/<event_id>`
* **Autentikasi**: **Wajib (Admin)**
* **Response (200 OK)**:
  ```json
  {
    "message": "Event deleted"
  }
  ```

### 2.6. Dapatkan QR Code Event
* **Endpoint**: `GET /api/events/<event_id>/qr`
* **Autentikasi**: **Wajib (Admin)**
* **Response (200 OK)**:
  ```json
  {
    "event_id": 1,
    "qr_url": "http://localhost:5001/uploads/qrcodes/event_1_qr.png",
    "qr_path": "qrcodes/event_1_qr.png"
  }
  ```

### 2.7. Statistik Dashboard Event
* **Endpoint**: `GET /api/events/<event_id>/dashboard`
* **Autentikasi**: **Wajib (Admin)**
* **Response (200 OK)**:
  ```json
  {
    "event": {
      "id": 1,
      "title": "Andi & Budi Wedding",
      "date": "2026-12-12",
      "location": "Gedung Serbaguna Jakarta",
      "is_started": false
    },
    "stats": {
      "total_guests": 120,
      "total_photos": 45,
      "completed_quests": 30
    }
  }
  ```

---

## 3. Quest Modul (`/api/events/<event_id>/quests`)

### 3.1. List Semua Quest Event
* **Endpoint**: `GET /api/events/<event_id>/quests`
* **Autentikasi**: **Wajib (Admin)**
* **Query Parameters (Opsional)**:
  * `active=true|false` (Filter berdasarkan status aktif quest)
* **Response (200 OK)**:
  ```json
  [
    {
      "id": 1,
      "title": "Foto dengan Pengantin",
      "description": "Ambil foto bersama kedua mempelai di pelaminan",
      "order_number": 1,
      "is_active": true
    }
  ]
  ```

### 3.2. Buat Quest Baru
* **Endpoint**: `POST /api/events/<event_id>/quests`
* **Autentikasi**: **Wajib (Admin)**
* **Request Body (JSON / Multipart)**:
  ```json
  {
    "title": "Foto dengan Makanan Favorit",
    "description": "Foto makanan yang paling kamu sukai di prasmanan",
    "order_number": 2,
    "is_active": true
  }
  ```
* **Response (201 Created)**:
  ```json
  {
    "message": "Quest created",
    "quest": {
      "id": 2,
      "title": "Foto dengan Makanan Favorit",
      "description": "Foto makanan yang paling kamu sukai di prasmanan",
      "order_number": 2,
      "is_active": true
    }
  }
  ```

### 3.3. Detail Quest
* **Endpoint**: `GET /api/events/<event_id>/quests/<quest_id>`
* **Autentikasi**: **Wajib (Admin)**
* **Response (200 OK)**:
  ```json
  {
    "id": 1,
    "title": "Foto dengan Pengantin",
    "description": "Ambil foto bersama kedua mempelai di pelaminan",
    "order_number": 1,
    "is_active": true
  }
  ```

### 3.4. Edit Quest
* **Endpoint**: `PUT /api/events/<event_id>/quests/<quest_id>`
* **Autentikasi**: **Wajib (Admin)**
* **Request Body (JSON / Multipart)**:
  ```json
  {
    "title": "Foto dengan Pengantin Cantik",
    "description": "Ambil foto bersama pengantin baru"
  }
  ```
* **Response (200 OK)**:
  ```json
  {
    "message": "Quest updated",
    "quest": {
      "id": 1,
      "title": "Foto dengan Pengantin Cantik",
      "description": "Ambil foto bersama pengantin baru",
      "order_number": 1,
      "is_active": true
    }
  }
  ```

### 3.5. Hapus Quest
* **Endpoint**: `DELETE /api/events/<event_id>/quests/<quest_id>`
* **Autentikasi**: **Wajib (Admin)**
* **Response (200 OK)**:
  ```json
  {
    "message": "Quest deleted"
  }
  ```

### 3.6. Toggle Aktif Quest
* **Endpoint**: `PATCH /api/events/<event_id>/quests/<quest_id>/toggle-active`
* **Autentikasi**: **Wajib (Admin)**
* **Response (200 OK)**:
  ```json
  {
    "message": "Quest is_active set to false",
    "quest_id": 1,
    "is_active": false
  }
  ```

### 3.7. Mengurutkan Ulang Quest (Reorder)
* **Endpoint**: `PATCH /api/events/<event_id>/quests/reorder`
* **Autentikasi**: **Wajib (Admin)**
* **Request Body (JSON)**:
  ```json
  [
    { "id": 1, "order_number": 2 },
    { "id": 2, "order_number": 1 }
  ]
  ```
* **Response (200 OK)**:
  ```json
  {
    "message": "Quests reordered",
    "quests": [
      {
        "id": 2,
        "title": "Foto dengan Makanan Favorit",
        "order_number": 1,
        "is_active": true
      },
      {
        "id": 1,
        "title": "Foto dengan Pengantin",
        "order_number": 2,
        "is_active": true
      }
    ]
  }
  ```

---

## 4. Guest Modul (`/api/guest`)

### 4.1. Tamu Bergabung ke Event
* **Endpoint**: `POST /api/guest/event/<event_id>/join`
* **Autentikasi**: Tidak ada (Public)
* **Request Body (JSON)**:
  ```json
  {
    "name": "Rian"
  }
  ```
* **Response (201 Created)**:
  ```json
  {
    "message": "Welcome! You have joined the event.",
    "guest": {
      "id": 12,
      "name": "Rian",
      "event_id": 1
    },
    "event_id": 1
  }
  ```

### 4.2. Lihat Event Detail (oleh Tamu)
* **Endpoint**: `GET /api/guest/<guest_id>/event`
* **Autentikasi**: Tidak ada (Public/Berdasarkan Guest ID)
* **Response (200 OK)**:
  ```json
  {
    "event": {
      "id": 1,
      "title": "Andi & Budi Wedding",
      "date": "2026-12-12",
      "location": "Gedung Serbaguna Jakarta"
    },
    "guest": {
      "id": 12,
      "name": "Rian"
    }
  }
  ```

### 4.3. Lihat Semua Quest & Progress Tamu
* **Endpoint**: `GET /api/guest/<guest_id>/quests`
* **Autentikasi**: Tidak ada (Public/Berdasarkan Guest ID)
* **Response (200 OK)**:
  ```json
  {
    "guest": {
      "id": 12,
      "name": "Rian"
    },
    "quests": [
      {
        "quest_id": 1,
        "title": "Foto dengan Pengantin",
        "order": 1,
        "is_complete": false,
        "message": null,
        "guest_quest_id": null,
        "photos": []
      }
    ]
  }
  ```

### 4.4. Upload Foto Quest
* **Endpoint**: `POST /api/guest/<guest_id>/quests/<quest_id>/photos`
* **Autentikasi**: Tidak ada (Public/Berdasarkan Guest ID)
* **Request Body (Multipart Form-Data)**:
  * Key: `photo` (File Gambar, e.g. `.png` atau `.jpg`)
* **Response (201 Created)**:
  ```json
  {
    "message": "Photo uploaded successfully",
    "photo": {
      "id": 8,
      "guest_quest_id": 4,
      "photo_url": "http://localhost:5001/uploads/photos/g12_q1_myphoto.jpg",
      "created_at": "2026-07-17T18:36:39Z"
    }
  }
  ```
