import streamlit as st
import pandas as pd
import urllib.parse

st.header("Unterstütze meine Bienen & Genieße ein Glas Honig 🍯 ")

st.write("""
Hier kannst du meinen Honig genießen und gleichzeitig etwas Gutes tun 🐝.  
Dein Beitrag unterstützt meine Bienenvölker und hilft, die Natur zu fördern 🌱.  
Spenden läuft per PayPal und ich bringe dir das Glas persönlich vorbei 🚴‍♂️🍯
""")

# Add an expander for "How it works"
with st.expander("ℹ️ So funktioniert es"):
    st.write("""
    **Schritt 1:** Klicke auf den 🍯 Bestellen Button unter der Honigsorte, die du unterstützen möchtest.  
    **Schritt 2:** Dein Browser öffnet PayPal mit dem gewünschten Betrag – du kannst frei entscheiden, wie viel du spenden möchtest.  
    **Schritt 3:** In den Mitteilungstext an, wie viele Gläser und wo wir uns treffen oder andere Hinweise (z.B. "Treffen am Gartenzaun", "Abholung am Wochenende").  
    """)

# Lagerbestand laden oder anlegen
lager_path = "src/data/honey_stock.csv"
try:
    stock_df = pd.read_csv(lager_path)
except FileNotFoundError:
    stock_df = pd.DataFrame([
        {"Sorte": "Raps", "Vorrat": 10, "Preis (€)": 6.0, "Bild": "src\data\Raps_2025.gif"},
        {"Sorte": "Sommerblüte", "Vorrat": 5, "Preis (€)": 6.0, "Bild": "src\data\Sommerblüte_2025.gif"},
    ])

# Display with columns
st.subheader("📦 Honigsorten of the Year")
col1, col2 = st.columns(2)
for i, row in stock_df.iterrows():
    col = col1 if i % 2 == 0 else col2
    
    # Bild anzeigen
    col.image(f"src/data/{row['Sorte']}_2025.gif")
    
    # Verfügbarkeit
    if row["Vorrat"] > 8:
        status = "🟢 verfügbar"
    elif row["Vorrat"] > 0:
        status = "🟠 bald leer"
    else:
        status = "🔴 ausverkauft"
    col.write(f"**{row['Sorte']}** – {row['Preis (€)']} € – {status}")
    
    # Bestellen Button nur aktiv, wenn verfügbar
    if row["Vorrat"] > 0:
        note = urllib.parse.quote(f"Honig: {row['Sorte']}, Treffpunkt: ...")
        paypal_link = f"https://www.paypal.com/paypalme/Wywiol/{row['Preis (€)']}?note={note}"
        col.markdown(f"""
            <a href="{paypal_link}" target="_blank">
                <button style="
                    padding: 10px 24px;
                    font-size:16px;
                    border-radius:8px;
                    border: 2px solid lightgrey;
                    background-color: white;
                    cursor: pointer;
                    transition: background-color 0.3s;
                " onmouseover="this.style.backgroundColor='#F3B700'" onmouseout="this.style.backgroundColor='white'">
                    🍯 Bestellen
                </button>
            </a>
            """, unsafe_allow_html=True)

       
    else:
        col.button("Ausverkauft", disabled=True)

st.write("---")
st.write("""
Kannst du herausfinden, wann dieser Honig geerntet wurde?  
Klicke auf den Link, um die Details auf einer anderen Seite zu entdecken!
""")
st.page_link("src/app/bee_monitoring.py", label="Bee Health Monitoring", icon="➡️", width="stretch")
