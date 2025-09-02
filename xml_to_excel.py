import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime, timezone

def xml_to_excel_raw(xml_file, excel_file):
    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "espi": "http://naesb.org/espi"
    }
    tree = ET.parse(xml_file)
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

            # ✅ 转换时间戳为可读时间（UTC）
            readable_time = datetime.fromtimestamp(int(start), tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

            # ✅ cost 换算成 CAD
            cost_raw = int(cost) if cost is not None else None
            cost_cad = cost_raw / 100.0 if cost_raw is not None else None

            records.append({
                "time_start (epoch)": start,
                "time_utc": readable_time,
                "duration_sec": duration,
                "value_raw": value,
                "cost_raw (cents)": cost_raw,
                "cost_CAD": cost_cad,
                "tou_raw": tou,
                "quality_raw": quality
            })

    df = pd.DataFrame(records)
    df.to_excel(excel_file, index=False)
    print(f"✅ 已导出原始 + 换算数据到: {excel_file}")

# 用法
xml_to_excel_raw("input.xml", "output_raw.xlsx")
