import streamlit as st
from services.api_client import APIClient, APIError

st.set_page_config(page_title="ProcureAI | Electronics Procurement", page_icon="⚙️", layout="wide")
api=APIClient()
st.markdown("""
<style>
.block-container{max-width:1400px;padding-top:1.5rem}
.hero{background:linear-gradient(110deg,#14233f,#29466f);padding:28px;border-radius:16px;color:white}
.hero h1{color:white;margin:0}.hero p{color:#dce5f2;margin:6px 0 0}
[data-testid="stSidebar"]{background:#14233f}[data-testid="stSidebar"] *{color:white}
div[data-testid="stMetric"]{background:#f4f6fa;padding:14px;border-radius:12px}
</style>
""",unsafe_allow_html=True)
with st.sidebar:
    st.markdown("## ⚙️ ProcureAI")
    st.caption("Electronics Procurement Intelligence")
    page=st.radio("WORKSPACE",["Dashboard","New Analysis","Recommendations","Approval History","System Status"])
    st.divider()
    st.caption("AI-assisted • Data-driven • Human-approved")
st.markdown('<div class="hero"><h1>Electronics Procurement</h1><p>AI-assisted. Data-driven. Human-approved.</p></div>',unsafe_allow_html=True)

if page=="Dashboard":
    st.subheader("Procurement workspace")
    a,b,c,d=st.columns(4)
    a.metric("Active projects","—"); b.metric("Completed analyses","—"); c.metric("Pending approvals","—"); d.metric("Estimated savings","—")
    st.info("Start a new analysis to upload a BOM, supplier quotations and stock evidence.")
    st.write("Use **New Analysis** in the sidebar to begin.")
elif page=="New Analysis":
    st.subheader("Create procurement analysis")
    with st.form("analysis"):
        l,r=st.columns(2)
        with l:
            project_name=st.text_input("Project name",placeholder="Smart Home Controller")
            project_id=st.text_input("Project ID",placeholder="PRJ-001")
            required_date=st.date_input("Required-by date")
        with r:
            budget=st.number_input("Target budget (₹)",min_value=0.0,step=500.0)
            notes=st.text_area("Procurement notes")
        bom=st.file_uploader("Bill of Materials",type=["csv","xlsx"])
        quotes=st.file_uploader("Supplier quotations",type=["csv","xlsx","pdf"],accept_multiple_files=True)
        stock=st.file_uploader("Stock / lead-time evidence (optional)",type=["csv","xlsx","pdf"],accept_multiple_files=True)
        submit=st.form_submit_button("Validate and start analysis",type="primary",use_container_width=True)
    if submit:
        if not project_name.strip() or not project_id.strip() or not bom:
            st.error("Project name, project ID and BOM file are required.")
        else:
            try:
                with st.spinner("Uploading files and starting agent workflow..."):
                    result=api.create_analysis(project_id,project_name,required_date.isoformat(),budget,notes,bom,quotes or [],stock or [])
                st.success("Analysis request accepted.")
                st.session_state["last_project_id"]=project_id
                st.json(result)
            except APIError as e: st.error(str(e))
elif page=="Recommendations":
    st.subheader("Recommendation review")
    pid=st.text_input("Project ID",value=st.session_state.get("last_project_id",""))
    if st.button("Load recommendation",type="primary"):
        try: st.session_state["recommendation"]=api.get_recommendation(pid)
        except APIError as e: st.error(str(e))
    data=st.session_state.get("recommendation")
    if data:
        st.write("**Analysis status:**",data.get("analysis_status",data.get("status","unknown")))
        x,y,z=st.columns(3)
        x.metric("Estimated total",f"₹{data.get('total_estimated_cost',0):,.2f}" if data.get("total_estimated_cost") is not None else "—")
        y.metric("Recommended supplier",data.get("recommended_supplier","—"))
        z.metric("Approval status",data.get("approval_status","pending"))
        rec=data.get("recommendation",{})
        st.markdown("### Recommendation")
        st.write(rec.get("reason",data.get("explanation","No explanation returned yet.")))
        for risk in rec.get("risks",data.get("risks",[])): st.warning(str(risk))
        if data.get("supplier_comparison"):
            st.markdown("### Supplier comparison")
            st.dataframe(data["supplier_comparison"],use_container_width=True,hide_index=True)
        if data.get("components"):
            st.markdown("### Component results")
            st.dataframe(data["components"],use_container_width=True,hide_index=True)
        with st.expander("Raw evidence / JSON"): st.json(data)
        st.markdown("### Human approval")
        comments=st.text_area("Review comments")
        a,b,c=st.columns(3)
        for col,label,decision in [(a,"Approve","approved"),(b,"Request changes","edit_requested"),(c,"Reject","rejected")]:
            if col.button(label,use_container_width=True,type="primary" if decision=="approved" else "secondary"):
                try:
                    result=api.submit_approval(pid,decision,comments); st.success("Decision saved."); st.json(result)
                except APIError as e: st.error(str(e))
    else: st.info("Run an analysis or enter an existing project ID.")
elif page=="Approval History":
    st.subheader("Approval history")
    pid=st.text_input("Project ID (optional)",value=st.session_state.get("last_project_id",""))
    if st.button("Refresh history"):
        try:
            result=api.approval_history(pid or None)
            st.dataframe(result.get("items",result if isinstance(result,list) else []),use_container_width=True,hide_index=True)
        except APIError as e: st.error(str(e))
    st.caption("Requires GET /api/approvals/history on your backend.")
else:
    st.subheader("System status")
    st.write("Backend URL:",api.base_url or "Not configured")
    if st.button("Check backend health",type="primary"):
        try: st.success("Backend reachable"); st.json(api.health())
        except APIError as e: st.error(str(e))
    st.markdown("Expected: Streamlit → Python API → SNS Agent Workbench → Python calculation engine → Supabase.")
    st.warning("Keep NVIDIA and Supabase secret keys on the backend. Never expose them in Streamlit.")
