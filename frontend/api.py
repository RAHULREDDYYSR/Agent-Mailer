import requests
import streamlit as st
import os

class APIClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url

    def _get_headers(self):
        token = st.session_state.get("access_token")
        if token:
            return {"Authorization": f"Bearer {token}"}
        return {}

    def login(self, username, password):
        url = f"{self.base_url}/auth/login"
        try:
            response = requests.post(url, json={"username": username, "password": password})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "details": response.text if 'response' in locals() else ""}

    def register(self, username, email, password, first_name=None, last_name=None, phone=None, linkedin=None, github=None, portfolio=None, role="user"):
        url = f"{self.base_url}/users/"
        payload = {
            "username": username,
            "email": email,
            "password": password,
            "role": role,
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,
            "linkedin": linkedin,
            "github": github,
            "portfolio": portfolio
        }
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return True
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 409:
                 return {"error": "Username already exists"}
            return {"error": str(e)}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def get_user_me(self):
        url = f"{self.base_url}/users/me"
        try:
            response = requests.get(url, headers=self._get_headers())
            return response.json()
        except requests.exceptions.RequestException:
            return None

    def upload_context(self, files):
        url = f"{self.base_url}/users/context"
        files_payload = [('files', (f.name, f.getvalue(), f.type)) for f in files]
        try:
            response = requests.post(url, headers=self._get_headers(), files=files_payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "details": response.text if 'response' in locals() else ""}

    def delete_context(self):
        url = f"{self.base_url}/users/context"
        try:
            response = requests.delete(url, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
             return {"error": str(e), "details": response.text if 'response' in locals() else ""}

    def get_jobs(self):
        url = f"{self.base_url}/users/jobs"
        try:
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return []

    def generate_context(self, job_description):
        url = f"{self.base_url}/generation/context"
        data = {"job_description": job_description}
        try:
            response = requests.post(url, headers=self._get_headers(), data=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
             return {"error": str(e), "details": response.text if 'response' in locals() else ""}

    def draft_context(self, jd_id, type_, feedback=None):
        url = f"{self.base_url}/generation/draft_context"
        params = {"jd_id": jd_id, "type": type_}
        data = {}
        if feedback:
            data["feedback"] = feedback
            
        try:
            response = requests.post(url, headers=self._get_headers(), params=params, data=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "details": response.text if 'response' in locals() else ""}
            
    def send_email(self, to_address, subject, body, files=None):
        url = f"{self.base_url}/generation/send_email"
        data = {
            "to_address": to_address,
            "subject": subject,
            "body": body
        }
        files_payload = []
        if files:
            files_payload = [('files', (f.name, f.getvalue(), f.type)) for f in files]
            
        try:
            response = requests.post(url, headers=self._get_headers(), data=data, files=files_payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "details": response.text if 'response' in locals() else ""}

    def get_all_generated_contents(self):
        url = f"{self.base_url}/generation/generated_contents"
        try:
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return []

    def get_generated_contents_by_type(self, content_type):
        url = f"{self.base_url}/generation/generated_contents/{content_type}"
        try:
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return []
            
    def get_generated_contents_by_job(self, jd_id):
        url = f"{self.base_url}/generation/generated_contents/job/{jd_id}"
        try:
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return []

api = APIClient()
