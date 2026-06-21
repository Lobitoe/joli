"""Joli V3 backend tests - new admin users/activity/suspend endpoints + regression.

Uses _auth_request helper that does NOT share cookies across logins, because backend
auth.py reads cookie first then Bearer (would mix users in a shared Session).
"""
import os
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://spec-to-launch.preview.emergentagent.com").rstrip("/")


def _login(email, password):
    r = requests.post(f"{BASE_URL}/api/auth/login",
                      json={"email": email, "password": password},
                      headers={"Content-Type": "application/json"})
    assert r.status_code == 200, f"Login failed {email}: {r.status_code} {r.text}"
    d = r.json()
    return d.get("token") or d.get("access_token")


def _auth(method, path, token, **kw):
    headers = kw.pop("headers", {}) or {}
    headers["Authorization"] = f"Bearer {token}"
    headers.setdefault("Content-Type", "application/json")
    return requests.request(method, f"{BASE_URL}{path}", headers=headers, **kw)


@pytest.fixture(scope="module")
def admin_token():
    return _login("admin@tryjoli.com", "AdminPass123!")


@pytest.fixture(scope="module")
def amara_token():
    return _login("amara@tryjoli.com", "Pass123!")


@pytest.fixture(scope="module")
def blessing_token():
    return _login("blessing@tryjoli.com", "Pass123!")


# --------------------------- REGRESSION basics ---------------------------
class TestRegression:
    def test_auth_me_admin(self, admin_token):
        r = _auth("GET", "/api/auth/me", admin_token)
        assert r.status_code == 200
        assert r.json().get("role") == "admin"

    def test_auth_me_client(self, amara_token):
        r = _auth("GET", "/api/auth/me", amara_token)
        assert r.status_code == 200
        assert r.json().get("role") == "client"

    def test_practitioners_list(self):
        r = requests.get(f"{BASE_URL}/api/practitioners")
        assert r.status_code == 200
        items = r.json() if isinstance(r.json(), list) else r.json().get("items", [])
        assert len(items) >= 5
        for p in items:
            assert "badges" in p and isinstance(p["badges"], list)

    def test_blog_index(self):
        r = requests.get(f"{BASE_URL}/api/blog")
        assert r.status_code == 200
        posts = r.json() if isinstance(r.json(), list) else r.json().get("items", [])
        assert len(posts) == 8


# --------------------------- NEW: GET /api/admin/users ---------------------------
class TestAdminUsers:
    def test_list_all_users(self, admin_token):
        r = _auth("GET", "/api/admin/users", admin_token)
        assert r.status_code == 200
        users = r.json()
        assert isinstance(users, list)
        assert len(users) >= 8  # 1 admin + 5 prac + 2 clients (at minimum)
        roles = {u["role"] for u in users}
        assert {"admin", "practitioner", "client"}.issubset(roles)
        # Every user has bookings_count
        for u in users:
            assert "bookings_count" in u
            assert isinstance(u["bookings_count"], int)
            # password_hash MUST be stripped
            assert "password_hash" not in u

    def test_practitioner_rows_have_enrichment(self, admin_token):
        r = _auth("GET", "/api/admin/users", admin_token, params={"role": "practitioner"})
        assert r.status_code == 200
        pracs = r.json()
        assert len(pracs) >= 5
        for u in pracs:
            assert u["role"] == "practitioner"
            assert "practitioner_id" in u
            assert "practitioner_display_name" in u
            assert "verification_status" in u
            assert "is_suspended" in u

    def test_filter_role_client(self, admin_token):
        r = _auth("GET", "/api/admin/users", admin_token, params={"role": "client"})
        assert r.status_code == 200
        clients = r.json()
        assert len(clients) >= 2
        for u in clients:
            assert u["role"] == "client"

    def test_search_blessing(self, admin_token):
        r = _auth("GET", "/api/admin/users", admin_token, params={"search": "blessing"})
        assert r.status_code == 200
        out = r.json()
        assert len(out) >= 1
        assert any("blessing" in (u.get("email", "") + u.get("name", "")).lower() for u in out)

    def test_non_admin_forbidden_users(self, amara_token):
        r = _auth("GET", "/api/admin/users", amara_token)
        assert r.status_code == 403

    def test_non_admin_forbidden_activity(self, amara_token):
        r = _auth("GET", "/api/admin/activity", amara_token)
        assert r.status_code == 403


# --------------------------- NEW: GET /api/admin/activity ---------------------------
class TestAdminActivity:
    def test_activity_feed(self, admin_token):
        r = _auth("GET", "/api/admin/activity", admin_token)
        assert r.status_code == 200
        items = r.json()
        assert isinstance(items, list)
        assert len(items) >= 10, f"Expected reasonable activity, got {len(items)}"
        kinds_present = {i["kind"] for i in items}
        # At least 3 of the 4 expected kinds must exist
        expected_kinds = {"user_joined", "booking_created", "review_posted", "verification_submitted"}
        assert len(kinds_present & expected_kinds) >= 3, f"Got kinds: {kinds_present}"
        # Sorted by 'at' desc
        ats = [i["at"] for i in items]
        assert ats == sorted(ats, reverse=True)
        # Each item has required fields
        for it in items:
            assert "kind" in it and "at" in it and "summary" in it


# --------------------------- NEW: Suspend toggle ---------------------------
class TestSuspend:
    def test_suspend_blessing_hides_from_public(self, admin_token):
        # Find Blessing practitioner_id
        r = requests.get(f"{BASE_URL}/api/practitioners")
        items = r.json() if isinstance(r.json(), list) else r.json().get("items", [])
        blessing = next((p for p in items if "blessing" in (p.get("display_name", "") + p.get("slug", "")).lower()), None)
        assert blessing, "Blessing must be in initial public list"
        pid = blessing["id"]

        # Suspend
        r2 = _auth("PUT", f"/api/admin/practitioners/{pid}/suspend", admin_token,
                   json={"suspended": True, "reason": "demo"})
        assert r2.status_code == 200, f"Suspend failed: {r2.status_code} {r2.text}"
        assert r2.json().get("is_suspended") is True

        try:
            # Public list should NOT include Blessing
            r3 = requests.get(f"{BASE_URL}/api/practitioners")
            items3 = r3.json() if isinstance(r3.json(), list) else r3.json().get("items", [])
            names = {p.get("display_name", "").lower() for p in items3}
            assert not any("blessing" in n for n in names), f"Blessing still showing: {names}"

            # Admin /admin/users should show is_suspended=True for Blessing
            r4 = _auth("GET", "/api/admin/users", admin_token, params={"search": "blessing"})
            blessings_row = next((u for u in r4.json() if u.get("practitioner_id") == pid), None)
            assert blessings_row, "Blessing row missing in admin/users"
            assert blessings_row["is_suspended"] is True
        finally:
            # Reinstate so subsequent tests / app are clean
            r5 = _auth("PUT", f"/api/admin/practitioners/{pid}/suspend", admin_token,
                       json={"suspended": False})
            assert r5.status_code == 200
            assert r5.json().get("is_suspended") is False

        # After reinstate, Blessing reappears
        r6 = requests.get(f"{BASE_URL}/api/practitioners")
        items6 = r6.json() if isinstance(r6.json(), list) else r6.json().get("items", [])
        names6 = {p.get("display_name", "").lower() for p in items6}
        assert any("blessing" in n for n in names6), f"Blessing missing after reinstate: {names6}"

    def test_suspend_non_admin_forbidden(self, amara_token):
        # Just need any practitioner id
        r = requests.get(f"{BASE_URL}/api/practitioners")
        items = r.json() if isinstance(r.json(), list) else r.json().get("items", [])
        pid = items[0]["id"]
        r2 = _auth("PUT", f"/api/admin/practitioners/{pid}/suspend", amara_token,
                   json={"suspended": True})
        assert r2.status_code == 403

    def test_suspend_404_unknown(self, admin_token):
        r = _auth("PUT", "/api/admin/practitioners/does-not-exist/suspend", admin_token,
                 json={"suspended": True})
        assert r.status_code == 404
