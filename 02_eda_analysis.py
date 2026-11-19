"""Task 2 - Step 2: univariate + multivariate EDA on the cleaned sales data.

Input : data/cleaned_sales_data.csv
Output: charts/*.png, eda_outputs/*.csv, eda_outputs/key_findings.json
Run   : python 02_eda_analysis.py
"""
import json
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
from scipy import stats

warnings.filterwarnings("ignore")
BASE = Path(__file__).parent
CH = BASE / "charts"
OUT = BASE / "eda_outputs"
CH.mkdir(exist_ok=True)
OUT.mkdir(exist_ok=True)

# ---- palette (validated reference palette, light mode) ----
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
BLUE, ORANGE = "#2a78d6", "#eb6834"
SEQ = LinearSegmentedColormap.from_list("seq_blue", ["#eaf2fc", "#9cc3f0", "#2a78d6", "#14407a"])
DIV = LinearSegmentedColormap.from_list("div", [ORANGE, "#efeeea", BLUE])

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.edgecolor": GRID, "axes.labelcolor": INK2, "text.color": INK, "xtick.color": INK2, "ytick.color": INK2,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
    "grid.linewidth": 0.8, "axes.axisbelow": True, "font.size": 10, "axes.titlesize": 12,
    "axes.titleweight": "bold", "axes.titlelocation": "left", "figure.dpi": 100,
})

df = pd.read_csv(BASE / "data" / "cleaned_sales_data.csv", parse_dates=["Order_Date"])
num = ["Age", "Quantity", "Unit_Price", "Total_Sales"]
AGE_ORDER = ["18-24", "25-34", "35-44", "45-54", "55+"]
findings = {}


def save(fig, name):
    fig.savefig(CH / name, dpi=160, bbox_inches="tight")
    plt.close(fig)


def money(x, _=None):
    return f"{x / 1e5:.0f}L" if abs(x) >= 1e5 else f"{x / 1e3:.0f}K"


# ============================================================ 1. DESCRIPTIVE STATISTICS
desc = df[num].agg(["count", "mean", "median", "std", "min", "max", "skew"]).T
desc["q1"] = df[num].quantile(.25)
desc["q3"] = df[num].quantile(.75)
desc["cv_pct"] = desc["std"] / desc["mean"] * 100
desc = desc[["count", "mean", "median", "std", "cv_pct", "min", "q1", "q3", "max", "skew"]].round(2)
desc.to_csv(OUT / "summary_numeric.csv")

cat_tables = {}
for c in ["Category", "Product", "City", "Gender", "Age_Group", "Order_Size", "Quarter", "Weekday"]:
    t = df[c].value_counts().rename("orders").to_frame()
    t["pct"] = (t["orders"] / len(df) * 100).round(1)
    t["revenue"] = df.groupby(c)["Total_Sales"].sum().round(0)
    t["avg_order_value"] = df.groupby(c)["Total_Sales"].mean().round(0)
    cat_tables[c] = t
    t.to_csv(OUT / f"summary_{c.lower()}.csv")

findings["n_orders"] = len(df)
findings["total_revenue"] = round(df.Total_Sales.sum())
findings["avg_order_value"] = round(df.Total_Sales.mean())
findings["median_order_value"] = round(df.Total_Sales.median())
findings["total_units"] = int(df.Quantity.sum())
findings["desc"] = desc.to_dict("index")

# ============================================================ 2. UNIVARIATE CHARTS
fig, axes = plt.subplots(2, 2, figsize=(11, 7))
specs = [("Age", 12, "Age (years)"), ("Quantity", 10, "Units per order"),
         ("Unit_Price", 20, "Unit price (INR)"), ("Total_Sales", 25, "Order value (INR)")]
for ax, (c, bins, lab) in zip(axes.ravel(), specs):
    ax.hist(df[c], bins=bins, color=BLUE, edgecolor=SURFACE, linewidth=1.5)
    ax.axvline(df[c].mean(), color=INK, lw=1.4, ls="-")
    ax.axvline(df[c].median(), color=ORANGE, lw=1.4, ls="--")
    ax.set_title(f"{lab.split(' (')[0]}  |  skew {df[c].skew():.2f}")
    ax.set_xlabel(lab)
    ax.set_ylabel("Orders")
    if c in ("Unit_Price", "Total_Sales"):
        ax.xaxis.set_major_formatter(plt.FuncFormatter(money))
    ax.grid(axis="x", visible=False)
axes[0, 0].plot([], [], color=INK, lw=1.4, label="Mean")
axes[0, 0].plot([], [], color=ORANGE, lw=1.4, ls="--", label="Median")
axes[0, 0].legend(frameon=False, loc="upper left", fontsize=9)
fig.suptitle("Distribution of numeric fields (K = thousand, L = lakh)", x=0.01, ha="left", fontweight="bold", fontsize=13)
fig.tight_layout()
save(fig, "01_histograms_numeric.png")

fig, axes = plt.subplots(2, 2, figsize=(11, 7))
for ax, (c, order) in zip(axes.ravel(), [("Category", None), ("City", None), ("Gender", None), ("Age_Group", AGE_ORDER)]):
    s = df[c].value_counts()
    s = s.reindex(order[::-1]) if order else s.sort_values()   # barh draws bottom-up, so reverse ordered groups
    ax.barh(s.index.astype(str), s.values, color=BLUE, height=0.62)
    for y, v in enumerate(s.values):
        ax.text(v + 3, y, f"{v}  ({v / len(df):.0%})", va="center", fontsize=9, color=INK2)
    ax.set_xlim(0, s.max() * 1.25)
    ax.set_title(f"Orders by {c.replace('_', ' ').lower()}")
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Orders")
fig.tight_layout()
save(fig, "02_bar_categorical_counts.png")

# revenue by category / product (bar)
fig, axes = plt.subplots(1, 2, figsize=(11, 4))
for ax, c in zip(axes, ["Category", "Product"]):
    s = df.groupby(c).Total_Sales.sum().sort_values()
    ax.barh(s.index, s.values, color=BLUE, height=0.62)
    for y, v in enumerate(s.values):
        ax.text(v + s.max() * 0.01, y, f"{v / 1e6:.1f}M  ({v / s.sum():.0%})", va="center", fontsize=9, color=INK2)
    ax.set_xlim(0, s.max() * 1.3)
    ax.set_title(f"Revenue by {c.lower()}")
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x / 1e6:.0f}M"))
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Revenue (INR, M = million)")
fig.tight_layout()
save(fig, "03_bar_revenue_category_product.png")

# order value spread by category (box)
order = df.groupby("Category").Total_Sales.median().sort_values().index
fig, ax = plt.subplots(figsize=(9, 4.2))
bp = ax.boxplot([df[df.Category == c].Total_Sales for c in order], vert=False, tick_labels=list(order), patch_artist=True,
                widths=0.55, medianprops=dict(color=INK, lw=1.6), flierprops=dict(markersize=3, markerfacecolor=INK2))
for b in bp["boxes"]:
    b.set(facecolor="#9cc3f0", edgecolor=BLUE)
ax.xaxis.set_major_formatter(plt.FuncFormatter(money))
ax.set_title("Order value by category (box = middle 50%, line = median)")
ax.set_xlabel("Order value (INR, K = thousand, L = lakh)")
ax.grid(axis="y", visible=False)
save(fig, "04_box_order_value_by_category.png")

# time trend (full months only)
m = df[df.Order_Date < "2026-01-01"].groupby(df.Order_Date.dt.to_period("M")).agg(
    revenue=("Total_Sales", "sum"), orders=("Order_ID", "count"))
fig, axes = plt.subplots(1, 2, figsize=(11, 3.8))
xl = [p.strftime("%b") for p in m.index]
axes[0].plot(xl, m.revenue / 1e6, color=BLUE, lw=2, marker="o", ms=5)
axes[0].set_title("Monthly revenue, 2025")
axes[0].set_ylabel("Revenue (INR M)")
axes[1].bar(xl, m.orders, color=BLUE, width=0.62)
axes[1].set_title("Monthly orders, 2025")
axes[1].set_ylabel("Orders")
axes[1].grid(axis="x", visible=False)
for ax in axes:
    ax.tick_params(axis="x", labelsize=9)
fig.tight_layout()
save(fig, "05_monthly_trend.png")
findings["monthly_revenue_m"] = {str(k): round(v / 1e6, 2) for k, v in m.revenue.items()}
findings["monthly_orders"] = {str(k): int(v) for k, v in m.orders.items()}
findings["monthly_rev_cv_pct"] = round(m.revenue.std() / m.revenue.mean() * 100, 1)
findings["best_month"] = str(m.revenue.idxmax())
findings["worst_month"] = str(m.revenue.idxmin())

# ============================================================ 3. MULTIVARIATE
corr = df[num].corr()
corr.round(3).to_csv(OUT / "correlation_pearson.csv")
spear = df[num].corr(method="spearman")
fig, ax = plt.subplots(figsize=(6, 4.8))
sns.heatmap(corr, annot=True, fmt=".2f", cmap=DIV, vmin=-1, vmax=1, center=0, linewidths=2,
            linecolor=SURFACE, cbar_kws={"shrink": .8}, ax=ax, annot_kws={"fontsize": 10})
ax.set_title("Correlation between numeric fields (Pearson)")
ax.grid(False)
ax.tick_params(axis="x", rotation=30)
save(fig, "06_heatmap_correlation.png")
findings["corr"] = corr.round(3).to_dict()

g = sns.pairplot(df[num], corner=True, diag_kind="hist", height=2.0,
                 plot_kws=dict(color=BLUE, s=10, alpha=.45, edgecolor="none"),
                 diag_kws=dict(color=BLUE, edgecolor=SURFACE))
g.figure.suptitle("Pair plot of numeric fields", x=0.02, ha="left", fontweight="bold", y=1.0)
for ax in g.axes.flatten():
    if ax is not None:
        ax.grid(color=GRID)
g.savefig(CH / "07_pairplot_numeric.png", dpi=140, bbox_inches="tight")
plt.close("all")

fig, ax = plt.subplots(figsize=(7.5, 5))
sc = ax.scatter(df.Unit_Price, df.Total_Sales, c=df.Quantity, cmap=SEQ, s=22, edgecolor=SURFACE, linewidth=.4)
cb = fig.colorbar(sc, ax=ax, shrink=.85)
cb.set_label("Units per order")
ax.xaxis.set_major_formatter(plt.FuncFormatter(money))
ax.yaxis.set_major_formatter(plt.FuncFormatter(money))
ax.set_xlabel("Unit price (INR)")
ax.set_ylabel("Order value (INR)")
ax.set_title("Order value = unit price x quantity")
save(fig, "08_scatter_price_vs_sales.png")

# heatmap city x category revenue
known = df[df.City != "Unknown"]
pv = known.pivot_table(index="City", columns="Category", values="Total_Sales", aggfunc="sum") / 1e6
pv = pv.loc[pv.sum(axis=1).sort_values(ascending=False).index]
fig, ax = plt.subplots(figsize=(8, 4.8))
sns.heatmap(pv, annot=True, fmt=".1f", cmap=SEQ, linewidths=2, linecolor=SURFACE, cbar_kws={"label": "Revenue (INR M)"}, ax=ax)
ax.set_title("Revenue by city and category (INR million)")
ax.grid(False)
ax.set_xlabel("")
ax.set_ylabel("")
save(fig, "09_heatmap_city_category.png")
pv.round(2).to_csv(OUT / "revenue_city_x_category_m.csv")

# heatmap age group x category: share of each age group's revenue (excluding imputed ages)
real = df[~df.Age_Imputed]
ct = real.pivot_table(index="Age_Group", columns="Category", values="Total_Sales", aggfunc="sum").reindex(AGE_ORDER)
share = ct.div(ct.sum(axis=1), axis=0) * 100
fig, ax = plt.subplots(figsize=(8, 4))
sns.heatmap(share, annot=True, fmt=".0f", cmap=SEQ, linewidths=2, linecolor=SURFACE,
            cbar_kws={"label": "% of age group's revenue"}, ax=ax)
ax.set_title("Category mix by age group (% of revenue)")
ax.grid(False)
ax.set_xlabel("")
ax.set_ylabel("")
save(fig, "10_heatmap_age_category.png")
share.round(1).to_csv(OUT / "category_mix_by_age_group_pct.csv")

# weekday x quarter orders
wk = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
wd = df.groupby("Weekday").agg(orders=("Order_ID", "count"), revenue=("Total_Sales", "sum"), aov=("Total_Sales", "mean")).reindex(wk)
fig, ax = plt.subplots(figsize=(8, 3.8))
ax.bar([w[:3] for w in wk], wd.orders, color=BLUE, width=0.62)
for i, v in enumerate(wd.orders):
    ax.text(i, v + 2, str(v), ha="center", fontsize=9, color=INK2)
ax.set_title("Orders by weekday")
ax.set_ylabel("Orders")
ax.grid(axis="x", visible=False)
save(fig, "11_bar_weekday.png")
findings["weekday_orders"] = wd.orders.to_dict()

# ============================================================ 4. STATISTICAL CHECKS
tests = []
for a, b in [("Age", "Total_Sales"), ("Quantity", "Total_Sales"), ("Unit_Price", "Total_Sales"),
             ("Age", "Unit_Price"), ("Age", "Quantity")]:
    r, p = stats.pearsonr(df[a], df[b])
    rs, ps = stats.spearmanr(df[a], df[b])
    tests.append(dict(test=f"Pearson / Spearman: {a} vs {b}", statistic=f"r={r:.3f}, rho={rs:.3f}", p_value=p,
                      reading="significant" if p < .05 else "no significant relationship"))
chi2, p, dof, _ = stats.chi2_contingency(pd.crosstab(real.Age_Group, real.Category))
n = len(real)
cramers = np.sqrt(chi2 / (n * (min(pd.crosstab(real.Age_Group, real.Category).shape) - 1)))
tests.append(dict(test="Chi-square: age group vs category (orders)", statistic=f"chi2={chi2:.1f}, dof={dof}, V={cramers:.3f}",
                  p_value=p, reading="significant" if p < .05 else "no significant relationship"))
chi2g, pg, dofg, _ = stats.chi2_contingency(pd.crosstab(df.Gender, df.Category))
tests.append(dict(test="Chi-square: gender vs category (orders)", statistic=f"chi2={chi2g:.1f}, dof={dofg}",
                  p_value=pg, reading="significant" if pg < .05 else "no significant relationship"))
h, p = stats.kruskal(*[g.Total_Sales for _, g in df.groupby("Category")])
tests.append(dict(test="Kruskal-Wallis: order value across categories", statistic=f"H={h:.2f}", p_value=p,
                  reading="significant" if p < .05 else "no significant relationship"))
h, p = stats.kruskal(*[g.Total_Sales for _, g in known.groupby("City")])
tests.append(dict(test="Kruskal-Wallis: order value across cities", statistic=f"H={h:.2f}", p_value=p,
                  reading="significant" if p < .05 else "no significant relationship"))
u, p = stats.mannwhitneyu(df[df.Gender == "Male"].Total_Sales, df[df.Gender == "Female"].Total_Sales)
tests.append(dict(test="Mann-Whitney: order value, male vs female", statistic=f"U={u:.0f}", p_value=p,
                  reading="significant" if p < .05 else "no significant relationship"))
wkend = df.groupby("Is_Weekend").Total_Sales
u, p = stats.mannwhitneyu(df[df.Is_Weekend].Total_Sales, df[~df.Is_Weekend].Total_Sales)
tests.append(dict(test="Mann-Whitney: order value, weekend vs weekday", statistic=f"U={u:.0f}", p_value=p,
                  reading="significant" if p < .05 else "no significant relationship"))
df["H2"] = df.Order_Date >= "2025-07-01"
tab = pd.crosstab(df.H2, df.Product == "Mobile")
p_mob = stats.chi2_contingency(tab)[1]
tests.append(dict(test="Chi-square: Mobile share of orders, Jan-Jun vs Jul-Jan (picked after seeing the data)",
                  statistic=f"Mobile orders {tab.loc[False, True]} -> {tab.loc[True, True]} of ~500", p_value=p_mob,
                  reading="significant on its own, but 1 of 6 products inspected" if p_mob < .05 else "not significant"))
chi2p, pp, dofp, _ = stats.chi2_contingency(pd.crosstab(df.H2, df.Product))
tests.append(dict(test="Chi-square: product mix of orders, Jan-Jun vs Jul-Jan (all 6 products)",
                  statistic=f"chi2={chi2p:.1f}, dof={dofp}", p_value=pp,
                  reading="significant" if pp < .05 else "no significant change in product mix"))
tt = pd.DataFrame(tests)
tt["p_value"] = tt["p_value"].map(lambda v: f"{v:.4f}" if v >= 1e-4 else "<0.0001")
tt.to_csv(OUT / "statistical_tests.csv", index=False)
findings["tests"] = tt.to_dict("records")

# ---- extra numbers used in the report ----
top_share = df.sort_values("Total_Sales", ascending=False)
k = int(len(df) * 0.2)
findings["top20pct_orders_revenue_share"] = round(top_share.head(k).Total_Sales.sum() / df.Total_Sales.sum() * 100, 1)
findings["category_rev_pct"] = (df.groupby("Category").Total_Sales.sum() / df.Total_Sales.sum() * 100).round(1).to_dict()
findings["city_rev_pct"] = (known.groupby("City").Total_Sales.sum() / known.Total_Sales.sum() * 100).round(1).to_dict()
findings["city_aov"] = known.groupby("City").Total_Sales.mean().round(0).to_dict()
findings["product_rev_m"] = (df.groupby("Product").Total_Sales.sum() / 1e6).round(2).sort_values(ascending=False).to_dict()
findings["gender_orders"] = df.Gender.value_counts().to_dict()
findings["age_group_rev_m"] = (real.groupby("Age_Group").Total_Sales.sum() / 1e6).round(2).reindex(AGE_ORDER).to_dict()
findings["quarter_rev_m"] = (df[df.Order_Date < "2026-01-01"].groupby("Quarter").Total_Sales.sum() / 1e6).round(2).to_dict()
findings["high_value_orders"] = int(df.Is_High_Value_Order.sum())
findings["high_value_rev_pct"] = round(df[df.Is_High_Value_Order].Total_Sales.sum() / df.Total_Sales.sum() * 100, 1)
findings["unknown_city_orders"] = int((df.City == "Unknown").sum())
findings["imputed_age_orders"] = int(df.Age_Imputed.sum())
(OUT / "key_findings.json").write_text(json.dumps(findings, indent=2, default=str), encoding="utf-8")

print(desc.to_string())
print()
print(tt.to_string(index=False))
print()
print({k: findings[k] for k in ["total_revenue", "avg_order_value", "median_order_value", "total_units",
                                "monthly_rev_cv_pct", "best_month", "worst_month", "top20pct_orders_revenue_share",
                                "high_value_orders", "high_value_rev_pct"]})
print(findings["category_rev_pct"], findings["city_rev_pct"], findings["quarter_rev_m"], findings["weekday_orders"])
print(corr.round(2).to_string())
print(share.round(0).to_string())
print(pv.round(1).to_string())
