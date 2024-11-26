import requests
from bs4 import BeautifulSoup
import pandas as pd
from unidecode import unidecode

# Baca file CSV yang berisi Title dan Link
csv_file = 'dentistry_journal_link.csv'  # Nama file CSV Anda
df_links = pd.read_csv(csv_file)

# Inisialisasi list untuk menyimpan data
data = {
    "Judul": [],
    "Abstrak": [],
    "Author": [],
    "Publisher": [],
    "Link_Artikel": [],
    "Nama_Jurnal": [],
    "Subject": []
}

# Set batas jumlah data yang ingin dikumpulkan
max_data = 700

# Variabel untuk menghitung jumlah data yang dikumpulkan
collected_data = 0

# Loop untuk memproses setiap baris (Title dan Link) dari file CSV
for index, row in df_links.iterrows():  # Menggunakan iterrows() untuk mendapatkan setiap baris
    Title = row['Title']  # Ambil Title dari CSV
    link = row['Link']    # Ambil Link dari CSV
    base_url = f"https://garuda.kemdikbud.go.id{link}?page="  # Menambahkan URL dasar
    page_number = 1
    journal_collected = 0  # Variabel untuk menghitung jumlah artikel per jurnal

    while True:
        # Buat URL untuk halaman yang sedang diproses
        url = base_url + str(page_number)
        response = requests.get(url)

        # Periksa apakah respons berhasil
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # Mencari elemen artikel
            articles = soup.find_all('div', class_='article-item')

            # Jika tidak ada artikel pada halaman, berarti halaman terakhir
            if not articles:
                break

            # Proses setiap artikel pada halaman
            for article in articles:
                # Mendapatkan judul artikel
                title_tag = article.find('a', class_='title-article').find('xmp')
                title = title_tag.text.strip() if title_tag else None

                # Mendapatkan abstrak artikel
                abstract_tag = article.find('div', class_='abstract-article').find('xmp', class_='abstract-article')
                abstract = abstract_tag.text.strip() if abstract_tag else None

                # Mendapatkan penulis artikel
                authors = article.find_all('a', class_='author-article')
                author_names = [author.find('xmp').text.strip() for author in authors]

                # Mendapatkan publisher artikel
                subtitles = article.find_all('xmp', class_='subtitle-article')
                publisher = subtitles[1].text.strip() if subtitles else None

                # Mendapatkan link artikel
                link_tag = article.find('a', class_='title-article')
                link = f"https://garuda.kemdikbud.go.id{link_tag['href']}" if link_tag else None

                # Mendapatkan nama jurnal
                journal_name = subtitles[0].text.strip() if subtitles else None

                # Mendapatkan Subject
                subjects = soup.find('div', class_="j-meta-subject").find_all('a', class_="ui tag label grey mini")
                subject_list = [subject.text.strip() for subject in subjects]

                # Membersihkan teks menggunakan Unidecode
                title = unidecode(title) if title else None
                abstract = unidecode(abstract) if abstract else None
                publisher = unidecode(publisher) if publisher else None
                journal_name = unidecode(journal_name) if journal_name else None
                subject_list = [unidecode(subject) for subject in subject_list]

                # Menyimpan data ke dalam list
                data["Judul"].append(title)
                data["Abstrak"].append(abstract)
                data["Author"].append(", ".join(author_names))
                data["Publisher"].append(publisher)
                data["Link_Artikel"].append(link)
                data["Nama_Jurnal"].append(journal_name)
                data["Subject"].append(', '.join(subject_list))

                # Menghitung jumlah artikel yang telah dikumpulkan untuk jurnal ini
                journal_collected += 1
                collected_data += 1

            # Pindah ke halaman berikutnya
            page_number += 1

        else:
            print(f"Gagal mengambil data dari {url}. Status code: {response.status_code}")
            break

        # Periksa apakah jumlah data yang dikumpulkan sudah mencapai batas
        if collected_data >= max_data:
            break

    # Cetak jumlah data yang dikumpulkan untuk jurnal ini
    print(f"Jumlah data yang dikumpulkan dari jurnal {Title}: {journal_collected} artikel.")

    # Hentikan seluruh proses jika batas data tercapai
    if collected_data >= max_data:
        print(f"Sudah mengumpulkan {collected_data} data, program berhenti.")
        break

# Konversi ke DataFrame
df = pd.DataFrame(data)

# Simpan ke file CSV
df.to_csv('file_output.csv', index=False, encoding='utf-8', sep=';')

# Tampilkan data
print(df)
