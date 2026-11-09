from datetime import datetime, timedelta
import os
from bs4 import BeautifulSoup
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

# ==========================================
# KONFIGURASI HALAMAN STREAMLIT
# ==========================================
st.set_page_config(
    page_title="UJB Monitoring & Efisiensi JICT",
    page_icon="⛽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================
# SISTEM STYLING TERUKUR & TERSTRUKTUR (CSS)
# ==========================================
st.markdown(
    """
<style>
    .stApp {
        background-color: #F1F5F9 !important;
        color: #1E293B !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
    }
    .stApp > header { display: none !important; }
    .main .block-container {
        max-width: 1500px !important;
        padding-top: 24px !important;
        padding-bottom: 40px !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }
    section[data-testid="stSidebar"] {
        width: 290px !important; min-width: 280px !important; max-width: 300px !important;
        background-color: #FFFFFF !important; border-right: 1px solid #E2E8F0 !important;
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 24px !important; padding-left: 16px !important; padding-right: 16px !important;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #102A43 !important; font-weight: 700 !important; letter-spacing: -0.01em !important; margin-top: 0 !important;
    }
    .compact-header {
        background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px;
        padding: 12px 20px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(16, 42, 67, 0.04);
        display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;
    }
    .compact-header-brand { display: flex; align-items: center; gap: 10px; }
    .compact-header-icon {
        background-color: #EFF6FF; color: #2563EB; border: 1px solid #DBEAFE;
        padding: 6px 10px; border-radius: 6px; font-size: 18px;
    }
    .compact-header-title { font-size: 17px; font-weight: 800; color: #102A43; margin: 0; line-height: 1.2; }
    .compact-header-badge {
        font-size: 9.5px; font-weight: 700; background-color: #EFF6FF; color: #2563EB;
        border: 1px solid #BFDBFE; padding: 1px 6px; border-radius: 4px; vertical-align: middle; margin-left: 6px;
    }
    .compact-header-desc { font-size: 11.5px; color: #64748B; margin: 2px 0 0 0; }
    .compact-header-meta { display: flex; align-items: center; gap: 10px; }
    .status-badge-green {
        display: inline-flex; align-items: center; gap: 5px; padding: 4px 10px; border-radius: 20px;
        font-size: 11px; font-weight: 600; background-color: #F0FDF4; color: #166534; border: 1px solid #BBF7D0;
    }
    .status-badge-red {
        display: inline-flex; align-items: center; gap: 5px; padding: 4px 10px; border-radius: 20px;
        font-size: 11px; font-weight: 600; background-color: #FEF2F2; color: #991B1B; border: 1px solid #FECACA;
    }
    .status-dot-g { height: 6px; width: 6px; border-radius: 50%; background-color: #16A34A; display: inline-block; }
    .status-dot-r { height: 6px; width: 6px; border-radius: 50%; background-color: #DC2626; display: inline-block; }
    .time-badge { font-size: 11px; color: #64748B; border-left: 1px solid #E2E8F0; padding-left: 10px; }
    .hero-banner-compact {
        background-color: #102A43; border-radius: 8px; padding: 18px 24px; color: #FFFFFF;
        margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;
        flex-wrap: wrap; gap: 14px; border-left: 4px solid #2563EB;
        box-shadow: 0 2px 4px rgba(16, 42, 67, 0.08); min-height: 120px; box-sizing: border-box;
    }
    .hero-banner-title { font-size: 16px; font-weight: 700; color: #FFFFFF; margin: 0 0 4px 0; }
    .hero-banner-sub { font-size: 12px; color: #CBD5E1; margin: 0; max-width: 680px; line-height: 1.5; }
    .hero-target-box {
        background-color: rgba(255, 255, 255, 0.08); border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 6px; padding: 8px 16px; text-align: right; flex-shrink: 0;
    }
    .hero-target-label { font-size: 10px; text-transform: uppercase; color: #94A3B8; font-weight: 600; letter-spacing: 0.05em; }
    .hero-target-val { font-size: 14px; font-weight: 800; color: #F59E0B; }
    .filter-bar-container {
        background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px;
        padding: 14px 18px 10px 18px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(16, 42, 67, 0.03);
    }
    label[data-testid="stWidgetLabel"], label[data-testid="stWidgetLabel"] p,
    .stDateInput label, .stTextInput label, .stSelectbox label {
        color: #64748B !important; font-size: 11px !important; font-weight: 700 !important;
        text-transform: uppercase !important; letter-spacing: 0.04em !important; margin-bottom: 3px !important;
    }
    div[data-baseweb="input"], div[data-baseweb="base-input"],
    .stDateInput div[data-baseweb="input"], .stTextInput div[data-baseweb="input"] {
        background-color: #FFFFFF !important; border: 1px solid #CBD5E1 !important; border-radius: 6px !important; height: 38px !important;
    }
    div[data-baseweb="input"] input, .stDateInput input, .stTextInput input {
        background-color: #FFFFFF !important; color: #1E293B !important; font-size: 12.5px !important; font-weight: 500 !important;
        -webkit-text-fill-color: #1E293B !important;
    }
    .stDownloadButton>button {
        background-color: #2563EB !important; color: #FFFFFF !important; border: none !important;
        border-radius: 6px !important; font-weight: 600 !important; font-size: 12px !important;
        height: 38px !important; margin-top: 19px !important; width: 100% !important;
        box-shadow: 0 1px 2px rgba(37, 99, 235, 0.2) !important;
    }
    .kpi-metric-box {
        background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px;
        padding: 14px 16px; box-shadow: 0 1px 3px rgba(16, 42, 67, 0.04); margin-bottom: 20px;
    }
    .kpi-metric-title { font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 4px; }
    .kpi-metric-value { font-size: 24px; font-weight: 800; letter-spacing: -0.02em; line-height: 1.1; }
    .c-navy { color: #102A43; } .c-blue { color: #2563EB; } .c-teal { color: #0D9488; } .c-amber { color: #D97706; }
    .chart-box-card {
        background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px;
        padding: 16px 16px 8px 16px; box-shadow: 0 1px 3px rgba(16, 42, 67, 0.03); margin-bottom: 20px;
    }
    .chart-box-title { font-size: 12px; font-weight: 700; color: #102A43; text-transform: uppercase; letter-spacing: 0.03em; margin-bottom: 6px; }
    .analysis-callout {
        background-color: #FFFFFF; border: 1px solid #E2E8F0; border-left: 4px solid #0D9488;
        border-radius: 6px; padding: 14px 18px; color: #1E293B; font-size: 12.5px; line-height: 1.6; margin-bottom: 20px;
    }
    .analysis-callout-title { font-size: 12.5px; font-weight: 700; color: #102A43; margin-bottom: 4px; }
    .table-section-header {
        background-color: #102A43; color: #FFFFFF; border-top-left-radius: 8px;
        border-top-right-radius: 8px; padding: 10px 16px; font-size: 12px; font-weight: 700;
    }
    .section-spacing { margin-top: 22px; margin-bottom: 12px; }
</style>
""",
    unsafe_allow_html=True,
)

PLOT_LAYOUT = dict(
    paper_bgcolor="#FFFFFF",
    plot_bgcolor="#FFFFFF",
    font=dict(color="#1E293B", size=11, family="sans-serif"),
    margin=dict(l=35, r=20, t=15, b=35),
    xaxis=dict(
        showgrid=True,
        gridcolor="#F1F5F9",
        linecolor="#E2E8F0",
        tickfont=dict(color="#64748B", size=10),
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor="#F1F5F9",
        linecolor="#E2E8F0",
        tickfont=dict(color="#64748B", size=10),
    ),
    legend=dict(font=dict(color="#102A43", size=11, weight="bold")),
)

LOGIN_URL = "https://dashboard.ujbgroup.com/login"
AUTH_URL = "https://dashboard.ujbgroup.com/login/auth"
TARGET_URL = (
    "https://dashboard.ujbgroup.com/data/transaction_data/get_data_detail_transaction_jict"
)

UJB_USERNAME = os.environ.get("UJB_USERNAME", "staffjict")
UJB_PASSWORD = os.environ.get("UJB_PASSWORD", "staffjict")
UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__))

if "ujb_session" not in st.session_state:
  st.session_state.ujb_session = requests.Session()
  st.session_state.logged_in = False
if "api_cache" not in st.session_state:
  st.session_state.api_cache = []


def auto_login():
  session = st.session_state.ujb_session
  try:
    get_res = session.get(LOGIN_URL, timeout=15)
    soup = BeautifulSoup(get_res.text, "html.parser")
    payload = {}
    for input_tag in soup.find_all("input"):
      name = input_tag.get("name")
      value = input_tag.get("value", "")
      if name:
        payload[name] = value
    payload["username"] = UJB_USERNAME
    payload["password"] = UJB_PASSWORD
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Referer": LOGIN_URL,
        "Origin": "https://dashboard.ujbgroup.com",
    }
    res = session.post(
        AUTH_URL, data=payload, headers=headers, allow_redirects=True, timeout=15
    )
    is_success = "login" not in res.url
    st.session_state.logged_in = is_success
    return is_success
  except Exception:
    st.session_state.logged_in = False
    return False


def load_local_mapping():
  """Membaca file lokal Excel (.xls, .xlsx): pencocokan fleksibel untuk data IHT Production."""
  excel_files = [
      f
      for f in os.listdir(UPLOAD_FOLDER)
      if (f.endswith(".xls") or f.endswith(".xlsx")) and not f.startswith("~$")
  ]
  if not excel_files:
    return {}

  prod_map = {}
  for file in excel_files:
    filepath = os.path.join(UPLOAD_FOLDER, file)
    try:
      df_test = pd.read_excel(filepath)
      cols_lower = [str(c).strip().lower() for c in df_test.columns]

      if any("trc id" in c or "report date" in c for c in cols_lower):
        date_col = next(c for c in df_test.columns if "date" in str(c).lower())
        id_col = next(c for c in df_test.columns if "id" in str(c).lower())
        box_col = next(c for c in df_test.columns if "box" in str(c).lower())

        df_test["tgl_dt"] = pd.to_datetime(df_test[date_col], errors="coerce")
        df_test["tgl_str"] = df_test["tgl_dt"].dt.strftime("%Y-%m-%d")

        for _, row in df_test.iterrows():
          tgl = str(row["tgl_str"]).strip()
          if tgl == "NaT" or not tgl:
            continue
          raw_id = str(row[id_col]).strip().upper()
          box_val = float(row[box_col]) if pd.notnull(row[box_col]) else 0.0

          clean_id = raw_id.replace("HT", "").strip()

          prod_map[(tgl, raw_id)] = (
              prod_map.get((tgl, raw_id), 0.0) + box_val
          )
          prod_map[(tgl, f"HT {clean_id}")] = (
              prod_map.get((tgl, f"HT {clean_id}"), 0.0) + box_val
          )
          prod_map[(tgl, clean_id)] = (
              prod_map.get((tgl, clean_id), 0.0) + box_val
          )

          prod_map[raw_id] = prod_map.get(raw_id, 0.0) + box_val
          prod_map[f"HT {clean_id}"] = (
              prod_map.get(f"HT {clean_id}", 0.0) + box_val
          )
          prod_map[clean_id] = prod_map.get(clean_id, 0.0) + box_val
    except Exception as e:
      print(f"Gagal memproses file {file}: {e}")

  return prod_map


def fetch_api_data(force_reload=False):
  if st.session_state.api_cache and not force_reload:
    return st.session_state.api_cache, None

  session = st.session_state.ujb_session
  if not st.session_state.logged_in:
    auto_login()

  try:
    today = datetime.now()
    today_str = today.strftime("%Y-%m-%d")
    start_date = (today - timedelta(days=180)).strftime("%Y-%m-%d")

    payload = {
        "startDate": start_date,
        "endDate": today_str,
        "site": "site_tj_priuk",
        "idLoc": "14",
        "unit": "",
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Referer": "https://dashboard.ujbgroup.com/",
    }

    response = session.post(TARGET_URL, data=payload, headers=headers, timeout=20)
    try:
      json_res = response.json()
    except Exception:
      if auto_login():
        response = session.post(
            TARGET_URL, data=payload, headers=headers, timeout=20
        )
        json_res = response.json()
      else:
        return [], "Sesi belum terautentikasi."

    if isinstance(json_res, dict) and "data" in json_res:
      data_list = json_res["data"]
      prod_map = load_local_mapping()
      if prod_map and isinstance(data_list, list):
        for item in data_list:
          raw_tgl = str(item.get("tgl", "")).strip()
          tgl = raw_tgl.split(" ")[0] if " " in raw_tgl else raw_tgl

          asset = str(item.get("asset_no", "")).strip().upper()
          clean_asset = asset.replace("HT", "").strip()

          box_found = prod_map.get(
              (tgl, asset),
              prod_map.get(
                  (tgl, f"HT {clean_asset}"),
                  prod_map.get(
                      (tgl, clean_asset),
                      prod_map.get(
                          asset,
                          prod_map.get(
                              f"HT {clean_asset}", prod_map.get(clean_asset, 0.0)
                          ),
                      ),
                  ),
              ),
          )
          item["total_box"] = box_found

      st.session_state.api_cache = data_list
      st.session_state.logged_in = True
      return data_list, None
    return [], "Format data API tidak sesuai."
  except Exception as e:
    return [], str(e)


def is_head_truck(asset_no):
  if not asset_no:
    return False
  clean = str(asset_no).upper().strip()
  return clean.startswith("HT") or clean.isdigit()


def get_sub_category(asset_no):
  if not asset_no:
    return "LAIN-LAIN"
  clean = str(asset_no).upper().strip()
  if (
      clean.startswith("RTGC")
      or (clean.startswith("RTG") and not clean.startswith("RANGGA"))
      or (clean.isdigit() and int(clean) <= 63)
  ):
    return "RTGC"
  if (
      clean.startswith("SL")
      or clean.startswith("RS")
      or clean.startswith("FRK")
      or ("TEREX" in clean)
  ):
    return "ALAT (SL/RS/FRK)"
  if "COMPRESOR" in clean or "COM" in clean:
    return "COM (COMPRESOR)"
  if clean.startswith("BUS"):
    return "BUS"
  if clean.startswith("ELF"):
    return "ELF"
  if clean.startswith("MODUL") or clean.startswith("STG"):
    return "MODUL"
  ops_kw = [
      "B ",
      "POL",
      "TVC",
      "CAJ",
      "BAY",
      "UAU",
      "UWM",
      "UAV",
      "UBE",
      "GALMON",
      "RANGGA",
      "TRAGA",
      "HLX",
      "INV",
  ]
  if any(k in clean for k in ops_kw):
    return "OPS (OPERASIONAL)"
  return "OPS / LAINNYA"


# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
  st.markdown(
      "<h3 style='font-size: 14px; margin-bottom: 2px;'>📁 Sinkronisasi Data"
      " Box</h3>",
      unsafe_allow_html=True,
  )
  uploaded_files = st.file_uploader(
      "Upload Excel",
      type=["xls", "xlsx"],
      accept_multiple_files=True,
      label_visibility="collapsed",
  )
  if uploaded_files:
    saved_count = 0
    for uf in uploaded_files:
      dest_path = os.path.join(UPLOAD_FOLDER, uf.name)
      with open(dest_path, "wb") as f_out:
        f_out.write(uf.getbuffer())
      saved_count += 1
    st.success(f"{saved_count} file tersimpan.")
    st.session_state.api_cache = []

  st.markdown("<hr>", unsafe_allow_html=True)
  if st.button("🔄 Segarkan Data API UJB", use_container_width=True):
    fetch_api_data(force_reload=True)
    st.rerun()

raw_data, api_err = fetch_api_data(force_reload=False)
if not raw_data:
  df_raw = pd.DataFrame(
      columns=["tgl", "jam", "asset_no", "volume", "grade_bbm", "total_box"]
  )
else:
  df_raw = pd.DataFrame(raw_data)
  if "tgl" not in df_raw.columns:
    df_raw["tgl"] = ""
  if "jam" not in df_raw.columns:
    df_raw["jam"] = df_raw.get("jm", "")
  if "asset_no" not in df_raw.columns:
    df_raw["asset_no"] = ""
  if "volume" not in df_raw.columns:
    df_raw["volume"] = 0.0
  if "grade_bbm" not in df_raw.columns:
    df_raw["grade_bbm"] = "BIO SOLAR"
  if "total_box" not in df_raw.columns:
    df_raw["total_box"] = 0.0
  df_raw["volume"] = pd.to_numeric(
      df_raw["volume"], errors="coerce"
  ).fillna(0.0)
  df_raw["total_box"] = pd.to_numeric(
      df_raw["total_box"], errors="coerce"
  ).fillna(0.0)
  df_raw["tgl"] = df_raw["tgl"].astype(str).str.strip()
  df_raw["asset_no"] = df_raw["asset_no"].astype(str).str.strip()

# ==========================================
# HEADER UTAMA
# ==========================================
status_badge_html = (
    '<span class="status-badge-green"><span'
    ' class="status-dot-g"></span>API Terhubung</span>'
    if st.session_state.logged_in
    else '<span class="status-badge-red"><span'
    ' class="status-dot-r"></span>Sesi Terputus</span>'
)
current_time_str = datetime.now().strftime("%H:%M:%S WIB")

st.markdown(
    f"""
<div class="compact-header">
  <div class="compact-header-brand">
    <div class="compact-header-icon">⛽</div>
    <div>
      <div class="compact-header-title">UJB Monitoring &amp; Efisiensi JICT<span class="compact-header-badge">TERMINAL FUEL OPS</span></div>
      <p class="compact-header-desc">Sistem pemantauan konsumsi BBM dan efisiensi operasional unit terminal petikemas.</p>
    </div>
  </div>
  <div class="compact-header-meta">
    {status_badge_html}
    <div class="time-badge">Pembaruan: <strong style="color:#102A43;">{current_time_str}</strong></div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# ==========================================
# HERO BANNER
# ==========================================
st.markdown(
    """
<div class="hero-banner-compact">
  <div>
    <div class="hero-banner-title">Jakarta International Container Terminal — Efisiensi Dispenser BBM</div>
    <p class="hero-banner-sub">Integrasi data otomatis transaksi dispenser harian dengan laporan produksi box Head Truck &amp; unit operasional.</p>
  </div>
  <div class="hero-target-box">
    <div class="hero-target-label">Target Efisiensi</div>
    <div class="hero-target-val">&lt; 0.85 L / Box</div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# ==========================================
# FILTER BAR
# ==========================================
min_date = datetime.now().date() - timedelta(days=180)
max_date = datetime.now().date()
if not df_raw.empty:
  valid_dates = pd.to_datetime(df_raw["tgl"], errors="coerce").dropna().dt.date
  if not valid_dates.empty:
    min_date = valid_dates.min()
    max_date = valid_dates.max()

st.markdown('<div class="filter-bar-container">', unsafe_allow_html=True)
f_col1, f_col2, f_col3, f_col4 = st.columns([2, 2, 3, 1.2])
with f_col1:
  filter_start = st.date_input(
      "DARI TANGGAL",
      value=min_date,
      min_value=min_date,
      max_value=max_date,
  )
with f_col2:
  filter_end = st.date_input(
      "SAMPAI TANGGAL", value=max_date, min_value=min_date, max_value=max_date
  )
with f_col3:
  search_unit = st.text_input(
      "PENCARIAN NOMOR UNIT", placeholder="Contoh: HT 170, RTGC, BUS..."
  ).strip().lower()
with f_col4:
  csv_bytes = df_raw.to_csv(index=False).encode("utf-8")
  st.download_button(
      label="📥 Ekspor CSV",
      data=csv_bytes,
      file_name=f"Laporan_UJB_JICT_{datetime.now().strftime('%Y%m%d')}.csv",
      mime="text/csv",
  )
st.markdown("</div>", unsafe_allow_html=True)

df_filtered = df_raw.copy()
if not df_filtered.empty:
  df_filtered["tgl_dt"] = (
      pd.to_datetime(df_filtered["tgl"], errors="coerce").dt.date
  )
  df_filtered = df_filtered[
      (df_filtered["tgl_dt"] >= filter_start)
      & (df_filtered["tgl_dt"] <= filter_end)
  ]
  if search_unit:
    df_filtered = df_filtered[
        df_filtered["asset_no"].str.lower().str.contains(search_unit, na=False)
    ]

df_filtered["is_ht"] = df_filtered["asset_no"].apply(is_head_truck)
df_filtered["sub_cat"] = df_filtered["asset_no"].apply(get_sub_category)

# ==========================================
# 1. KPI UTAMA & GRAFIK UMUM + ANALISIS GLOBAL
# ==========================================
total_trx_all = len(df_filtered)
total_vol_all = (
    df_filtered["volume"].sum() if not df_filtered.empty else 0.0
)
total_box_all = (
    df_filtered[df_filtered["is_ht"]]["total_box"].sum()
    if not df_filtered.empty
    else 0.0
)
ht_vol_for_rate = (
    df_filtered[df_filtered["is_ht"]]["volume"].sum()
    if not df_filtered.empty
    else 0.0
)
rate_all = (
    (ht_vol_for_rate / total_box_all) if total_box_all > 0 else 0.0
)

k1, k2, k3, k4 = st.columns(4)
with k1:
  st.markdown(
      f"""
    <div class="kpi-metric-box">
        <div class="kpi-metric-title">Total Transaksi (All)</div>
        <div class="kpi-metric-value c-navy">{total_trx_all:,}</div>
    </div>
    """,
      unsafe_allow_html=True,
  )
with k2:
  st.markdown(
      f"""
    <div class="kpi-metric-box">
        <div class="kpi-metric-title">Total Volume BBM (All)</div>
        <div class="kpi-metric-value c-blue">{total_vol_all:,.1f} <span style="font-size: 14px; font-weight: 600;">L</span></div>
    </div>
    """,
      unsafe_allow_html=True,
  )
with k3:
  st.markdown(
      f"""
    <div class="kpi-metric-box">
        <div class="kpi-metric-title">Total Produksi Box (HT)</div>
        <div class="kpi-metric-value c-teal">{int(total_box_all):,} <span style="font-size: 14px; font-weight: 600;">Box</span></div>
    </div>
    """,
      unsafe_allow_html=True,
  )
with k4:
  st.markdown(
      f"""
    <div class="kpi-metric-box">
        <div class="kpi-metric-title">Rasio Rata-rata (L/Box)</div>
        <div class="kpi-metric-value c-amber">{rate_all:.2f}</div>
    </div>
    """,
      unsafe_allow_html=True,
  )

c1, c2 = st.columns(2)
with c1:
  st.markdown(
      '<div class="chart-box-card"><div class="chart-box-title">📊'
      " Perbandingan Volume &amp; Transaksi (HT vs Non-HT)</div>",
      unsafe_allow_html=True,
  )
  ht_vol = (
      df_filtered[df_filtered["is_ht"]]["volume"].sum()
      if not df_filtered.empty
      else 0.0
  )
  non_ht_vol = (
      df_filtered[~df_filtered["is_ht"]]["volume"].sum()
      if not df_filtered.empty
      else 0.0
  )
  ht_trx = len(df_filtered[df_filtered["is_ht"]])
  non_ht_trx = len(df_filtered[~df_filtered["is_ht"]])
  fig_cmp = go.Figure(
      data=[
          go.Bar(
              name="Head Truck (HT)",
              x=["Volume BBM (L)", "Total Transaksi"],
              y=[ht_vol, ht_trx],
              marker_color="#2563EB",
          ),
          go.Bar(
              name="Non-HT",
              x=["Volume BBM (L)", "Total Transaksi"],
              y=[non_ht_vol, non_ht_trx],
              marker_color="#0D9488",
          ),
      ]
  )
  fig_cmp.update_layout(barmode="group", height=270, **PLOT_LAYOUT)
  st.plotly_chart(fig_cmp, use_container_width=True)
  st.markdown("</div>", unsafe_allow_html=True)

with c2:
  st.markdown(
      '<div class="chart-box-card"><div class="chart-box-title">📈 Tren'
      " Pengisian BBM Harian Seluruh Unit</div>",
      unsafe_allow_html=True,
  )
  if not df_filtered.empty:
    daily_df = (
        df_filtered.groupby("tgl")["volume"].sum().reset_index().sort_values("tgl")
    )
    fig_daily = px.bar(
        daily_df,
        x="tgl",
        y="volume",
        labels={"tgl": "Tanggal", "volume": "Volume (L)"},
        color_discrete_sequence=["#2563EB"],
    )
  else:
    fig_daily = px.bar(x=[], y=[])
  fig_daily.update_layout(height=270, **PLOT_LAYOUT)
  st.plotly_chart(fig_daily, use_container_width=True)
  st.markdown("</div>", unsafe_allow_html=True)

# Analisis Global langsung di bawah grafik umum
analysis_global_text = (
    "Belum ada data transaksi yang cukup untuk dianalisis dalam rentang ini."
)
if not df_filtered.empty:
  df_filtered["bulan"] = df_filtered["tgl"].str.slice(0, 7)
  month_agg = (
      df_filtered.groupby("bulan")
      .agg({"volume": "sum", "asset_no": "count"})
      .reset_index()
      .sort_values("bulan")
  )
  if not month_agg.empty:
    latest = month_agg.iloc[-1]
    analysis_global_text = (
        "Berdasarkan data operasional terpilih, aktivitas transaksi"
        f" terkonsentrasi pada bulan <strong>{latest['bulan']}</strong> dengan"
        " total volume mencapai <strong>"
        f"{latest['volume']:,.1f} Liter</strong> dari <strong>"
        f"{latest['asset_no']}</strong> kali pengisian."
    )
    if len(month_agg) >= 2:
      prev = month_agg.iloc[-2]
      diff = latest["volume"] - prev["volume"]
      pct = (diff / prev["volume"] * 100) if prev["volume"] > 0 else 0
      arah = "peningkatan" if diff >= 0 else "penurunan"
      analysis_global_text += (
          f" Dibandingkan bulan sebelumnya ({prev['bulan']}), terjadi {arah}"
          f" volume BBM sebesar <strong>{abs(pct):.1f}%</strong>."
      )

st.markdown(
    f"""
<div class="analysis-callout">
    <div class="analysis-callout-title">📈 Evaluasi Tren Konsumsi BBM Global</div>
    {analysis_global_text}
</div>
""",
    unsafe_allow_html=True,
)


# ==========================================
# 2. GRAFIK HEAD TRUCK (TOP 15) & ANALISISNYA
# ==========================================
st.markdown(
    "<div class='section-spacing'><h3 style='font-size: 15px;'>🚛 Kategori"
    " 1: Head Truck (HT) - Top 15 Unit Teratas</h3></div>",
    unsafe_allow_html=True,
)

df_ht = df_filtered[df_filtered["is_ht"]].copy()
if not df_ht.empty:
  ht_unit_agg = (
      df_ht.groupby("asset_no")
      .agg({"volume": "sum", "total_box": "sum", "tgl": "count"})
      .rename(columns={"tgl": "trx"})
      .reset_index()
  )
  top15_units = (
      ht_unit_agg.sort_values(by="volume", ascending=False)
      .head(15)["asset_no"]
      .tolist()
  )
  df_ht_top15 = df_ht[df_ht["asset_no"].isin(top15_units)]
else:
  top15_units = []
  df_ht_top15 = pd.DataFrame()

ht_trx_top15 = len(df_ht_top15)
ht_vol_top15 = (
    df_ht_top15["volume"].sum() if not df_ht_top15.empty else 0.0
)
ht_box_top15 = (
    df_ht_top15["total_box"].sum() if not df_ht_top15.empty else 0.0
)
ht_rate_top15 = (
    (ht_vol_top15 / ht_box_top15) if ht_box_top15 > 0 else 0.0
)

hk1, hk2, hk3, hk4 = st.columns(4)
with hk1:
  st.markdown(
      f"""
    <div class="kpi-metric-box">
        <div class="kpi-metric-title">Total Transaksi (HT)</div>
        <div class="kpi-metric-value c-navy">{ht_trx_top15:,}</div>
    </div>
    """,
      unsafe_allow_html=True,
  )
with hk2:
  st.markdown(
      f"""
    <div class="kpi-metric-box">
        <div class="kpi-metric-title">Total Volume (HT)</div>
        <div class="kpi-metric-value c-blue">{ht_vol_top15:,.1f} <span style="font-size: 14px; font-weight: 600;">L</span></div>
    </div>
    """,
      unsafe_allow_html=True,
  )
with hk3:
  st.markdown(
      f"""
    <div class="kpi-metric-box">
        <div class="kpi-metric-title">Total Box (HT)</div>
        <div class="kpi-metric-value c-teal">{int(ht_box_top15):,} <span style="font-size: 14px; font-weight: 600;">Box</span></div>
    </div>
    """,
      unsafe_allow_html=True,
  )
with hk4:
  st.markdown(
      f"""
    <div class="kpi-metric-box">
        <div class="kpi-metric-title">Rasio Rate (L/Box)</div>
        <div class="kpi-metric-value c-amber">{ht_rate_top15:.2f}</div>
    </div>
    """,
      unsafe_allow_html=True,
  )

if not df_ht_top15.empty:
  ht_chart_df = (
      df_ht_top15.groupby("asset_no")
      .agg({"volume": "sum", "total_box": "sum", "tgl": "count"})
      .rename(columns={"tgl": "trx"})
      .loc[top15_units]
      .reset_index()
  )
  ht_chart_df["rate"] = ht_chart_df.apply(
      lambda r: (r["volume"] / r["total_box"]) if r["total_box"] > 0 else 0.0,
      axis=1,
  )
else:
  ht_chart_df = pd.DataFrame(
      columns=["asset_no", "trx", "volume", "total_box", "rate"]
  )

h_g1, h_g2 = st.columns(2)
with h_g1:
  st.markdown(
      '<div class="chart-box-card"><div class="chart-box-title">📊 Total'
      " Transaksi (Top 15 HT)</div>",
      unsafe_allow_html=True,
  )
  fig_ht_trx = px.bar(
      ht_chart_df,
      x="asset_no",
      y="trx",
      labels={"asset_no": "Nomor Unit HT", "trx": "Transaksi"},
      color_discrete_sequence=["#102A43"],
  )
  fig_ht_trx.update_layout(height=260, **PLOT_LAYOUT)
  st.plotly_chart(fig_ht_trx, use_container_width=True)
  st.markdown("</div>", unsafe_allow_html=True)

with h_g2:
  st.markdown(
      '<div class="chart-box-card"><div class="chart-box-title">📊 Total'
      " Volume Konsumsi BBM (Top 15 HT)</div>",
      unsafe_allow_html=True,
  )
  fig_ht_vol = px.bar(
      ht_chart_df,
      x="asset_no",
      y="volume",
      labels={"asset_no": "Nomor Unit HT", "volume": "Volume (L)"},
      color_discrete_sequence=["#2563EB"],
  )
  fig_ht_vol.update_layout(height=260, **PLOT_LAYOUT)
  st.plotly_chart(fig_ht_vol, use_container_width=True)
  st.markdown("</div>", unsafe_allow_html=True)

h_g3, h_g4 = st.columns(2)
with h_g3:
  st.markdown(
      '<div class="chart-box-card"><div class="chart-box-title">📦 Total'
      " Produksi Box (Top 15 HT)</div>",
      unsafe_allow_html=True,
  )
  fig_ht_box = px.bar(
      ht_chart_df,
      x="asset_no",
      y="total_box",
      labels={"asset_no": "Nomor Unit HT", "total_box": "Box"},
      color_discrete_sequence=["#0D9488"],
  )
  fig_ht_box.update_layout(height=260, **PLOT_LAYOUT)
  st.plotly_chart(fig_ht_box, use_container_width=True)
  st.markdown("</div>", unsafe_allow_html=True)

with h_g4:
  st.markdown(
      '<div class="chart-box-card"><div class="chart-box-title">⚡ Rasio'
      " Konsumsi BBM (L/Box)</div>",
      unsafe_allow_html=True,
  )
  fig_ht_rate = px.bar(
      ht_chart_df,
      x="asset_no",
      y="rate",
      labels={"asset_no": "Nomor Unit HT", "rate": "L / Box"},
      color_discrete_sequence=["#F59E0B"],
  )
  fig_ht_rate.update_layout(height=260, **PLOT_LAYOUT)
  st.plotly_chart(fig_ht_rate, use_container_width=True)
  st.markdown("</div>", unsafe_allow_html=True)

# Analisis Head Truck langsung di bawah grafik Head Truck
analysis_ht_text = "Tidak ada data Head Truck yang tersedia."
if not ht_chart_df.empty:
  top_ht_unit = ht_chart_df.iloc[0]
  analysis_ht_text = (
      "Unit Head Truck dengan konsumsi BBM tertinggi adalah"
      f" <strong>{top_ht_unit['asset_no']}</strong> dengan total volume"
      f" <strong>{top_ht_unit['volume']:,.1f} Liter</strong>. Pastikan"
      " pemeliharaan berkala dilakukan pada unit dengan rasio konsumsi tinggi"
      " untuk menjaga efisiensi operasional JICT."
  )

st.markdown(
    f"""
<div class="analysis-callout">
    <div class="analysis-callout-title">🚛 Analisis Efisiensi Head Truck (Top 15)</div>
    {analysis_ht_text}
</div>
""",
    unsafe_allow_html=True,
)


# ==========================================
# 3. GRAFIK NON-HEAD TRUCK & ANALISISNYA
# ==========================================
st.markdown(
    "<div class='section-spacing'><h3 style='font-size: 15px;'>⚙️ Kategori"
    " 2: Non-Head Truck (RTGC, ALAT, COM, OPS, dll.)</h3></div>",
    unsafe_allow_html=True,
)

df_non_ht = df_filtered[~df_filtered["is_ht"]].copy()
non_ht_trx = len(df_non_ht)
non_ht_vol = (
    df_non_ht["volume"].sum() if not df_non_ht.empty else 0.0
)

if not df_non_ht.empty:
  cat_agg = (
      df_non_ht.groupby("sub_cat")
      .agg({"volume": "sum", "tgl": "count"})
      .rename(columns={"tgl": "trx"})
      .reset_index()
      .sort_values("volume", ascending=False)
  )
  top_cat_name = cat_agg.iloc[0]["sub_cat"] if not cat_agg.empty else "-"
  unit_agg_non = (
      df_non_ht.groupby("asset_no")
      .agg({"volume": "sum", "tgl": "count"})
      .rename(columns={"tgl": "trx"})
      .reset_index()
      .sort_values("volume", ascending=False)
      .head(10)
  )
else:
  cat_agg = pd.DataFrame(columns=["sub_cat", "volume", "trx"])
  top_cat_name = "-"
  unit_agg_non = pd.DataFrame(columns=["asset_no", "volume", "trx"])

nk1, nk2, nk3, nk4 = st.columns(4)
with nk1:
  st.markdown(
      f"""
    <div class="kpi-metric-box">
        <div class="kpi-metric-title">Total Transaksi (Non-HT)</div>
        <div class="kpi-metric-value c-navy">{non_ht_trx:,}</div>
    </div>
    """,
      unsafe_allow_html=True,
  )
with nk2:
  st.markdown(
      f"""
    <div class="kpi-metric-box">
        <div class="kpi-metric-title">Total Volume (Non-HT)</div>
        <div class="kpi-metric-value c-blue">{non_ht_vol:,.1f} <span style="font-size: 14px; font-weight: 600;">L</span></div>
    </div>
    """,
      unsafe_allow_html=True,
  )
with nk3:
  st.markdown(
      f"""
    <div class="kpi-metric-box">
        <div class="kpi-metric-title">Sub-Kategori Terbesar</div>
        <div class="kpi-metric-value c-teal" style="font-size: 18px;">{top_cat_name}</div>
    </div>
    """,
      unsafe_allow_html=True,
  )
with nk4:
  st.markdown(
      f"""
    <div class="kpi-metric-box">
        <div class="kpi-metric-title">Status Operasional</div>
        <div class="kpi-metric-value c-teal" style="font-size: 18px;">Optimal</div>
    </div>
    """,
      unsafe_allow_html=True,
  )

n_g1, n_g2 = st.columns(2)
with n_g1:
  st.markdown(
      '<div class="chart-box-card"><div class="chart-box-title">📊'
      " Frekuensi Transaksi Per Unit (Non-HT)</div>",
      unsafe_allow_html=True,
  )
  fig_nu_trx = px.bar(
      unit_agg_non,
      x="asset_no",
      y="trx",
      labels={"asset_no": "Nomor Unit", "trx": "Transaksi"},
      color_discrete_sequence=["#102A43"],
  )
  fig_nu_trx.update_layout(height=260, **PLOT_LAYOUT)
  st.plotly_chart(fig_nu_trx, use_container_width=True)
  st.markdown("</div>", unsafe_allow_html=True)

with n_g2:
  st.markdown(
      '<div class="chart-box-card"><div class="chart-box-title">📊 Total'
      " Volume Konsumsi BBM Per Unit (Non-HT)</div>",
      unsafe_allow_html=True,
  )
  fig_nu_vol = px.bar(
      unit_agg_non,
      x="asset_no",
      y="volume",
      labels={"asset_no": "Nomor Unit", "volume": "Volume (L)"},
      color_discrete_sequence=["#2563EB"],
  )
  fig_nu_vol.update_layout(height=260, **PLOT_LAYOUT)
  st.plotly_chart(fig_nu_vol, use_container_width=True)
  st.markdown("</div>", unsafe_allow_html=True)

n_g3, n_g4 = st.columns(2)
with n_g3:
  st.markdown(
      '<div class="chart-box-card"><div class="chart-box-title">🏷️'
      " Frekuensi Transaksi Per Sub-Kategori</div>",
      unsafe_allow_html=True,
  )
  fig_nc_trx = px.bar(
      cat_agg,
      x="sub_cat",
      y="trx",
      labels={"sub_cat": "Sub-Kategori", "trx": "Transaksi"},
      color_discrete_sequence=["#0D9488"],
  )
  fig_nc_trx.update_layout(height=260, **PLOT_LAYOUT)
  st.plotly_chart(fig_nc_trx, use_container_width=True)
  st.markdown("</div>", unsafe_allow_html=True)

with n_g4:
  st.markdown(
      '<div class="chart-box-card"><div class="chart-box-title">🏷️ Total'
      " Volume BBM Per Sub-Kategori</div>",
      unsafe_allow_html=True,
  )
  fig_nc_vol = px.bar(
      cat_agg,
      x="sub_cat",
      y="volume",
      labels={"sub_cat": "Sub-Kategori", "volume": "Volume (L)"},
      color_discrete_sequence=["#0D9488"],
  )
  fig_nc_vol.update_layout(height=260, **PLOT_LAYOUT)
  st.plotly_chart(fig_nc_vol, use_container_width=True)
  st.markdown("</div>", unsafe_allow_html=True)

# Analisis Non-HT langsung di bawah grafik Non-HT
analysis_non_ht_text = "Tidak ada data transaksi Non-Head Truck."
if non_ht_vol > 0 and not cat_agg.empty:
  top_c = cat_agg.iloc[0]
  pct = (top_c["volume"] / non_ht_vol * 100) if non_ht_vol > 0 else 0
  analysis_non_ht_text = (
      f"Sub-kategori <strong>{top_c['sub_cat']}</strong> mendominasi pemakaian"
      " BBM Non-HT dengan total konsumsi mencapai <strong>"
      f"{top_c['volume']:,.1f} Liter</strong> atau sekitar <strong>"
      f"{pct:.1f}%</strong> dari keseluruhan volume Non-Head Truck."
  )

st.markdown(
    f"""
<div class="analysis-callout">
    <div class="analysis-callout-title">⚙️ Analisis Konsumsi Non-Head Truck</div>
    {analysis_non_ht_text}
</div>
""",
    unsafe_allow_html=True,
)


# ==========================================
# 4. TABEL RINCIAN TRANSAKSI & INSPEKTOR
# ==========================================
st.markdown(
    "<div class='section-spacing'><h3 style='font-size: 15px;'>📋 Data"
    " Rincian Transaksi Dispenser BBM</h3></div>",
    unsafe_allow_html=True,
)
tab_ht, tab_non_ht, tab_inspector = st.tabs(
    ["Head Truck (Top 15)", "Non-Head Truck", "Inspektor Histori Unit"]
)

with tab_ht:
  st.markdown(
      '<div class="table-section-header">Rincian Transaksi Dispenser'
      " BBM - Head Truck (Top 15)</div>",
      unsafe_allow_html=True,
  )
  if not df_ht_top15.empty:
    st.dataframe(
        df_ht_top15[[
            "tgl",
            "jam",
            "asset_no",
            "volume",
            "grade_bbm",
            "total_box",
        ]].rename(
            columns={
                "tgl": "Tanggal",
                "jam": "Jam",
                "asset_no": "No Unit",
                "volume": "Volume (L)",
                "grade_bbm": "Grade BBM",
                "total_box": "Total Box",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )
  else:
    st.info("Tidak ada data transaksi Head Truck yang cocok.")

with tab_non_ht:
  st.markdown(
      '<div class="table-section-header">Rincian Transaksi Dispenser'
      " BBM - Non-Head Truck</div>",
      unsafe_allow_html=True,
  )
  df_non_ht_all = df_filtered[~df_filtered["is_ht"]]
  if not df_non_ht_all.empty:
    st.dataframe(
        df_non_ht_all[[
            "tgl",
            "jam",
            "asset_no",
            "sub_cat",
            "volume",
            "grade_bbm",
        ]].rename(
            columns={
                "tgl": "Tanggal",
                "jam": "Jam",
                "asset_no": "No Unit",
                "sub_cat": "Sub-Kategori",
                "volume": "Volume (L)",
                "grade_bbm": "Grade BBM",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )
  else :
