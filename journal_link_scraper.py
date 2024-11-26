import requests
from bs4 import BeautifulSoup
import pandas as pd

# URL target tanpa nomor halaman
base_url = "https://garuda.kemdikbud.go.id/area/index/85?page="

# List untuk menyimpan data jurnal (judul dan link)
journals = []

# Daftar kata-kata yang tidak boleh ada dalam judul jurnal (ubah ke lowercase)
excluded_keywords = ['abdi', 'pengabdian', 'masyarakat']

# Loop untuk memproses beberapa halaman
page_number = 1
while True:
    # Buat URL untuk halaman yang sedang diproses
    url = base_url + str(page_number)
    response = requests.get(url)

    # Periksa apakah respons berhasil
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Mencari semua elemen jurnal (tag <tr>)
        articles = soup.find_all('tr')  # Pada kode Anda, artikel ada dalam tag <tr>

        # Jika tidak ada artikel pada halaman, berarti halaman terakhir
        if not articles:
            break

        # Ambil data dari setiap artikel di halaman
        for article in articles:
            # Mendapatkan link artikel dan judul
            link_tag = article.find('a', class_='title-journal')  # Gunakan kelas yang sesuai untuk link jurnal
            if link_tag:
                title = link_tag.get_text(strip=True)  # Mendapatkan teks dari judul jurnal
                # Ubah judul dan kata-kata yang dicek menjadi huruf kecil
                title_lower = title.lower()

                # Cek apakah judul jurnal mengandung kata yang tidak diinginkan (juga dalam huruf kecil)
                if not any(keyword.lower() in title_lower for keyword in excluded_keywords):
                    link = link_tag['href']
                    # Simpan judul dan link jurnal ke dalam list
                    journals.append({"Title": title, "Link": link})

        # Pindah ke halaman berikutnya
        page_number += 1
    else:
        print(f"Failed to retrieve page {page_number}")
        break

# Membuat DataFrame untuk menyimpan dan menampilkan hasil
df = pd.DataFrame(journals)

# Menyimpan DataFrame ke dalam file CSV
df.to_csv('dentistry_journal_link.csv', index=False, encoding='utf-8')

# Menampilkan pesan jika berhasil
print("Data berhasil disimpan dalam 'dentistry_journal_link.csv'")
