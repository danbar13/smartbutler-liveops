"""
SmartButler® LiveOps Digest Dashboard — Dual Language (Hebrew RTL / English LTR)
תוסף מערכת סמארט-באטלר מבית ג'ייבי מערכות (JAYBEE Systems Ltd. - www.jaybee.com)
ניתוח דוחות תפעוליים מסוג "Log Report - Providers", מעקב עמידה בזמני תקן (SLA), זיהוי חריגים והפקת תדריך בוקר להנהלה.
"""

import os
import io
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime
from collections import defaultdict, Counter
from typing import Optional, Dict, Any, List

import importlib
import db
from parsers import parse_smartbutler_document, ParsedLogReport
from engine import SmartButlerEngine
import i18n
importlib.reload(i18n)
from i18n import (
    t, get_dept_name, classify_specific_request, get_location_cluster,
    generate_executive_briefing, generate_departmental_action_items,
    FLAG_IL_SVG, FLAG_GB_SVG,
    LANG_HE, LANG_EN
)

# Page configuration
st.set_page_config(
    page_title="SmartButler® — LiveOps Digest",
    page_icon="🛎️",
    layout="wide",
    initial_sidebar_state="auto"
)

# Initialize Language State from Query Params or Session State
if "lang" in st.query_params:
    st.session_state.lang = st.query_params["lang"]
elif "lang" not in st.session_state:
    st.session_state.lang = LANG_HE

lang = st.session_state.lang
if lang not in [LANG_HE, LANG_EN]:
    lang = LANG_HE
    st.session_state.lang = LANG_HE

is_rtl = (lang == LANG_HE)
dir_css = "rtl" if is_rtl else "ltr"
align_css = "right" if is_rtl else "left"

# Initialize Theme State from Query Params or Session State
THEME_DARK = "dark"
THEME_LIGHT = "light"

if "theme" in st.query_params:
    st.session_state.theme = st.query_params["theme"]
elif "theme" not in st.session_state:
    st.session_state.theme = THEME_DARK

theme = st.session_state.theme
if theme not in [THEME_DARK, THEME_LIGHT]:
    theme = THEME_DARK
    st.session_state.theme = THEME_DARK

is_light = (theme == THEME_LIGHT)

# Hide Streamlit Cloud viewer badges and "Manage app" button from parent document
components.html("""
<script>
function hideCloudManageApp() {
    try {
        const docs = [document];
        if (window.parent && window.parent.document) docs.push(window.parent.document);
        if (window.top && window.top.document && window.top !== window.parent) docs.push(window.top.document);
        docs.forEach(doc => {
            if (!doc.getElementById('hide-cloud-manage-css')) {
                const s = doc.createElement('style');
                s.id = 'hide-cloud-manage-css';
                s.innerHTML = `
                    [class*="viewerBadge"],
                    [class*="profileContainer"],
                    [data-testid="manage-app-button"],
                    ._viewerBadge_1j65n_23,
                    ._profileContainer_gzau3_53,
                    .viewerBadge_container__1333V,
                    ._container_gzau3_1 {
                        display: none !important;
                        visibility: hidden !important;
                        opacity: 0 !important;
                        pointer-events: none !important;
                        width: 0 !important;
                        height: 0 !important;
                    }
                `;
                doc.head.appendChild(s);
            }
            doc.querySelectorAll('[class*="viewerBadge"], [class*="profileContainer"], [data-testid="manage-app-button"], ._container_gzau3_1').forEach(el => {
                el.style.display = 'none';
            });
        });
    } catch(e) {}
}
hideCloudManageApp();
setInterval(hideCloudManageApp, 500);
</script>
""", height=0, width=0)

# Theme Palette Configuration (Strict Contrast for Light and Dark)
if is_light:
    app_bg = "#f8fafc"
    app_text = "#0f172a"
    sidebar_bg = "#f1f5f9"
    sidebar_border = "#cbd5e1"
    
    header_bg = "#ffffff"
    header_border = "#cbd5e1"
    header_title_col = "#0f172a"
    header_sub_col = "#475569"
    header_link_col = "#0284c7"
    header_badge_bg = "#f1f5f9"
    header_badge_border = "#cbd5e1"
    header_badge_col = "#0369a1"
    
    metric_bg = "#ffffff"
    metric_border = "#cbd5e1"
    metric_label_col = "#475569"
    metric_val_col = "#0f172a"
    metric_delta_col = "#0284c7"
    metric_shadow = "0 2px 8px rgba(0, 0, 0, 0.05)"
    
    expander_bg = "#ffffff"
    expander_border = "#cbd5e1"
    expander_summary_bg = "#f8fafc"
    expander_summary_col = "#0f172a"
    expander_summary_border = "1px solid #e2e8f0"
    expander_summary_hover = "#0284c7"
    expander_details_text = "#334155"
    expander_details_head = "#0f172a"
    expander_shadow = "0 2px 8px rgba(0, 0, 0, 0.04)"
    
    table_container_bg = "#ffffff"
    table_border = "#cbd5e1"
    table_th_bg = "#f1f5f9"
    table_th_col = "#0f172a"
    table_th_border = "2px solid #cbd5e1"
    table_tr_border = "1px solid #e2e8f0"
    table_tr_even = "#f8fafc"
    table_tr_hover = "#f1f5f9"
    table_td_col = "#1e293b"
    table_shadow = "0 2px 8px rgba(0, 0, 0, 0.04)"
    
    badge_succ_bg = "#dcfce7"
    badge_succ_col = "#15803d"
    badge_succ_bord = "1px solid #86efac"
    
    badge_att_bg = "#fee2e2"
    badge_att_col = "#b91c1c"
    badge_att_bord = "1px solid #fca5a5"
    
    badge_info_bg = "#e0f2fe"
    badge_info_col = "#0369a1"
    badge_info_bord = "1px solid #7dd3fc"
    
    code_bg = "#e2e8f0"
    code_col = "#0f172a"
    code_bord = "#cbd5e1"
    
    dropzone_bg = "#f8fafc"
    dropzone_border = "#94a3b8"
    dropzone_text = "#1e293b"
    
    tab_text = "#475569"
    tab_active_text = "#0284c7"
    tab_active_border = "#0284c7"
    
    alert_bg = "#ffffff"
    alert_border = "#cbd5e1"
    alert_text = "#0f172a"
    
    settings_btn_bg = "#f1f5f9"
    settings_btn_col = "#0f172a"
    settings_btn_bord = "#cbd5e1"
    settings_menu_bg = "#ffffff"
    settings_menu_border = "#cbd5e1"
    settings_item_bg = "#f8fafc"
    settings_item_col = "#334155"
    settings_item_bord = "#e2e8f0"
    settings_divider = "#e2e8f0"
else:
    app_bg = "#070d14"
    app_text = "#ffffff"
    sidebar_bg = "#091421"
    sidebar_border = "rgba(75, 189, 219, 0.2)"
    
    header_bg = "linear-gradient(135deg, #0d2838, #0a1924)"
    header_border = "rgba(75, 189, 219, 0.3)"
    header_title_col = "#ffffff"
    header_sub_col = "#cbd5e1"
    header_link_col = "#60a5fa"
    header_badge_bg = "rgba(75, 189, 219, 0.15)"
    header_badge_border = "rgba(75, 189, 219, 0.4)"
    header_badge_col = "#38bdf8"
    
    metric_bg = "#0d1e2e"
    metric_border = "rgba(75, 189, 219, 0.35)"
    metric_label_col = "#e2e8f0"
    metric_val_col = "#ffffff"
    metric_delta_col = "#38bdf8"
    metric_shadow = "0 4px 12px rgba(0, 0, 0, 0.25)"
    
    expander_bg = "#0d1726"
    expander_border = "rgba(75, 189, 219, 0.22)"
    expander_summary_bg = "rgba(255, 255, 255, 0.02)"
    expander_summary_col = "#ffffff"
    expander_summary_border = "none"
    expander_summary_hover = "#38bdf8"
    expander_details_text = "#cbd5e1"
    expander_details_head = "#ffffff"
    expander_shadow = "0 2px 8px rgba(0, 0, 0, 0.18)"
    
    table_container_bg = "#0d1522"
    table_border = "rgba(255, 255, 255, 0.12)"
    table_th_bg = "#17253a"
    table_th_col = "#94a3b8"
    table_th_border = "2px solid rgba(75, 189, 219, 0.4)"
    table_tr_border = "1px solid rgba(255, 255, 255, 0.05)"
    table_tr_even = "rgba(255, 255, 255, 0.02)"
    table_tr_hover = "rgba(75, 189, 219, 0.08)"
    table_td_col = "#f1f5f9"
    table_shadow = "0 2px 8px rgba(0,0,0,0.2)"
    
    badge_succ_bg = "rgba(16, 185, 129, 0.18)"
    badge_succ_col = "#34d399"
    badge_succ_bord = "1px solid rgba(16, 185, 129, 0.3)"
    
    badge_att_bg = "rgba(245, 158, 11, 0.18)"
    badge_att_col = "#fbbf24"
    badge_att_bord = "1px solid rgba(245, 158, 11, 0.3)"
    
    badge_info_bg = "rgba(56, 189, 248, 0.18)"
    badge_info_col = "#38bdf8"
    badge_info_bord = "1px solid rgba(56, 189, 248, 0.3)"
    
    code_bg = "#0f172a"
    code_col = "#10b981"
    code_bord = "rgba(75, 189, 219, 0.3)"
    
    dropzone_bg = "#0e1e2e"
    dropzone_border = "rgba(75, 189, 219, 0.4)"
    dropzone_text = "#cbd5e1"
    
    tab_text = "#94a3b8"
    tab_active_text = "#38bdf8"
    tab_active_border = "#38bdf8"
    
    alert_bg = "#0f1e2e"
    alert_border = "rgba(75, 189, 219, 0.35)"
    alert_text = "#f1f5f9"
    
    settings_btn_bg = "rgba(75, 189, 219, 0.15)"
    settings_btn_col = "#e2e8f0"
    settings_btn_bord = "rgba(75, 189, 219, 0.4)"
    settings_menu_bg = "#0c1a29"
    settings_menu_border = "rgba(75, 189, 219, 0.4)"
    settings_item_bg = "#132437"
    settings_item_col = "#cbd5e1"
    settings_item_bord = "rgba(75, 189, 219, 0.25)"
    settings_divider = "rgba(75, 189, 219, 0.2)"

# Dynamic CSS Styling based on Active Language (Hebrew RTL vs English LTR)
st.markdown(f"""
<style>
    /* Typography and Font Family */
    html, body {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
        direction: {dir_css} !important;
    }}

    /* Complete elimination of Streamlit developer actions (Share, Star, Edit, GitHub, Deploy) */
    .stAppDeployButton,
    [data-testid="stToolbarActions"], 
    [data-testid="stDecoration"], 
    [data-testid="stStatusWidget"], 
    .stStatusWidget,
    [data-testid="stToolbarNav"],
    [data-testid="manage-app-button"],
    div[class*="viewerBadge"], 
    div[class*="profileContainer"] {{
        visibility: hidden !important;
        display: none !important;
        opacity: 0 !important;
        pointer-events: none !important;
        height: 0 !important;
        width: 0 !important;
        overflow: hidden !important;
    }}
    footer, [data-testid="stFooter"] {{
        visibility: hidden !important;
        display: none !important;
        height: 0 !important;
    }}
    /* Keep Streamlit header transparent so sidebar toggle chevron button works on mobile & desktop */
    header, [data-testid="stHeader"], .stAppHeader {{
        background: transparent !important;
        border: none !important;
        z-index: 9999 !important;
    }}
    /* Sidebar toggle chevron button: ensure ALWAYS accessible and visible on mobile & desktop */
    [data-testid="stSidebarCollapseButton"] {{
        visibility: visible !important;
        display: inline-flex !important;
        opacity: 1 !important;
        pointer-events: auto !important;
        z-index: 999999 !important;
    }}

    /* Keep Streamlit's outer shell LTR so sidebar collapse/expand works natively */
    [data-testid="stAppViewContainer"] {{
        direction: ltr !important;
    }}

    /* App Canvas & Background */
    .stApp, [data-testid="stAppViewContainer"], .main, .block-container {{
        background-color: {app_bg} !important;
        color: {app_text} !important;
    }}
    [data-testid="stSidebar"], [data-testid="stSidebarContent"], section[data-testid="stSidebar"] {{
        background-color: {sidebar_bg} !important;
        color: {app_text} !important;
        border-inline-end: 1px solid {sidebar_border} !important;
    }}

    /* Main Dashboard Area */
    .main, .block-container {{
        direction: {dir_css} !important;
        text-align: {align_css} !important;
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 100% !important;
    }}

    /* Sidebar Content */
    [data-testid="stSidebar"], [data-testid="stSidebarContent"] {{
        direction: {dir_css} !important;
        text-align: {align_css} !important;
    }}

    /* Typography & Markdown elements */
    h1, h2, h3, h4, h5, h6, p, label, li, [data-testid="stMarkdownContainer"] {{
        direction: {dir_css} !important;
        text-align: {align_css} !important;
        color: {app_text} !important;
    }}
    .stMarkdown p, .stMarkdown span {{
        color: {expander_details_text} !important;
    }}

    /* Inline Code Spans across ALL tabs */
    code, [data-testid="stMarkdownContainer"] code {{
        background: {code_bg} !important;
        color: {code_col} !important;
        border: 1px solid {code_bord} !important;
        font-weight: 600 !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
        font-size: 12.5px !important;
    }}

    /* File Uploader Dropzone */
    [data-testid="stFileUploadDropzone"] {{
        background: {dropzone_bg} !important;
        border: 2px dashed {dropzone_border} !important;
        color: {dropzone_text} !important;
        border-radius: 8px !important;
    }}
    [data-testid="stFileUploadDropzone"] * {{
        color: {dropzone_text} !important;
    }}
    [data-testid="stFileUploadDropzone"] button {{
        background: #0284c7 !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: 600 !important;
    }}
    [data-testid="stUploadedFileData"] {{
        background: {expander_bg} !important;
        border: 1px solid {expander_border} !important;
        color: {app_text} !important;
    }}

    /* Alert Boxes (st.info, st.success, st.warning, st.error) */
    div[data-testid="stAlert"] {{
        background: {alert_bg} !important;
        border: 1px solid {alert_border} !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04) !important;
        border-radius: 8px !important;
    }}
    div[data-testid="stAlert"] * {{
        color: {alert_text} !important;
    }}

    /* Main Header Banner */
    .main-header {{
        background: {header_bg} !important;
        color: {header_title_col} !important;
        padding: 16px 22px;
        border-radius: 10px;
        margin-bottom: 20px;
        direction: {dir_css} !important;
        text-align: {align_css} !important;
        border: 1px solid {header_border} !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, {'0.06' if is_light else '0.15'}) !important;
        box-sizing: border-box !important;
        width: 100% !important;
    }}
    .header-layout {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 14px;
        direction: {dir_css} !important;
    }}
    .header-brand-section {{
        display: flex;
        align-items: center;
        gap: 16px;
        direction: {dir_css} !important;
    }}
    .header-info-container h2 {{
        margin: 0 0 4px 0 !important;
        font-size: 20px !important;
        font-weight: 700 !important;
        color: {header_title_col} !important;
    }}
    .header-info-container h2 span {{
        color: {header_title_col} !important;
    }}
    .header-info-container p {{
        margin: 0 !important;
        font-size: 13px !important;
        color: {header_sub_col} !important;
    }}
    .header-info-container p strong {{
        color: {header_title_col} !important;
    }}
    .header-info-container a {{
        color: {header_link_col} !important;
        text-decoration: none !important;
    }}
    .header-controls-section {{
        display: flex;
        align-items: center;
        gap: 10px;
        flex-wrap: wrap;
        direction: {dir_css} !important;
    }}
    .header-badge-section {{
        background: {header_badge_bg} !important;
        border: 1px solid {header_badge_border} !important;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
        color: {header_badge_col} !important;
        white-space: nowrap;
        direction: ltr !important;
    }}

    /* Settings Gear Dropdown Component */
    .sb-settings-dropdown {{
        position: relative;
        display: inline-block;
        direction: {dir_css} !important;
        text-align: {align_css} !important;
    }}
    .sb-settings-dropdown summary {{
        list-style: none !important;
        cursor: pointer;
    }}
    .sb-settings-dropdown summary::-webkit-details-marker {{
        display: none !important;
    }}
    .sb-settings-btn {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s ease;
        user-select: none;
        background: {settings_btn_bg} !important;
        color: {settings_btn_col} !important;
        border: 1px solid {settings_btn_bord} !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
    }}
    .sb-settings-btn:hover {{
        border-color: #0284c7 !important;
        color: #0284c7 !important;
        transform: translateY(-1px);
    }}
    .sb-settings-menu {{
        position: absolute;
        top: calc(100% + 8px);
        {'left: 0;' if is_rtl else 'right: 0;'}
        z-index: 99999999 !important;
        min-width: 220px;
        padding: 12px 14px;
        border-radius: 10px;
        box-shadow: 0 10px 25px -5px rgba(0,0,0,0.35), 0 8px 10px -6px rgba(0,0,0,0.2);
        background: {settings_menu_bg} !important;
        border: 1px solid {settings_menu_border} !important;
        direction: {dir_css} !important;
        text-align: {align_css} !important;
    }}
    .sb-settings-group {{
        margin-bottom: 6px;
    }}
    .sb-settings-title {{
        font-size: 11.5px;
        font-weight: 700;
        color: {'#64748b' if is_light else '#94a3b8'};
        margin-bottom: 6px;
        letter-spacing: 0.3px;
    }}
    .sb-settings-options {{
        display: flex;
        gap: 6px;
    }}
    .sb-setting-item {{
        flex: 1;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 5px;
        padding: 6px 8px;
        border-radius: 6px;
        font-size: 12.5px;
        font-weight: 600;
        text-decoration: none !important;
        transition: all 0.15s ease;
        background: {settings_item_bg} !important;
        color: {settings_item_col} !important;
        border: 1px solid {settings_item_bord} !important;
    }}
    .sb-setting-item:hover {{
        border-color: #0284c7 !important;
        color: #0284c7 !important;
    }}
    .sb-setting-item.active {{
        background: linear-gradient(135deg, #0284c7, #0369a1) !important;
        color: #ffffff !important;
        border-color: #0284c7 !important;
        box-shadow: 0 0 8px rgba(2, 132, 199, 0.4);
    }}
    .sb-settings-divider {{
        height: 1px;
        background: {settings_divider} !important;
        margin: 10px 0;
    }}

    /* Metric Cards Styling */
    div[data-testid="stMetric"] {{
        text-align: {align_css} !important;
        direction: {dir_css} !important;
        background: {metric_bg} !important;
        padding: 14px 16px !important;
        border-radius: 8px !important;
        border: 1px solid {metric_border} !important;
        box-shadow: {metric_shadow} !important;
        box-sizing: border-box !important;
        min-height: 90px !important;
    }}
    [data-testid="stMetricLabel"],
    [data-testid="stMetricLabel"] * {{
        text-align: {align_css} !important;
        direction: {dir_css} !important;
        justify-content: flex-start !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        color: {metric_label_col} !important;
    }}
    [data-testid="stMetricValue"],
    [data-testid="stMetricValue"] * {{
        text-align: {align_css} !important;
        direction: {dir_css} !important;
        font-weight: 700 !important;
        font-size: 24px !important;
        color: {metric_val_col} !important;
    }}
    [data-testid="stMetricDelta"] svg {{
        fill: {metric_delta_col} !important;
    }}
    [data-testid="stMetricDelta"] div,
    [data-testid="stMetricDelta"] p {{
        color: {metric_delta_col} !important;
        font-weight: 600 !important;
    }}

    /* Streamlit Tabs Navigation Bar */
    div[data-baseweb="tab-list"] {{
        direction: {dir_css} !important;
        justify-content: flex-start !important;
        gap: 8px !important;
        border-bottom: 2px solid {'#e2e8f0' if is_light else 'rgba(255, 255, 255, 0.1)'} !important;
    }}
    button[data-baseweb="tab"] {{
        direction: {dir_css} !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        padding: 10px 16px !important;
        color: {tab_text} !important;
        background: transparent !important;
        border: none !important;
        border-bottom: 3px solid transparent !important;
        transition: all 0.2s ease !important;
    }}
    button[data-baseweb="tab"]:hover {{
        color: {tab_active_text} !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        color: {tab_active_text} !important;
        border-bottom: 3px solid {tab_active_border} !important;
        background: {'rgba(2, 132, 199, 0.05)' if is_light else 'rgba(56, 189, 248, 0.05)'} !important;
        border-radius: 4px 4px 0 0 !important;
    }}

    /* Native Styled HTML Tables */
    .custom-table-container {{
        width: 100%;
        max-height: 480px;
        overflow-y: auto;
        overflow-x: auto;
        margin: 10px 0 20px 0;
        border-radius: 8px;
        border: 1px solid {table_border};
        background: {table_container_bg};
        box-shadow: {table_shadow};
    }}
    .sb-table {{
        width: 100%;
        border-collapse: collapse;
        direction: {dir_css} !important;
        text-align: {align_css} !important;
        font-family: inherit;
        font-size: 13.5px;
        background: {table_container_bg};
    }}
    .sb-table thead tr {{
        background: {table_th_bg};
        border-bottom: {table_th_border};
    }}
    .sb-table th {{
        position: sticky;
        top: 0;
        background: {table_th_bg};
        z-index: 2;
        padding: 12px 14px;
        color: {table_th_col};
        font-weight: 700;
        text-align: {align_css} !important;
        direction: {dir_css} !important;
        white-space: nowrap;
        font-size: 13px;
    }}
    .sb-table tbody tr {{
        border-bottom: {table_tr_border};
        transition: background-color 0.15s ease;
    }}
    .sb-table tbody tr:nth-child(even) {{
        background: {table_tr_even};
    }}
    .sb-table tbody tr:hover {{
        background: {table_tr_hover};
    }}
    .sb-table td {{
        padding: 11px 14px;
        color: {table_td_col};
        text-align: {align_css} !important;
        direction: {dir_css} !important;
        vertical-align: middle;
        font-size: 13.5px;
    }}

    /* Badges */
    .badge-success {{
        background: {badge_succ_bg};
        color: {badge_succ_col};
        padding: 3px 9px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 600;
        display: inline-block;
        border: {badge_succ_bord};
    }}
    .badge-attention {{
        background: {badge_att_bg};
        color: {badge_att_col};
        padding: 3px 9px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 600;
        display: inline-block;
        border: {badge_att_bord};
    }}
    .badge-info {{
        background: {badge_info_bg};
        color: {badge_info_col};
        padding: 3px 9px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 600;
        display: inline-block;
        border: {badge_info_bord};
    }}

    /* Refined Collapsible Dropdown Windows (st.expander) */
    div[data-testid="stExpander"] {{
        background: {expander_bg} !important;
        border: 1px solid {expander_border} !important;
        border-radius: 8px !important;
        margin-bottom: 12px !important;
        box-shadow: {expander_shadow} !important;
        max-width: 620px !important;
        width: 100% !important;
        transition: max-width 0.25s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    }}
    div[data-testid="stExpander"]:has(details[open]) {{
        max-width: 100% !important;
    }}
    div[data-testid="stExpander"]:hover {{
        border-color: {expander_summary_hover} !important;
        box-shadow: 0 4px 14px rgba(2, 132, 199, 0.12) !important;
    }}
    /* Universal Expander Header Title & Icon Styling */
    div[data-testid="stExpander"] summary,
    div[data-testid="stExpander"] summary *,
    details summary,
    details summary * {{
        direction: {dir_css} !important;
        text-align: {align_css} !important;
        color: {expander_summary_col} !important;
        font-weight: 600 !important;
        font-size: 15px !important;
    }}
    div[data-testid="stExpander"] summary {{
        padding: 11px 16px !important;
        background: {expander_summary_bg} !important;
        border-radius: 8px !important;
        border-bottom: {expander_summary_border} !important;
    }}
    div[data-testid="stExpander"] summary:hover,
    div[data-testid="stExpander"] summary:hover * {{
        color: {expander_summary_hover} !important;
    }}
    div[data-testid="stExpander"] summary svg,
    div[data-testid="stExpander"] summary [data-testid="stIconMaterial"] {{
        color: {expander_summary_hover} !important;
        fill: {expander_summary_hover} !important;
    }}

    /* Expander Details Inside: High Contrast Text for Light & Dark Themes */
    div[data-testid="stExpander"] div[data-testid="stExpanderDetails"],
    div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] p,
    div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] span,
    div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] label,
    div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] li {{
        color: {expander_details_text} !important;
    }}
    div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] strong,
    div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] b,
    div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] h1,
    div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] h2,
    div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] h3,
    div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] h4,
    div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] h5,
    div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] h6 {{
        color: {expander_details_head} !important;
    }}

    /* =========================================================================
       COMPREHENSIVE MOBILE RESPONSIVE ADAPTATIONS (<= 768px)
       ========================================================================= */
    @media (max-width: 768px) {{
        /* Reduce viewport container padding */
        .main .block-container {{
            padding-top: 0.85rem !important;
            padding-bottom: 2rem !important;
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
            max-width: 100% !important;
        }}

        /* Header Banner Responsive Layout */
        .main-header {{
            padding: 12px 14px !important;
            margin-bottom: 14px !important;
            border-radius: 8px !important;
        }}
        .header-layout {{
            flex-direction: column !important;
            align-items: stretch !important;
            gap: 12px !important;
        }}
        .header-brand-section {{
            flex-direction: column !important;
            align-items: flex-start !important;
            gap: 8px !important;
            width: 100% !important;
        }}
        .header-logo-box {{
            padding: 6px 10px !important;
        }}
        .header-logo-box svg {{
            width: 115px !important;
            height: auto !important;
        }}
        .header-info-container {{
            width: 100% !important;
        }}
        .header-info-container h2 {{
            font-size: 16px !important;
            line-height: 1.35 !important;
            margin: 0 0 4px 0 !important;
            word-break: break-word !important;
        }}
        .header-info-container p {{
            font-size: 11.5px !important;
            line-height: 1.4 !important;
            word-break: break-word !important;
        }}
        .header-controls-section {{
            width: 100% !important;
            display: flex !important;
            justify-content: space-between !important;
            align-items: center !important;
            flex-wrap: wrap !important;
            gap: 8px !important;
            padding-top: 8px !important;
            border-top: 1px solid rgba(75, 189, 219, 0.2) !important;
        }}
        .header-badge-section {{
            font-size: 11px !important;
            padding: 4px 10px !important;
            white-space: normal !important;
            text-align: center !important;
        }}
        .top-flags-bar {{
            gap: 6px !important;
        }}
        .lang-flag-pill {{
            padding: 4px 8px !important;
            font-size: 11.5px !important;
        }}

        /* Streamlit Tabs Navigation Bar */
        div[data-baseweb="tab-list"] {{
            overflow-x: auto !important;
            flex-wrap: nowrap !important;
            -webkit-overflow-scrolling: touch !important;
            scrollbar-width: thin !important;
            gap: 4px !important;
            padding-bottom: 6px !important;
        }}
        button[data-baseweb="tab"] {{
            font-size: 12px !important;
            padding: 8px 10px !important;
            white-space: nowrap !important;
            flex-shrink: 0 !important;
        }}

        /* Compact 2x2 Grid for Metric Cards on Mobile */
        div[data-testid="stHorizontalBlock"]:has(div[data-testid="stMetric"]) {{
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: wrap !important;
            gap: 8px !important;
            width: 100% !important;
        }}
        div[data-testid="stHorizontalBlock"]:has(div[data-testid="stMetric"]) > div[data-testid="stColumn"] {{
            width: calc(50% - 4px) !important;
            min-width: calc(50% - 4px) !important;
            max-width: calc(50% - 4px) !important;
            flex: 0 0 calc(50% - 4px) !important;
            margin: 0 !important;
            box-sizing: border-box !important;
        }}
        div[data-testid="stMetric"] {{
            padding: 10px 12px !important;
            min-height: 78px !important;
            border-radius: 6px !important;
        }}
        [data-testid="stMetricLabel"],
        [data-testid="stMetricLabel"] * {{
            font-size: 11px !important;
            line-height: 1.25 !important;
        }}
        [data-testid="stMetricValue"],
        [data-testid="stMetricValue"] * {{
            font-size: 18.5px !important;
            margin: 2px 0 !important;
        }}
        [data-testid="stMetricDelta"] div,
        [data-testid="stMetricDelta"] p {{
            font-size: 10.5px !important;
        }}

        /* Expander Containers & Headers */
        div[data-testid="stExpander"] {{
            max-width: 100% !important;
            margin-bottom: 8px !important;
            border-radius: 6px !important;
        }}
        div[data-testid="stExpander"] summary,
        div[data-testid="stExpander"] summary * {{
            font-size: 13px !important;
            line-height: 1.35 !important;
        }}
        div[data-testid="stExpander"] summary {{
            padding: 9px 12px !important;
        }}

        /* Tab 2 Briefing Banner */
        .tab2-brief-banner {{
            padding: 10px 14px !important;
            margin-bottom: 12px !important;
            border-radius: 6px !important;
        }}
        .tab2-brief-banner h3 {{
            font-size: 15px !important;
            line-height: 1.3 !important;
        }}
        .tab2-brief-banner p {{
            font-size: 11.5px !important;
            line-height: 1.4 !important;
        }}

        /* Responsive HTML Tables */
        .custom-table-container {{
            margin: 6px 0 14px 0 !important;
            max-height: 380px !important;
            -webkit-overflow-scrolling: touch !important;
            border-radius: 6px !important;
        }}
        .sb-table th,
        .sb-table td {{
            padding: 8px 10px !important;
            font-size: 11.5px !important;
            white-space: nowrap !important;
        }}
        .badge-success, .badge-attention, .badge-info {{
            font-size: 10.5px !important;
            padding: 2px 5px !important;
        }}

        /* Touch target improvements */
        button[kind="primary"],
        button[kind="secondary"],
        .stButton button {{
            min-height: 42px !important;
            font-size: 13px !important;
        }}

        /* Sidebar overlay width on mobile */
        section[data-testid="stSidebar"] {{
            width: 86vw !important;
            max-width: 320px !important;
        }}
    }}
</style>
""", unsafe_allow_html=True)


def render_styled_table(df: pd.DataFrame) -> None:
    """Renders a fully responsive, RTL/LTR-aware HTML table without canvas truncation."""
    if df is None or df.empty:
        st.info(t("no_data_table", lang))
        return

    headers = df.columns.tolist()
    html = [f'<div class="custom-table-container"><table class="sb-table" style="direction: {dir_css} !important; text-align: {align_css} !important;">']
    html.append(f'<thead><tr style="direction: {dir_css} !important; text-align: {align_css} !important;">')
    for h in headers:
        html.append(f'<th style="text-align: {align_css} !important; direction: {dir_css} !important;">{h}</th>')
    html.append("</tr></thead><tbody>")

    for _, row in df.iterrows():
        html.append(f'<tr style="direction: {dir_css} !important; text-align: {align_css} !important;">')
        for h in headers:
            val = str(row[h]) if pd.notna(row[h]) else "-"
            # Custom formatting badges
            if any(w in val for w in ["עמד בתקן", "תקין", "100.0%", "Met SLA", "Optimal"]):
                html.append(f'<td style="text-align: {align_css} !important;"><span class="badge-success">{val}</span></td>')
            elif any(w in val for w in ["חריגה", "ממתין", "בהמתנה", "דרוש תיאום", "פתוחה", "Breached", "Pending", "Open", "Needs Coordination", "exceeding"]):
                html.append(f'<td style="text-align: {align_css} !important;"><span class="badge-attention">{val}</span></td>')
            elif any(w in val for w in ["מעקב", "שיפור", "אדיבות", "יזומה", "תשומת לב", "Improving", "Monitoring", "Courtesy", "Follow-up"]):
                html.append(f'<td style="text-align: {align_css} !important;"><span class="badge-info">{val}</span></td>')
            else:
                html.append(f'<td style="text-align: {align_css} !important;">{val}</td>')
        html.append("</tr>")
    html.append("</tbody></table></div>")

    st.markdown("".join(html), unsafe_allow_html=True)


# Official JAYBEE Vector Logo
JAYBEE_LOGO_SVG = """<svg width="140" height="34" viewBox="0 0 134 34" fill="none" xmlns="http://www.w3.org/2000/svg">
<g clip-path="url(#clip0_jb)">
<path d="M42.3543 8.99414V25.1151C42.3543 26.0493 41.949 26.5165 41.1391 26.5165H40.3867V30.0212H41.6594C43.145 30.0212 44.2829 29.6515 45.0736 28.9115C45.8644 28.1714 46.2604 26.9742 46.2604 25.3193V8.99414H42.3543Z" fill="white"/>
<path d="M60.8213 8.99493V11.3899C60.416 10.5718 59.8467 9.91515 59.1142 9.41867C58.381 8.92219 57.3582 8.67395 56.0471 8.67395C55.0051 8.67395 54.0359 8.88349 53.1387 9.30189C52.2422 9.72097 51.4561 10.2949 50.781 11.0249C50.1053 11.7549 49.5751 12.6018 49.1896 13.5654C48.8035 14.529 48.6105 15.5566 48.6105 16.6463C48.6105 18.1071 48.9437 19.4357 49.6088 20.6329C50.2746 21.83 51.1718 22.7843 52.2997 23.495C53.4283 24.2057 54.6772 24.5607 56.0471 24.5607C57.417 24.5607 58.4438 24.2978 59.1862 23.7726C59.9287 23.2467 60.5026 22.5561 60.9079 21.6992V24.181H64.6982V8.99493H60.8213ZM60.3869 18.8078C60.0398 19.4698 59.5525 20.0003 58.9257 20.3993C58.299 20.7984 57.5512 20.9979 56.6838 20.9979C55.8164 20.9979 55.1255 20.7937 54.4987 20.3846C53.8719 19.9756 53.3846 19.4357 53.0375 18.7637C52.6904 18.0924 52.5172 17.3764 52.5172 16.6177C52.5172 15.8195 52.6904 15.0888 53.0375 14.4269C53.3846 13.7656 53.8719 13.235 54.4987 12.8353C55.1255 12.4369 55.854 12.2367 56.6838 12.2367C57.5135 12.2367 58.299 12.4409 58.9257 12.85C59.5525 13.2591 60.0398 13.7949 60.3869 14.4562C60.734 15.1182 60.9079 15.8482 60.9079 16.6463C60.9079 17.4445 60.734 18.1458 60.3869 18.8078Z" fill="white"/>
<path d="M77.8707 8.99414L74.9478 17.6679C74.678 18.4466 74.4658 19.2548 74.3118 20.0916C74.157 19.2548 73.9448 18.4466 73.6751 17.6679L70.7528 8.99414H66.0361L71.9971 23.4795L71.7941 24.1221C71.5819 24.7835 71.2348 25.334 70.7528 25.7724C70.2701 26.2102 69.6533 26.429 68.9009 26.429C68.2642 26.429 67.6758 26.361 67.1356 26.2249L66.5571 29.9918C66.9426 30.1086 67.3769 30.1867 67.8589 30.2261C68.3409 30.2648 68.7753 30.2841 69.1614 30.2841C70.9359 30.2841 72.3343 29.8117 73.3564 28.8674C74.3792 27.9232 75.2083 26.682 75.845 25.1445L82.5001 8.99414H77.8707Z" fill="white"/>
<path d="M99.3472 13.5644C98.961 12.6008 98.4308 11.754 97.7558 11.0239C97.0801 10.2939 96.2946 9.71998 95.3974 9.3009C94.5003 8.8825 93.531 8.67296 92.4897 8.67296C91.1972 8.67296 90.1843 8.91653 89.4517 9.403C88.7178 9.89014 88.1493 10.5321 87.744 11.3302V2.86133H83.8379V24.18H87.6283V21.6983C88.0335 22.5551 88.6074 23.2458 89.3499 23.7716C90.0924 24.2968 91.139 24.5597 92.4897 24.5597C93.8404 24.5597 95.1323 24.2047 96.251 23.494C97.3697 22.7833 98.2622 21.8291 98.9273 20.6319C99.5931 19.4347 99.9257 18.1061 99.9257 16.6454C99.9257 15.5556 99.7326 14.528 99.3472 13.5644ZM95.4986 18.7627C95.1515 19.4347 94.6642 19.9746 94.0375 20.3837C93.4107 20.7927 92.6821 20.9969 91.853 20.9969C91.0239 20.9969 90.2616 20.7974 89.6249 20.3983C88.9882 19.9993 88.4964 19.4688 88.1493 18.8068C87.8021 18.1448 87.6283 17.4248 87.6283 16.6454C87.6283 15.8659 87.8021 15.1172 88.1493 14.4552C88.4964 13.7939 88.9882 13.2581 89.6249 12.849C90.2616 12.4399 91.0041 12.2358 91.853 12.2358C92.7019 12.2358 93.4107 12.4359 94.0375 12.8343C94.6642 13.2341 95.1515 13.7646 95.4986 14.4259C95.8457 15.0878 96.0196 15.8186 96.0196 16.6167C96.0196 17.4148 95.8457 18.0914 95.4986 18.7627Z" fill="white"/>
<path d="M116.068 12.6018C115.421 11.3853 114.525 10.4163 113.377 9.69628C112.229 8.97625 110.903 8.61523 109.399 8.61523C107.895 8.61523 106.558 8.97625 105.391 9.69628C104.224 10.4163 103.303 11.3853 102.628 12.6018C101.952 13.8189 101.615 15.1569 101.615 16.6177C101.615 18.0784 101.938 19.4064 102.584 20.6035C103.23 21.8014 104.142 22.7603 105.319 23.4803C106.495 24.2003 107.855 24.5607 109.399 24.5607C110.943 24.5607 112.224 24.2591 113.421 23.6558C114.617 23.0526 115.513 22.2731 116.112 21.3196L113.074 19.012C112.727 19.5965 112.239 20.083 111.612 20.4721C110.985 20.8618 110.247 21.0566 109.399 21.0566C108.415 21.0566 107.6 20.7744 106.954 20.2098C106.307 19.6453 105.878 18.9152 105.666 18.019H116.922C116.96 17.7661 116.989 17.5225 117.009 17.289C117.027 17.0554 117.037 16.8319 117.037 16.6177C117.037 15.1569 116.714 13.8189 116.068 12.6018ZM105.666 15.0695C105.878 14.1546 106.312 13.4152 106.969 12.85C107.624 12.2855 108.415 12.0032 109.341 12.0032C110.266 12.0032 111.121 12.3055 111.786 12.9087C112.451 13.512 112.89 14.2327 113.102 15.0695H105.666Z" fill="white"/>
<path d="M133.031 12.6017C132.384 11.3852 131.487 10.4163 130.34 9.69622C129.192 8.97619 127.866 8.61517 126.361 8.61517C124.856 8.61517 123.521 8.97619 122.354 9.69622C121.187 10.4163 120.266 11.3852 119.591 12.6017C118.915 13.8189 118.578 15.1569 118.578 16.6176C118.578 18.0784 118.901 19.4063 119.547 20.6035C120.193 21.8013 121.105 22.7602 122.282 23.4803C123.458 24.2003 124.818 24.5606 126.361 24.5606C127.904 24.5606 129.187 24.259 130.384 23.6558C131.579 23.0525 132.476 22.2731 133.074 21.3195L130.036 19.0119C129.689 19.5965 129.201 20.083 128.575 20.472C127.948 20.8617 127.21 21.0566 126.361 21.0566C125.377 21.0566 124.563 20.7743 123.916 20.2097C123.27 19.6452 122.841 18.9152 122.629 18.019H133.884C133.923 17.766 133.952 17.5225 133.971 17.2889C133.99 17.0554 134 16.8318 134 16.6176C134 15.1569 133.677 13.8189 133.031 12.6017ZM122.629 15.0694C122.841 14.1545 123.275 13.4152 123.931 12.8499C124.587 12.2854 125.377 12.0031 126.304 12.0031C127.23 12.0031 128.083 12.3054 128.748 12.9087C129.414 13.5119 129.853 14.2326 130.065 15.0694H122.629Z" fill="white"/>
<path d="M26.7029 17.0933C27.1227 17.894 27.3329 18.7776 27.3329 19.7432C27.3329 20.7088 27.1227 21.5269 26.7029 22.3397C26.2824 23.1525 25.6933 23.8058 24.935 24.3003C24.1766 24.7947 23.2953 25.0423 22.2923 25.0423C21.2894 25.0423 20.3671 24.8014 19.5968 24.3183C18.8272 23.8358 18.2322 23.1938 17.8117 22.3924C17.3919 21.5923 17.1816 20.7208 17.1816 19.7785C17.1816 18.8363 17.3919 17.9294 17.8117 17.1286C18.2322 16.3279 18.8272 15.6799 19.5968 15.1854C20.3671 14.6909 21.2649 14.4434 22.2923 14.4434C23.3198 14.4434 24.1766 14.6849 24.935 15.1674C25.6933 15.6505 26.2824 16.2925 26.7029 17.0933Z" fill="#4BBDDB"/>
<path d="M33.0178 17C32.7963 18.1258 32.4684 19.2248 32.0465 20.2872C32.0538 20.1197 32.0578 19.9495 32.0578 19.7787C32.0578 18.4594 31.8244 17.2169 31.3576 16.0511C30.8909 14.8853 30.2489 13.861 29.4324 12.9774C28.6152 12.0939 27.6651 11.3999 26.5795 10.8927C25.4945 10.3869 24.3223 10.1333 23.0622 10.1333C21.4986 10.1333 20.2734 10.4283 19.3868 11.0169C18.4996 11.6054 17.8113 12.3829 17.3214 13.3485V3.10252H12.5962V28.8935H17.1812V25.8906C17.6712 26.927 18.3654 27.7631 19.2639 28.3991C20.1624 29.035 21.4285 29.3526 23.0622 29.3526C23.9197 29.3526 24.7349 29.2405 25.5071 29.0163C22.0341 31.7963 17.7578 33.5 13.4219 33.5C4.39393 33.5 -1.47114 26.1128 0.322564 17C1.08289 13.1363 3.09874 9.58214 5.85639 6.77075V22.6048C5.85639 23.7352 5.36648 24.3004 4.38666 24.3004H3.47625V28.5405H5.01673C6.81308 28.5405 8.18959 28.0928 9.14694 27.1979C10.1036 26.3024 10.5823 24.8536 10.5823 22.8523V3.10719C13.4524 1.45693 16.6682 0.5 19.9177 0.5C28.9464 0.5 34.8115 7.88783 33.0178 17Z" fill="#4BBDDB"/>
</g>
<defs>
<clipPath id="clip0_jb">
<rect width="134" height="33" fill="white" transform="translate(0 0.5)"/>
</clipPath>
</defs>
</svg>"""

# Ensure database is initialized
db.init_db()

# Session State Initialization for Report ID
keep_arch = (st.query_params.get("arch") == "1")
if "report_id" in st.query_params:
    try:
        qid = int(st.query_params["report_id"])
        st.session_state.active_report_id = qid
    except Exception:
        pass

if "active_report_id" not in st.session_state:
    latest = db.get_latest_report()
    if latest:
        st.session_state.active_report_id = latest["id"]
    else:
        sample_pdf = os.path.join(os.path.dirname(__file__), "Log_Report_-_Providers_2026_09_23_17.pdf")
        if os.path.exists(sample_pdf):
            try:
                p_rep = parse_smartbutler_document(sample_pdf, filename="Log_Report_-_Providers_2026_09_23_17.pdf")
                new_id = db.save_report(p_rep.to_report_dict(), p_rep.tickets_as_dicts(), p_rep.departments_as_dicts())
                st.session_state.active_report_id = new_id
            except Exception:
                st.session_state.active_report_id = None
        else:
            st.session_state.active_report_id = None

# Sidebar Controls
with st.sidebar:
    st.markdown(f'<div style="background:#0D2838; padding:12px; border-radius:8px; text-align:center; margin-bottom:12px;">{JAYBEE_LOGO_SVG}</div>', unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align:{align_css}; margin:0 0 4px 0;'><span style='direction:ltr; display:inline-block;'>SmartButler<sup>&reg;</sup></span> LiveOps</h3>", unsafe_allow_html=True)
    st.caption(t("by_jaybee", lang))
    
    # Language Switcher in Sidebar
    sb_active_id = st.session_state.active_report_id or 1
    theme_color = "#475569" if is_light else "#94a3b8"
    theme_label_text = t("theme_label", lang)
    bg_he = 'linear-gradient(135deg, #0284c7, #0369a1)' if lang == LANG_HE else ('#ffffff' if is_light else '#1e293b')
    col_he = '#ffffff' if lang == LANG_HE else ('#0f172a' if is_light else '#cbd5e1')
    bord_he = '#38bdf8' if lang == LANG_HE else ('#cbd5e1' if is_light else 'rgba(75, 189, 219, 0.25)')
    sh_he = '0 0 10px rgba(56,189,248,0.4)' if lang == LANG_HE else 'none'

    bg_en = 'linear-gradient(135deg, #0284c7, #0369a1)' if lang == LANG_EN else ('#ffffff' if is_light else '#1e293b')
    col_en = '#ffffff' if lang == LANG_EN else ('#0f172a' if is_light else '#cbd5e1')
    bord_en = '#38bdf8' if lang == LANG_EN else ('#cbd5e1' if is_light else 'rgba(75, 189, 219, 0.25)')
    sh_en = '0 0 10px rgba(56,189,248,0.4)' if lang == LANG_EN else 'none'

    bg_light = 'linear-gradient(135deg, #0284c7, #0369a1)' if is_light else ('#ffffff' if is_light else '#1e293b')
    col_light = '#ffffff' if is_light else ('#0f172a' if is_light else '#cbd5e1')
    bord_light = '#38bdf8' if is_light else ('#cbd5e1' if is_light else 'rgba(75, 189, 219, 0.25)')
    sh_light = '0 0 10px rgba(56,189,248,0.4)' if is_light else 'none'

    bg_dark = 'linear-gradient(135deg, #0284c7, #0369a1)' if not is_light else ('#ffffff' if is_light else '#1e293b')
    col_dark = '#ffffff' if not is_light else ('#0f172a' if is_light else '#cbd5e1')
    bord_dark = '#38bdf8' if not is_light else ('#cbd5e1' if is_light else 'rgba(75, 189, 219, 0.25)')
    sh_dark = '0 0 10px rgba(56,189,248,0.4)' if not is_light else 'none'

    st.markdown(
        f'<div style="margin-top: 10px; margin-bottom: 6px; font-weight: 600; font-size: 13px; color: {theme_color};">🌐 שפה / Language:</div>'
        f'<div style="display:flex; gap:8px; margin-bottom:10px;">'
        f'<a href="?lang={LANG_HE}&report_id={sb_active_id}&theme={theme}" target="_self" style="flex:1; text-align:center; padding:7px 8px; border-radius:6px; text-decoration:none; display:flex; align-items:center; justify-content:center; gap:6px; font-size:13px; font-weight:600; background:{bg_he}; color:{col_he} !important; border:1px solid {bord_he}; box-shadow:{sh_he};">{FLAG_IL_SVG} עברית</a>'
        f'<a href="?lang={LANG_EN}&report_id={sb_active_id}&theme={theme}" target="_self" style="flex:1; text-align:center; padding:7px 8px; border-radius:6px; text-decoration:none; display:flex; align-items:center; justify-content:center; gap:6px; font-size:13px; font-weight:600; background:{bg_en}; color:{col_en} !important; border:1px solid {bord_en}; box-shadow:{sh_en};">{FLAG_GB_SVG} English</a>'
        f'</div>'
        f'<div style="margin-top: 10px; margin-bottom: 6px; font-weight: 600; font-size: 13px; color: {theme_color};">{theme_label_text}</div>'
        f'<div style="display:flex; gap:8px; margin-bottom:12px;">'
        f'<a href="?lang={lang}&report_id={sb_active_id}&theme={THEME_LIGHT}" target="_self" style="flex:1; text-align:center; padding:7px 8px; border-radius:6px; text-decoration:none; display:flex; align-items:center; justify-content:center; gap:6px; font-size:13px; font-weight:600; background:{bg_light}; color:{col_light} !important; border:1px solid {bord_light}; box-shadow:{sh_light};">☀️ {t("theme_light", lang)}</a>'
        f'<a href="?lang={lang}&report_id={sb_active_id}&theme={THEME_DARK}" target="_self" style="flex:1; text-align:center; padding:7px 8px; border-radius:6px; text-decoration:none; display:flex; align-items:center; justify-content:center; gap:6px; font-size:13px; font-weight:600; background:{bg_dark}; color:{col_dark} !important; border:1px solid {bord_dark}; box-shadow:{sh_dark};">🌙 {t("theme_dark", lang)}</a>'
        f'</div>',
        unsafe_allow_html=True
    )

    st.divider()

    historical_reports = db.list_reports()
    if historical_reports:
        active_meta = next((r for r in historical_reports if r["id"] == st.session_state.active_report_id), historical_reports[0])
        if active_meta:
            st.info(t("sidebar_active_box", lang, id=active_meta['id'], filename=active_meta['raw_filename'], tickets=active_meta['total_tickets'], rate=active_meta['overall_success_rate']))
    else:
        st.caption(t("sidebar_empty", lang))

    st.divider()
    st.subheader(t("sidebar_quick_load", lang))
    if st.button(t("sidebar_load_pdf", lang), use_container_width=True):
        sample_pdf = os.path.join(os.path.dirname(__file__), "Log_Report_-_Providers_2026_09_23_17.pdf")
        if os.path.exists(sample_pdf):
            p = parse_smartbutler_document(sample_pdf, "Log_Report_-_Providers_2026_09_23_17.pdf")
            nid = db.save_report(p.to_report_dict(), p.tickets_as_dicts(), p.departments_as_dicts())
            st.session_state.active_report_id = nid
            st.success(t("sidebar_pdf_success", lang, id=nid))
            st.rerun()

    if st.button(t("sidebar_load_csv", lang), use_container_width=True):
        sample_csv = os.path.join(os.path.dirname(__file__), "reports", "sample_smartbutler_digest.csv")
        if os.path.exists(sample_csv):
            p = parse_smartbutler_document(sample_csv, "sample_smartbutler_digest.csv")
            nid = db.save_report(p.to_report_dict(), p.tickets_as_dicts(), p.departments_as_dicts())
            st.session_state.active_report_id = nid
            st.success(t("sidebar_csv_success", lang, id=nid))
            st.rerun()

    st.caption(t("sidebar_footer", lang))

# Load Active Report Data
active_report = None
if st.session_state.active_report_id:
    active_report = db.get_report(st.session_state.active_report_id)

engine = SmartButlerEngine(report_dict=active_report) if active_report else None
kpi = engine.get_kpi_summary() if engine else None

# Header Banner Details
period_text = kpi["period"] if kpi else t("no_report_selected", lang)
site_text = kpi["site"] if kpi else "SmartButler System"
active_id_val = st.session_state.active_report_id or 1
rep_param_he = f"&report_id={active_id_val}" if active_id_val else ""
rep_param_en = f"&report_id={active_id_val}" if active_id_val else ""

# TOP FLAG SWITCHER BAR & HEADER BANNER
st.markdown(f"""
<div class="main-header">
    <div class="header-layout">
        <div class="header-brand-section">
            <div class="header-logo-box" style="background:#0D2838; padding:8px 12px; border-radius:6px; display:inline-flex; align-items:center;">
                {JAYBEE_LOGO_SVG}
            </div>
            <div class="header-info-container">
                <h2><span style="direction:ltr; display:inline-block;">SmartButler<sup>&reg;</sup></span> — {t('header_title', lang).replace('SmartButler® — ', '')}</h2>
                <p>{t('header_subtitle_prefix', lang)} <span style="direction:ltr; display:inline-block;">SmartButler<sup>&reg;</sup></span> {t('header_subtitle_mid', lang)}<a href="https://www.jaybee.com" target="_blank" style="color:#60a5fa; text-decoration:none;">www.jaybee.com</a>) | {t('header_site', lang)}: <strong>{site_text}</strong></p>
            </div>
        </div>
        <div class="header-controls-section">
            <div class="header-badge-section">
                📅 {period_text}
            </div>
            <details class="sb-settings-dropdown">
                <summary class="sb-settings-btn" title="{t('settings_label', lang)}">
                    <span style="font-size:15px; line-height:1;">⚙️</span>
                    <span class="sb-settings-btn-text">{t('settings_label', lang)}</span>
                </summary>
                <div class="sb-settings-menu">
                    <div class="sb-settings-group">
                        <div class="sb-settings-title">🌐 {t('language_label', lang)}</div>
                        <div class="sb-settings-options">
                            <a href="?lang={LANG_HE}{rep_param_he}&theme={theme}" target="_self" class="sb-setting-item {'active' if lang == LANG_HE else ''}">
                                {FLAG_IL_SVG} <span>עברית</span>
                            </a>
                            <a href="?lang={LANG_EN}{rep_param_en}&theme={theme}" target="_self" class="sb-setting-item {'active' if lang == LANG_EN else ''}">
                                {FLAG_GB_SVG} <span>English</span>
                            </a>
                        </div>
                    </div>
                    <div class="sb-settings-divider"></div>
                    <div class="sb-settings-group">
                        <div class="sb-settings-title">🎨 {t('theme_label', lang)}</div>
                        <div class="sb-settings-options">
                            <a href="?lang={lang}{rep_param_he}&theme={THEME_LIGHT}" target="_self" class="sb-setting-item {'active' if is_light else ''}">
                                <span>☀️</span> <span>{t('theme_light', lang)}</span>
                            </a>
                            <a href="?lang={lang}{rep_param_he}&theme={THEME_DARK}" target="_self" class="sb-setting-item {'active' if not is_light else ''}">
                                <span>🌙</span> <span>{t('theme_dark', lang)}</span>
                            </a>
                        </div>
                    </div>
                </div>
            </details>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------------------------------------
# EXACT 4-TAB WORKFLOW
# -------------------------------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    t("tab1_name", lang),
    t("tab2_name", lang),
    t("tab3_name", lang),
    t("tab4_name", lang)
])

# =================================================================================================
# TAB 1: UPLOAD & INGESTION ONLY
# =================================================================================================
with tab1:
    st.subheader(t("tab1_header", lang))

    with st.expander(t("tab1_up_expander", lang), expanded=False):
        st.markdown(t("tab1_up_desc", lang))

        col_up, col_info = st.columns([3, 2])

        with col_up:
            uploaded_file = st.file_uploader(
                t("tab1_file_label", lang),
                type=["pdf", "csv", "json"],
                help=t("tab1_file_help", lang)
            )

            if uploaded_file is not None:
                upload_key = f"{uploaded_file.name}_{uploaded_file.size}"
                # Auto-save and activate immediately upon upload
                if st.session_state.get("last_uploaded_file_key") != upload_key:
                    try:
                        bytes_content = uploaded_file.getvalue()
                        parsed = parse_smartbutler_document(bytes_content, filename=uploaded_file.name)
                        if parsed.total_tickets > 0:
                            rep_id = db.save_report(
                                parsed.to_report_dict(),
                                parsed.tickets_as_dicts(),
                                parsed.departments_as_dicts()
                            )
                            st.session_state.active_report_id = rep_id
                            st.session_state.last_uploaded_file_key = upload_key
                            st.session_state["just_saved_report_id"] = rep_id
                            st.query_params["report_id"] = rep_id
                            st.rerun()
                        else:
                            st.error(t("tab1_no_tickets_err", lang, filename=uploaded_file.name))
                    except Exception as e:
                        st.error(t("tab1_parse_err", lang, err=e))
                else:
                    # File is already active
                    if active_report:
                        st.success(t("tab1_up_success", lang, filename=active_report['raw_filename'], id=active_report['id']))
                        preview_col1, preview_col2 = st.columns(2)
                        with preview_col1:
                            st.write(f"**{t('tab1_title_label', lang)}** {active_report['report_title']}")
                            st.write(f"**{t('tab1_site_label', lang)}** {active_report['site_name']}")
                            st.write(f"**{t('tab1_date_label', lang)}** {active_report['date_range']}")
                        with preview_col2:
                            st.write(f"**{t('tab1_tickets_label', lang)}** {active_report['total_tickets']}")
                            depts_trans = [get_dept_name(d['department'], lang) for d in active_report.get('departments', [])]
                            st.write(f"**{t('tab1_depts_label', lang)}** {', '.join(depts_trans)}")
                            st.write(f"**{t('tab1_sla_label', lang)}** {active_report['overall_success_rate']}%")

                        st.info(t("tab1_next_info", lang))

        with col_info:
            st.markdown(f"#### {t('tab1_spec_title', lang)}")
            st.markdown(t("tab1_spec_body", lang))

    all_reports = db.list_reports()
    if all_reports:
        with st.expander(t("tab1_arch_expander", lang, count=len(all_reports)), expanded=keep_arch):
            st.markdown(f"**{t('tab1_arch_prompt', lang)}**")

            active_id = st.session_state.active_report_id or all_reports[0]["id"]

            # Build RTL/LTR HTML table
            border_active = "border-right: 4px solid #10b981;" if is_rtl else "border-left: 4px solid #10b981;"
            html = [f'<div class="custom-table-container"><table class="sb-table" style="direction: {dir_css} !important; text-align: {align_css} !important;">']
            html.append(f"""<thead><tr>
                <th style="width: 55px; text-align: center;">{t('t1_col_select', lang)}</th>
                <th style="width: 50px; text-align: center;">{t('t1_col_status', lang)}</th>
                <th style="width: 65px; text-align: center;">{t('t1_col_id', lang)}</th>
                <th>{t('t1_col_hotel', lang)}</th>
                <th>{t('t1_col_period', lang)}</th>
                <th style="width: 85px; text-align: center;">{t('t1_col_tickets', lang)}</th>
                <th style="width: 105px; text-align: center;">{t('t1_col_sla', lang)}</th>
                <th style="width: 95px; text-align: center;">{t('t1_col_avg', lang)}</th>
                <th>{t('t1_col_file', lang)}</th>
            </tr></thead><tbody>""")

            for r in all_reports:
                is_active = (r["id"] == active_id)
                row_bg = f"background: rgba(16, 185, 129, 0.12); {border_active}" if is_active else ""

                if is_active:
                    sel_icon = '<span style="display:inline-flex; align-items:center; justify-content:center; width:22px; height:22px; border-radius:50%; background:#10b981; color:#fff; font-size:12px; font-weight:bold; box-shadow:0 0 6px rgba(16,185,129,0.5);">✓</span>'
                else:
                    sel_icon = f'<a href="?report_id={r["id"]}&lang={lang}&arch=1" target="_self" title="{t("t1_col_select", lang)}" style="text-decoration:none;"><span style="display:inline-flex; align-items:center; justify-content:center; width:20px; height:20px; border-radius:50%; border:2px solid #64748b; background:rgba(255,255,255,0.04); color:#94a3b8; font-size:11px; cursor:pointer;">○</span></a>'

                status_circle = '<span style="font-size:15px;">🟢</span>' if is_active else ''

                html.append(f"""<tr onclick="window.location.search='?report_id={r['id']}&lang={lang}&arch=1'" style="cursor: pointer; {row_bg}">
                    <td style="text-align: center; vertical-align: middle;">{sel_icon}</td>
                    <td style="text-align: center; vertical-align: middle;">{status_circle}</td>
                    <td style="text-align: center; vertical-align: middle; font-weight: bold; color: #38bdf8;">#{r['id']}</td>
                    <td style="font-weight: 600; vertical-align: middle;">{r['site_name']}</td>
                    <td style="vertical-align: middle;">{r['date_range']}</td>
                    <td style="text-align: center; font-weight: bold; vertical-align: middle;">{r['total_tickets']}</td>
                    <td style="text-align: center; vertical-align: middle;"><span class="badge-success">{r['overall_success_rate']}%</span></td>
                    <td style="text-align: center; vertical-align: middle;">{r.get('avg_duration_str') or '-'}</td>
                    <td style="vertical-align: middle; font-family: monospace; font-size: 12px; color: #94a3b8;">{r['raw_filename']}</td>
                </tr>""")

            html.append("</tbody></table></div>")
            st.markdown("".join(html), unsafe_allow_html=True)

            active_meta = next((r for r in all_reports if r["id"] == st.session_state.active_report_id), None)
            if active_meta:
                c_info, c_del = st.columns([4, 1])
                with c_info:
                    st.info(t("tab1_active_banner", lang, id=active_meta['id'], site=active_meta['site_name'], period=active_meta['date_range'], tickets=active_meta['total_tickets'], rate=active_meta['overall_success_rate']))
                with c_del:
                    st.markdown("<div style='margin-top:2px;'></div>", unsafe_allow_html=True)
                    if st.button(t("tab1_del_active_btn", lang), use_container_width=True, key="btn_del_active_report"):
                        db.delete_report(active_meta['id'])
                        st.success(t("tab1_del_confirm", lang, id=active_meta['id']))
                        rem = db.list_reports()
                        st.session_state.active_report_id = rem[0]["id"] if rem else None
                        st.rerun()
    else:
        st.info(t("tab1_no_history", lang))


# =================================================================================================
# TAB 2: EXECUTIVE STANDUP BRIEFING
# =================================================================================================
with tab2:
    if not engine:
        st.warning(t("no_report_warn", lang))
    else:
        accent_col = "#0284c7" if is_light else "#38bdf8"
        border_brief = f"border-right: 4px solid {accent_col};" if is_rtl else f"border-left: 4px solid {accent_col};"
        st.markdown(f"""
        <div class="tab2-brief-banner" style="background: {metric_bg}; {border_brief} padding: 14px 20px; border-radius: 8px; margin-bottom: 20px; direction: {dir_css}; text-align: {align_css}; border: 1px solid {metric_border}; box-shadow: {metric_shadow};">
            <h3 style="margin: 0; color: {accent_col};">{t('tab2_brief_header', lang)}</h3>
            <p style="margin: 6px 0 0 0; color: {expander_details_text}; font-size: 14px;">{t('tab2_brief_meta', lang, period=kpi['period'], site=kpi['site'], id=st.session_state.active_report_id)}</p>
        </div>
        """, unsafe_allow_html=True)

        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.metric(t("kpi_total_tickets", lang), f"{kpi['total_tickets']}", delta=t("kpi_active_depts", lang, count=kpi['department_count']))
        with k2:
            succ = kpi['overall_success_rate']
            delta_label = t("kpi_sla_ok", lang) if succ >= 80 else (t("kpi_sla_monitor", lang) if succ < 50 else t("kpi_sla_improve", lang))
            st.metric(t("kpi_sla", lang), f"{succ}%", delta=delta_label, delta_color="normal" if succ >= 80 else "inverse")
        with k3:
            st.metric(t("kpi_avg_duration", lang), f"{kpi['avg_duration_str']}{t('hours_suffix', lang)}", delta=t("kpi_avg_sub", lang))
        with k4:
            st.metric(t("kpi_total_time", lang), f"{kpi['total_time_str']}{t('hours_suffix', lang)}", delta=t("kpi_total_sub", lang))

        st.markdown("---")

        with st.expander(t("tab2_briefing_expander", lang), expanded=False):
            briefing_text = generate_executive_briefing(engine, kpi, lang=lang)
            st.markdown(briefing_text)

        dept_analysis = engine.get_department_analysis()
        with st.expander(t("tab2_dept_comp_expander", lang, count=len(dept_analysis)), expanded=False):
            summary_rows = []
            for d in dept_analysis:
                dept_name = get_dept_name(d["department"], lang)
                status = t("status_optimal_100", lang) if d["success_rate"] == 100 else (t("status_improving", lang) if d["success_rate"] >= 50 else t("status_needs_coordination", lang))
                summary_rows.append({
                    t("t2_col_dept", lang): dept_name,
                    t("t2_col_tickets", lang): d["total_tickets"],
                    t("t2_col_sla", lang): f"{d['success_rate']}%",
                    t("t2_col_avg", lang): f"{d['avg_duration_str']}{t('hours_suffix', lang)}",
                    t("t2_col_total", lang): f"{d['total_time_str']}{t('hours_suffix', lang)}",
                    t("t2_col_status", lang): status
                })
            df_dept_summary = pd.DataFrame(summary_rows)
            render_styled_table(df_dept_summary)


# =================================================================================================
# TAB 3: KEY INSIGHTS & SLA BOTTLENECKS
# =================================================================================================
with tab3:
    if not engine:
        st.warning(t("no_report_warn", lang))
    else:
        st.subheader(t("tab3_header", lang))
        st.caption(t("tab3_caption", lang))

        # 1. Problematic Rooms / Units under Special Focus
        problematic_rooms = engine.detect_problematic_rooms()
        with st.expander(t("t3_sec1_title", lang, count=len(problematic_rooms)), expanded=False):
            if problematic_rooms:
                r_rows = []
                for r in problematic_rooms:
                    depts_str = ", ".join(get_dept_name(dp, lang) for dp in r["departments"])
                    rec_action = t("t3_sec1_courtesy", lang) if r["is_cross_dept"] else t("t3_sec1_routine", lang)
                    status_label = t("t3_sec1_cross_class", lang) if r["is_cross_dept"] else t("t3_sec1_single_class", lang)
                    r_rows.append({
                        t("t3_sec1_col_room", lang): f"{t('room_prefix', lang)}{r['room']}",
                        t("t3_sec1_col_depts", lang): depts_str,
                        t("t3_sec1_col_tickets", lang): r["ticket_count"],
                        t("t3_sec1_col_unresolved", lang): r["unresolved_count"],
                        t("t3_sec1_col_class", lang): status_label,
                        t("t3_sec1_col_rec", lang): rec_action
                    })
                render_styled_table(pd.DataFrame(r_rows))
            else:
                st.success(t("t3_sec1_none", lang))

        # 2. Recurring Issues & Room/Floor Patterns
        room_cat_counts = defaultdict(lambda: {"count": 0, "tickets": [], "depts": set()})
        floor_cluster_counts = defaultdict(lambda: {"total": 0, "categories": Counter()})

        for t_item in engine.tickets:
            loc = str(t_item.get("location", "")).strip()
            spec_cat = classify_specific_request(t_item.get("description", ""), t_item.get("task_category", ""), lang=lang)
            dept_trans = get_dept_name(t_item.get("department", "General"), lang)

            if loc.isdigit():
                room_cat_counts[(loc, spec_cat)]["count"] += 1
                room_cat_counts[(loc, spec_cat)]["tickets"].append(t_item)
                room_cat_counts[(loc, spec_cat)]["depts"].add(dept_trans)

                cluster_label = get_location_cluster(loc, lang=lang)
                floor_cluster_counts[cluster_label]["total"] += 1
                floor_cluster_counts[cluster_label]["categories"][spec_cat] += 1

        recurring_room_rows = []
        for (room, spec_cat), data in sorted(room_cat_counts.items(), key=lambda x: x[1]["count"], reverse=True):
            if data["count"] >= 2:
                durs = [tk.get("duration_minutes") for tk in data["tickets"] if tk.get("duration_minutes") is not None]
                avg_d = f"{round(sum(durs)/len(durs))}{t('mins_suffix', lang)}" if durs else t("pending_label", lang)
                rec_tip = t("t3_sec2_rec_high", lang) if data["count"] >= 3 else t("t3_sec2_rec_normal", lang)
                recurring_room_rows.append({
                    t("t3_sec2_room_col_room", lang): f"{t('room_prefix', lang)}{room}",
                    t("t3_sec2_room_col_type", lang): spec_cat,
                    t("t3_sec2_room_col_count", lang): f"{data['count']}{t('times_suffix', lang)}",
                    t("t3_sec2_room_col_dept", lang): ", ".join(data["depts"]),
                    t("t3_sec2_room_col_avg", lang): avg_d,
                    t("t3_sec2_room_col_rec", lang): rec_tip
                })

        floor_rows = []
        for cluster, cdata in sorted(floor_cluster_counts.items(), key=lambda x: x[1]["total"], reverse=True):
            top_3 = ", ".join([f"{cat} ({cnt})" for cat, cnt in cdata["categories"].most_common(3)])
            floor_rows.append({
                t("t3_sec2_floor_col_cluster", lang): cluster,
                t("t3_sec2_floor_col_total", lang): cdata["total"],
                t("t3_sec2_floor_col_top3", lang): top_3,
                t("t3_sec2_floor_col_insight", lang): t("t3_sec2_floor_heavy", lang) if cdata["total"] > 100 else t("t3_sec2_floor_normal", lang)
            })

        with st.expander(t("t3_sec2_title", lang, rooms=len(recurring_room_rows), floors=len(floor_rows)), expanded=False):
            sub_tab_room, sub_tab_floor = st.tabs([t("t3_sec2_subtab_room", lang), t("t3_sec2_subtab_floor", lang)])

            with sub_tab_room:
                if recurring_room_rows:
                    render_styled_table(pd.DataFrame(recurring_room_rows))
                else:
                    st.info(t("t3_sec2_room_none", lang))

            with sub_tab_floor:
                if floor_rows:
                    render_styled_table(pd.DataFrame(floor_rows))

        # 3. Frequency of Specific Requests
        cat_stats = defaultdict(lambda: {"total": 0, "met": 0, "durations": [], "dept_counts": Counter()})
        for t_item in engine.tickets:
            spec_cat = classify_specific_request(t_item.get("description", ""), t_item.get("task_category", ""), lang=lang)
            cat_stats[spec_cat]["total"] += 1
            if t_item.get("sla_met"):
                cat_stats[spec_cat]["met"] += 1
            if t_item.get("duration_minutes") is not None:
                cat_stats[spec_cat]["durations"].append(t_item.get("duration_minutes"))
            dept_trans = get_dept_name(t_item.get("department", "General"), lang)
            cat_stats[spec_cat]["dept_counts"][dept_trans] += 1

        common_rows = []
        for cat_name, data in sorted(cat_stats.items(), key=lambda x: x[1]["total"], reverse=True):
            tot = data["total"]
            succ_pct = round((data["met"] / tot) * 100, 1) if tot > 0 else 0.0
            avg_m = round(sum(data["durations"]) / len(data["durations"])) if data["durations"] else 0
            main_dept = data["dept_counts"].most_common(1)[0][0] if data["dept_counts"] else get_dept_name("General", lang)
            common_rows.append({
                t("t3_sec3_col_cat", lang): cat_name,
                t("t3_sec3_col_total", lang): tot,
                t("t3_sec3_col_dept", lang): main_dept,
                t("t3_sec3_col_sla", lang): f"{succ_pct}%",
                t("t3_sec3_col_avg", lang): f"{avg_m}{t('mins_suffix', lang)}",
                t("t3_sec3_col_status", lang): t("t3_sec3_stat_target", lang) if succ_pct >= 85 else (t("t3_sec3_stat_monitor", lang) if succ_pct < 60 else t("t3_sec3_stat_ok", lang))
            })

        with st.expander(t("t3_sec3_title", lang, count=len(common_rows)), expanded=False):
            if common_rows:
                render_styled_table(pd.DataFrame(common_rows))

        # 4. Extreme Delays -> Calls Under Extended Duration Tracking
        extreme_breaches = engine.detect_extreme_sla_breaches()
        with st.expander(t("t3_sec4_title", lang, count=len(extreme_breaches)), expanded=False):
            if extreme_breaches:
                ex_rows = []
                for eb in extreme_breaches:
                    t_item = eb["ticket"]
                    dept_trans = get_dept_name(t_item.get("department"), lang)
                    ratio_val = eb["severity_ratio"]
                    ratio_str = t("t3_sec4_ratio_str", lang, ratio=ratio_val) if ratio_val < 900 else t("t3_sec4_unres_str", lang)
                    desc_text = t_item.get("description") if (t_item.get("description") and t_item.get("description") != "-") else (t_item.get("task_category") or t("pending_label", lang))
                    ex_rows.append({
                        t("t3_sec4_col_dept", lang): dept_trans,
                        t("t3_sec4_col_loc", lang): f"{t('room_prefix', lang)}{t_item.get('location')}" if str(t_item.get('location')).isdigit() else t_item.get('location'),
                        t("t3_sec4_col_desc", lang): desc_text,
                        t("t3_sec4_col_dur", lang): t_item.get("duration_str"),
                        t("t3_sec4_col_sla", lang): t_item.get("standard_str"),
                        t("t3_sec4_col_ratio", lang): ratio_str,
                        t("t3_sec4_col_creator", lang): t_item.get("creator"),
                        t("t3_sec4_col_resolver", lang): t_item.get("resolver")
                    })
                render_styled_table(pd.DataFrame(ex_rows))
            else:
                st.info(t("t3_sec4_none", lang))

        # 5. Breaching Staff Tracking (Exclusively Staff Exceeding SLA)
        staff_stats = defaultdict(lambda: {"total": 0, "breaches": 0, "breach_durations": [], "samples": [], "depts": set()})
        for t_item in engine.tickets:
            res = t_item.get("resolver", "").strip()
            if not res or res == "-" or res.lower() == "unassigned":
                continue
            dept_trans = get_dept_name(t_item.get("department", "General"), lang)
            sla_met = t_item.get("sla_met", 1)
            dur_min = t_item.get("duration_minutes") or 0
            std_min = t_item.get("standard_minutes") or 15
            desc = t_item.get("description") if (t_item.get("description") and t_item.get("description") != "-") else (t_item.get("task_category") or "Task")
            loc = f"{t('room_prefix', lang)}{t_item.get('location')}" if str(t_item.get('location')).isdigit() else t_item.get('location')

            staff_stats[res]["total"] += 1
            staff_stats[res]["depts"].add(dept_trans)
            if not sla_met or dur_min > std_min:
                staff_stats[res]["breaches"] += 1
                staff_stats[res]["breach_durations"].append(dur_min)
                if len(staff_stats[res]["samples"]) < 2:
                    staff_stats[res]["samples"].append(f"{desc} in {loc} ({t_item.get('duration_str')}{t('hours_suffix', lang)})")

        breaching_staff_rows = []
        for res_name, sdata in sorted(staff_stats.items(), key=lambda x: x[1]["breaches"], reverse=True):
            if sdata["breaches"] > 0:
                tot = sdata["total"]
                brk = sdata["breaches"]
                comp_pct = round(((tot - brk) / tot) * 100, 1)
                avg_brk = round(sum(sdata["breach_durations"]) / len(sdata["breach_durations"])) if sdata["breach_durations"] else 0
                sample_str = sdata["samples"][0] if sdata["samples"] else "-"
                breaching_staff_rows.append({
                    t("t3_sec5_col_staff", lang): res_name,
                    t("t3_sec5_col_dept", lang): ", ".join(sdata["depts"]),
                    t("t3_sec5_col_breaches", lang): brk,
                    t("t3_sec5_col_total", lang): tot,
                    t("t3_sec5_col_sla", lang): f"{comp_pct}%",
                    t("t3_sec5_col_avg_breach", lang): f"{avg_brk}{t('mins_suffix', lang)}",
                    t("t3_sec5_col_sample", lang): sample_str
                })

        with st.expander(t("t3_sec5_title", lang, count=len(breaching_staff_rows)), expanded=False):
            if breaching_staff_rows:
                render_styled_table(pd.DataFrame(breaching_staff_rows))
            else:
                st.success(t("t3_sec5_none", lang))


# =================================================================================================
# TAB 4: DEPARTMENT MODULES & DETAILED TABLES
# =================================================================================================
with tab4:
    if not engine:
        st.warning(t("no_report_warn", lang))
    else:
        st.subheader(t("tab4_header", lang))
        st.caption(t("tab4_caption", lang))

        dept_analysis = engine.get_department_analysis()
        action_items = generate_departmental_action_items(engine, lang=lang)

        icon_map = {
            "Housekeeping": "🧹",
            "Maintenance": "🔧",
            "Reception": "🛎️",
            "Front Desk": "🛎️",
            "F&B": "🍽️",
            "Food & Beverage": "🍽️",
            "Security": "🛡️"
        }

        for d in dept_analysis:
            raw_dept = d["department"]
            dept_trans = get_dept_name(raw_dept, lang)
            icon = icon_map.get(raw_dept, "📁")
            succ = d["success_rate"]
            status_text = t("tab4_status_ok", lang) if succ >= 80 else (t("tab4_status_improve", lang) if succ >= 50 else t("tab4_status_coords", lang))

            with st.expander(t("tab4_expander_title", lang, icon=icon, dept_name=dept_trans, tickets=d['total_tickets'], succ=succ, status=status_text), expanded=False):
                
                # Mini metric cards
                mc1, mc2, mc3, mc4 = st.columns(4)
                mc1.metric(t("tab4_mc_tickets", lang), d["total_tickets"])
                mc2.metric(t("tab4_mc_sla", lang), f"{succ}%")
                mc3.metric(t("tab4_mc_avg", lang), f"{d['avg_duration_str']}{t('hours_suffix', lang)}")
                mc4.metric(t("tab4_mc_breaches", lang), d["unresolved_count"] + d["breach_count"])

                # Actionable Directives
                st.markdown(t("tab4_actions_title", lang))
                fallback_action = f"Continue standard SLA tracking and routine service pace for {dept_trans}." if lang == LANG_EN else f"המשך מעקב שוטף ועמידה בזמני תקן למחלקת {dept_trans}."
                dept_actions = action_items.get(raw_dept, [fallback_action])
                for act in dept_actions:
                    st.markdown(f"- **{act}**")

                st.markdown(t("tab4_tickets_title", lang))
                t_list = d["tickets"]
                if t_list:
                    formatted_tickets = []
                    for t_item in t_list:
                        status_str = t("t4_stat_met", lang) if t_item.get("sla_met") else (t("t4_stat_open", lang) if t_item.get("duration_str") == "N/A" else t("t4_stat_breach", lang))
                        loc_display = f"{t('room_prefix', lang)}{t_item.get('location')}" if str(t_item.get('location')).isdigit() else t_item.get('location')
                        dur_display = t_item.get("duration_str") if t_item.get("duration_str") != "N/A" else t("waiting_close", lang)

                        formatted_tickets.append({
                            t("t4_col_received", lang): t_item.get("received_at"),
                            t("t4_col_loc", lang): loc_display,
                            t("t4_col_desc", lang): t_item.get("description"),
                            t("t4_col_dur", lang): dur_display,
                            t("t4_col_sla", lang): t_item.get("standard_str"),
                            t("t4_col_status", lang): status_str,
                            t("t4_col_creator", lang): t_item.get("creator"),
                            t("t4_col_resolver", lang): t_item.get("resolver")
                        })
                    df_dept_tickets = pd.DataFrame(formatted_tickets)
                    render_styled_table(df_dept_tickets)
                else:
                    st.info(t("tab4_no_tickets", lang))
