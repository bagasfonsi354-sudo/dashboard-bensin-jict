"""
UJB Monitoring & Efisiensi JICT  --  versi Streamlit
Port 1:1 dari versi localhost (Flask: app.py + templates/index.html).

Kebutuhan: streamlit>=1.40  (lihat requirements.txt)
"""

import base64
import html as _html
import inspect
import os
import re
import threading
from datetime import date, datetime, timedelta, timezone
from functools import lru_cache

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st
from bs4 import BeautifulSoup

st.set_page_config(
    page_title="UJB Monitoring & Efisiensi JICT",
    page_icon="⛽",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =============================================================================
# KONFIGURASI  (urutan prioritas: st.secrets -> environment variable -> default)
# =============================================================================


def _secret(name, default=""):
    try:
        if name in st.secrets:
            return str(st.secrets[name])
    except Exception:
        pass
    return os.environ.get(name, default)


LOGIN_URL = "https://dashboard.ujbgroup.com/login"
AUTH_URL = "https://dashboard.ujbgroup.com/login/auth"
TARGET_URL = (
    "https://dashboard.ujbgroup.com/data/transaction_data/"
    "get_data_detail_transaction_jict"
)
UJB_USERNAME = _secret("UJB_USERNAME", "staffjict")
UJB_PASSWORD = _secret("UJB_PASSWORD", "staffjict")
MANUAL_COOKIE_NAME = "ci_session"
MANUAL_COOKIE_VALUE = _secret("UJB_SESSION_COOKIE", "")  # opsional

try:
    REFRESH_SECONDS = int(_secret("AUTO_REFRESH_SECONDS", "10"))  # 0 = nonaktif
except ValueError:
    REFRESH_SECONDS = 10

UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__))
WIB = timezone(timedelta(hours=7))
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
FONT = (
    "ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto,"
    " Helvetica Neue, Arial, sans-serif"
)

# =============================================================================
# IKON (Lucide, sama seperti index.html) -> dirender sebagai <img> data-URI
# =============================================================================
_ICONS = {
    "port": '<path d="M2 20h20"/><path d="M5 20V8h14v12"/><path d="M5 12h14"/><path d="M2 6h8l2 2"/><rect x="9" y="14" width="6" height="4" fill="currentColor" opacity="0.3"/>',
    "ship": '<path d="M2 21c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1 .6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/><path d="M19.38 20A11.6 11.6 0 0 0 21 14l-9-4-9 4c0 2.9.94 5.34 2.81 7.76"/><path d="M19 13V7a2 2 0 0 0-2-2H7a2 2 0 0 0-2 2v6"/><path d="M12 10v4"/><path d="M12 2v3"/>',
    "container": '<path d="M22 7.7c0-.6-.4-1.2-.8-1.5l-6.3-3.9a1.72 1.72 0 0 0-1.7 0l-10.3 6c-.5.2-.9.8-.9 1.4v6.6c0 .5.4 1.2.8 1.5l6.3 3.9a1.72 1.72 0 0 0 1.7 0l10.3-6c.5-.3.9-1 .9-1.5Z"/><path d="M10 21.9V14L2.1 9.1"/><path d="m10 14 11.9-6.9"/><path d="M14 19.8v-8.1"/><path d="M18 17.5V9.4"/>',
    "fuel": '<line x1="3" x2="15" y1="22" y2="22"/><line x1="4" x2="14" y1="9" y2="9"/><path d="M14 22V4a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v18"/><path d="M14 13h2a2 2 0 0 1 2 2v2a2 2 0 0 0 2 2a2 2 0 0 0 2-2V9.83a2 2 0 0 0-.59-1.42L18 5"/>',
    "gauge": '<path d="m12 14 4-4"/><path d="M3.34 19a10 10 0 1 1 17.32 0"/>',
    "file-spreadsheet": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M8 13h2"/><path d="M14 13h2"/><path d="M8 17h2"/><path d="M14 17h2"/>',
    "sliders": '<line x1="4" x2="4" y1="21" y2="14"/><line x1="4" x2="4" y1="10" y2="3"/><line x1="12" x2="12" y1="21" y2="12"/><line x1="12" x2="12" y1="8" y2="3"/><line x1="20" x2="20" y1="21" y2="16"/><line x1="20" x2="20" y1="12" y2="3"/><line x1="2" x2="6" y1="14" y2="14"/><line x1="10" x2="14" y1="8" y2="8"/><line x1="18" x2="22" y1="16" y2="16"/>',
    "globe": '<circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/>',
    "activity": '<path d="M22 12h-2.48a2 2 0 0 0-1.93 1.46l-2.35 8.36a.25.25 0 0 1-.48 0L9.24 2.18a.25.25 0 0 0-.48 0l-2.35 8.36A2 2 0 0 1 4.49 12H2"/>',
    "droplet": '<path d="M12 22a7 7 0 0 0 7-7c0-2-1-3.9-3-5.5s-3.5-4-4-6.5c-.5 2.5-2 4.9-4 6.5C6 11.1 5 13 5 15a7 7 0 0 0 7 7z"/>',
    "box": '<path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/>',
    "zap": '<path d="M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z"/>',
    "pie-chart": '<path d="M21.21 15.89A10 10 0 1 1 8 2.83"/><path d="M22 12A10 10 0 0 0 12 2v10z"/>',
    "line-chart": '<path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/>',
    "trending-up": '<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/>',
    "truck": '<path d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2"/><path d="M15 18H9"/><path d="M19 18h2a1 1 0 0 0 1-1v-3.65a1 1 0 0 0-.22-.624l-3.48-4.35A1 1 0 0 0 17.52 8H14"/><circle cx="17" cy="18" r="2"/><circle cx="7" cy="18" r="2"/>',
    "info": '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/>',
    "cpu": '<rect width="16" height="16" x="4" y="4" rx="2"/><rect width="6" height="6" x="9" y="9" rx="1"/><path d="M15 2v2"/><path d="M15 20v2"/><path d="M2 15h2"/><path d="M2 9h2"/><path d="M20 15h2"/><path d="M20 9h2"/><path d="M9 2v2"/><path d="M9 20v2"/>',
    "table": '<path d="M12 3v18"/><rect width="18" height="18" x="3" y="3" rx="2"/><path d="M3 9h18"/><path d="M3 15h18"/>',
    "bar-chart-2": '<line x1="18" x2="18" y1="20" y2="10"/><line x1="12" x2="12" y1="20" y2="4"/><line x1="6" x2="6" y1="20" y2="14"/>',
    "search": '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
}


@lru_cache(maxsize=None)
def _svg_b64(name, size, color, sw):
    inner = _ICONS[name].replace("currentColor", color)
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}"'
        f' viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{sw}"'
        f' stroke-linecap="round" stroke-linejoin="round">{inner}</svg>'
    )
    return base64.b64encode(svg.encode("utf-8")).decode("ascii")


def icon(name, size=16, color="#FBBF24", sw=2):
    return (
        f'<img src="data:image/svg+xml;base64,{_svg_b64(name, size, color, sw)}"'
        f' width="{size}" height="{size}" alt=""'
        ' style="display:inline-block;vertical-align:middle;flex-shrink:0">'
    )


SEARCH_URI = "data:image/svg+xml;base64," + _svg_b64("search", 16, "#94A3B8", 2)

# =============================================================================
# CSS  (padanan dari kelas Tailwind di index.html)
# =============================================================================
CSS = """
<style>
@keyframes pulse-slow{0%,100%{opacity:1}50%{opacity:.4}}
.stApp{
  background-color:#F8F6F0;
  background-image:radial-gradient(at 0% 0%,rgba(3,11,30,.03) 0px,transparent 50%),radial-gradient(at 100% 100%,rgba(0,0,128,.04) 0px,transparent 50%);
  background-attachment:fixed;color:#1E293B;-webkit-font-smoothing:antialiased;
}
.stApp,.stApp p,.stApp label,.stApp input,.stApp button,.stApp textarea,.stApp [data-baseweb],.stApp [data-testid="stMarkdownContainer"]{
  font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif!important;
}
header[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"],footer,#MainMenu,
section[data-testid="stSidebar"],[data-testid="stSidebarCollapsedControl"],[data-testid="collapsedControl"]{display:none!important}
.block-container{max-width:80rem!important;padding:7.8rem 1.5rem 4rem 1.5rem!important}
[data-testid="stMarkdownContainer"] p{margin:0}
[data-testid="stVerticalBlock"]{gap:1.5rem}
[data-testid="stHorizontalBlock"]{gap:1.5rem}
::-webkit-scrollbar{width:6px;height:6px}
::-webkit-scrollbar-track{background:#F1EFE9}
::-webkit-scrollbar-thumb{background:#1E2942;border-radius:4px}
::-webkit-scrollbar-thumb:hover{background:#000080}

/* ---------- Header (sticky) ---------- */
.st-key-app_header{position:fixed;top:0;left:0;right:0;width:100%;box-sizing:border-box;z-index:999;
  background:#030B1E;border-bottom:2px solid #000080;box-shadow:0 4px 6px -1px rgba(0,0,0,.2);
  padding:14px 24px!important;gap:0!important}
.st-key-app_header [data-testid="stHorizontalBlock"]{align-items:center;gap:.75rem}
.st-key-app_header [data-testid="stVerticalBlock"]{gap:0}
.hd-brand{display:flex;align-items:center;gap:16px}
.hd-logo{background:linear-gradient(to bottom right,#1E3A8A,#0F172A);padding:8px;border-radius:12px;border:1px solid rgba(96,165,250,.3);
  box-shadow:0 4px 6px -1px rgba(0,0,0,.3);display:flex;align-items:center;justify-content:center}
.hd-title{font-size:24px;font-weight:800;color:#FFFDF9;letter-spacing:-.025em;display:flex;align-items:center;gap:8px;line-height:1.25}
.hd-chip{font-size:10px;font-weight:600;background:rgba(30,58,138,.8);color:#BFDBFE;padding:2px 8px;border-radius:9999px;
  border:1px solid rgba(29,78,216,.5);text-transform:uppercase;letter-spacing:.1em}
.hd-sub{font-size:12px;color:#CBD5E1;margin-top:2px;display:flex;align-items:center;gap:6px}
.hd-right{display:flex;justify-content:flex-end}
.hd-pill{display:flex;align-items:center;gap:12px;background:#0A1633;padding:6px;border-radius:9999px;border:1px solid rgba(30,58,138,.6);
  box-shadow:inset 0 2px 4px rgba(0,0,0,.25)}
.hd-status{display:flex;align-items:center;gap:8px;padding:6px 12px;border-radius:9999px;font-size:12px;font-weight:500;white-space:nowrap}
.hd-status.ok{background:rgba(2,44,34,.6);color:#6EE7B7;border:1px solid rgba(16,185,129,.3)}
.hd-status.bad{background:rgba(76,5,25,.6);color:#FDA4AF;border:1px solid rgba(244,63,94,.3)}
.hd-dot{width:8px;height:8px;border-radius:9999px}
.hd-status.ok .hd-dot{background:#34D399;animation:pulse-slow 2s cubic-bezier(.4,0,.6,1) infinite}
.hd-status.bad .hd-dot{background:#FB7185}
.hd-upd{font-size:12px;color:#CBD5E1;padding:0 12px;border-left:1px solid rgba(30,58,138,.8);white-space:nowrap}
.hd-upd b{color:#FCD34D;font-weight:600}
.st-key-btn_refresh button{background:#0A1633;border:1px solid rgba(30,58,138,.6);color:#CBD5E1;border-radius:9999px;
  width:38px;height:38px;min-height:0;padding:0;box-shadow:0 1px 2px rgba(0,0,0,.3)}
.st-key-btn_refresh button:hover{background:#000080;color:#fff;border-color:#000080}
.st-key-btn_refresh button p{display:none}
.st-key-btn_refresh button [data-testid="stIconMaterial"]{margin:0}
@media(max-width:900px){
  .st-key-app_header{position:static!important;margin:0 -1.5rem}
  .block-container{padding-top:0!important}
  .hd-title{font-size:20px}.hd-chip{display:none}
}

/* ---------- Banner ---------- */
.banner{background:linear-gradient(to right,#030B1E,#0A1633,#000080);border-radius:16px;padding:24px;color:#fff;
  box-shadow:0 10px 15px -3px rgba(0,0,0,.15);border:1px solid rgba(30,58,138,.5);position:relative;overflow:hidden;
  display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:16px}
.banner-wm{position:absolute;right:-32px;bottom:-32px;opacity:.05;pointer-events:none;line-height:0}
.banner-l{position:relative;z-index:1}
.kicker{display:flex;align-items:center;gap:8px;color:#FCD34D;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.05em;margin-bottom:4px}
.banner-t{font-size:20px;font-weight:800;color:#FFFDF9;margin-bottom:4px}
.banner-s{font-size:12px;color:#CBD5E1;max-width:42rem}
.banner-r{position:relative;z-index:1;flex-shrink:0;background:rgba(255,255,255,.1);backdrop-filter:blur(12px);padding:10px 16px;
  border-radius:12px;border:1px solid rgba(255,255,255,.15);display:flex;align-items:center;gap:12px}
.banner-r .gauge{padding:8px;background:rgba(251,191,36,.2);border-radius:8px;display:flex}
.banner-r .tl{font-size:10px;color:#CBD5E1;text-transform:uppercase;letter-spacing:.05em}
.banner-r .tv{font-size:12px;font-weight:700;color:#fff}

/* ---------- Kartu putih (ivory) ---------- */
div[class*="st-key-card_"],div[class*="st-key-tbl_"]{background:#FFFDF9;border:1px solid rgba(120,53,15,.1);border-radius:16px;
  box-shadow:0 4px 6px -1px rgba(0,0,0,.1),0 2px 4px -2px rgba(0,0,0,.1);box-sizing:border-box}
div[class*="st-key-card_"]{padding:24px;gap:.75rem!important}
div[class*="st-key-card_"] [data-testid="stVerticalBlock"]{gap:.75rem}
.st-key-card_upload{padding:20px!important}
div[class*="st-key-tbl_"]{padding:0!important;overflow:hidden;gap:0!important}
div[class*="st-key-tbl_"] [data-testid="stVerticalBlock"]{gap:0}
div[class*="st-key-card_detail_"]{max-width:448px;border-color:rgba(120,53,15,.2);box-shadow:0 25px 50px -12px rgba(0,0,0,.25)}
.ct{display:flex;align-items:center;gap:8px;font-size:12px;font-weight:700;color:#030B1E;text-transform:uppercase;letter-spacing:.05em}
.h2s{display:flex;align-items:center;gap:8px;font-size:14px;font-weight:700;color:#030B1E}

/* ---------- Judul seksi ---------- */
.sec{display:flex;align-items:center;gap:10px;font-size:18px;font-weight:800;color:#030B1E}
.sec .ib{padding:6px;background:#030B1E;border-radius:8px;display:flex;box-shadow:0 1px 3px rgba(0,0,0,.2)}
.sec.bt{padding-top:24px;border-top:1px solid rgba(203,213,225,.8)}

/* ---------- KPI ---------- */
.kpi-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}
@media(min-width:768px){.kpi-grid{grid-template-columns:repeat(4,minmax(0,1fr))}}
.kpi{background:#030B1E;padding:20px;border-radius:16px;border:1px solid rgba(30,58,138,.4);
  box-shadow:0 4px 6px -1px rgba(0,0,0,.15);position:relative;overflow:hidden;transition:border-color .15s}
.kpi:hover{border-color:#000080}
.kpi .wm{position:absolute;right:-12px;bottom:-12px;pointer-events:none;line-height:0}
.kpi .t{font-size:11px;font-weight:700;color:#CBD5E1;text-transform:uppercase;letter-spacing:.05em;display:block;position:relative}
.kpi .v{font-size:30px;font-weight:800;margin-top:8px;display:block;line-height:1.2;position:relative}
.kpi .v.sm{font-size:20px;line-height:1.75;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
@media(max-width:767px){.kpi .v{font-size:24px}}

/* ---------- Kotak analisis ---------- */
.ana{background:#030B1E;border:1px solid rgba(30,58,138,.5);padding:20px;border-radius:16px;font-size:12px;color:#E2E8F0;
  box-shadow:0 4px 6px -1px rgba(0,0,0,.15)}
.ana h4{margin:0 0 6px 0;font-size:14px;font-weight:700;color:#FCD34D;display:flex;align-items:center;gap:8px;line-height:1.4}
.ana p{color:#CBD5E1;line-height:1.625;margin:0}

/* ---------- Header tabel & panel detail ---------- */
.th{padding:16px;background:#030B1E;color:#fff;display:flex;justify-content:space-between;align-items:center;gap:12px}
.th .tt{font-size:14px;font-weight:700;display:flex;align-items:center;gap:8px}
.th .hint{font-size:11px;color:#94A3B8}
.empty{padding:32px 16px;text-align:center;font-size:12px;color:#94A3B8}
.dh{display:flex;align-items:center;gap:8px;font-size:16px;font-weight:800;color:#030B1E;padding-bottom:12px;border-bottom:1px solid #E2E8F0}
.dbox{padding:14px;background:#030B1E;color:#fff;border-radius:12px;border:1px solid rgba(30,58,138,.4);font-size:12px}
.dbox .r{display:flex;justify-content:space-between;gap:12px;padding-bottom:6px;margin-bottom:8px;border-bottom:1px solid rgba(30,58,138,.6)}
.dbox .r:last-child{border-bottom:0;margin-bottom:0;padding-bottom:0}
.dbox .r b{color:#94A3B8;font-weight:700}

/* ---------- Upload & daftar file ---------- */
.frow{display:flex;align-items:center;gap:6px;background:#fff;padding:8px 12px;border-radius:12px;border:1px solid #E2E8F0;font-size:12px;color:#334155;height:36px;box-sizing:border-box}
.frow span{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.frow.warn{border-color:#FECDD3;background:#FFF1F2;color:#9F1239}
.nofile{font-size:12px;color:#94A3B8;font-style:italic}
.upmsg{font-size:12px;font-weight:500}
[data-testid="stFileUploaderDropzone"]{background:#fff;border:1px solid rgba(203,213,225,.8);border-radius:12px;padding:8px}
[data-testid="stFileUploaderDropzone"] button{background:#030B1E;color:#FDE68A;border:0;border-radius:12px;font-size:12px;font-weight:600}
[data-testid="stFileUploaderDropzone"] button:hover{background:#000080;color:#fff}
[data-testid="stFileUploaderDropzone"] small,[data-testid="stFileUploaderDropzone"] span{font-size:11px}

/* ---------- Tombol ---------- */
.st-key-btn_sync button,.st-key-btn_close_ht button,.st-key-btn_close_nht button{background:#030B1E;color:#FFFDF9;border:1px solid rgba(30,58,138,.4);
  border-radius:12px;font-size:12px;font-weight:600;padding:8px 16px;box-shadow:0 1px 3px rgba(0,0,0,.2);width:100%}
.st-key-btn_sync button:hover,.st-key-btn_close_ht button:hover,.st-key-btn_close_nht button:hover{background:#000080;color:#fff;border-color:rgba(30,58,138,.4)}
.st-key-btn_close_ht button,.st-key-btn_close_nht button{width:auto;float:right}
.st-key-dl_csv button{background:#047857;color:#fff;border:0;border-radius:12px;font-size:12px;font-weight:500;padding:8px 14px;
  box-shadow:0 1px 3px rgba(0,0,0,.2);width:100%}
.st-key-dl_csv button:hover{background:#065F46;color:#fff}
div[class*="st-key-del_"] button,div[class*="st-key-no_"] button{background:transparent;border:0;color:#E11D48;font-size:11px;font-weight:600;
  padding:0;min-height:36px;box-shadow:none;width:100%}
div[class*="st-key-del_"] button:hover,div[class*="st-key-yes_"] button:hover{color:#9F1239;background:transparent}
div[class*="st-key-yes_"] button{background:transparent;border:0;color:#E11D48;font-size:11px;font-weight:700;padding:0;min-height:36px;width:100%}
div[class*="st-key-no_"] button{color:#64748B}

/* ---------- Input ---------- */
[data-testid="stWidgetLabel"] p{font-size:11px!important;font-weight:700!important;color:#64748B!important;text-transform:uppercase;letter-spacing:.05em}
div[data-baseweb="input"]{background:#fff!important;border:1px solid #CBD5E1!important;border-radius:12px!important;box-shadow:0 1px 2px rgba(0,0,0,.05)}
div[data-baseweb="input"]:focus-within{border-color:#000080!important;box-shadow:0 0 0 2px #000080!important}
div[data-baseweb="base-input"]{background:transparent!important}
div[data-baseweb="input"] input{font-size:12px!important;color:#1E293B!important;padding:10px 12px!important;-webkit-text-fill-color:#1E293B}
.st-key-f_search input{padding-left:36px!important;background:url("__SEARCH__") no-repeat 12px center!important}
[data-testid="stDataFrame"]{border-radius:0}
</style>
"""
st.markdown(CSS.replace("__SEARCH__", SEARCH_URI), unsafe_allow_html=True)

# =============================================================================
# HELPER UMUM
# =============================================================================


def md(markup):
    """Render HTML ke satu baris supaya tidak 'pecah' oleh parser markdown."""
    st.markdown(re.sub(r"\s*\n\s*", "", markup.strip()), unsafe_allow_html=True)


def esc(x):
    return _html.escape(str(x), quote=True)


def fmt_id(v, max_dec=3):
    """Padanan Number.toLocaleString('id-ID', {maximumFractionDigits})."""
    try:
        v = float(v)
    except (TypeError, ValueError):
        v = 0.0
    s = f"{v:,.{max_dec}f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s.replace(",", "\x00").replace(".", ",").replace("\x00", ".")


def num(v):
    v = float(v or 0)
    return str(int(v)) if v == int(v) else f"{v:.3f}".rstrip("0").rstrip(".")


def _stretch(fn):
    p = inspect.signature(fn).parameters
    w = p.get("width")
    if w is not None and w.default == "stretch":
        return {"width": "stretch"}
    if "use_container_width" in p:
        return {"use_container_width": True}
    return {}


PLOT_STRETCH = _stretch(st.plotly_chart)
DF_STRETCH = _stretch(st.dataframe)

# =============================================================================
# KLASIFIKASI UNIT  (sama persis dengan isHeadTruck / getSubCategory di index.html)
# =============================================================================


def is_head_truck(asset_no):
    if not asset_no:
        return False
    c = str(asset_no).upper().strip()
    return c.startswith("HT") or re.fullmatch(r"\d+", c) is not None


def _numeric_le_63(s):
    try:
        return int(float(s)) <= 63
    except (ValueError, OverflowError):
        return False


def sub_category(asset_no):
    if not asset_no:
        return "LAIN-LAIN"
    c = str(asset_no).upper().strip()
    if (
        c.startswith("RTGC")
        or (c.startswith("RTG") and not c.startswith("RANGGA"))
        or _numeric_le_63(c)
    ):
        return "RTGC"
    if c.startswith(("SL", "RS", "FRK")) or "TEREX" in c:
        return "ALAT (SL/RS/FRK)"
    if "COMPRESOR" in c or "COM" in c:
        return "COM (COMPRESOR)"
    if c.startswith("BUS"):
        return "BUS"
    if c.startswith("ELF"):
        return "ELF"
    if c.startswith(("MODUL", "STG")):
        return "MODUL"
    if (
        c.startswith(("B ", "POL", "RANGGA", "TRAGA", "HLX", "INV"))
        or any(k in c for k in ("TVC", "CAJ", "BAY", "UAU", "UWM", "UAV", "UBE", "GALMON"))
    ):
        return "OPS (OPERASIONAL)"
    return "OPS / LAINNYA"


# =============================================================================
# KONEKSI API UJB  (padanan initialize_session & /api/data di app.py)
# Satu sesi HTTP dipakai bersama semua pengunjung -> login cukup sekali.
# =============================================================================


@st.cache_resource
def _http():
    return {"s": requests.Session(), "lock": threading.Lock(), "ok": False}


def _login(h):
    s = h["s"]
    if MANUAL_COOKIE_VALUE.strip():
        s.cookies.set(MANUAL_COOKIE_NAME, MANUAL_COOKIE_VALUE, domain="dashboard.ujbgroup.com")
        h["ok"] = True
        return True
    try:
        r = s.get(LOGIN_URL, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        payload = {}
        for tag in soup.find_all("input"):
            name = tag.get("name")
            if name:
                payload[name] = tag.get("value", "")
        payload["username"] = UJB_USERNAME
        payload["password"] = UJB_PASSWORD
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": UA,
            "Referer": LOGIN_URL,
            "Origin": "https://dashboard.ujbgroup.com",
        }
        res = s.post(AUTH_URL, data=payload, headers=headers, allow_redirects=True, timeout=15)
        h["ok"] = "login" not in res.url
    except Exception:
        h["ok"] = False
    return h["ok"]


@st.cache_data(ttl=max(REFRESH_SECONDS - 1, 5), show_spinner=False)
def fetch_api():
    """Return (rows, error). Cache bersama semua pengunjung, ~sepanjang interval refresh."""
    h = _http()
    with h["lock"]:
        if not h["ok"]:
            _login(h)
        now = datetime.now(WIB)
        payload = {
            "startDate": (now - timedelta(days=180)).strftime("%Y-%m-%d"),
            "endDate": now.strftime("%Y-%m-%d"),
            "site": "site_tj_priuk",
            "idLoc": "14",
            "unit": "",
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": UA,
            "Referer": "https://dashboard.ujbgroup.com/",
        }
        try:
            js = None
            for attempt in range(2):
                res = h["s"].post(TARGET_URL, data=payload, headers=headers, timeout=20)
                try:
                    js = res.json()
                    break
                except Exception:
                    if attempt == 0 and _login(h):
                        continue
                    return [], "Sesi belum terautentikasi penuh."
        except Exception as e:
            h["ok"] = False
            return [], f"Gagal menghubungi API UJB: {e}"
    if isinstance(js, dict) and js.get("status") is False:
        return [], str(js.get("error") or "API UJB menolak permintaan.")
    if isinstance(js, dict) and isinstance(js.get("data"), list):
        return js["data"], None
    return [], "Format data API tidak sesuai."


# =============================================================================
# FILE EXCEL PENGAYA (BOX)  (padanan load_local_mapping di app.py)
# =============================================================================


def excel_files():
    return sorted(
        f
        for f in os.listdir(UPLOAD_FOLDER)
        if f.lower().endswith((".xls", ".xlsx")) and not f.startswith("~$")
    )


def files_signature():
    sig = []
    for f in excel_files():
        try:
            stt = os.stat(os.path.join(UPLOAD_FOLDER, f))
            sig.append((f, stt.st_mtime_ns, stt.st_size))
        except OSError:
            pass
    return tuple(sig)


@st.cache_data(show_spinner=False)
def load_mapping(sig):
    prod_map = {}
    for fname, _, _ in sig:
        path = os.path.join(UPLOAD_FOLDER, fname)
        try:
            try:
                df = pd.read_excel(path, engine="calamine")
            except Exception:
                df = pd.read_excel(path)
            df.columns = [str(c).strip().lower() for c in df.columns]
            if not any("trc" in c or "box" in c for c in df.columns):
                continue
            cols = list(df.columns)
            date_col = next((c for c in cols if "date" in c or "tgl" in c), cols[0])
            id_col = next((c for c in cols if "id" in c or "trc" in c), cols[1])
            box_col = next((c for c in cols if "box" in c), cols[-1])
            tgl = pd.to_datetime(df[date_col], errors="coerce").dt.strftime("%Y-%m-%d")
            asset = "HT " + df[id_col].astype(str).str.strip()
            for t, a, b in zip(tgl, asset, df[box_col]):
                prod_map[(str(t), str(a))] = float(b) if pd.notnull(b) else 0.0
        except Exception as e:
            print(f"Gagal memproses file lokal {fname}: {e}")
    return prod_map


def build_frame(rows, prod_map):
    raw = pd.DataFrame(rows) if rows else pd.DataFrame()
    n = len(raw)

    def col(name, default=""):
        if name in raw.columns:
            return raw[name]
        return pd.Series([default] * n, index=raw.index)

    def txt(name):
        return col(name).fillna("").astype(str).str.strip()

    jam = txt("jam")
    jam = jam.where(jam != "", txt("jm"))
    grade = txt("grade_bbm")
    grade = grade.where(grade != "", "BIO SOLAR")
    df = pd.DataFrame({
        "tgl": txt("tgl"),
        "jam": jam,
        "asset_no": txt("asset_no"),
        "volume": pd.to_numeric(col("volume", 0), errors="coerce").fillna(0.0),
        "grade_bbm": grade,
    })
    if prod_map:
        df["total_box"] = [prod_map.get((t, a), 0.0) for t, a in zip(df["tgl"], df["asset_no"])]
    else:
        df["total_box"] = pd.to_numeric(col("total_box", 0), errors="coerce").fillna(0.0)
    return df


# =============================================================================
# STATE & CALLBACK
# =============================================================================
ss = st.session_state
ss.setdefault("up_key", 0)
ss.setdefault("up_msg", None)
ss.setdefault("pending_del", None)
ss.setdefault("last_rows", [])
ss.setdefault("ver_ht", 0)
ss.setdefault("ver_nht", 0)
ss.setdefault("start_touched", False)
ss.setdefault("end_touched", False)


def _refresh_now():
    fetch_api.clear()


def _do_upload():
    files = ss.get(f"uploader_{ss.up_key}") or []
    saved = 0
    for uf in files:
        name = os.path.basename(uf.name)
        if name and name.lower().endswith((".xls", ".xlsx")):
            with open(os.path.join(UPLOAD_FOLDER, name), "wb") as fh:
                fh.write(uf.getbuffer())
            saved += 1
    if saved:
        ss.up_msg = ("ok", f"Berhasil mengunggah {saved} file pengaya ke folder lokal!")
        ss.up_key += 1
    else:
        ss.up_msg = ("err", "Pilih file Excel (.xls / .xlsx) terlebih dahulu.")


def _ask_del(name):
    ss.pending_del = name


def _cancel_del():
    ss.pending_del = None


def _do_del():
    name, ss.pending_del = ss.pending_del, None
    if name and name in excel_files():
        os.remove(os.path.join(UPLOAD_FOLDER, name))
        ss.up_msg = ("ok", f"File {name} berhasil dihapus.")


def _close_detail(ver_key):
    ss[ver_key] += 1  # ganti key tabel -> pilihan baris ter-reset


def _touch(which):
    ss[f"{which}_touched"] = True


# =============================================================================
# KOMPONEN TAMPILAN
# =============================================================================


def kpi_grid(items):
    cells = ""
    for it in items:
        wm = ""
        if it.get("wm"):
            name, color, op = it["wm"]
            wm = f'<div class="wm" style="opacity:{op}">{icon(name, 80, color)}</div>'
        cls = "v sm" if it.get("small") else "v"
        cells += (
            f'<div class="kpi">{wm}<span class="t">{esc(it["t"])}</span>'
            f'<span class="{cls}" style="color:{it["c"]}">{esc(it["v"])}</span></div>'
        )
    md(f'<div class="kpi-grid">{cells}</div>')


def section(title, ico, bt=False):
    md(
        f'<div class="sec{" bt" if bt else ""}"><div class="ib">{icon(ico, 16, "#FCD34D")}</div>'
        f"<span>{esc(title)}</span></div>"
    )


def analysis(title, ico, ico_color, text):
    md(
        f'<div class="ana"><h4>{icon(ico, 16, ico_color)}<span>{esc(title)}</span></h4>'
        f"<p>{esc(text)}</p></div>"
    )


def make_fig(traces, grouped=False):
    fig = go.Figure(traces)
    axis = dict(
        showgrid=True,
        gridcolor="rgba(0,0,0,0.05)",
        zeroline=False,
        linecolor="rgba(0,0,0,0.08)",
        tickfont=dict(color="#475569", size=10),
        automargin=True,
    )
    fig.update_layout(
        height=288,
        margin=dict(l=4, r=4, t=8, b=4),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT, size=10, color="#475569"),
        showlegend=grouped,
        barmode="group",
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5,
            font=dict(color="#030B1E", size=11),
        ),
        hoverlabel=dict(font=dict(family=FONT, size=11)),
    )
    fig.update_xaxes(type="category", **axis)
    fig.update_yaxes(**axis)
    try:
        fig.update_layout(barcornerradius=6)  # bar membulat (Plotly baru)
    except Exception:
        pass
    return fig


def bar_fig(x, y, name, color):
    return make_fig([
        go.Bar(
            x=list(x), y=list(y), name=name, marker_color=color,
            hovertemplate="%{x}<br>" + name + ": %{y:,.2f}<extra></extra>",
        )
    ])


def chart_card(key, title, ico, ico_color, fig):
    with st.container(key=f"card_{key}"):
        md(f'<div class="ct">{icon(ico, 16, ico_color)}<span>{esc(title)}</span></div>')
        st.plotly_chart(
            fig, config={"displayModeBar": False}, theme=None, key=f"plt_{key}", **PLOT_STRETCH
        )


def detail_panel(r, tag):
    def row(label, value, style):
        return f'<div class="r"><b>{label}</b><span style="{style}">{value}</span></div>'

    body = (
        row("Tanggal:", esc(r["tgl"] or "-"), "color:#fff")
        + row("Jam:", esc(r["jam"] or "-"), "color:#fff")
        + row("Nomor Unit:", esc(r["asset_no"] or "-"), "color:#FCD34D;font-weight:700")
        + row("Volume BBM:", f'{num(r["volume"])} Liter', "color:#60A5FA;font-weight:600")
        + row("Grade BBM:", esc(r["grade_bbm"] or "BIO SOLAR"), "color:#fff")
        + row("Total Box:", f'{num(r["total_box"])} Box', "color:#D8B4FE;font-weight:600")
    )
    with st.container(key=f"card_detail_{tag}"):
        md(f'<div class="dh">{icon("truck", 20, "#000080")}<span>Detail Unit: {esc(r["asset_no"] or "N/A")}</span></div>')
        md(f'<div class="dbox">{body}</div>')
        st.button("Tutup", key=f"btn_close_{tag}", on_click=_close_detail, args=(f"ver_{tag}",))


def table_card(tag, title, df_show, df_src, column_config):
    """Tabel dengan header navy + klik baris untuk membuka panel Detail Unit."""
    with st.container(key=f"tbl_{tag}"):
        md(
            f'<div class="th"><div class="tt">{icon("table", 16, "#FCD34D")}<span>{esc(title)}</span></div>'
            '<div class="hint">Klik baris untuk melihat detail unit</div></div>'
        )
        if df_show.empty:
            kind = "Head Truck" if tag == "ht" else "Non-Head Truck"
            md(f'<div class="empty">Tidak ada data transaksi {kind} yang cocok.</div>')
            return
        ev = st.dataframe(
            df_show, hide_index=True, height=384, key=f"df_{tag}_{ss[f'ver_{tag}']}",
            on_select="rerun", selection_mode="single-row",
            column_config=column_config, **DF_STRETCH,
        )
    try:
        rows = list(ev.selection.rows)
    except Exception:
        rows = []
    if rows and rows[0] < len(df_src):
        detail_panel(df_src.iloc[rows[0]], tag)


# =============================================================================
# DASHBOARD  (auto-refresh tiap REFRESH_SECONDS, seperti setInterval di index.html)
# =============================================================================
_fragment = st.fragment(run_every=REFRESH_SECONDS) if REFRESH_SECONDS > 0 else st.fragment


@_fragment
def dashboard():
    now = datetime.now(WIB)

    # ---- ambil data ---------------------------------------------------------
    rows, err = fetch_api()
    if err is None:
        ss.last_rows = rows
    else:
        rows = ss.last_rows  # seperti versi lokal: data terakhir tetap tampil
    connected = err is None
    prod_map = load_mapping(files_signature())
    df_all = build_frame(rows, prod_map)

    # ---- header -------------------------------------------------------------
    cls, label = ("ok", "Terhubung ke API UJB") if connected else ("bad", "Sesi/Koneksi Terputus")
    with st.container(key="app_header"):
        h1, h2, h3 = st.columns([6.3, 4.3, 0.6], vertical_alignment="center")
        with h1:
            md(
                f'<div class="hd-brand"><div class="hd-logo">{icon("port", 32, "#FBBF24")}</div><div>'
                '<div class="hd-title">UJB Monitoring &amp; Efisiensi JICT<span class="hd-chip">Terminal Fuel Ops</span></div>'
                f'<div class="hd-sub">{icon("ship", 14, "#22D3EE")}'
                "<span>Sistem Pemantauan Konsumsi BBM &amp; Produktivitas Unit Pelabuhan</span></div></div></div>"
            )
        with h2:
            md(
                f'<div class="hd-right"><div class="hd-pill"><div class="hd-status {cls}"><span class="hd-dot"></span>'
                f'<span>{label}</span></div><div class="hd-upd">Terakhir Diperbarui: '
                f'<b>{now.strftime("%H.%M.%S")}</b></div></div></div>'
            )
        with h3:
            st.button(" ", icon=":material/refresh:", key="btn_refresh", help="Refresh Data Sekarang", on_click=_refresh_now)

    if err:
        md(
            '<div style="font-size:12px;color:#9F1239;background:#FFF1F2;border:1px solid #FECDD3;'
            f'border-radius:12px;padding:10px 14px">Detail koneksi: {esc(err)}</div>'
        )

    # ---- banner -------------------------------------------------------------
    md(
        f'<div class="banner"><div class="banner-wm">{icon("fuel", 256, "#FFFFFF")}</div>'
        f'<div class="banner-l"><div class="kicker">{icon("container", 16, "#FCD34D")}'
        "<span>Jakarta International Container Terminal (JICT)</span></div>"
        '<div class="banner-t">Dashboard Efisiensi Pengisian Bahan Bakar Terminal</div>'
        '<div class="banner-s">Integrasi otomatis data transaksi dispanser BBM dengan laporan produksi harian '
        "Head Truck &amp; Unit Operasional Pelabuhan.</div></div>"
        f'<div class="banner-r"><div class="gauge">{icon("gauge", 20, "#FCD34D")}</div><div>'
        '<div class="tl">Target Efisiensi</div><div class="tv">&lt; 0.85 L / Box Kontainer</div></div></div></div>'
    )

    # ---- tanggal default = rentang data (hanya selama belum diubah pengguna) --
    dts = pd.to_datetime(df_all["tgl"].str[:10], format="%Y-%m-%d", errors="coerce").dropna()
    d_min = dts.min().date() if len(dts) else None
    d_max = dts.max().date() if len(dts) else None
    today = now.date()
    if not ss.start_touched:
        ss["f_start"] = d_min or (today - timedelta(days=180))
    if not ss.end_touched:
        ss["f_end"] = d_max or today

    # ---- baris 1: unggah Excel + filter -------------------------------------
    col_u, col_f = st.columns([1, 2])
    with col_u:
        with st.container(key="card_upload"):
            md(f'<div class="h2s">{icon("file-spreadsheet", 18, "#D97706")}<span>Unggah Laporan Excel Pengaya (Box)</span></div>')
            st.file_uploader(
                "Excel pengaya", type=["xls", "xlsx"], accept_multiple_files=True,
                label_visibility="collapsed", key=f"uploader_{ss.up_key}",
            )
            st.button(
                "Sinkronkan File Lokal", icon=":material/cloud_upload:", key="btn_sync", on_click=_do_upload
            )
            if ss.up_msg:
                color = "#16A34A" if ss.up_msg[0] == "ok" else "#DC2626"
                md(f'<div class="upmsg" style="color:{color}">{esc(ss.up_msg[1])}</div>')
            with st.container(height=128, border=False, key="files_list"):
                files = excel_files()
                if ss.pending_del and ss.pending_del not in files:
                    ss.pending_del = None
                if ss.pending_del:
                    c1, c2, c3 = st.columns([5, 1.2, 1.2], vertical_alignment="center")
                    with c1:
                        md(f'<div class="frow warn"><span>Hapus file {esc(ss.pending_del)}?</span></div>')
                    with c2:
                        st.button("Ya", key="yes_del", on_click=_do_del)
                    with c3:
                        st.button("Batal", key="no_del", on_click=_cancel_del)
                if files:
                    for i, f in enumerate(files):
                        c1, c2 = st.columns([5, 1.3], vertical_alignment="center")
                        with c1:
                            md(f'<div class="frow">{icon("file-spreadsheet", 14, "#059669")}<span>{esc(f)}</span></div>')
                        with c2:
                            st.button("Hapus", key=f"del_{i}", on_click=_ask_del, args=(f,))
                else:
                    md('<div class="nofile">Belum ada file pengaya.</div>')

    with col_f:
        with st.container(key="card_filter"):
            t1, t2 = st.columns([3, 1], vertical_alignment="center")
            with t1:
                md(f'<div class="h2s">{icon("sliders", 18, "#000080")}<span>Filter Tanggal &amp; Pencarian Unit Interaktif</span></div>')
            with t2:
                export = df_all.rename(columns={
                    "tgl": "Tanggal", "jam": "Jam", "asset_no": "No Unit", "volume": "Volume (L)",
                    "grade_bbm": "Grade BBM", "total_box": "Total Box",
                })
                st.download_button(
                    "Ekspor CSV", data=export.to_csv(index=False).encode("utf-8"),
                    file_name=f"Laporan_UJB_JICT_{today.isoformat()}.csv", mime="text/csv",
                    icon=":material/download:", key="dl_csv",
                )
            d1, d2, d3 = st.columns(3)
            with d1:
                st.date_input(
                    "Dari Tanggal", key="f_start", min_value=date(2000, 1, 1), max_value=date(2100, 12, 31),
                    on_change=_touch, args=("start",),
                )
            with d2:
                st.date_input(
                    "Sampai Tanggal", key="f_end", min_value=date(2000, 1, 1), max_value=date(2100, 12, 31),
                    on_change=_touch, args=("end",),
                )
            with d3:
                st.text_input("Cari No Unit", placeholder="Contoh: HT 170, RTGC, BUS...", key="f_search")

    # ---- terapkan filter (renderDashboard) ----------------------------------
    start_iso, end_iso = ss["f_start"].isoformat(), ss["f_end"].isoformat()
    q = (ss.get("f_search") or "").lower().strip()
    mask = (df_all["tgl"] >= start_iso) & (df_all["tgl"] <= end_iso)
    if q:
        mask &= df_all["asset_no"].str.lower().str.contains(q, regex=False)
    f = df_all[mask].copy()
    f["is_ht"] = f["asset_no"].map(is_head_truck).astype(bool)
    ht = f[f["is_ht"]]
    nht = f[~f["is_ht"]].copy()

    # =========================================================================
    # BAGIAN 1 - KESELURUHAN UNIT & TREN
    # =========================================================================
    g_trx, g_vol, g_box = len(f), f["volume"].sum(), f["total_box"].sum()
    ht_vol_g, nht_vol_g = ht["volume"].sum(), nht["volume"].sum()
    g_rate = ht_vol_g / g_box if g_box > 0 else 0.0

    section("Ringkasan Keseluruhan Unit & Perbandingan Tren Operasional", "globe")
    kpi_grid([
        dict(t="Total Transaksi (All)", v=fmt_id(g_trx), c="#FFFDF9", wm=("activity", "#FFFFFF", .05)),
        dict(t="Total Volume BBM (All)", v=f"{fmt_id(g_vol, 1)} L", c="#60A5FA", wm=("droplet", "#60A5FA", .10)),
        dict(t="Total Produksi Box (HT)", v=f"{fmt_id(g_box)} Box", c="#D8B4FE", wm=("box", "#C084FC", .10)),
        dict(t="Rate Keseluruhan (L/Box)", v=f"{g_rate:.2f}", c="#FBBF24", wm=("zap", "#FB7185", .10)),
    ])

    dated = f[f["tgl"] != ""]
    daily = dated.groupby("tgl")["volume"].sum().sort_index()
    month = dated.assign(m=dated["tgl"].str[:7]).groupby("m").agg(vol=("volume", "sum"), trx=("volume", "size")).sort_index()

    cmp_fig = make_fig([
        go.Bar(name="<b>Head Truck (HT)</b>", x=["Volume BBM (L)", "Total Transaksi"], y=[ht_vol_g, len(ht)], marker_color="#000080"),
        go.Bar(name="<b>Non-HT</b>", x=["Volume BBM (L)", "Total Transaksi"], y=[nht_vol_g, len(nht)], marker_color="#0284C7"),
    ], grouped=True)
    a, b = st.columns(2)
    with a:
        chart_card("cmp", "Perbandingan Konsumsi BBM: Head Truck vs Non-HT", "pie-chart", "#000080", cmp_fig)
    with b:
        chart_card("daily", "Tren Konsumsi BBM Harian Keseluruhan Unit", "line-chart", "#059669",
                   bar_fig(daily.index, daily.values, "Volume Harian (L)", "#059669"))

    if month.empty:
        g_text = "Belum ada data transaksi yang cukup untuk dianalisis dalam rentang ini."
    else:
        last = month.iloc[-1]
        g_text = (
            f"Berdasarkan data operasional terpilih, aktivitas transaksi terkonsentrasi pada bulan {month.index[-1]} "
            f"dengan total volume mencapai {fmt_id(last['vol'], 1)} Liter dari {int(last['trx'])} pengisian."
        )
        if len(month) >= 2:
            prev = month.iloc[-2]
            diff = last["vol"] - prev["vol"]
            pct = f"{abs(diff / prev['vol'] * 100):.1f}" if prev["vol"] > 0 else "0"
            g_text += (
                f" Dibandingkan bulan sebelumnya ({month.index[-2]}), terjadi "
                f"{'peningkatan' if diff >= 0 else 'penurunan'} volume BBM sebesar {pct}%."
            )
    analysis("Evaluasi Tren Efisiensi BBM Keseluruhan", "trending-up", "#34D399", g_text)

    # =========================================================================
    # BAGIAN 2 - HEAD TRUCK (TOP 15)
    # =========================================================================
    section("Kategori 1: Head Truck (HT) - Top 15 Unit Teratas", "truck", bt=True)
    ht_agg = (
        ht.groupby("asset_no", sort=False)
        .agg(trx=("volume", "size"), vol=("volume", "sum"), box=("total_box", "sum"))
        .sort_values("vol", ascending=False, kind="stable")
        .head(15)
    )
    ht_final = ht[ht["asset_no"].isin(ht_agg.index)].reset_index(drop=True)
    h_trx, h_vol, h_box = len(ht_final), ht_final["volume"].sum(), ht_final["total_box"].sum()
    h_rate = h_vol / h_box if h_box > 0 else 0.0

    kpi_grid([
        dict(t="Total Transaksi (HT)", v=fmt_id(h_trx), c="#FFFDF9"),
        dict(t="Total Volume (HT)", v=f"{fmt_id(h_vol, 1)} L", c="#60A5FA"),
        dict(t="Total Box (HT)", v=f"{fmt_id(h_box)} Box", c="#D8B4FE"),
        dict(t="Rate L/Box (HT)", v=f"{h_rate:.2f}", c="#FBBF24"),
    ])

    labels = ht_agg.index.tolist()
    rate_vals = [(v / bx if bx > 0 else 0) for v, bx in zip(ht_agg["vol"], ht_agg["box"])]
    a, b = st.columns(2)
    with a:
        chart_card("ht_trx", "Grafik Total Transaksi (Top 15 HT)", "bar-chart-2", "#000080",
                   bar_fig(labels, ht_agg["trx"], "Total Transaksi", "#000080"))
    with b:
        chart_card("ht_vol", "Grafik Total Volume BBM (Top 15 HT)", "bar-chart-2", "#000080",
                   bar_fig(labels, ht_agg["vol"], "Volume (L)", "#000080"))
    a, b = st.columns(2)
    with a:
        chart_card("ht_box", "Grafik Total Box Produksi (Top 15 HT)", "bar-chart-2", "#7E22CE",
                   bar_fig(labels, ht_agg["box"], "Box Produksi", "#7E22CE"))
    with b:
        chart_card("ht_rate", "Grafik Rasio Rate L/Box (Top 15 HT)", "bar-chart-2", "#E11D48",
                   bar_fig(labels, rate_vals, "Rate (L/Box)", "#E11D48"))

    if labels:
        ht_text = (
            f"Unit Head Truck dengan konsumsi BBM tertinggi adalah {labels[0]} dengan total volume "
            f"{fmt_id(ht_agg['vol'].iloc[0], 1)} Liter. Pastikan pemeliharaan berkala dilakukan pada unit "
            "dengan rasio konsumsi tinggi untuk menjaga efisiensi operasional JICT."
        )
    else:
        ht_text = "Tidak ada data Head Truck yang tersedia."
    analysis("Analisis Otomatis - Head Truck (Top 15)", "info", "#22D3EE", ht_text)

    t = ht_final[["tgl", "jam", "asset_no", "volume", "grade_bbm", "total_box"]].copy()
    t["total_box"] = t["total_box"].map(lambda v: f"{num(v)} Box" if v > 0 else "-")
    t.columns = ["Tanggal", "Jam", "No Unit", "Volume (L)", "Grade BBM", "Total Box"]
    table_card(
        "ht", "Tabel Data Transaksi - Head Truck (Top 15)", t, ht_final,
        {"Volume (L)": st.column_config.NumberColumn("Volume (L)", format="%.1f L")},
    )

    # =========================================================================
    # BAGIAN 3 - NON-HEAD TRUCK
    # =========================================================================
    section("Kategori 2: Non-Head Truck (RTGC, ALAT, COM, OPS, BUS, ELF, MODUL)", "cpu", bt=True)
    nht["sub_cat"] = nht["asset_no"].map(sub_category)
    nht["unit"] = nht["asset_no"].where(nht["asset_no"] != "", "UNKNOWN")
    unit_agg = (
        nht.groupby("unit", sort=False).agg(trx=("volume", "size"), vol=("volume", "sum"))
        .sort_values("vol", ascending=False, kind="stable").head(10)
    )
    cat_agg = (
        nht.groupby("sub_cat", sort=False).agg(trx=("volume", "size"), vol=("volume", "sum"))
        .sort_values("vol", ascending=False, kind="stable")
    )
    top_cat = cat_agg.index[0] if len(cat_agg) else "-"

    kpi_grid([
        dict(t="Total Transaksi (Non-HT)", v=fmt_id(len(nht)), c="#FFFDF9"),
        dict(t="Total Volume (Non-HT)", v=f"{fmt_id(nht_vol_g, 1)} L", c="#60A5FA"),
        dict(t="Sub-Kategori Terbesar", v=top_cat, c="#D8B4FE", small=True),
        dict(t="Estimasi Konsumsi", v="Optimal", c="#34D399"),
    ])

    a, b = st.columns(2)
    with a:
        chart_card("nht_u_trx", "Grafik Non-HT Per Unit Individu (Trx)", "bar-chart-2", "#000080",
                   bar_fig(unit_agg.index, unit_agg["trx"], "Transaksi", "#000080"))
    with b:
        chart_card("nht_u_vol", "Grafik Non-HT Per Unit Individu (Volume L)", "bar-chart-2", "#000080",
                   bar_fig(unit_agg.index, unit_agg["vol"], "Volume (L)", "#000080"))
    a, b = st.columns(2)
    with a:
        chart_card("nht_c_trx", "Grafik Non-HT Sub-Kategori (Trx)", "bar-chart-2", "#7E22CE",
                   bar_fig(cat_agg.index, cat_agg["trx"], "Transaksi", "#7E22CE"))
    with b:
        chart_card("nht_c_vol", "Grafik Non-HT Sub-Kategori (Volume L)", "bar-chart-2", "#7E22CE",
                   bar_fig(cat_agg.index, cat_agg["vol"], "Volume (L)", "#7E22CE"))

    if nht_vol_g == 0:
        n_text = "Tidak ada data transaksi Non-Head Truck."
    else:
        top_vol = cat_agg["vol"].iloc[0]
        n_text = (
            f"Sub-kategori {top_cat} mendominasi pemakaian BBM Non-HT dengan total konsumsi mencapai "
            f"{fmt_id(top_vol, 1)} Liter atau sekitar {top_vol / nht_vol_g * 100:.1f}% dari keseluruhan volume Non-Head Truck."
        )
    analysis("Analisis Otomatis - Non-Head Truck", "info", "#22D3EE", n_text)

    nht = nht.reset_index(drop=True)
    t = nht[["tgl", "jam", "asset_no", "sub_cat", "volume", "grade_bbm"]].copy()
    t.columns = ["Tanggal", "Jam", "No Unit", "Sub-Kategori", "Volume (L)", "Grade BBM"]
    table_card(
        "nht", "Tabel Data Transaksi - Non-Head Truck", t, nht,
        {"Volume (L)": st.column_config.NumberColumn("Volume (L)", format="%.1f L")},
    )


dashboard()
