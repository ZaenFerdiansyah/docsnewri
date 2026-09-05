# Tutorial SR-IOV & TRex Network Testing

100G WAN Testing: Jakarta ↔ Denpasar

|               |                               |
|---------------|-------------------------------|
| **Informasi** | **Detail**                    |
| Platform      | VMware ESXi 6.7               |
| NIC           | HPE ConnectX-4 (MT27700) 100G |
| Server        | Dell PowerEdge R620           |
| Tool          | Cisco TRex Traffic Generator  |
| Tanggal       | 30 April 2026                 |

## 1. Overview & Topologi

### 1.1 Topologi Jaringan

Berikut adalah topologi yang digunakan dalam tutorial ini:

|                           |                           |
|---------------------------|---------------------------|
| **Mesin A (Jakarta)**     | **Mesin B (Denpasar)**    |
| ESXi 6.7 - Dell R620      | ESXi 6.7 - Dell R620      |
| HPE ConnectX-4 100G       | HPE ConnectX-4 100G       |
| TRex Traffic Generator    | Router/DUT (IP Forwarder) |
| 2x VF SR-IOV (eth1, eth2) | 2x VF SR-IOV (eth1, eth2) |

Diagram alur traffic:

> Mesin A (TRex) Mesin B (Router/DUT)
>
> eth0 = Management (172.16.x.x) eth0 = Management
>
> eth1 VF0 \[192.168.10.5\] ---- Link 1 ----\> \[192.168.10.1\] eth1 VF0
>
> eth2 VF1 \[192.168.20.5\] \<--- Link 2 ----- \[192.168.20.1\] eth2 VF1
>
> TRex generate traffic: 16.0.0.0/16 \<-\> 48.0.0.0/16

### 1.2 Konsep SR-IOV

SR-IOV (Single Root I/O Virtualization) memungkinkan 1 NIC fisik dibagi menjadi beberapa Virtual Functions (VF) yang dapat diakses langsung oleh VM dengan performa mendekati bare metal.

|                   |             |                |
|-------------------|-------------|----------------|
| **Fitur**         | **VMXNET3** | **SR-IOV VF**  |
| Lewat ESXi Kernel | Ya          | Tidak (bypass) |
| Max Throughput    | ~40-50 Gbps | Mendekati 100G |
| DPDK Support      | Terbatas    | Full           |
| Cocok untuk TRex  | Tidak       | Ya             |

## 2. Setup SR-IOV di ESXi Jakarta (Mesin A)

### 2.1 Enable SR-IOV di Firmware NIC via mlxconfig

Langkah ini adalah yang paling kritis. SR-IOV harus di-enable di level firmware NIC terlebih dahulu.

1.  SSH ke ESXi Jakarta:

> ssh root@\<IP-ESXi-Jakarta\>

2.  Start MFT dan cek device:

> /opt/mellanox/bin/mst start
>
> /opt/mellanox/bin/mst status
>
> \# Catat nama device, contoh: mt4115_pciconf1

3.  Cek status SR-IOV di firmware:

> /opt/mellanox/bin/mlxconfig -d mt4115_pciconf1 query \| grep -i 'SRIOV\\NUM_OF_VFS'
>
> \# Output yang diharapkan:
>
> \# SRIOV_EN False(0) \<- belum aktif
>
> \# NUM_OF_VFS 0

4.  Enable SR-IOV di firmware NIC:

> /opt/mellanox/bin/mlxconfig -d mt4115_pciconf1 set SRIOV_EN=1 NUM_OF_VFS=2
>
> \# Ketik 'y' saat diminta konfirmasi

5.  Verifikasi perubahan:

> /opt/mellanox/bin/mlxconfig -d mt4115_pciconf1 query \| grep -i 'SRIOV\\NUM_OF_VFS'
>
> \# Output yang diharapkan:
>
> \# SRIOV_EN True(1)
>
> \# NUM_OF_VFS 2

### 2.2 Enable SR-IOV di BIOS Dell via iDRAC

6.  SSH ke iDRAC:

> ssh root@\<IP-iDRAC\>

7.  Cek status SR-IOV:

> racadm get BIOS.IntegratedDevices.SriovGlobalEnable

8.  Enable SR-IOV jika belum aktif:

> racadm set BIOS.IntegratedDevices.SriovGlobalEnable Enabled
>
> racadm jobqueue create BIOS.Setup.1-1
>
> racadm serveraction powercycle

### 2.3 Set Parameter max_vfs di Driver ESXi

9.  SSH ke ESXi Jakarta:

> ssh root@\<IP-ESXi-Jakarta\>

10. Set parameter max_vfs:

> esxcli system module parameters set -m nmlx5_core -p 'max_vfs=2'
>
> \# Verifikasi:
>
> esxcli system module parameters list -m nmlx5_core \| grep max_vfs

11. Power cycle server:

> \# Via iDRAC
>
> ssh root@\<IP-iDRAC\>
>
> racadm serveraction powercycle

### 2.4 Verifikasi SR-IOV Aktif

> \# Cek SR-IOV list
>
> esxcli network sriovnic list
>
> \# Output yang diharapkan:
>
> \# Name PCI Device Driver Link Speed
>
> \# vmnic5 0000:42:00.0 nmlx5_core Up 100000
>
> \# Cek VF tersedia
>
> esxcli network sriovnic vf list -n vmnic5
>
> \# Output yang diharapkan:
>
> \# VF ID Active PCI Address
>
> \# 0 false 00000:066:00.1
>
> \# 1 false 00000:066:00.2
>
> \# Cek di PCI list
>
> esxcli hardware pci list \| grep -i '42:0'
>
> \# Harusnya muncul:
>
> \# 0000:42:00.0 (Physical Function)
>
> \# 0000:42:00.1 (VF0)
>
> \# 0000:42:00.2 (VF1)

## 3. Assign VF ke VM Mesin A di vSphere

|                                                                                         |
|-----------------------------------------------------------------------------------------|
| *PENTING: VM Mesin A harus dalam kondisi Power Off sebelum menambahkan SR-IOV adapter.* |

12. Di vSphere Client, klik kanan VM Mesin A -\> Edit Settings

13. Klik 'Add New Device' -\> 'PCI Device'

14. Pilih: 0000:42:00.1 \| MT27700 Family \[ConnectX-4 Virtual Function\] (VF0)

15. Klik 'Add New Device' lagi -\> 'PCI Device'

16. Pilih: 0000:42:00.2 \| MT27700 Family \[ConnectX-4 Virtual Function\] (VF1)

17. Klik OK dan Power On VM Mesin A

### 3.1 Verifikasi di Dalam VM Mesin A

> \# Cek interface baru
>
> ip addr show
>
> \# Harusnya muncul:
>
> \# ens192 \<- VF0 (TRex Port 0)
>
> \# ens224 \<- VF1 (TRex Port 1)
>
> \# Cek PCI device
>
> lspci \| grep -i mellanox
>
> \# Output:
>
> \# 0b:00.0 Ethernet controller: Mellanox Technologies MT27700 Family \[ConnectX-4 Virtual Function\]
>
> \# 13:00.0 Ethernet controller: Mellanox Technologies MT27700 Family \[ConnectX-4 Virtual Function\]
>
> \# Cek driver
>
> ethtool -i ens192
>
> ethtool -i ens224
>
> \# Driver: mlx5_core

## 4. Setup SR-IOV di ESXi Denpasar (Mesin B)

Lakukan langkah yang SAMA persis seperti Bab 2 dan 3 untuk ESXi Denpasar (Mesin B).

|                                                                                                                                                                                                                                                                                 |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| *Ringkasan langkah di ESXi Denpasar: 1. mlxconfig set SRIOV_EN=1 NUM_OF_VFS=2 2. racadm set BIOS.IntegratedDevices.SriovGlobalEnable Enabled 3. esxcli system module parameters set -m nmlx5_core -p 'max_vfs=2' 4. Power cycle server 5. Assign 2 VF ke VM Mesin B di vSphere* |

### 4.1 Konfigurasi Mesin B sebagai Router

Mesin B tidak menjalankan TRex. Mesin B hanya dikonfigurasi sebagai router yang meneruskan traffic antara dua interface.

18. Enable IP forwarding permanen:

> echo 'net.ipv4.ip_forward=1' \>\> /etc/sysctl.conf
>
> sysctl -p
>
> \# Verifikasi:
>
> sysctl net.ipv4.ip_forward
>
> \# Output: net.ipv4.ip_forward = 1

19. Set IP di interface data (sesuaikan nama interface):

> \# Set IP di VF0 dan VF1 Mesin B
>
> ip addr add 192.168.10.1/24 dev ens192
>
> ip addr add 192.168.20.1/24 dev ens224
>
> ip link set ens192 up
>
> ip link set ens224 up

20. Tambahkan static route ke subnet virtual TRex:

> \# Route untuk subnet client virtual TRex (Port 0)
>
> ip route add 16.0.0.0/16 via 192.168.10.5
>
> \# Route untuk subnet server virtual TRex (Port 1)
>
> ip route add 48.0.0.0/16 via 192.168.20.5

21. Buat konfigurasi permanen (Ubuntu/Netplan):

> \# Edit /etc/netplan/01-netcfg.yaml
>
> network:
>
> version: 2
>
> ethernets:
>
> ens192:
>
> addresses: \[192.168.10.1/24\]
>
> routes:
>
> \- to: 16.0.0.0/16
>
> via: 192.168.10.5
>
> ens224:
>
> addresses: \[192.168.20.1/24\]
>
> routes:
>
> \- to: 48.0.0.0/16
>
> via: 192.168.20.5
>
> netplan apply

## 5. Install & Konfigurasi TRex di Mesin A

### 5.1 Install TRex

> \# Buat direktori dan download TRex
>
> sudo mkdir -p /opt/trex
>
> cd /opt/trex
>
> sudo wget --no-cache https://trex-tgn.cisco.com/trex/release/latest
>
> sudo tar -xzvf latest
>
> sudo rm latest
>
> \# Masuk ke direktori TRex
>
> cd /opt/trex/v3.\*/
>
> \# Cek versi
>
> ls /opt/trex/

### 5.2 Cek PCI Address Interface

> cd /opt/trex/v3.\*/
>
> sudo ./dpdk_setup_ports.py -t
>
> \# Catat PCI address untuk ens192 dan ens224
>
> \# Contoh:
>
> \# ID \| PCI \| Name \| Driver
>
> \# 0 \| 0b:00.0 \| ens192\| mlx5_core
>
> \# 1 \| 13:00.0 \| ens224\| mlx5_core

### 5.3 Buat Konfigurasi TRex

> sudo nano /etc/trex_cfg.yaml

Isi file /etc/trex_cfg.yaml:

> \- version: 2
>
> interfaces: \['0000:0b:00.0', '0000:13:00.0'\]
>
> port_info:
>
> \- ip: 192.168.10.5 \# IP TRex Port 0 (ens192)
>
> default_gw: 192.168.10.1 \# IP eth1 Mesin B
>
> \- ip: 192.168.20.5 \# IP TRex Port 1 (ens224)
>
> default_gw: 192.168.20.1 \# IP eth2 Mesin B
>
> platform:
>
> master_thread_id: 0
>
> latency_thread_id: 1
>
> dual_if:
>
> \- socket: 0
>
> threads: \[2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19\]

|                                                                                                                    |
|--------------------------------------------------------------------------------------------------------------------|
| *Catatan: Sesuaikan PCI address (0000:0b:00.0 dan 0000:13:00.0) dengan output dpdk_setup_ports.py di sistem kamu.* |

## 6. Menjalankan Test TRex

### 6.1 Test Pertama - Multiplier Rendah

Selalu mulai dengan multiplier rendah untuk memastikan traffic berjalan dengan benar sebelum menaikkan ke 100G.

> cd /opt/trex/v3.\*/
>
> \# Test pertama - 30 detik, multiplier 1x
>
> sudo ./t-rex-64 -f cap2/http_simple.yaml -d 30 -m 1 -c 4 --nc
>
> \# Keterangan parameter:
>
> \# -f : traffic profile yang digunakan
>
> \# -d : durasi test (detik)
>
> \# -m : multiplier (1 = baseline)
>
> \# -c : jumlah core yang digunakan
>
> \# --nc: no cleanup setelah test

### 6.2 Monitor Traffic Real-time

Buka terminal baru ke Mesin A dan jalankan TRex console:

> cd /opt/trex/v3.\*/
>
> sudo ./trex-console
>
> \# Di dalam TRex console:
>
> trex\> tui \# Tampilan real-time (tekan 'q' untuk keluar)
>
> trex\> stats \# Statistik per port
>
> trex\> portattr \# Informasi port
>
> trex\> quit \# Keluar dari console

### 6.3 Naikkan Traffic Bertahap Menuju 100G

> \# Tahap 1: 10x multiplier
>
> sudo ./t-rex-64 -f cap2/http_simple.yaml -d 60 -m 10 -c 8 --nc
>
> \# Tahap 2: 100x multiplier
>
> sudo ./t-rex-64 -f cap2/http_simple.yaml -d 60 -m 100 -c 16 --nc
>
> \# Tahap 3: 500x multiplier
>
> sudo ./t-rex-64 -f cap2/http_simple.yaml -d 60 -m 500 -c 20 --nc
>
> \# Tahap 4: Maximum (mendekati 100G)
>
> sudo ./t-rex-64 -f cap2/http_simple.yaml -d 60 -m 1000 -c 20 --nc

### 6.4 Memahami Output TRex

|           |                           |                    |
|-----------|---------------------------|--------------------|
| **Field** | **Keterangan**            | **Target**         |
| Tx bps    | Bandwidth yang dikirim    | Mendekati 100 Gbps |
| Rx bps    | Bandwidth yang diterima   | Sama dengan Tx bps |
| Tx pps    | Packet per second dikirim | Semaksimal mungkin |
| Drop      | Packet yang hilang        | 0 (nol)            |
| Latency   | Waktu round-trip          | Serendah mungkin   |

## 7. Troubleshooting

### 7.1 SR-IOV Tidak Muncul Setelah Setup

|                                     |                           |                                      |
|-------------------------------------|---------------------------|--------------------------------------|
| **Gejala**                          | **Penyebab**              | **Solusi**                           |
| esxcli network sriovnic list kosong | SRIOV_EN=0 di firmware    | mlxconfig set SRIOV_EN=1             |
| esxcli network sriovnic list kosong | BIOS SR-IOV disabled      | racadm set SriovGlobalEnable Enabled |
| esxcli network sriovnic list kosong | max_vfs tidak di-set      | esxcli system module parameters set  |
| VF tidak muncul di vSphere          | Perlu power cycle         | Power cycle server via iDRAC         |
| SR-IOV menu tidak ada di vSphere    | Driver lama/tidak support | Update driver nmlx5_core             |

### 7.2 TRex Error Saat Start

|                          |                                             |
|--------------------------|---------------------------------------------|
| **Error**                | **Solusi**                                  |
| DPDK init failed         | Cek PCI address di trex_cfg.yaml            |
| ARP failed / no response | Pastikan Mesin B up dan IP forwarding aktif |
| Permission denied        | Jalankan dengan sudo                        |
| Port not found           | Cek interface dengan dpdk_setup_ports.py -t |

### 7.3 Command Referensi Cepat

> \# Cek status SR-IOV firmware NIC
>
> /opt/mellanox/bin/mlxconfig -d mt4115_pciconf1 query \| grep -i 'SRIOV\\NUM_OF_VFS'
>
> \# Cek SR-IOV aktif di ESXi
>
> esxcli network sriovnic list
>
> esxcli network sriovnic vf list -n vmnic5
>
> \# Cek VF di PCI
>
> esxcli hardware pci list \| grep -i '42:0'
>
> \# Cek parameter driver
>
> esxcli system module parameters list -m nmlx5_core \| grep max_vfs
>
> \# Cek log SR-IOV
>
> grep -i sriov /var/log/vmkernel.log \| tail -20
>
> \# Verifikasi IP forwarding Mesin B
>
> sysctl net.ipv4.ip_forward
>
> \# Verifikasi route di Mesin B
>
> ip route show \| grep -i '16.0\\48.0'

## 8. Ringkasan Langkah

|                                                                                                         |
|---------------------------------------------------------------------------------------------------------|
| *Ikuti checklist berikut secara berurutan untuk memastikan semua langkah sudah dilakukan dengan benar.* |

### Checklist ESXi Jakarta & Denpasar (Lakukan di Keduanya)

|        |                                              |             |              |
|--------|----------------------------------------------|-------------|--------------|
| **No** | **Langkah**                                  | **Jakarta** | **Denpasar** |
| 1      | Update firmware NIC (mlxconfig SRIOV_EN=1)   | \[ \]       | \[ \]        |
| 2      | Enable SR-IOV di BIOS (iDRAC racadm)         | \[ \]       | \[ \]        |
| 3      | Set max_vfs=2 di driver nmlx5_core           | \[ \]       | \[ \]        |
| 4      | Power cycle server                           | \[ \]       | \[ \]        |
| 5      | Verifikasi esxcli network sriovnic list      | \[ \]       | \[ \]        |
| 6      | Assign 2x VF ke VM via vSphere (PCI Device)  | \[ \]       | \[ \]        |
| 7      | Verifikasi VF terdeteksi di dalam VM (lspci) | \[ \]       | \[ \]        |

### Checklist Konfigurasi VM

|        |                                           |             |             |
|--------|-------------------------------------------|-------------|-------------|
| **No** | **Langkah**                               | **Mesin A** | **Mesin B** |
| 1      | Install TRex                              | \[ \]       | N/A         |
| 2      | Buat /etc/trex_cfg.yaml                   | \[ \]       | N/A         |
| 3      | Enable IP forwarding                      | N/A         | \[ \]       |
| 4      | Set IP di eth1 dan eth2                   | N/A         | \[ \]       |
| 5      | Tambah static route (16.0/16 dan 48.0/16) | N/A         | \[ \]       |
| 6      | Jalankan TRex test pertama (m=1)          | \[ \]       | N/A         |
| 7      | Naikkan traffic bertahap ke 100G          | \[ \]       | N/A         |

|                                                                                                                               |
|-------------------------------------------------------------------------------------------------------------------------------|
| *Selamat! Jika semua checklist sudah selesai, TRex sudah berjalan dan traffic 100G sudah ditest antara Jakarta dan Denpasar.* |
