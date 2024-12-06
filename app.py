from flask import Flask, render_template, request, redirect, url_for, flash
from supabase import create_client, Client
import pandas as pd
import pytz
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secret_key'  # Flash mesajları için gizli anahtar

# Supabase bilgileri
url = "https://ezyhoocwfrocaqsehler.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV6eWhvb2N3ZnJvY2Fxc2VobGVyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjcyOTkzOTUsImV4cCI6MjA0Mjg3NTM5NX0.3A2pCuleW0RnGIlCaM5pALWw8fB_KW_y2-qsIJ1_FJI"
supabase_DB = "siparislistesi"
supabase: Client = create_client(url, key)

turkey_tz = pytz.timezone('Europe/Istanbul')

def get_current_time():
    return datetime.now(turkey_tz).strftime("%Y-%m-%d %H:%M:%S")

@app.route('/')
def index():
    data = supabase.table(supabase_DB).select("*").eq("siparis_durumu", "1").order("id", desc=False).execute()
    siparisler = pd.DataFrame(data.data)
    return render_template('index.html', siparisler=siparisler.to_dict(orient='records'))

@app.route('/add_order', methods=['GET', 'POST'])
def add_order():
    if request.method == 'POST':
        bilgiler = request.form['bilgiler']
        lines = bilgiler.title().split('\n')
        iller = {'Adana': ['Aladağ', 'Ceyhan', 'Çukurova', 'Feke', 'İmamoğlu', 'Karaisalı', 'Karataş', 'Kozan']}

        if len(lines) >= 6:
            isim_soyisim = lines[0]
            adres_bilgisi = lines[1]
            ilce_il = lines[2].split()

            if len(ilce_il) == 2:
                ilce = ilce_il[0]
                il = ilce_il[1]
                telefon = lines[3]
                ucret = lines[4]
                urun_bilgisi = '\n'.join(lines[6:])
            else:
                flash('Adres bilgileri hatalı.', 'danger')
                return redirect(url_for('add_order'))

            telefon = telefon.replace(" ", "")
            if il not in iller:
                flash(f'İl doğru değil: {il}', 'warning')
                return redirect(url_for('add_order'))

            if ilce not in iller[il]:
                flash(f'İlçe doğru değil: {ilce}', 'warning')
                return redirect(url_for('add_order'))

            if len(telefon) != 11:
                flash(f'Telefon numarası hatalı: {telefon}', 'danger')
                return redirect(url_for('add_order'))

            siparis = {
                'tarih': get_current_time(),
                'İSİM SOYİSİM': isim_soyisim,
                'İLÇE': ilce,
                'İL': il,
                'ADRES': adres_bilgisi,
                'TELEFON': telefon,
                'TUTAR': ucret,
                'ÜRÜN': urun_bilgisi,
                'siparis_durumu': '1'
            }

            response = supabase.table(supabase_DB).insert(siparis).execute()
            flash('Sipariş başarıyla kaydedildi.', 'success')
            return redirect(url_for('index'))

    return render_template('add_order.html')

@app.route('/delete_order/<int:order_id>', methods=['POST'])
def delete_order(order_id):
    response = supabase.table(supabase_DB).delete().eq("id", order_id).execute()
    flash('Sipariş başarıyla silindi.', 'success')
    return redirect(url_for('index'))

@app.route('/update_order/<int:order_id>', methods=['GET', 'POST'])
def update_order(order_id):
    if request.method == 'POST':
        isim_soyisim = request.form['isim_soyisim']
        adres = request.form['adres']
        il = request.form['il']
        ilce = request.form['ilce']
        telefon = request.form['telefon']
        tutar = request.form['tutar']
        urun = request.form['urun']

        update_data = {
            'İSİM SOYİSİM': isim_soyisim,
            'ADRES': adres,
            'İL': il,
            'İLÇE': ilce,
            'TELEFON': telefon,
            'TUTAR': tutar,
            'ÜRÜN': urun
        }

        response = supabase.table(supabase_DB).update(update_data).eq("id", order_id).execute()
        flash('Sipariş başarıyla güncellendi.', 'success')
        return redirect(url_for('index'))

    siparis = supabase.table(supabase_DB).select("*").eq("id", order_id).execute()
    return render_template('update_order.html', siparis=siparis.data[0])

if __name__ == '__main__':
    app.run(debug=True)
