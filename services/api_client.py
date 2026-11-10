import os
import requests
import streamlit as st

class APIError(Exception): pass

class APIClient:
    def __init__(self):
        secret_url=""
        try: secret_url=st.secrets.get("BACKEND_BASE_URL","")
        except Exception: pass
        self.base_url=(os.getenv("BACKEND_BASE_URL") or secret_url).rstrip("/")
        try: secret_key=st.secrets.get("BACKEND_API_KEY","")
        except Exception: secret_key=""
        self.api_key=os.getenv("BACKEND_API_KEY") or secret_key
        self.timeout=int(os.getenv("API_TIMEOUT_SECONDS","120"))

    def request(self,method,path,**kwargs):
        if not self.base_url: raise APIError("Set BACKEND_BASE_URL in your .env file.")
        headers={"Accept":"application/json"}
        if self.api_key: headers["Authorization"]="Bearer "+self.api_key
        try:
            r=requests.request(method,self.base_url+path,headers=headers,timeout=self.timeout,**kwargs)
            if not r.ok: raise APIError(f"Backend HTTP {r.status_code}: {r.text[:1000]}")
            return r.json() if r.content else {}
        except requests.RequestException as e: raise APIError(f"Backend connection failed: {e}")

    def health(self): return self.request("GET","/health")
    def create_analysis(self,pid,name,date,budget,notes,bom,quotes,stock):
        data={"project_id":pid,"project_name":name,"required_date":date,"budget_inr":str(budget),"currency":"INR","notes":notes}
        files=[("bom_file",(bom.name,bom.getvalue(),bom.type or "application/octet-stream"))]
        files += [("quotation_files",(f.name,f.getvalue(),f.type or "application/octet-stream")) for f in quotes]
        files += [("availability_files",(f.name,f.getvalue(),f.type or "application/octet-stream")) for f in stock]
        return self.request("POST","/api/analysis",data=data,files=files)
    def get_recommendation(self,pid): return self.request("GET",f"/api/recommendations/{pid}")
    def submit_approval(self,pid,decision,comments):
        return self.request("POST","/api/approvals",json={"project_id":pid,"decision":decision,"comments":comments})
    def approval_history(self,pid=None):
        return self.request("GET","/api/approvals/history",params={"project_id":pid} if pid else {})
