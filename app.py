import io
import json
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Prospect Explorer", page_icon="🚗", layout="wide")

st.markdown(
    """
    <style>
      .big-title {font-size: 44px; font-weight: 800; letter-spacing:-0.4px;}
      .tiny {opacity:.7; font-size:12px}
      .badge {background:#e5f2ff; color:#1f77b4; padding:2px 8px; border-radius:999px; font-size:12px;}
      .contact-card {border:1px solid #e6e8eb; border-radius:16px; padding:14px; background:white}
      div[data-testid="stHorizontalBlock"] > div {gap: 12px}
      .stTabs [data-baseweb="tab"] {font-size:16px}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="big-title">Prospect Explorer – EV & Sustainability</div>', unsafe_allow_html=True)

st.sidebar.title("Data")
st.sidebar.caption("Upload your Excel/CSV or use sample data.")
use_sample = st.sidebar.toggle("Use sample data", value=False)
uploaded = None if use_sample else st.sidebar.file_uploader("Excel (.xlsx) or CSV", type=["xlsx", "csv"]) 


def load_df(file):
    if file is None:
        data = {
            "Name": [
                "Aisha Tan","Lucas Meyer","Priya Shah","Elena Rossi","Kenji Sato","John Smith",
                "Sara Lee","Juan Perez","Fatima Noor","Li Wei","Amira Hassan","James Park"
            ],
            "Email": [
                "a.tan@example.com","lucas@greenwatt.de","priya@evgrid.in","elena@eco-italia.it",
                "kenji@nippon-sustain.jp","john@us-ev.org","","juan@solaris.mx",
                "fatima@qatarleaders.com","","amira@mena-green.ae","j.park@k-ev.co.kr"
            ],
            "Phone": [
                "+65 6123 4567","+49 30 123456","+91 98 7654 3210","+39 06 1234 5678","+81 3-1234-5678","+1 415-555-0100",
                "+61 3 9000 1111","+52 55 1234 5678","+974 5555 1234","+86 10 8888 0000","+971 50 555 1234","+82 2-555-0000"
            ],
            "Company": [
                "SolarFuture","GreenWatt","EVGrid","EcoItalia","Nippon Sustain","EV Alliance",
                "BlueCharge","Solaris","Qatar Green Leaders","China EV","MENA Green","K-EV"
            ],
            "Role": [
                "CEO","Sustainability Manager","Head of EV","VP Sustainability","Director Sustainability",
                "CEO","Partnerships Lead","Country Manager","Director","CTO","CEO","Head of Strategy"
            ],
            "Country": [
                "Singapore","Germany","India","Italy","Japan","United States","Australia","Mexico",
                "Qatar","China","United Arab Emirates","South Korea"
            ],
            "Status": ["New","Contacted","Replied","New","New","Qualified","New","Contacted","Replied","New","Meeting","Qualified"],
            "Priority": ["High","Med","High","Low","Med","High","Low","Med","High","Low","High","Med"],
            "Owner": ["Bruno","Bruno","Bruno","Ana","Ana","Luis","Ana","Luis","Bruno","Wei","Nadia","Min"],
            "LastContacted": ["", "2025-08-24", "2025-09-18", "", "2025-09-01", "2025-09-10", "", "2025-09-05", "2025-09-17", "", "2025-09-20", "2025-09-12"],
            "Present in CRM": ["No","Yes","Yes","No","No","Yes","No","No","Yes","No","Yes","No"],
            "Notes": ["","Intro call done","Strong EV fit","Specializes in solar","Battery projects","Decision maker",
                       "Gmail domain","LATAM entry","Gov relationships","Hardware heavy","ME partnerships","Korea rollout"],
        }
        return pd.DataFrame(data)
    else:
        if file.name.lower().endswith(".csv"):
            df = pd.read_csv(file)
        else:
            xls = pd.ExcelFile(file)
            sheet = st.sidebar.selectbox("Sheet", xls.sheet_names, index=0)
            df = pd.read_excel(xls, sheet_name=sheet)
        for c in df.columns:
            if pd.api.types.is_object_dtype(df[c]):
                df[c] = df[c].astype(str).str.strip()
        return df


try:
    df_raw = load_df(uploaded)
except Exception as e:
    st.error(f"Couldn't read the file. Make sure it's a valid CSV/XLSX. Error: {e}")
    st.stop()


st.sidebar.subheader("Columns")

def selectbox_guess(label, options, guesses):
    opts = [None] + list(options)
    lower = [str(o).lower() for o in options]
    guess = None
    for g in guesses:
        if g.lower() in lower:
            guess = options[lower.index(g.lower())]
            break
    idx = opts.index(guess) if guess in opts else 0
    return st.sidebar.selectbox(label, opts, index=idx)

name_col     = selectbox_guess("Name*",    df_raw.columns, ["name","full name","contact","person"])
email_col    = selectbox_guess("Email",     df_raw.columns, ["email","e-mail","mail","contact email"])
phone_col    = selectbox_guess("Phone",     df_raw.columns, ["phone","mobile","telephone","tel","phone number","cell"])
company_col  = selectbox_guess("Company*", df_raw.columns, ["company","organisation","organization","employer"])
role_col     = selectbox_guess("Role",      df_raw.columns, ["role","title","job title","position"])
country_col  = selectbox_guess("Country*", df_raw.columns, ["country","nation","location","country name"])
status_col   = selectbox_guess("Status",    df_raw.columns, ["status","stage","pipeline","funnel"])
priority_col = selectbox_guess("Priority",  df_raw.columns, ["priority","tier","score"])
owner_col    = selectbox_guess("Owner",     df_raw.columns, ["owner","assignee","rep","account owner"])
lastc_col    = selectbox_guess("Last Contacted", df_raw.columns, ["last_contacted","last contacted","last touch","last reached"])
crm_col      = selectbox_guess("Present in CRM", df_raw.columns, ["present in crm","present","crm","in crm","crm_present","crm present"])
notes_col    = selectbox_guess("Notes",     df_raw.columns, ["notes","remarks","comment","description"])

missing = [lbl for lbl, c in {"Name":name_col, "Company":company_col, "Country":country_col}.items() if not c]
if missing:
    st.warning("Please map required columns: " + ", ".join(missing))
    st.stop()

std = pd.DataFrame({
    "Name": df_raw[name_col],
    "Email": df_raw[email_col] if email_col else "",
    "Phone": df_raw[phone_col] if phone_col else "",
    "Company": df_raw[company_col],
    "Role": df_raw[role_col] if role_col else "",
    "Country": df_raw[country_col],
    "Status": df_raw[status_col] if status_col else "",
    "Priority": df_raw[priority_col] if priority_col else "",
    "Owner": df_raw[owner_col] if owner_col else "",
    "LastContacted": df_raw[lastc_col] if lastc_col else "",
    "PresentInCRM": df_raw[crm_col] if crm_col else "",
    "Notes": df_raw[notes_col] if notes_col else "",
})

std = std.astype(str).apply(lambda s: s.str.strip())

ALIASES = {
    "UAE":"United Arab Emirates","Abu Dhabi":"United Arab Emirates","KSA":"Saudi Arabia",
    "USA":"United States","US":"United States","UK":"United Kingdom","Korea":"South Korea",
}
std["Country"] = std["Country"].replace(ALIASES)

REGION = {
    "United Arab Emirates":"MENA","Qatar":"MENA","Bahrain":"MENA","Kuwait":"MENA","Saudi Arabia":"MENA","Lebanon":"MENA",
    "India":"APAC","Japan":"APAC","Singapore":"APAC","Indonesia":"APAC","Malaysia":"APAC","Thailand":"APAC","Philippines":"APAC","China":"APAC","South Korea":"APAC","Australia":"APAC",
    "Germany":"EMEA","Italy":"EMEA","United Kingdom":"EMEA","France":"EMEA","Spain":"EMEA","Netherlands":"EMEA",
    "United States":"AMER","Canada":"AMER","Mexico":"AMER","Brazil":"AMER"
}
std["Region"] = std["Country"].map(REGION).fillna("Other")

std["EmailDomain"] = std["Email"].str.extract(r'@([^>\s,;]+)')[0].str.lower()
GENERIC = {"gmail.com","yahoo.com","hotmail.com","outlook.com","icloud.com","proton.me","aol.com"}
std["IsGenericDomain"] = std["EmailDomain"].isin(GENERIC)
std["RoleNorm"] = std["Role"].str.title()

std["LastContacted_dt"] = pd.to_datetime(std["LastContacted"], errors="coerce")
std["DaysSinceContact"] = (pd.Timestamp.today().normalize() - std["LastContacted_dt"]).dt.days

YES = {"1","true","yes","y","present","in crm","crm","✓","check","checked","x"}
NO  = {"0","false","no","n","absent","not in crm","-",""}
crm_norm = std["PresentInCRM"].str.lower().map(lambda x: "Yes" if x in YES else ("No" if x in NO else ""))
std["PresentInCRM"] = crm_norm

st.sidebar.subheader("Filters")
sel_regions   = st.sidebar.multiselect("Region", sorted(std["Region"].unique().tolist()))
sel_countries = st.sidebar.multiselect("Country", sorted([c for c in std["Country"].unique() if c]))
sel_companies = st.sidebar.multiselect("Company", sorted([c for c in std["Company"].unique() if c]))
sel_owners    = st.sidebar.multiselect("Owner", sorted([o for o in std["Owner"].replace({"":"(unassigned)"}).unique()]))
sel_roles     = st.sidebar.text_input("Role contains")
sel_domains   = st.sidebar.multiselect("Email domain", sorted([d for d in std["EmailDomain"].dropna().unique() if d]))
hide_generic  = st.sidebar.toggle("Hide generic email providers", value=False)
sel_status    = st.sidebar.multiselect("Status", sorted([s for s in std["Status"].replace({"":"(blank)"}).unique()]))
sel_priority  = st.sidebar.multiselect("Priority", sorted([p for p in std["Priority"].replace({"":"(blank)"}).unique()]))
crm_filter    = st.sidebar.selectbox("Present in CRM", ["All","Yes","No"], index=0)
query         = st.sidebar.text_input("Search name/company")
unique_emails = st.sidebar.toggle("Show unique emails only", value=False)

cad_high = st.sidebar.slider("High priority follow-up (days)", 7, 60, 14)
cad_med  = st.sidebar.slider("Medium priority follow-up (days)", 7, 90, 30)
cad_low  = st.sidebar.slider("Low priority follow-up (days)", 7, 120, 45)

f = std.copy()
if sel_regions:
    f = f[f["Region"].isin(sel_regions)]
if sel_countries:
    f = f[f["Country"].isin(sel_countries)]
if sel_companies:
    f = f[f["Company"].isin(sel_companies)]
if sel_owners:
    owners = [o if o != "(unassigned)" else "" for o in sel_owners]
    f = f[f["Owner"].isin(owners)]
if sel_roles:
    f = f[f["Role"].str.contains(sel_roles, case=False, na=False)]
if sel_domains:
    f = f[f["EmailDomain"].isin(sel_domains)]
if hide_generic:
    f = f[~f["IsGenericDomain"]]
if sel_status:
    st_status = [s if s != "(blank)" else "" for s in sel_status]
    f = f[f["Status"].isin(st_status)]
if sel_priority:
    st_pr = [p if p != "(blank)" else "" for p in sel_priority]
    f = f[f["Priority"].isin(st_pr)]
if crm_filter != "All":
    f = f[f["PresentInCRM"] == crm_filter]
if query:
    mask = f["Name"].str.contains(query, case=False, na=False) | f["Company"].str.contains(query, case=False, na=False)
    f = f[mask]
if unique_emails:
    f = f.sort_values("Email").drop_duplicates(subset=["Email"], keep="first")

PR_MAP = {"high":3, "med":2, "medium":2, "low":1}
role_ceo_bonus = 2
non_generic_bonus = 1
priority_points = f["Priority"].str.lower().map(PR_MAP).fillna(0)
ceo_points = f["Role"].str.contains("CEO", case=False, na=False).astype(int) * role_ceo_bonus
non_gen_points = (~f["IsGenericDomain"]).astype(int) * non_generic_bonus
recency_points = (-f["DaysSinceContact"].fillna(60) / 60.0).clip(-1, 0)
f["Score"] = (priority_points + ceo_points + non_gen_points + recency_points).round(2)

cadence_map = f["Priority"].str.lower().map({"high":cad_high, "med":cad_med, "medium":cad_med, "low":cad_low}).fillna(cad_low)
f["NextFollowUp"] = f["LastContacted_dt"] + pd.to_timedelta(cadence_map, unit="D")
f["Overdue"] = (pd.Timestamp.today().normalize() > f["NextFollowUp"]).fillna(False)

col1,col2,col3,col4,col5,col6 = st.columns(6)
col1.metric("Prospects", f"{len(f):,}")
col2.metric("Countries", f"{f['Country'].nunique():,}")
col3.metric("Companies", f"{f['Company'].nunique():,}")
col4.metric("CEOs", f"{f['Role'].str.contains('CEO', case=False, na=False).sum():,}")
col5.metric("Unique domains", f"{f['EmailDomain'].nunique():,}")
col6.metric("Overdue follow-ups", int(f["Overdue"].sum()))

(tab_overview, tab_map, tab_companies, tab_roles, tab_funnel, tab_quality, tab_contacts, tab_tools) = st.tabs([
    "Overview","Map","Companies","Roles","Funnel","Data Quality","Contacts","Tools"])

with tab_overview:
    st.subheader("Prospect List")
    visible_cols = st.multiselect(
        "Columns to display",
        ["Name","Email","Phone","Company","Role","Country","Region","Status","Priority","Owner","LastContacted","NextFollowUp","PresentInCRM","Score","Notes"],
        default=["Name","Email","Phone","Company","Role","Country","Region","Status","Priority","Owner","PresentInCRM","Score"],
    )
    tbl = f.sort_values(["Region","Country","Company","Name"]).reset_index(drop=True).copy()
    tbl["Email"] = tbl["Email"].apply(lambda x: f"[{x}](mailto:{x})" if isinstance(x,str) and "@" in x else x)
    tbl["Phone"] = tbl["Phone"].apply(lambda x: f"[{x}](tel:{x})" if isinstance(x,str) and len(x.strip())>0 else x)
    st.data_editor(
        tbl[visible_cols],
        hide_index=True,
        use_container_width=True,
        column_config={
            "Email": st.column_config.LinkColumn("Email"),
            "Phone": st.column_config.LinkColumn("Phone"),
        },
        num_rows="dynamic",
    )

    st.subheader("Charts")
    if not f.empty:
        by_region = f.groupby("Region").size().reset_index(name="Prospects").sort_values("Prospects", ascending=False)
        st.plotly_chart(px.bar(by_region, x="Region", y="Prospects", title="Prospects by Region"), use_container_width=True)
        by_country = f.groupby("Country").size().reset_index(name="Prospects").sort_values("Prospects", ascending=False)
        st.plotly_chart(px.bar(by_country.head(20), x="Country", y="Prospects", title="Top Countries"), use_container_width=True)
        by_company = f.groupby("Company").size().reset_index(name="Prospects").sort_values("Prospects", ascending=False)
        st.plotly_chart(px.treemap(by_company, path=["Company"], values="Prospects", title="Company Treemap"), use_container_width=True)
    else:
        st.info("No rows match your filters.")

with tab_map:
    st.subheader("Prospects by Country (Map)")
    by_country = f.groupby("Country").size().reset_index(name="Prospects")
    if not by_country.empty:
        try:
            figm = px.choropleth(by_country, locations="Country", locationmode="country names", color="Prospects")
            st.plotly_chart(figm, use_container_width=True)
        except Exception:
            st.info("Some country names were not recognized. Consider using full names, e.g., 'United States'.")
    else:
        st.info("No data to show on the map.")

with tab_companies:
    st.subheader("Company summary")
    comp = (
        f.groupby("Company").agg(
            Prospects=("Company","size"),
            Countries=("Country", "nunique"),
            Regions=("Region", "nunique"),
        ).reset_index().sort_values("Prospects", ascending=False)
    )
    st.dataframe(comp, use_container_width=True)
    if not comp.empty:
        st.plotly_chart(px.bar(comp.head(30), x="Company", y="Prospects", title="Top Companies"), use_container_width=True)
        st.plotly_chart(px.sunburst(f, path=["Region","Country","Company"], title="Region → Country → Company"), use_container_width=True)

with tab_roles:
    st.subheader("Role distribution")
    rc = f["RoleNorm"].replace({"":np.nan}).dropna().value_counts().reset_index()
    rc.columns = ["Role","Prospects"]
    if not rc.empty:
        st.plotly_chart(px.bar(rc.head(30), x="Role", y="Prospects", title="Top Roles"), use_container_width=True)
    else:
        st.info("No roles found.")

with tab_funnel:
    st.subheader("Pipeline funnel")
    order = ["New","Contacted","Replied","Meeting","Qualified","Won","Lost"]
    funnel = f["Status"].replace({"":"(blank)"}).value_counts().reindex(order + [s for s in f["Status"].unique() if s not in order], fill_value=0)
    df_funnel = funnel.reset_index(); df_funnel.columns = ["Stage","Prospects"]
    st.plotly_chart(px.bar(df_funnel, x="Stage", y="Prospects", title="Prospects by Stage"), use_container_width=True)

with tab_quality:
    st.subheader("Data quality checks")
    invalid_email = ~std["Email"].str.contains(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", case=False, na=False)
    missing_email = (std["Email"].eq("") | std["Email"].isna())
    dup_by_email = std["Email"].str.lower().duplicated(keep=False) & std["Email"].str.contains("@", na=False)
    dup_name_company = std.assign(_key=(std["Name"].str.lower()+"|"+std["Company"].str.lower()))._key.duplicated(keep=False)

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Invalid emails", int(invalid_email.sum()))
    c2.metric("Missing emails", int(missing_email.sum()))
    c3.metric("Duplicate emails", int(dup_by_email.sum()))
    c4.metric("Dup name+company", int(dup_name_company.sum()))

    with st.expander("Show invalid or missing emails"):
        st.dataframe(std[invalid_email | missing_email][["Name","Email","Phone","Company","Country","Role"]], use_container_width=True)
    with st.expander("Show duplicate emails"):
        st.dataframe(std[dup_by_email][["Name","Email","Company","Country","Role"]].sort_values("Email"), use_container_width=True)
    with st.expander("Show duplicate name+company"):
        st.dataframe(std[dup_name_company][["Name","Company","Email","Country","Role"]].sort_values(["Company","Name"]), use_container_width=True)

with tab_contacts:
    st.subheader("Quick contact finder")
    q = st.text_input("Search by name or company")
    dfc = f.copy()
    if q:
        m = dfc["Name"].str.contains(q, case=False, na=False) | dfc["Company"].str.contains(q, case=False, na=False)
        dfc = dfc[m]
    if dfc.empty:
        st.info("No contacts match your search or filters.")
    else:
        for _, row in dfc.sort_values(["Score"], ascending=False).head(60).iterrows():
            contact_line = ""
            if isinstance(row["Email"], str) and "@" in row["Email"]:
                contact_line = f"📧 <a href=\"mailto:{row['Email']}\">{row['Email']}</a>"
            elif isinstance(row["Phone"], str) and row["Phone"].strip():
                contact_line = f"📞 <a href=\"tel:{row['Phone']}\">{row['Phone']}</a>"
            else:
                contact_line = "📭 —"

            with st.container():
                st.markdown(
                    f"""
                    <div class='contact-card'>
                      <div style='display:flex; justify-content:space-between; align-items:center;'>
                        <div>
                          <div style='font-weight:700;font-size:18px'>{row['Name']}</div>
                          <div class='tiny'>{row['Role']} • {row['Company']}</div>
                          <div class='tiny'>{row['Country']} · Owner: {row['Owner'] if row['Owner'] else '—'} · CRM: {row['PresentInCRM'] if row['PresentInCRM'] else '—'}</div>
                        </div>
                        <div><span class='badge'>Score {row['Score']}</span></div>
                      </div>
                      <div style='margin-top:8px'>
                        {contact_line}
                      </div>
                      <div class='tiny' style='margin-top:6px'>Last contacted: {row['LastContacted'] if row['LastContacted'] else '—'} · Next follow-up: {row['NextFollowUp'].date() if pd.notnull(row['NextFollowUp']) else '—'} {('· OVERDUE' if row['Overdue'] else '')}</div>
                      <div style='margin-top:6px' class='tiny'>{row['Notes'] if row['Notes'] else ''}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

with tab_tools:
    st.subheader("Toolbox")

    st.markdown("**Copy email list (filtered)**")
    emails = ", ".join(sorted([e for e in f["Email"].dropna().unique() if "@" in e]))
    st.text_area("Emails", emails, height=120)

    st.markdown("**Copy phone list (filtered)**")
    phones = ", ".join(sorted([p for p in f["Phone"].dropna().unique() if str(p).strip()]))
    st.text_area("Phones", phones, height=120)

    st.markdown("**CRM export format**")
    template = st.selectbox("Choose template", ["None","Salesforce","HubSpot"])
    export_df = f.copy()
    if template == "Salesforce":
        export_df = export_df.rename(columns={
            "Name":"FullName","Email":"Email","Phone":"Phone","Company":"AccountName","Role":"Title","Country":"Country",
            "Status":"LeadStatus","Priority":"Rating","Owner":"Owner","Notes":"Description","PresentInCRM":"PresentInCRM"
        })[["FullName","Title","Email","Phone","AccountName","Country","LeadStatus","Rating","Owner","NextFollowUp","PresentInCRM","Description"]]
    elif template == "HubSpot":
        export_df = export_df.rename(columns={
            "Name":"firstname lastname","Email":"email","Phone":"phone","Company":"company","Role":"jobtitle","Country":"country",
            "Status":"lifecyclestage","Priority":"hs_lead_rating","Owner":"hubspot_owner_id","Notes":"notes","PresentInCRM":"present_in_crm"
        })[["firstname lastname","jobtitle","email","phone","company","country","lifecyclestage","hs_lead_rating","hubspot_owner_id","NextFollowUp","present_in_crm","notes"]]

    colA,colB = st.columns([1,1])
    with colA:
        st.download_button("Download filtered CSV", export_df.to_csv(index=False).encode("utf-8"), "prospects_filtered.csv", "text/csv")
    with colB:
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="xlsxwriter") as wr:
            export_df.to_excel(wr, index=False, sheet_name="Prospects")
        st.download_button("Download filtered Excel", buf.getvalue(), "prospects_filtered.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
