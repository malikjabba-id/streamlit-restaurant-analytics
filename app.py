import pandas as pd
import plotly.express as px
import streamlit as st

# Konfigurasi Tampilan Halaman
st.set_page_config(
    page_title="Dashboard Penjualan Restoran", page_icon="🍽️", layout="wide"
)

# Fungsi untuk Membaca Data Excel
@st.cache_data
def load_data():
  file_path = "Soal_05_Dataset_05_Restoran_1000_Transaksi (1).xlsx"
  df = pd.read_excel(file_path, sheet_name="Dataset Transaksi")

  # Bersihkan baris kosong jika ada
  df = df.dropna(
      subset=["id_transaksi", "tanggal", "produk", "qty", "harga", "cabang"]
  )

  # Ubah format tanggal menjadi format waktu Python
  df["tanggal"] = pd.to_datetime(df["tanggal"])

  # Kalkulasi Omzet secara otomatis (Jumlah x Harga)
  df["omzet"] = df["qty"] * df["harga"]

  return df


df_raw = load_data()

# Panel Filter di Sidebar
st.sidebar.title("🎛️ Panel Filter")
all_cabang = ["Semua"] + sorted(df_raw["cabang"].unique().tolist())
selected_cabang = st.sidebar.selectbox("Lokasi Cabang", all_cabang)

all_kategori = ["Semua"] + sorted(df_raw["kategori"].unique().tolist())
selected_kategori = st.sidebar.selectbox("Kategori Produk", all_kategori)

# Terapkan Filter
df_filtered = df_raw.copy()
if selected_cabang != "Semua":
  df_filtered = df_filtered[df_filtered["cabang"] == selected_cabang]
if selected_kategori != "Semua":
  df_filtered = df_filtered[df_filtered["kategori"] == selected_kategori]

# Tampilan Utama Dashboard
st.title("📊 Dashboard Eksekutif Penjualan Restoran")
st.markdown("Berikut adalah ringkasan performa penjualan secara real-time.")
st.markdown("---")

# Kartu Metrik (KPI Cards)
total_omzet = df_filtered["omzet"].sum()
total_transaksi = df_filtered["id_transaksi"].nunique()
total_qty = df_filtered["qty"].sum()
basket_size = total_omzet / total_transaksi if total_transaksi > 0 else 0

col1, col2, col3, col4 = st.columns(4)
with col1:
  st.metric(
      label="💰 Total Omzet", value=f"Rp {total_omzet:,.0f}".replace(",", ".")
  )
with col2:
  st.metric(
      label="🧾 Total Transaksi", value=f"{total_transaksi:,}".replace(",", ".")
  )
with col3:
  st.metric(
      label="📦 Total Qty Terjual", value=f"{total_qty:,}".replace(",", ".")
  )
with col4:
  st.metric(
      label="🛒 Rata-rata Basket Size",
      value=f"Rp {basket_size:,.0f}".replace(",", "."),
  )

st.markdown("---")

# Grafik Tren Penjualan Harian
st.subheader("📈 Tren Penjualan Harian")
df_trend = (
    df_filtered.groupby(df_filtered["tanggal"].dt.date)["omzet"]
    .sum()
    .reset_index()
)
df_trend.columns = ["Tanggal", "Omzet"]

fig_trend = px.line(
    df_trend,
    x="Tanggal",
    y="Omzet",
    markers=True,
    title="Grafik Perkembangan Omzet Harian",
    template="plotly_white",
)
st.plotly_chart(fig_trend, width="stretch")

# Grafik Performa Produk & Kategori
col_p1, col_p2 = st.columns(2)

with col_p1:
  st.subheader("🏆 Top Produk")
  top_produk = (
      df_filtered.groupby("produk")["omzet"]
      .sum()
      .reset_index()
      .sort_values(by="omzet", ascending=False)
      .head(5)
  )
  fig_top = px.bar(
      top_produk,
      x="omzet",
      y="produk",
      orientation="h",
      title="5 Produk dengan Omzet Tertinggi",
      template="plotly_white",
  )
  st.plotly_chart(fig_top, width="stretch")

with col_p2:
  st.subheader("🥧 Kontribusi Kategori")
  df_kat = df_filtered.groupby("kategori")["omzet"].sum().reset_index()
  fig_kat = px.pie(
      df_kat,
      names="kategori",
      values="omzet",
      title="Persentase Omzet Berdasarkan Kategori",
      hole=0.4,
      template="plotly_white",
  )
  st.plotly_chart(fig_kat, width="stretch")