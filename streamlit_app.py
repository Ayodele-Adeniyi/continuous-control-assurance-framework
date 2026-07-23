"""Browser-based reviewer workspace for the CCAF synthetic demonstration."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path
from uuid import uuid4

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from ccaf.generate_data import DEFAULT_SEED  # noqa: E402
from ccaf.web_support import (  # noqa: E402
    build_evidence_zip,
    execute_synthetic_run,
    load_artifacts,
    load_control_catalog,
    render_review_response,
)


REPOSITORY_URL = (
    "https://github.com/Ayodele-Adeniyi/continuous-control-assurance-framework"
)
RELEASE_URL = f"{REPOSITORY_URL}/releases/tag/v1.3.1"
PRIORITY_ORDER = ["Critical", "High", "Medium", "Low"]
OFFICIAL_SEED = DEFAULT_SEED

st.set_page_config(page_title="CCAF Review Workspace", layout="wide")
st.markdown(
    """
    <style>
      :root { --ccaf-ink: #17212b; --ccaf-blue: #1f5e82; --ccaf-green: #2d6a4f; }
      [data-testid="stAppViewContainer"] { background: #f4f6f8; color: var(--ccaf-ink); }
      [data-testid="stHeader"] { background: rgba(244, 246, 248, 0.96); }
      .block-container { max-width: 1240px; padding-top: 1.35rem; padding-bottom: 3rem; }
      h1, h2, h3, p, label, button { letter-spacing: 0 !important; }
      h1 { color: var(--ccaf-ink); font-size: 2rem !important; margin-bottom: 0.25rem !important; }
      h2 { color: var(--ccaf-ink); font-size: 1.35rem !important; }
      h3 { color: var(--ccaf-ink); font-size: 1.05rem !important; }
      [data-testid="stMetric"] { background: #ffffff; border: 1px solid #d7dde3; border-radius: 6px; padding: 0.8rem 1rem; }
      [data-testid="stMetricLabel"] { color: #4b5965; }
      [data-testid="stMetricValue"] { color: var(--ccaf-ink); }
      .ccaf-kicker { color: var(--ccaf-blue); font-size: 0.82rem; font-weight: 700; text-transform: uppercase; }
      .ccaf-subtitle { color: #53616d; max-width: 850px; margin: 0 0 0.9rem 0; }
      .ccaf-boundary { background: #ffffff; border-left: 4px solid var(--ccaf-green); padding: 0.8rem 1rem; margin: 0.9rem 0 1.2rem; }
      .ccaf-boundary strong { color: var(--ccaf-ink); }
      .ccaf-objective { background: #ffffff; border: 1px solid #d7dde3; padding: 1rem 1.15rem; margin: 0.7rem 0 1.2rem; }
      .ccaf-objective strong { color: var(--ccaf-blue); }
      .ccaf-flow { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 0.7rem; margin: 0.75rem 0 1.25rem; }
      .ccaf-flow-step { background: #ffffff; border-top: 3px solid var(--ccaf-blue); padding: 0.8rem; min-height: 8.2rem; }
      .ccaf-flow-step b { display: block; color: var(--ccaf-ink); margin-bottom: 0.35rem; }
      .ccaf-flow-step span { color: #53616d; font-size: 0.9rem; line-height: 1.4; }
      .ccaf-step-number { color: var(--ccaf-blue) !important; font-size: 0.78rem !important; font-weight: 700; text-transform: uppercase; }
      @media (max-width: 900px) {
        .ccaf-flow { grid-template-columns: 1fr; }
        .ccaf-flow-step { min-height: auto; }
      }
      div.stButton > button, div.stDownloadButton > button { border-radius: 5px; min-height: 2.6rem; }
      div[data-testid="stTabs"] button { letter-spacing: 0 !important; }
      [data-testid="stDataFrame"] { border: 1px solid #d7dde3; }
      footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def release_snapshot() -> dict[str, object]:
    return load_artifacts(ROOT / "output")


@st.cache_data(show_spinner=False)
def control_catalog() -> pd.DataFrame:
    return load_control_catalog(ROOT / "docs" / "control-test-catalog.md")


def synthetic_run_context(artifacts: dict[str, object]) -> tuple[int, str]:
    metadata = artifacts.get("run_metadata", {})
    assert isinstance(metadata, dict)
    seed = int(metadata.get("synthetic_seed", OFFICIAL_SEED) or OFFICIAL_SEED)
    status = str(metadata.get("benchmark_status", "")).strip()
    if not status:
        status = (
            "official release benchmark"
            if seed == OFFICIAL_SEED else "exploratory synthetic run"
        )
    return seed, status


def current_artifacts() -> tuple[dict[str, object], str, Path, Path, Path | None]:
    run_dir_value = st.session_state.get("ccaf_run_dir")
    if run_dir_value:
        run_dir = Path(run_dir_value)
        observed = load_artifacts(run_dir / "outputs")
        return (
            observed,
            "Observed in this browser session",
            run_dir / "synthetic_inputs",
            run_dir / "outputs",
            run_dir,
        )
    snapshot = release_snapshot()
    return (
        snapshot,
        "Documented release snapshot",
        ROOT / "data" / "synthetic",
        ROOT / "output",
        None,
    )


def show_metrics(artifacts: dict[str, object], source_label: str) -> None:
    metrics = artifacts["metrics"]
    assert isinstance(metrics, dict)
    columns = st.columns(4)
    columns[0].metric("Control tests", f"{metrics['tests']:,}")
    columns[1].metric("Eligible evaluations", f"{metrics['evaluations']:,}")
    columns[2].metric("Reported exceptions", f"{metrics['exceptions']:,}")
    columns[3].metric(
        "Planted detections",
        f"{metrics['seeded_detected']:,} / {metrics['seeded_conditions']:,}",
    )
    st.caption(
        f"Source: {source_label}. Detection is synthetic regression evidence, "
        "not a production accuracy rate."
    )


st.markdown('<div class="ccaf-kicker">Independent technical review</div>', unsafe_allow_html=True)
st.title("CCAF Review Workspace")
st.markdown(
    '<p class="ccaf-subtitle">Review the methodology, understand how the framework works, '
    'inspect selected controls and evidence, and prepare an independent professional response '
    'without installing software.</p>',
    unsafe_allow_html=True,
)
st.markdown(
    """
    <div class="ccaf-boundary"><strong>Evidence boundary.</strong> This workspace uses only
    seeded synthetic data and accepts no institutional uploads. Reported exceptions are items
    for professional review, not confirmed deficiencies, compliance conclusions, or production
    performance claims.</div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.subheader("Release record")
    st.write("**Version:** 1.3.1")
    st.write("**License:** Apache-2.0")
    st.write("**Scope:** 20 bounded control tests")
    st.markdown(f"[Repository]({REPOSITORY_URL})")
    st.markdown(f"[Release tag]({RELEASE_URL})")
    st.divider()
    st.caption(
        "The site is a convenience layer over the same documented Python runner. "
        "Each demonstration is generated in an isolated temporary directory."
    )

artifacts, source_label, data_dir, output_dir, run_dir = current_artifacts()
overview_tab, controls_tab, run_tab, evidence_tab, review_tab = st.tabs(
    ["Overview", "Controls", "Run Demo", "Evidence", "Review"]
)

with overview_tab:
    st.header("Purpose and reviewer orientation")
    st.markdown(
        """
        <div class="ccaf-objective"><strong>Objective.</strong> CCAF is a transparent,
        adaptable reference prototype showing how selected IT and transaction-control
        objectives can be converted into repeatable analytics. It evaluates every eligible
        record in a supplied extract, identifies items requiring professional review, and
        preserves evidence showing what data, configuration, and rule version produced each
        result.</div>
        """,
        unsafe_allow_html=True,
    )

    problem_column, use_column = st.columns(2)
    with problem_column:
        st.subheader("The assurance problem it addresses")
        st.write(
            "Control teams need a consistent way to test structured records, explain why an "
            "item was reported, and retain enough evidence for another professional to reproduce "
            "the work. CCAF demonstrates that operating model across access, change, logging, "
            "reconciliation, and payment-monitoring risks."
        )
    with use_column:
        st.subheader("Who can use the approach")
        st.write(
            "The reference methods are intended for authorized IT audit, cybersecurity assurance, "
            "GRC, internal-control, and technology-risk teams. An institution can map its own "
            "approved extracts, thresholds, and policies to the same processing and evidence pattern."
        )

    st.subheader("What happens during a CCAF run")
    st.markdown(
        """
        <div class="ccaf-flow">
          <div class="ccaf-flow-step"><span class="ccaf-step-number">Step 1</span><b>Receive authorized extracts</b><span>Structured records and source metadata are supplied for the controls being evaluated.</span></div>
          <div class="ccaf-flow-step"><span class="ccaf-step-number">Step 2</span><b>Check data quality</b><span>Required fields, keys, dates, values, and selected relationships are checked before testing.</span></div>
          <div class="ccaf-flow-step"><span class="ccaf-step-number">Step 3</span><b>Apply control procedures</b><span>Configured rules and comparison methods evaluate every eligible record in the supplied population.</span></div>
          <div class="ccaf-flow-step"><span class="ccaf-step-number">Step 4</span><b>Prioritize review items</b><span>Reported exceptions are organized for professional follow-up; they are not treated as confirmed deficiencies.</span></div>
          <div class="ccaf-flow-step"><span class="ccaf-step-number">Step 5</span><b>Preserve evidence</b><span>Hashes, source details, configuration, populations, rule versions, and results support reproducibility.</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    output_column, boundary_column = st.columns(2)
    with output_column:
        st.subheader("What the framework produces")
        st.markdown(
            """
            - A status and eligible population for each control test
            - Structured review items with the rule and reason reported
            - Data-quality, configuration, and source-assurance records
            - Input hashes and run metadata for reproducibility
            - Control and module summaries for reviewer navigation
            """
        )
    with boundary_column:
        st.subheader("What it deliberately does not claim")
        st.markdown(
            """
            - It does not certify compliance or control effectiveness
            - It does not replace IAM, SIEM, GRC, ERP, fraud, or audit platforms
            - It does not treat a reported exception as a confirmed deficiency
            - It does not claim production accuracy or institutional adoption
            - It requires institution-authorized integration and professional judgment
            """
        )

    st.subheader("Suggested review path")
    st.write(
        "Use **Controls** to inspect the procedure and logic for selected tests. Then use "
        "**Run Demo** to test the framework with one browser click and record the result you "
        "observe. Use **Evidence** to inspect the retained artifacts, then record your "
        "professional judgment under **Review**. No GitHub access or local installation is required."
    )
    show_metrics(artifacts, source_label)

with run_tab:
    st.header("Browser demonstration")
    st.write(
        "Run the fixed Version 1.3.1 demonstration directly in the browser. The run checks "
        "data-quality preconditions, executes all 20 control tests, and preserves the evidence "
        "needed to understand and reproduce the result."
    )
    selected_seed = OFFICIAL_SEED
    st.info(
        "This browser run uses the fixed demonstration associated with the documented release."
    )
    with st.expander("What happens during the run?", expanded=True):
        st.markdown(
            """
            1. **Create an isolated workspace.** The app creates a temporary session folder so
               this run does not alter the documented release snapshot.
            2. **Generate the fixed demonstration data.** CCAF recreates the same synthetic
               access, change, logging, reconciliation, and payment records used for the
               Version 1.3.1 demonstration.
            3. **Check whether the records are usable.** Required files, fields, identifiers,
               timestamps, values, and selected relationships are checked before testing.
               Critical or High data-quality findings stop the run.
            4. **Execute all 20 control procedures.** The framework evaluates every eligible
               record in the supplied extracts and records each test as Completed or Not
               Evaluable.
            5. **Organize conditions for professional review.** Records meeting a documented
               test condition are reported as exceptions; CCAF does not make the final control
               conclusion.
            6. **Preserve the evidence.** The app records eligible populations, exceptions,
               configuration, rule versions, file identities, and run metadata in a
               downloadable evidence bundle.
            """
        )
    run_column, download_column = st.columns([1, 1])
    with run_column:
        if st.button("Run CCAF demonstration", type="primary", width="stretch"):
            with st.spinner("Generating data and executing 20 control tests..."):
                try:
                    session_root = ROOT / "tmp" / "web_runs" / uuid4().hex
                    session_root.mkdir(parents=True, exist_ok=False)
                    execute_synthetic_run(ROOT, session_root, seed=selected_seed)
                    st.session_state["ccaf_run_dir"] = str(session_root)
                    st.session_state.pop("review_response", None)
                    st.rerun()
                except Exception as exc:  # surfaced for reviewer troubleshooting
                    st.error(f"The demonstration did not complete: {exc}")
    with download_column:
        evidence_zip = build_evidence_zip(data_dir, output_dir, run_dir)
        st.download_button(
            "Download evidence bundle",
            data=evidence_zip,
            file_name="CCAF_v1.3.1_review_evidence.zip",
            mime="application/zip",
            width="stretch",
        )
    if run_dir:
        st.success(
            "This browser session independently completed the documented demonstration."
        )
    else:
        st.info("Run the demonstration to replace the release snapshot with session-observed results.")
    show_metrics(artifacts, source_label)

    st.subheader("Module results")
    modules = artifacts["module_summary"]
    assert isinstance(modules, pd.DataFrame)
    chart_data = modules.set_index("module")[["exceptions_per_1000_evaluations"]]
    st.bar_chart(chart_data, color="#1f5e82", height=280)
    st.dataframe(
        modules,
        hide_index=True,
        width="stretch",
        column_config={
            "exceptions_per_1000_evaluations": st.column_config.NumberColumn(
                "Exceptions per 1,000", format="%.2f"
            ),
            "review_priority_score": st.column_config.NumberColumn(
                "Priority score", format="%.2f"
            ),
        },
    )
    if run_dir:
        with st.expander("Run console"):
            st.code((run_dir / "run_console.txt").read_text(encoding="utf-8"), language="text")

with controls_tab:
    st.header("Control explorer")
    st.write(
        "Each control follows the same professional logic: identify the risk, state the intended "
        "control condition, define the automated inspection or reperformance procedure, and "
        "identify the evidence and human follow-up needed before reaching a conclusion. Select "
        "a module and control below to inspect that logic."
    )
    controls = artifacts["control_summary"]
    exceptions = artifacts["exceptions"]
    assert isinstance(controls, pd.DataFrame)
    assert isinstance(exceptions, pd.DataFrame)

    st.subheader("Complete 20-control catalog")
    module_names = {
        "M1 Privileged Access": "Privileged Access",
        "M2 Change & Logging": "Change & Logging",
        "M3 Reconciliation & Payments": "Reconciliation & Payments",
    }
    catalog_metrics = st.columns(4)
    catalog_metrics[0].metric("Total control tests", "20")
    catalog_metrics[1].metric("Privileged Access", "7")
    catalog_metrics[2].metric("Change & Logging", "7")
    catalog_metrics[3].metric("Reconciliation & Payments", "6")
    full_catalog = controls[["module", "control_id", "control_name"]].copy()
    full_catalog["module"] = full_catalog["module"].map(module_names)
    full_catalog["module_order"] = full_catalog["module"].map(
        {"Privileged Access": 1, "Change & Logging": 2, "Reconciliation & Payments": 3}
    )
    full_catalog = full_catalog.sort_values(["module_order", "control_id"]).drop(
        columns="module_order"
    )
    full_catalog = full_catalog.rename(
        columns={"module": "Module", "control_id": "ID", "control_name": "Control test"}
    ).set_index("ID")
    st.table(
        full_catalog,
        border="horizontal",
    )

    st.divider()
    st.subheader("Inspect one control in detail")
    module_options = controls["module"].drop_duplicates().tolist()
    selected_module = st.selectbox("Module", module_options)
    module_controls = controls[controls["module"].eq(selected_module)]
    control_labels = {
        row.control_id: f"{row.control_id} - {row.control_name}"
        for row in module_controls.itertuples()
    }
    selected_control = st.selectbox(
        "Control test",
        list(control_labels),
        format_func=lambda value: control_labels[value],
    )
    control_row = module_controls[module_controls["control_id"].eq(selected_control)].iloc[0]
    detail_columns = st.columns(4)
    detail_columns[0].metric("Status", str(control_row["evaluation_status"]))
    detail_columns[1].metric("Eligible population", f"{int(control_row['eligible_population']):,}")
    detail_columns[2].metric("Exceptions", f"{int(control_row['exceptions']):,}")
    rate = control_row["exceptions_per_1000"]
    detail_columns[3].metric(
        "Exceptions per 1,000",
        "Not evaluable" if pd.isna(rate) else f"{float(rate):,.2f}",
    )
    st.caption(
        f"Demonstration review priority: {control_row['review_priority']}. "
        "The priority orders follow-up; it is not a probability of loss or a confirmed deficiency."
    )
    catalog_row = control_catalog()[
        control_catalog()["control_id"].eq(selected_control)
    ].iloc[0]
    st.subheader("Procedure and evidence")
    st.markdown(f"**Risk addressed:** {catalog_row['risk']}")
    st.markdown(f"**Intended control state:** {catalog_row['control_statement']}")
    st.markdown(f"**Automated procedure:** {catalog_row['automated_procedure']}")
    st.markdown(f"**Evidence and follow-up:** {catalog_row['evidence_follow_up']}")
    st.caption(f"Procedure type: {catalog_row['control_test_type']}")
    st.subheader("Reported review items")
    selected_exceptions = exceptions[exceptions["control_id"].eq(selected_control)].copy()
    if selected_exceptions.empty:
        st.info("No exceptions were reported for this control in the selected result set.")
    else:
        st.dataframe(
            selected_exceptions[
                [
                    "exception_id",
                    "entity_id",
                    "detail",
                    "review_priority",
                    "rule_version",
                    "review_priority_score",
                ]
            ],
            hide_index=True,
            width="stretch",
            height=390,
        )
    st.download_button(
        "Download selected exceptions",
        data=selected_exceptions.to_csv(index=False).encode("utf-8"),
        file_name=f"{selected_control}_exceptions.csv",
        mime="text/csv",
    )

with evidence_tab:
    st.header("Evidence explorer")
    st.write(
        "Inspect the evidence CCAF retains about source files, configuration, data quality, "
        "test populations, exceptions, and seeded-condition verification."
    )
    artifact_files = sorted(path for path in output_dir.iterdir() if path.is_file())
    selected_path = st.selectbox(
        "Artifact",
        artifact_files,
        format_func=lambda path: path.name,
    )
    st.caption(f"{selected_path.name} | {selected_path.stat().st_size:,} bytes")
    if selected_path.suffix.lower() == ".csv":
        selected_frame = pd.read_csv(selected_path)
        st.dataframe(selected_frame, hide_index=True, width="stretch", height=470)
    elif selected_path.suffix.lower() == ".json":
        st.json(selected_path.read_text(encoding="utf-8"))
    else:
        st.code(selected_path.read_text(encoding="utf-8"), language="text")
    st.download_button(
        "Download selected artifact",
        data=selected_path.read_bytes(),
        file_name=selected_path.name,
        mime="application/octet-stream",
    )

with review_tab:
    st.header("Independent review")
    st.write(
        "The primary task is to assess whether the methodology is coherent, technically sound, "
        "appropriately bounded, and adaptable. The normal review can be completed entirely on "
        "this website; GitHub and local reproduction are optional. Record only materials and "
        "procedures personally examined, and write all professional opinions in your own words."
    )
    st.info(
        "The review workspace uses the fixed Version 1.3.1 demonstration documented in the "
        "release materials."
    )
    document_columns = st.columns(3)
    document_columns[0].download_button(
        "Methodology PDF",
        data=(ROOT / "docs" / "CCAF_Framework_Methodology.pdf").read_bytes(),
        file_name="CCAF_Framework_Methodology_v1.3.1.pdf",
        mime="application/pdf",
        width="stretch",
    )
    document_columns[1].download_button(
        "Reviewer guide",
        data=(ROOT / "REVIEWER_GUIDE.md").read_bytes(),
        file_name="CCAF_Independent_Review_Guide.md",
        mime="text/markdown",
        width="stretch",
    )
    document_columns[2].download_button(
        "Blank response template",
        data=(ROOT / "REVIEW_RESPONSE_TEMPLATE.md").read_bytes(),
        file_name="CCAF_Independent_Review_Response.md",
        mime="text/markdown",
        width="stretch",
    )

    with st.form("review_response_form"):
        st.subheader("Reviewer and scope")
        reviewer = st.text_input("Reviewer name and role")
        experience = st.text_area("Relevant experience", height=100)
        review_date = st.date_input("Review date", value=date.today())
        relationship = st.text_input("Prior relationship, conflict, or compensation, if any")
        depth = st.radio(
            "Review depth",
            ["Website methodology review", "Source-code enhanced", "Detailed", "Other"],
            horizontal=True,
        )
        st.subheader("Procedures personally performed")
        procedure_options = [
            "Reviewed the website Overview, methodology, and stated limitations",
            "Inspected selected control procedures and their logic in Controls",
            "Ran the browser demonstration and recorded the result observed",
            "Inspected selected output or reproducibility artifacts in Evidence",
            "Inspected source code or reproduced the demonstration locally (optional)",
            "Ran the automated test suite (optional)",
        ]
        procedures = [option for option in procedure_options if st.checkbox(option)]
        observed_result = st.text_input(
            "Result personally observed in the browser or local reproduction",
            placeholder="Record what you observed; do not merely repeat the documented result.",
        )
        st.subheader("Professional opinion")
        soundness = st.text_area(
            "Technical soundness",
            help="Is the methodology technically sound and consistent with professional control-testing practice for a synthetic reference prototype?",
            height=160,
        )
        boundaries = st.text_area(
            "Claims and limitations",
            help="Are the claims appropriately bounded to what the demonstration establishes?",
            height=160,
        )
        transferability = st.text_area(
            "Transferability",
            help="Could this methodology be adapted by other institutions or practitioners to their own authorized data and control environments?",
            height=160,
        )
        observations = st.text_area(
            "Observations",
            help="What strengths, limitations, or improvements, if any, would you note?",
            height=180,
        )
        consent = st.checkbox(
            "I understand that this response may be cited publicly and in professional or immigration-related submissions as evidence of independent review."
        )
        submitted = st.form_submit_button("Prepare review response", type="primary")
        if submitted:
            if not reviewer.strip():
                st.error("Enter the reviewer name and role before preparing the response.")
            elif not consent:
                st.error("Confirm the disclosure statement before preparing the response.")
            else:
                st.session_state["review_response"] = render_review_response(
                    {
                        "reviewer": reviewer,
                        "experience": experience,
                        "review_date": review_date.isoformat(),
                        "relationship": relationship,
                        "depth": depth,
                        "procedures": procedures,
                        "observed_result": observed_result,
                        "soundness": soundness,
                        "boundaries": boundaries,
                        "transferability": transferability,
                        "observations": observations,
                    }
                )
    response = st.session_state.get("review_response")
    if response:
        st.success("The response is ready. Review it carefully before signing or sharing it.")
        st.download_button(
            "Download completed response",
            data=response.encode("utf-8"),
            file_name="CCAF_Independent_Review_Response.md",
            mime="text/markdown",
            type="primary",
        )
