# Praktikum Protokol IoT: HTTP, MQTT, CoAP

Paket praktikum lengkap untuk mempelajari dan membandingkan protokol komunikasi IoT (HTTP, MQTT, CoAP) dengan implementasi nyata dan analisis performa.

## 📋 Daftar Isi
- [Penjelasan Protokol](#penjelasan-protokol)
- [Struktur Proyek](#struktur-proyek)
- [Prasyarat](#prasyarat)
- [Instalasi](#instalasi)
- [Cara Menjalankan](#cara-menjalankan)
- [Benchmark](#benchmark)
- [Testing](#testing)

---

## 🔍 Penjelasan Protokol

### HTTP (HyperText Transfer Protocol)
**Transport:** TCP  
**Port Default:** 80 (HTTP), 443 (HTTPS)  
**Overhead:** Tinggi (~200-500 bytes header)  
**State:** Stateless (setiap request independen)  
**QoS:** Tidak ada (bergantung TCP reliability)

**Karakteristik:**
- Request-response model (client harus meminta data)
- Header verbose (banyak metadata)
- Mudah untuk debugging (text-based)
- Firewall-friendly (port 80/443 biasanya terbuka)
- Cocok untuk REST API dan integrasi web

**Kapan Menggunakan HTTP:**
- Integrasi dengan sistem web existing
- Data query yang tidak periodik
- Membutuhkan caching dan CDN
- Infrastruktur sudah familiar dengan REST

### MQTT (Message Queuing Telemetry Transport)
**Transport:** TCP  
**Port Default:** 1883 (non-TLS), 8883 (TLS), 9001 (WebSocket)  
**Overhead:** Rendah (fixed header 2 bytes + variable header)  
**State:** Stateful (persistent connection)  
**QoS:** 3 level (0, 1, 2)

**Karakteristik:**
- Publish-subscribe model (broker sebagai intermediary)
- Lightweight protocol (dirancang untuk IoT)
- Support retained messages (last known good value)
- Last Will & Testament (deteksi koneksi putus)
- Topic-based filtering

**QoS Levels:**
- **QoS 0:** At most once (fire and forget)
- **QoS 1:** At least once (acknowledged delivery, duplikasi mungkin)
- **QoS 2:** Exactly once (4-way handshake, no duplikasi)

**Kapan Menggunakan MQTT:**
- Telemetri sensor berkala
- Battery-powered devices
- Network tidak stabil (auto-reconnect)
- Publish ke banyak subscriber
- Real-time monitoring

### CoAP (Constrained Application Protocol)
**Transport:** UDP (dapat pakai TCP/DTLS)  
**Port Default:** 5683 (non-TLS), 5684 (DTLS)  
**Overhead:** Sangat rendah (4 bytes header)  
**State:** Stateless (seperti HTTP)  
**QoS:** 2 level (CON/NON)

**Karakteristik:**
- RESTful model (GET/POST/PUT/DELETE)
- Binary protocol (compact)
- Observe pattern (push notification seperti pub-sub)
- Multicast support
- Dirancang untuk constrained devices (RAM <64KB)

**Kapan Menggunakan CoAP:**
- Jaringan constrained (bandwidth rendah)
- Perangkat dengan resource terbatas
- Multicast diperlukan
- Latency critical (UDP lebih cepat)
- Mesh network / LoRaWAN

---

## 📁 Struktur Proyek

```
iot-protocols-lab/
├── README.md                    # Dokumentasi ini
├── env.example                  # Template konfigurasi
├── requirements.txt             # Dependencies Python
├── Makefile                     # Shortcut commands
├── broker/
│   └── docker-compose.yml       # MQTT broker (Mosquitto)
├── mqtt/
│   ├── mqtt_publisher.py        # MQTT publisher
│   └── mqtt_subscriber.py       # MQTT subscriber
├── http/
│   ├── http_server.py           # HTTP server (Flask)
│   └── http_client.py           # HTTP client
├── coap/
│   ├── coap_server.py           # CoAP server
│   └── coap_client.py           # CoAP client
├── benchmark/
│   └── benchmark_runner.py      # Script benchmark otomatis
├── tools/
│   └── payload_gen.py           # Generator payload
├── tests/
│   └── smoke_test.py            # Uji end-to-end
├── results/
│   ├── metrics.csv              # Hasil benchmark
│   └── *.png                    # Grafik visualisasi
└── report.md                    # Laporan analisis
```

---

## 🛠 Prasyarat

- **Python:** 3.10 atau lebih baru
- **Docker & Docker Compose:** Untuk MQTT broker
- **OS:** Linux/macOS (optimal), Windows dengan WSL2

---

## 📦 Instalasi

### 1. Clone atau Extract Proyek
```bash
mkdir iot-protocols-lab
cd iot-protocols-lab
```

### 2. Buat Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables
```bash
cp env.example .env
# Edit .env sesuai kebutuhan
```

### 5. Jalankan MQTT Broker
```bash
docker compose -f broker/docker-compose.yml up -d
```

Verifikasi broker berjalan:
```bash
docker compose -f broker/docker-compose.yml ps
```

---

## 🚀 Cara Menjalankan

### A. Uji MQTT

**Terminal 1 - Subscriber:**
```bash
python mqtt/mqtt_subscriber.py
```

**Terminal 2 - Publisher:**
```bash
# Kirim 10 pesan dengan QoS 1, payload 1024 bytes
python mqtt/mqtt_publisher.py --qos 1 --count 10 --payload 1024

# Kirim retained message
python mqtt/mqtt_publisher.py --retain --count 1 --payload 256

# Kirim dengan last will
python mqtt/mqtt_publisher.py --will "Client disconnected" --count 5
```

**Parameter Publisher:**
- `--qos`: 0, 1, atau 2 (default: 0)
- `--count`: Jumlah pesan (default: 10)
- `--payload`: Ukuran payload bytes (default: 128)
- `--retain`: Aktifkan retained message
- `--will`: Pesan last will & testament
- `--interval`: Delay antar pesan (detik, default: 0.1)

### B. Uji HTTP

**Terminal 1 - Server:**
```bash
python http/http_server.py
```

**Terminal 2 - Client:**
```bash
# Kirim 100 request dengan payload 1KB
python http/http_client.py --count 100 --payload 1024

# Kirim dengan interval 0.5 detik
python http/http_client.py --count 50 --interval 0.5
```

**Parameter Client:**
- `--count`: Jumlah request (default: 10)
- `--payload`: Ukuran payload bytes (default: 128)
- `--interval`: Delay antar request (detik, default: 0.1)

### C. Uji CoAP

**Terminal 1 - Server:**
```bash
python coap/coap_server.py
```

**Terminal 2 - Client:**
```bash
# Kirim 100 request dengan payload 1KB
python coap/coap_client.py --count 100 --payload 1024

# Confirmable messages (CON)
python coap/coap_client.py --confirmable --count 50
```

**Parameter Client:**
- `--count`: Jumlah request (default: 10)
- `--payload`: Ukuran payload bytes (default: 128)
- `--confirmable`: Gunakan CON (default: NON)
- `--interval`: Delay antar request (detik, default: 0.1)

---

## 📊 Benchmark

### Menjalankan Benchmark Lengkap

```bash
# Benchmark semua protokol dengan semua skenario
python benchmark/benchmark_runner.py --all --output results/metrics.csv

# Benchmark protokol tertentu
python benchmark/benchmark_runner.py --protocols http mqtt --output results/metrics.csv

# Benchmark dengan payload tertentu
python benchmark/benchmark_runner.py --payloads 1024 10240 --all

# Custom iterations
python benchmark/benchmark_runner.py --all --iterations 10
```

**Parameter Benchmark:**
- `--all`: Jalankan semua protokol
- `--protocols`: Pilih protokol (http, mqtt, coap)
- `--payloads`: Ukuran payload dalam bytes (default: 32, 1024, 10240)
- `--scenarios`: Kondisi jaringan (normal, high_latency, jittery)
- `--iterations`: Jumlah ulangan per skenario (default: 5)
- `--output`: File output CSV (default: results/metrics.csv)

### Skenario Jaringan

1. **Normal:** Kondisi jaringan ideal (tanpa delay tambahan)
2. **High Latency:** Tambahan delay ±150ms (simulasi jaringan jarak jauh)
3. **Jittery:** Variasi delay ±50ms random (simulasi jaringan tidak stabil)

### Metrik yang Diukur

- **Latency:** p50, p95, max (milliseconds)
- **Throughput:** Pesan per detik
- **Loss Rate:** Persentase pesan hilang
- **Payload Size:** Rata-rata ukuran data
- **Overhead:** Header dan metadata protokol
- **CPU Usage:** Konsumsi CPU client & server

### Output

Hasil benchmark disimpan di:
- `results/metrics.csv`: Data mentah dalam format CSV
- `results/latency_comparison.png`: Grafik perbandingan latensi
- `results/throughput_comparison.png`: Grafik perbandingan throughput
- `results/overhead_comparison.png`: Grafik overhead protokol

---

## 🧪 Testing

### Smoke Test (Verifikasi End-to-End)

```bash
# Pastikan broker MQTT sudah berjalan
docker compose -f broker/docker-compose.yml up -d

# Jalankan smoke test
python tests/smoke_test.py
```

Smoke test akan:
1. Verifikasi MQTT publish-subscribe
2. Verifikasi HTTP request-response
3. Verifikasi CoAP request-response
4. Melaporkan status PASS/FAIL untuk setiap protokol

---

## 🔧 Troubleshooting

### MQTT Broker Tidak Terhubung
```bash
# Cek status container
docker compose -f broker/docker-compose.yml ps

# Lihat logs
docker compose -f broker/docker-compose.yml logs

# Restart broker
docker compose -f broker/docker-compose.yml restart
```

### Port Sudah Digunakan
Edit file `.env` dan ubah port yang konflik:
```env
MQTT_PORT=1884  # Ubah dari 1883
HTTP_PORT=8081  # Ubah dari 8080
COAP_PORT=5684  # Ubah dari 5683
```

### Permission Denied (Docker)
```bash
# Tambahkan user ke group docker
sudo usermod -aG docker $USER
# Logout dan login kembali
```

### CoAP Client Error
CoAP menggunakan UDP, pastikan firewall tidak memblokir:
```bash
# Linux
sudo ufw allow 5683/udp
```

---

## 🧹 Cleanup

```bash
# Stop MQTT broker
docker compose -f broker/docker-compose.yml down

# Hapus hasil benchmark
make clean

# Atau manual
rm -rf results/*.csv results/*.png
```

---

## 📖 Referensi

- [MQTT Specification v5.0](https://docs.oasis-open.org/mqtt/mqtt/v5.0/mqtt-v5.0.html)
- [RFC 7252 - CoAP](https://datatracker.ietf.org/doc/html/rfc7252)
- [HTTP/1.1 RFC 2616](https://datatracker.ietf.org/doc/html/rfc2616)
- [Eclipse Mosquitto](https://mosquitto.org/)
- [Paho MQTT Python](https://www.eclipse.org/paho/index.php?page=clients/python/index.php)
- [aiocoap Documentation](https://aiocoap.readthedocs.io/)

---

## 📝 Lisensi

Proyek ini dibuat untuk keperluan edukasi. Silakan digunakan dan dimodifikasi sesuai kebutuhan pembelajaran.

---

