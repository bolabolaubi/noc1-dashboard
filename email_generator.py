def make_email(data):
    no_tiket = data.get("No Ticket", "-")
    device = data.get("Device", "-")
    insiden = data.get("Insiden", "-")
    waktu_down = data.get("Waktu Down Time", "-")

    subject = f"[{no_tiket}] [ ] ({device}) #Notifikasi Mitra Teknologi Andalan Utama"

    body = f"""\
Pelanggan yang terhormat,

Terima kasih telah menggunakan layanan Mitra Teknologi Andalan Utama.

Kami ingin menginformasikan kepada Anda tentang **Gangguan pada Layanan Jaringan** Anda.
Berikut ini adalah rinciannya:

Nomor Tiket        : {no_tiket}
Type               : 
Layanan yang terdampak : {data.get("Layanan", "-")}
Insiden            : {insiden}
Waktu gangguan     : {waktu_down}
Waktu perbaikan    : 
Action             : 
Penyebab gangguan  : 

Jika Anda memiliki pertanyaan atau masalah terkait pemberitahuan ini,
silakan hubungi tim kami melalui email ini dan lampirkan nomor tiket.

Hormat kami,  
Tim NOC  
PT. Mitra Teknologi Andalan Utama
"""

    return f"Subject: {subject}\n\n{body}"
