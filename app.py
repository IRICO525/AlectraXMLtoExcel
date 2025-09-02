import streamlit as st
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime, timezone
from io import BytesIO

def parse_alectra_xml(uploaded_file):
    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "espi": "http://naesb.org/espi"
    }
    uploaded_file.seek(0)
    tree = ET.parse(uploaded_file)
    root = tree.getroot()

    records = []
    for block in root.findall(".//atom:entry/atom:content/espi:IntervalBlock", ns):
        for reading in block.findall("espi:IntervalReading", ns):
            start = reading.find("espi:timePeriod/espi:start", ns).text
            duration = reading.find("espi:timePeriod/espi:duration", ns).text
            value = reading.find("espi:value", ns).text
            cost = reading.find("espi:cost", ns).text if reading.find("espi:cost", ns) is not None else None
            tou = reading.find("espi:tou", ns).text if reading.find("espi:tou", ns) is not None else None
            quality = reading.find("espi:ReadingQuality/espi:quality", ns).text if reading.find("espi:ReadingQuality/espi:quality", ns) is not None else None

            # Convert epoch → readable UTC time
            readable_time = datetime.fromtimestamp(int(start), tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

            # Cost raw (cents) and CAD
            cost_raw = int(cost) if cost is not None else None
            cost_cad = cost_raw / 100.0 if cost_raw is not None else None

            records.append({
                "time_start_epoch": start,
                "time_utc": readable_time,
                "duration_sec": duration,
                "value_raw": value,
                "cost_raw_cents": cost_raw,
                "cost_CAD": cost_cad,
                "tou_raw": tou,
                "quality_raw": quality
            })

    return pd.DataFrame(records)


# ---------------- Streamlit UI ----------------

st.title("⚡ Alectra Green Button XML Parser")

uploaded_file = st.file_uploader("Upload XML file", type=["xml"])

if uploaded_file:
    st.success("✅ File uploaded successfully. Parsing data...")
    df = parse_alectra_xml(uploaded_file)

    st.subheader("📊 Data Preview")
    st.dataframe(df.head(20))  # preview first 20 rows

    # Download button
    output = BytesIO()
    df.to_excel(output, index=False)
    st.download_button(
        label="⬇️ Download full Excel",
        data=output.getvalue(),
        file_name="output_raw.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
