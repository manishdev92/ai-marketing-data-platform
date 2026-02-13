import streamlit as st
import requests

st.set_page_config(page_title="AI Marketing Recommender", layout="centered")

st.title("AI Marketing Recommendation Demo")
st.caption("Enter a user_id → fetch similar users + campaign recommendations from FastAPI")

# IMPORTANT: inside docker-compose network, use service name "api"
API_BASE = "http://api:8000"

user_id = st.text_input("User ID", value="user_1")

col1, col2 = st.columns([1, 1])
with col1:
    fetch = st.button("Get Recommendations", type="primary")
with col2:
    health = st.button("Check API")

if health:
    try:
        r = requests.get(f"{API_BASE}/docs", timeout=5)
        st.success(f"API reachable ✅ (status={r.status_code})")
    except Exception as e:
        st.error(f"API not reachable ❌ {e}")

if fetch:
    if not user_id.strip():
        st.warning("Please enter a user_id")
    else:
        try:
            r = requests.get(f"{API_BASE}/recommendations/{user_id.strip()}", timeout=10)

            if r.status_code == 404:
                st.warning(r.json().get("detail", "No data found"))
            else:
                r.raise_for_status()
                data = r.json()

                st.subheader("Raw Response")
                st.json(data)

                st.subheader("Similar Users")
                similar = data.get("similar_users", [])
                if similar:
                    st.write(similar)
                else:
                    st.info("No similar users found yet.")

                st.subheader("Recommendations")
                recos = data.get("recommendations", [])
                if recos:
                    for rec in recos:
                        st.write(f"• **{rec.get('campaign_id')}** — score: `{rec.get('score')}`")
                else:
                    st.info("No recommendations returned yet.")
        except Exception as e:
            st.error(f"Error calling API: {e}")
