import streamlit as st
import pandas as pd
import os

if 'matches' not in st.session_state:
    if os.path.exists('backup_palites.csv'):
        df = pd.read_csv('backup_palites.csv')
        st.session_state.matches = df.to_dict('records')
    else:
        st.session_state.matches = []
df = pd.DataFrame(st.session_state.matches)

import os




st.set_page_config(page_title="US Open Predictions", layout="wide")
st.title("🎾 US Open Predictions — Sardas vs Malhas")

# --------------------
df = pd.DataFrame(st.session_state.matches)
# Estado inicial
# --------------------
if 'matches' not in st.session_state:
    st.session_state.matches = []
df = pd.DataFrame(st.session_state.matches)



# Util
# --------------------
def _parse_score(s: str):
    """Aceita '3-1', '3–1', espaços, etc. Devolve [a,b] ou None."""
    if not s:
        return None
    try:
        s = s.strip().replace("–", "-").replace("—", "-").replace(" ", "")
        a, b = s.split("-")
        return [int(a), int(b)]
    except Exception:
        return None

def calculate_points(prediction: str, result: str) -> int:
    p = _parse_score(prediction)
    r = _parse_score(result)
    if not p or not r:
        return 0
    points = 0
    # acertou o vencedor
    if (p[0] > p[1] and r[0] > r[1]) or (p[1] > p[0] and r[1] > r[0]):
        points += 3
    # acertou resultado exato
    if p == r:
        points += 2
    return points

st.divider()

# --------------------
# 1) Adicionar jogos
# --------------------
st.subheader("➕ Adicionar jogo")
with st.form("add_match_form", clear_on_submit=True):
    p1 = st.text_input("Jogador 1")
    p2 = st.text_input("Jogador 2")
    ok = st.form_submit_button("Adicionar")
    if ok and p1 and p2:
        st.session_state.matches.append({
            "match": f"{p1} vs {p2}",
            "pred_sardas": "",
            "pred_malhas": "",
            "result": ""
        })
        pd.DataFrame(st.session_state.matches).to_csv('backup_palites.csv', index=False)
        st.success(f"✅ Adicionado: {p1} vs {p2}")

st.divider()

# --------------------
# 2) Palpites & Resultados (tabela editável)
# --------------------
if st.session_state.matches:
    st.subheader("Lista de jogos e palpites")
    df_lista = pd.DataFrame(st.session_state.matches)
    st.table(df_lista)
    st.subheader("📝 Palpites & Resultados")

    for idx, m in enumerate(st.session_state.matches):
        col1, col2, col3, col4 = st.columns([3,2,2,2])
        with col1:
            st.text_input("Jogo", value=m["match"], key=f"match_{idx}")
        with col2:
            st.text_input("Predict Sardas", value=m["pred_sardas"], key=f"sardas_{idx}")
        with col3:
            st.text_input("Predict Malhas", value=m["pred_malhas"], key=f"malhas_{idx}")
        with col4:
            st.text_input("Resultado", value=m["result"], key=f"result_{idx}")

        # Sincronizar os valores
        m["match"] = st.session_state[f"match_{idx}"]
        m["pred_sardas"] = st.session_state[f"sardas_{idx}"]
        m["pred_malhas"] = st.session_state[f"malhas_{idx}"]
        m["result"] = st.session_state[f"result_{idx}"]

    # Guardar automaticamente no CSV
    pd.DataFrame(st.session_state.matches).to_csv('backup_palites.csv', index=False)

st.divider()

# --------------------
# 3) Resultados & Pontuação
# --------------------
if st.session_state.matches:
    st.subheader("📊 Pontuação por jogo")

    total_sardas = 0
    total_malhas = 0
    rows = []
    for m in st.session_state.matches:
        ps = calculate_points(m["pred_sardas"], m["result"])
        pm = calculate_points(m["pred_malhas"], m["result"])
        total_sardas += ps
        total_malhas += pm
        rows.append({
            "Jogo": m["match"],
            "Pontos Sardas": ps,
            "Pontos Malhas": pm
        })

    results_df = pd.DataFrame(rows)
    st.dataframe(results_df, use_container_width=True)

    # Leaderboard
    st.subheader("🏆 Leaderboard")
    c1, c2 = st.columns([1, 1])
    with c1:
        st.metric("Sardas", total_sardas)
    with c2:
        st.metric("Malhas", total_malhas)
else:
    st.info("Ainda não há jogos. Adiciona acima em ➕ Adicionar jogo.")
