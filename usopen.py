import streamlit as st
import pandas as pd




st.set_page_config(page_title="US Open Predictions", layout="wide")
st.title("🎾 US Open Predictions — Sardas vs Malhas")

# --------------------
# Estado inicial
# --------------------
if 'matches' not in st.session_state or not st.session_state.matches:
    df = pd.read_csv('backup_palites.csv')
    st.session_state.matches = df.to_dict('records')
else:
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
        st.success(f"✅ Adicionado: {p1} vs {p2}")

st.divider()

# --------------------
# 2) Palpites & Resultados (tabela editável)
# --------------------
if st.session_state.matches:
    st.subheader("📝 Palpites & Resultados")

    edit_rows = []
    for m in st.session_state.matches:
        edit_rows.append({
            "Jogo": m["match"],
            "Predict Sardas": m["pred_sardas"],
            "Predict Malhas": m["pred_malhas"],
            "Resultado Final": m["result"],
        })
    edit_df = pd.DataFrame(edit_rows)

    edited_df = st.data_editor(
        edit_df,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "Jogo": st.column_config.TextColumn("Jogo"),
            "Predict Sardas": st.column_config.TextColumn("Predict Sardas", help="Formato: 3-1, 3–0, etc."),
            "Predict Malhas": st.column_config.TextColumn("Predict Malhas", help="Formato: 1-3, 2–3, etc."),
            "Resultado Final": st.column_config.TextColumn("Resultado Final", help="Ex.: 3-0"),
        },
    )

    # Sincronizar alterações
    for i, row in edited_df.iterrows():
        st.session_state.matches[i]["match"] = row["Jogo"]
        st.session_state.matches[i]["pred_sardas"] = row["Predict Sardas"]
        st.session_state.matches[i]["pred_malhas"] = row["Predict Malhas"]
        st.session_state.matches[i]["result"] = row["Resultado Final"]

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
