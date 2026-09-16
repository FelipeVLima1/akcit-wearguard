CORES = {
    "fundo": "#f6f8fb",
    "cartao": "#ffffff",
    "texto": "#1e293b",
    "texto_suave": "#64748b",
    "destaque": "#2563eb",
    "faixa_normal": "#dbeafe",
    "evento": "#fecaca",
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
    div[data-testid="stDataFrame"] {{
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        overflow: hidden;
    }}
    button[data-baseweb="tab"] {{
        font-weight: 600;
    }}
</style>
"""
