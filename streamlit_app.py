import streamlit as st
import pandas as pd
import altair as alt
import json
import numpy as np

with open("burtin.json", "r") as f:
    data = json.load(f)
df = pd.DataFrame(data)

for drug in ["Penicillin", "Streptomycin", "Neomycin"]:
    df[drug] = pd.to_numeric(df[drug], errors='coerce')

df_melted = df.melt(
    id_vars=["Bacteria", "Gram_Staining"],
    value_vars=["Penicillin", "Streptomycin", "Neomycin"],
    var_name="Antibiotic", value_name="MIC")
df_melted["Effectiveness"] = -np.log10(df_melted["MIC"])
df_melted["Label"] = df_melted["Bacteria"]

def bar_chart(data, title_text, show_legend=True, show_y_axis=True, show_x_axis=True, antibiotic=None):
    data = data.sort_values("Effectiveness", ascending=True).copy()
    data["Label_Unique"] = pd.Categorical(
        data["Bacteria"], categories=data["Bacteria"].tolist(), ordered=True
    )
    base = alt.Chart(data).encode(
        x=alt.X(
            "Effectiveness:Q",
            title="Effectiveness (-log₁₀ MIC)",
            scale=alt.Scale(domain=[-3.5, data["Effectiveness"].max() + 0.5]), 
            axis=alt.Axis(titleFontWeight='bold')
        ),
        y=alt.Y(
            "Label_Unique:N",
            sort=None,
            title="Bacteria" if show_y_axis else None,
            axis=alt.Axis(
                labelLimit=400,
                labelFontSize=13,
                titleFontSize=14,
                labels=show_y_axis,
                ticks=show_y_axis,
                titleFontWeight='bold')
        ),
        color=alt.Color(
            "Gram_Staining:N",
            scale=alt.Scale(domain=["positive", "negative"], range=["#2481c3", "#f5974f"]),
            legend=alt.Legend(title="Gram-Stain") if show_legend else None
        ),
        tooltip=["Bacteria", "Antibiotic", "Gram_Staining", "MIC", "Effectiveness"]
    )

    bars = base.mark_bar()

    rule = alt.Chart(pd.DataFrame({'x': [0]})).mark_rule(
        color='black',
        strokeDash=[10, 10]
    ).encode(x='x:Q')

    pos_labels = alt.Chart(data[data["Effectiveness"] > 0]).mark_text(
        align='left',
        baseline='middle',
        dx=6
    ).encode(
        x="Effectiveness:Q",
        y=alt.Y("Label_Unique:N", sort=None),
        text=alt.Text("Effectiveness:Q", format=".2f")
    )
    neg_labels = alt.Chart(data[data["Effectiveness"] <= 0]).mark_text(
        align='right',
        baseline='middle',
        dx=-6
    ).encode(
        x="Effectiveness:Q",
        y=alt.Y("Label_Unique:N", sort=None),
        text=alt.Text("Effectiveness:Q", format=".2f")
    )
    chart = bars + pos_labels + neg_labels + rule

    if antibiotic and antibiotic != "All":
        annotation_dict = {
            "Penicillin": "💡 High effectiveness shown for Gram-Positive",
            "Streptomycin": "💡 Effectiveness varies for Gram-Positive/Negative",
            "Neomycin": "💡 Broadly effective for Gram-Positive/Negative"
        }
        if antibiotic in annotation_dict:
            dx_val = 175 if antibiotic == "Penicillin" else 190
            dy_val = 60 if antibiotic == "Neomycin" else 40
            annotation = alt.Chart(pd.DataFrame({
                'x': [data["Effectiveness"].max() - 1],
                'y': [str(data["Label_Unique"].astype(str).tolist()[len(data)//2])],
                'text': [annotation_dict[antibiotic]]
            })).mark_text(
                align='right',
                baseline='middle',
                fontSize=14,
                fontStyle='italic',
                dx=dx_val,
                dy=dy_val,
                color='black',
                tooltip=None
            ).encode(
                x='x:Q',
                y=alt.Y('y:N', sort=None),
                text='text:N'
            )
            chart += annotation
    return chart.properties(
        width=380 if show_y_axis else 350,
        height=max(30 * len(data), 600)
    )


st.set_page_config(layout="wide")
st.title("🧪 Which Antibiotic Works Best by Gram Stain Type? ")

st.markdown("""
#### What Makes an Antibiotic Effective?

Not all bacteria respond the same way to antibiotics — and one major factor is their **Gram stain type**.  
This chart compares how **Penicillin**, **Streptomycin**, and **Neomycin** perform against 16 bacterial species, using calculated effectiveness scores and color to distinguish between **Gram-positive** (blue) and **Gram-negative** (orange) stains.
""")

st.markdown("""
<div style="margin-top: 0.1px; margin-bottom: 1px;">
<hr style="border: 0.5px solid #ccc;" />
</div>
""", unsafe_allow_html=True)

st.markdown("""
##### 📊 Exploring the Data:            
- **Effectiveness**: higher = more potent.  
- **Hover** over any bar for further details.
- **Key insights** at bottom of the page.
""")

choice = st.selectbox("Choose an antibiotic:", ["Penicillin", "Streptomycin", "Neomycin", "All"])

if choice == "All":
    pen = df_melted[df_melted["Antibiotic"] == "Penicillin"]
    strep = df_melted[df_melted["Antibiotic"] == "Streptomycin"]
    neo = df_melted[df_melted["Antibiotic"] == "Neomycin"]

    col1, col2, col3 = st.columns([1.2, 1, 1])
    with col1:
        st.markdown(
            "<h6 style='text-align: center; font-weight: bold;'>Penicillin Is Highly Effective Against Gram-Positive Bacteria, But Fails Against Gram-Negative</h6>",
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            "<h6 style='text-align: center; font-weight: bold;'>Streptomycin Shows Moderate Effectiveness Across Both Gram Types, With Some Variation</h6>",
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            "<h6 style='text-align: center; font-weight: bold;'>Neomycin Performs Well Across Most Bacteria, Especially Gram-Negative Stains</h6>",
            unsafe_allow_html=True
        )

    col1, col2, col3 = st.columns([1.2, 1, 1])
    with col1:
        st.altair_chart(bar_chart(pen, "", show_legend=False, show_y_axis=True, show_x_axis=True, antibiotic=None))
    with col2:
        st.altair_chart(bar_chart(strep, "", show_legend=False, show_y_axis=False, show_x_axis=True, antibiotic=None))
    with col3:
        st.altair_chart(bar_chart(neo, "", show_legend=True, show_y_axis=False, show_x_axis=True, antibiotic=None))
else:
    df_filtered = df_melted[df_melted["Antibiotic"] == choice]
    if choice == "Penicillin":
        chart_title = "Penicillin Is Highly Effective Against Gram-Positive Bacteria, But Fails Against Gram-Negative"
    elif choice == "Streptomycin":
        chart_title = "Streptomycin Shows Moderate Effectiveness Across Both Gram Types, With Some Variation"
    elif choice == "Neomycin":
        chart_title = "Neomycin Performs Well Across Most Bacteria, Especially Gram-Negative Stains"

    st.markdown(
        f"<h6 style='text-align: center; font-weight: bold;'>{chart_title}</h6>",
        unsafe_allow_html=True
    )
    st.altair_chart(
        bar_chart(df_filtered, chart_title, show_legend=True, antibiotic=choice),
        use_container_width=True
    )

st.markdown("""
<div style="margin-top: 0.1px; margin-bottom: 1px;">
<hr style="border: 0.5px solid #ccc;" />
</div>
""", unsafe_allow_html=True)

st.markdown("#### 💡 **Key Insights**")

if choice == "Penicillin":
    st.markdown("""
- **Penicillin** is **highly effective** against **Gram-positive bacteria**, showing strong inhibition.
- It is **mostly ineffective** against **Gram-negative bacteria**.
- This reflects its known mechanism: it targets peptidoglycan in Gram-positive cell walls.
    """)
elif choice == "Streptomycin":
    st.markdown("""
- **Streptomycin** shows **moderate, broad-spectrum effectiveness**.
- Some Gram-positive and Gram-negative species respond well, but resistance is noticeable.
- It performs better than Penicillin on several Gram-negative stains. """)
elif choice == "Neomycin":
    st.markdown("""
- **Neomycin** has **broad-spectrum potency**, especially against **Gram-negative bacteria**.
- Some Gram-positive species show reduced sensitivity.
- It's among the strongest overall in this dataset. """)
else:
    st.markdown("""
- **Penicillin** is effective mainly for **Gram-positive** bacteria.
- **Streptomycin** and **Neomycin** offer **broader spectrum** coverage.
- **Gram-negative species** tend to be more resistant overall.
- Understanding **Gram stain type** helps guide antibiotic selection. """)
