"""Task 2 - Step 3: static dashboard mock-up (PowerPoint) built from the cleaned data.

Slide 1: one-page KPI dashboard mock-up (native, editable PowerPoint charts)
Slide 2: the proposed KPIs - formula, rationale, current value
Output: dashboard_mockup.pptx
Run   : python 03_build_dashboard_mockup.py
"""
from pathlib import Path

import pandas as pd
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

BASE = Path(__file__).parent
df = pd.read_csv(BASE / "data" / "cleaned_sales_data.csv", parse_dates=["Order_Date"])

BG, CARD, BORDER = RGBColor(0xF6, 0xF6, 0xF4), RGBColor(0xFF, 0xFF, 0xFF), RGBColor(0xE4, 0xE3, 0xDF)
INK, INK2, BLUE, ORANGE = RGBColor(0x0B, 0x0B, 0x0B), RGBColor(0x52, 0x51, 0x4E), RGBColor(0x2A, 0x78, 0xD6), RGBColor(0xEB, 0x68, 0x34)
FONT = "Calibri"

# ------------------------------------------------------------------ numbers
rev, orders, units = df.Total_Sales.sum(), len(df), int(df.Quantity.sum())
aov, med = df.Total_Sales.mean(), df.Total_Sales.median()
full = df[df.Order_Date < "2026-01-01"]
monthly = full.groupby(full.Order_Date.dt.to_period("M")).Total_Sales.sum()
mom = monthly.pct_change().dropna() * 100
cat = df.groupby("Category").Total_Sales.sum().sort_values()
known = df[df.City != "Unknown"]
city = known.groupby("City").Total_Sales.sum().sort_values()
real = df[~df.Age_Imputed]
AGE = ["18-24", "25-34", "35-44", "45-54", "55+"]
age = real.groupby("Age_Group").Total_Sales.sum().reindex(AGE)
wk = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
wd = df.groupby("Weekday").Order_ID.count().reindex(wk)
hv_n, hv_pct = int(df.Is_High_Value_Order.sum()), df[df.Is_High_Value_Order].Total_Sales.sum() / rev * 100
elec_pct = cat["Electronics"] / rev * 100
top_city, top_city_pct = city.idxmax(), city.max() / known.Total_Sales.sum() * 100
city_miss_pct = (df.City == "Unknown").mean() * 100
age_imp_pct = df.Age_Imputed.mean() * 100
M = lambda v: f"₹{v / 1e6:,.1f}M"
K = lambda v: f"₹{v / 1e3:,.1f}K"

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
blank = prs.slide_layouts[6]


def rect(slide, x, y, w, h, fill=CARD, line=BORDER, radius=True):
    s = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid()
    s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(0.75)
    if radius:
        s.adjustments[0] = 0.05
    s.shadow.inherit = False
    return s


def text(slide, x, y, w, h, t, size=12, bold=False, color=INK, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0.05)
    tf.margin_top = tf.margin_bottom = Inches(0.02)
    lines = t if isinstance(t, list) else [t]
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        r = p.add_run()
        r.text = ln
        r.font.size, r.font.bold, r.font.name = Pt(size), bold, FONT
        r.font.color.rgb = color
    return tb


def style_chart(chart, labels_fmt=None, label_size=9, horizontal=False, color=BLUE):
    chart.has_legend = False
    chart.has_title = False
    chart.font.size, chart.font.name = Pt(9), FONT
    chart.font.color.rgb = INK2
    plot = chart.plots[0]
    ser = plot.series[0]
    ser.format.fill.solid()
    ser.format.fill.fore_color.rgb = color
    if hasattr(plot, "gap_width"):
        plot.gap_width = 60
    va = chart.value_axis
    va.visible = False
    va.has_major_gridlines = False
    ca = chart.category_axis
    ca.format.line.color.rgb = BORDER
    ca.has_major_gridlines = False
    ca.tick_labels.font.size = Pt(9)
    if labels_fmt:
        plot.has_data_labels = True
        dl = plot.data_labels
        dl.number_format, dl.number_format_is_linked = labels_fmt, False
        dl.font.size, dl.font.color.rgb = Pt(label_size), INK2
        dl.position = XL_LABEL_POSITION.OUTSIDE_END


def add_bar(slide, x, y, w, h, cats, vals, fmt, horizontal=False):
    cd = CategoryChartData()
    cd.categories = list(cats)
    cd.add_series("Revenue", [float(v) for v in vals])
    kind = XL_CHART_TYPE.BAR_CLUSTERED if horizontal else XL_CHART_TYPE.COLUMN_CLUSTERED
    gf = slide.shapes.add_chart(kind, Inches(x), Inches(y), Inches(w), Inches(h), cd)
    style_chart(gf.chart, fmt)
    return gf.chart


def card(slide, x, y, w, h, title):
    rect(slide, x, y, w, h)
    text(slide, x + 0.1, y + 0.06, w - 0.2, 0.3, title, size=11, bold=True)


# ================================================================== SLIDE 1: dashboard
s = prs.slides.add_slide(blank)
s.background.fill.solid()
s.background.fill.fore_color.rgb = BG
text(s, 0.4, 0.2, 9, 0.5, "Sales Performance Dashboard", size=24, bold=True)
text(s, 0.4, 0.68, 9, 0.3, "MOCK-UP  |  1,000 orders, 1 Jan 2025 - 1 Jan 2026  |  source: cleaned_sales_data.csv", size=11, color=INK2)
for i, lab in enumerate(["Date range: 2025 ▾", "City: All ▾", "Category: All ▾"]):
    b = rect(s, 9.0 + i * 1.5, 0.32, 1.4, 0.34, fill=CARD, line=BORDER)
    text(s, 9.0 + i * 1.5, 0.32, 1.4, 0.34, lab, size=10, color=INK2, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

kpis = [("Total revenue", M(rev), "sum of Total_Sales"),
        ("Orders", f"{orders:,}", "count of Order_ID"),
        ("Avg order value", K(aov), f"median {K(med)}"),
        ("Units sold", f"{units:,}", f"{units / orders:.1f} units per order"),
        ("Electronics share", f"{elec_pct:.1f}%", "of total revenue")]
tw, gap = 2.38, 0.15
for i, (lab, val, sub) in enumerate(kpis):
    x = 0.4 + i * (tw + gap)
    rect(s, x, 1.15, tw, 1.15)
    text(s, x + 0.1, 1.2, tw - 0.2, 0.28, lab, size=11, color=INK2)
    text(s, x + 0.1, 1.46, tw - 0.2, 0.5, val, size=26, bold=True)
    text(s, x + 0.1, 1.95, tw - 0.2, 0.28, sub, size=10, color=INK2)

# monthly revenue line
card(s, 0.4, 2.45, 6.3, 2.35, "Monthly revenue, 2025 (INR million)")
cd = CategoryChartData()
cd.categories = [p.strftime("%b") for p in monthly.index]
cd.add_series("Revenue", [round(v / 1e6, 2) for v in monthly.values])
gf = s.shapes.add_chart(XL_CHART_TYPE.LINE_MARKERS, Inches(0.5), Inches(2.8), Inches(6.1), Inches(1.95), cd)
ch = gf.chart
style_chart(ch)
ser = ch.plots[0].series[0]
ser.format.line.color.rgb, ser.format.line.width, ser.smooth = BLUE, Pt(2.25), False
ser.marker.format.fill.solid()
ser.marker.format.fill.fore_color.rgb = BLUE
ser.marker.format.line.color.rgb = CARD
ch.value_axis.visible = True
ch.value_axis.minimum_scale = 0
ch.value_axis.has_major_gridlines = True
ch.value_axis.major_gridlines.format.line.color.rgb = BORDER
ch.value_axis.format.line.fill.background()
ch.value_axis.tick_labels.font.size = Pt(9)

card(s, 6.85, 2.45, 3.0, 2.35, "Revenue by category (M)")
add_bar(s, 6.9, 2.8, 2.9, 1.95, cat.index, cat.values / 1e6, '0.0', horizontal=True)
card(s, 10.0, 2.45, 2.93, 2.35, "Revenue by city (M)")
add_bar(s, 10.05, 2.8, 2.85, 1.95, city.index, city.values / 1e6, '0.0', horizontal=True)

card(s, 0.4, 4.95, 3.9, 2.3, "Revenue by age group (M)")
add_bar(s, 0.45, 5.3, 3.8, 1.9, age.index, age.values / 1e6, '0.0')
card(s, 4.45, 4.95, 3.9, 2.3, "Orders by weekday")
add_bar(s, 4.5, 5.3, 3.8, 1.9, [w[:3] for w in wk], wd.values, '0')

rect(s, 8.5, 4.95, 4.43, 2.3)
text(s, 8.6, 5.0, 4.2, 0.3, "What stands out", size=11, bold=True)
text(s, 8.6, 5.35, 4.25, 1.85, [
    f"• Electronics earns {elec_pct:.0f}% of revenue; other categories are 14-18% each.",
    f"• Monthly revenue swings between {mom.min():.0f}% and +{mom.max():.0f}% (best {monthly.idxmax().strftime('%b')}, weakest {monthly.idxmin().strftime('%b')}).",
    f"• {top_city} leads with {top_city_pct:.0f}% of revenue; Gaya and Pune trail at about 10%.",
    f"• {hv_n} high-value orders bring {hv_pct:.0f}% of revenue.",
], size=10.5, color=INK)

# ================================================================== SLIDE 2: proposed KPIs
s2 = prs.slides.add_slide(blank)
s2.background.fill.solid()
s2.background.fill.fore_color.rgb = BG
text(s2, 0.4, 0.25, 12, 0.5, "Proposed KPIs for the dashboard", size=24, bold=True)
text(s2, 0.4, 0.78, 12, 0.3, "Chosen from the EDA: they answer where revenue comes from, how it moves, and how far the data can be trusted.", size=12, color=INK2)

rows = [
    ("KPI", "Formula", "Why it matters", "Current value"),
    ("Total revenue", "SUM(Total_Sales)", "Headline size of the business; base for every share.", M(rev)),
    ("Orders", "COUNT(Order_ID)", "Demand volume, independent of price.", f"{orders:,}"),
    ("Average order value (AOV)", "Revenue / Orders", "Order value is right-skewed, so show the median too.", f"{K(aov)} (median {K(med)})"),
    ("MoM revenue growth", "(Rev this month - Rev last month) / Rev last month", "Revenue is volatile month to month; spots dips early.", f"{mom.min():.0f}% to +{mom.max():.0f}%"),
    ("Category revenue share", "Category revenue / Total revenue", "Shows dependence on Electronics.", f"Electronics {elec_pct:.1f}%"),
    ("High-value order share", "Share of revenue from orders above Q3 + 1.5 x IQR", "A few large orders carry a lot of revenue.", f"{hv_n} orders, {hv_pct:.1f}% of revenue"),
    ("Data completeness", "% of orders with known City and Age", "Tells viewers how much to trust regional and age cuts.", f"City {100 - city_miss_pct:.1f}%, Age {100 - age_imp_pct:.1f}%"),
]
colw = [2.5, 3.6, 4.0, 2.4]
tbl = s2.shapes.add_table(len(rows), 4, Inches(0.4), Inches(1.35), Inches(sum(colw)), Inches(0.55 * len(rows))).table
for j, w in enumerate(colw):
    tbl.columns[j].width = Inches(w)
for i, r in enumerate(rows):
    tbl.rows[i].height = Inches(0.55)
    for j, v in enumerate(r):
        c = tbl.cell(i, j)
        c.fill.solid()
        c.fill.fore_color.rgb = BLUE if i == 0 else (CARD if i % 2 else RGBColor(0xF0, 0xF4, 0xFA))
        c.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf = c.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        run = p.add_run()
        run.text = v
        run.font.name, run.font.size = FONT, Pt(12 if i == 0 else 11.5)
        run.font.bold = (i == 0) or (j == 0)
        run.font.color.rgb = CARD if i == 0 else INK
text(s2, 0.4, 6.35, 12.5, 0.8, [
    "Notes: revenue figures are in INR. Month-over-month figures use the 12 full months of 2025 (January 2026 holds only 5 orders).",
    "City and age cuts exclude orders where those fields were missing and filled in Task 1. This is a static mock-up; Task 3 turns it into an interactive dashboard.",
], size=10.5, color=INK2)

prs.save(BASE / "dashboard_mockup.pptx")
print("saved dashboard_mockup.pptx")
