import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from khukra.core.experiment import ExperimentRunner
from khukra.data.repositories.runs import RunRepository
from khukra.domains.registry import (
    get_model,
    list_domains,
    list_models,
    list_subdomains,
    subdomain_label,
)

st.set_page_config(page_title="Khukra Inference", layout="wide")
st.title("Khukra")
st.caption("Legacy Streamlit UI — use the Next.js dashboard for full features")

store = RunRepository()
runner = ExperimentRunner(store)

domain = st.sidebar.selectbox("Domain", list_domains())
subdomain = st.sidebar.selectbox(
    "Subdomain",
    list_subdomains(domain),
    format_func=lambda s: subdomain_label(domain, s),
)
model_name = st.sidebar.selectbox("Model", list_models(domain, subdomain))
model = get_model(domain, subdomain, model_name)
defaults = model.default_parameters()

st.subheader(subdomain_label(domain, subdomain))

params: dict = {}
cols = st.columns(3)
for i, (key, value) in enumerate(defaults.items()):
    with cols[i % 3]:
        if isinstance(value, int):
            params[key] = st.number_input(key, value=value, step=1)
        elif isinstance(value, float):
            params[key] = st.number_input(key, value=float(value), format="%.4f")
        else:
            params[key] = st.text_input(key, value=str(value))

if st.button("Run inference", type="primary"):
    with st.spinner("Running inference..."):
        result = runner.run_once(model, params)
    st.success(f"Inference {result.metadata['run_id']} complete")
    for name, value in result.metrics.items():
        st.metric(name.replace("_", " ").title(), f"{value:,.4f}")
    if result.series:
        df = pd.DataFrame(result.series)
        fig, ax = plt.subplots(figsize=(10, 4))
        x_col = df.columns[0]
        for col in df.columns[1:]:
            ax.plot(df[x_col], df[col], label=col)
        ax.legend()
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)
        plt.close(fig)
