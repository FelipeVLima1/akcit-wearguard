CORES = {
    "fundo": "#f6f8fb",
    "cartao": "#ffffff",
    "texto": "#1e293b",
    "texto_suave": "#64748b",
    "destaque": "#2563eb",
    "faixa_normal": "#dbeafe",
    "evento": "#fecaca",
    "evento_forte": "#dc2626",
    "limiar_simples": "#f97316",
    "persistencia": "#16a34a",
}

CSS_PERSONALIZADO = f"""
<style>
    .stApp {{
        background-color: {CORES["fundo"]};
    }}
    section[data-testid="stSidebar"] {{
        background-color: {CORES["cartao"]};
        border-right: 1px solid #e2e8f0;
    }}
    h1, h2, h3, h4 {{
        color: {CORES["texto"]};
    }}
    div[data-testid="stMetric"] {{
        background-color: {CORES["cartao"]};
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 14px 16px;
    }}
    div[data-testid="stMetricLabel"] {{
        color: {CORES["texto_suave"]};
    }}
    div[data-testid="stMetricValue"] {{
        color: {CORES["texto"]};
    }}
    div[data-testid="stDataFrame"] {{
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        overflow: hidden;
    }}
    div[data-baseweb="tab-list"] {{
        gap: 4px;
    }}
    button[data-baseweb="tab"] {{
        font-weight: 600;
    }}
    button[data-baseweb="tab"] p {{
        color: {CORES["texto_suave"]} !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] p {{
        color: {CORES["destaque"]} !important;
    }}
    button[data-baseweb="tab"]:hover p {{
        color: {CORES["destaque"]} !important;
    }}
</style>
"""


def montar_cartao_html(label: str, valor: str, cor: str, legenda: str = "") -> str:
    """Monta o HTML de um card colorido (borda de destaque à esquerda) usado no dashboard."""
    legenda_html = f'<div style="font-size:11px;color:{CORES["texto_suave"]};margin-top:4px;">{legenda}</div>' if legenda else ""
    return f"""
    <div style="background-color:{CORES["cartao"]};border-left:5px solid {cor};border-radius:10px;padding:14px 16px;box-shadow:0 1px 3px rgba(15,23,42,0.08);height:100%;">
        <div style="font-size:12px;font-weight:600;color:{CORES["texto_suave"]};text-transform:uppercase;letter-spacing:0.04em;">{label}</div>
        <div style="font-size:26px;font-weight:700;color:{CORES["texto"]};line-height:1.35;margin-top:2px;">{valor}</div>
        {legenda_html}
    </div>
    """
