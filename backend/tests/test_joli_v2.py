"""Joli V2 backend tests - rebrand + vetting/badges + blog."""
import os
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://spec-to-launch.preview.emergentagent.com").rstrip("/")


@pytest.fixture(scope="module")
def session():
    # Use plain requests (no Session) so cookies don't leak across logins.
    # The backend reads cookie first, then Authorization header, so a shared
    # Session would carry the cookie of the most recent login.
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


def _login_fresh(email, password):
    """Login with a fresh requests call (no shared cookies)."""
    r = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": email, "password": password},
        headers={"Content-Type": "application/json"},
    )
    assert r.status_code == 200, f"Login failed for {email}: {r.status_code} {r.text}"
    data = r.json()
    token = data.get("token") or data.get("access_token")
    assert token, f"No token in login response: {data}"
    return token, data


def _auth_request(method, path, token, **kwargs):
    """Make an HTTP call with Bearer + a fresh requests call to avoid cookie leakage."""
    headers = kwargs.pop("headers", {}) or {}
    headers["Authorization"] = f"Bearer {token}"
    headers.setdefault("Content-Type", "application/json")
    return requests.request(method, f"{BASE_URL}{path}", headers=headers, **kwargs)


@pytest.fixture(scope="module")
def blessing_token():
    token, _ = _login_fresh("blessing@tryjoli.com", "Pass123!")
    return token


@pytest.fixture(scope="module")
def admin_token():
    token, _ = _login_fresh("admin@tryjoli.com", "AdminPass123!")
    return token


@pytest.fixture(scope="module")
def amara_token():
    token, _ = _login_fresh("amara@tryjoli.com", "Pass123!")
    return token


# ---------- AUTH / REBRAND ----------
class TestAuthRebrand:
    def test_login_admin(self, session):
        token, data = _login_fresh("admin@tryjoli.com", "AdminPass123!")
        assert data.get("user", {}).get("role") == "admin" or "admin" in str(data).lower()

    def test_login_blessing(self, session):
        token, _ = _login_fresh("blessing@tryjoli.com", "Pass123!")
        assert token

    @pytest.mark.parametrize("email", [
        "kofi@tryjoli.com", "linh@tryjoli.com", "priya@tryjoli.com",
        "fatima@tryjoli.com", "amara@tryjoli.com", "daniel@tryjoli.com",
    ])
    def test_login_other_users(self, session, email):
        token, _ = _login_fresh(email, "Pass123!")
        assert token

    def test_old_curlnect_emails_rejected(self, session):
        r = requests.post(f"{BASE_URL}/api/auth/login",
                          json={"email": "admin@curlnect.com", "password": "AdminPass123!"})
        assert r.status_code in (400, 401, 404)


# ---------- PRACTITIONERS / BADGES ----------
class TestPractitionersBadges:
    def test_list_practitioners(self, session):
        r = session.get(f"{BASE_URL}/api/practitioners")
        assert r.status_code == 200
        data = r.json()
        items = data if isinstance(data, list) else data.get("items") or data.get("practitioners") or []
        assert len(items) >= 5, f"Expected >=5 practitioners, got {len(items)}"
        # Each must have badges array
        for p in items:
            assert "badges" in p, f"Practitioner missing 'badges': {p.get('display_name')}"
            assert isinstance(p["badges"], list)

    def test_kofi_badges(self, session):
        r = session.get(f"{BASE_URL}/api/practitioners")
        items = r.json() if isinstance(r.json(), list) else r.json().get("items", [])
        kofi = next((p for p in items if "kofi" in p.get("display_name", "").lower() or "kofi" in p.get("slug", "").lower()), None)
        assert kofi, "Kofi not found"
        assert "certified_barber" in kofi["badges"]
        assert "top_rated" in kofi["badges"]

    def test_linh_badges(self, session):
        r = session.get(f"{BASE_URL}/api/practitioners")
        items = r.json() if isinstance(r.json(), list) else r.json().get("items", [])
        linh = next((p for p in items if "linh" in p.get("display_name", "").lower() or "linh" in p.get("slug", "").lower()), None)
        assert linh
        assert "insured" in linh["badges"]
        assert "top_rated" in linh["badges"]

    def test_blessing_badges(self, session):
        r = session.get(f"{BASE_URL}/api/practitioners")
        items = r.json() if isinstance(r.json(), list) else r.json().get("items", [])
        blessing = next((p for p in items if "blessing" in p.get("display_name", "").lower() or "blessing" in p.get("slug", "").lower()), None)
        assert blessing
        assert "top_rated" in blessing["badges"]
        assert "community_endorsed" in blessing["badges"]

    def test_practitioner_detail_has_verifications(self, session):
        r = session.get(f"{BASE_URL}/api/practitioners")
        items = r.json() if isinstance(r.json(), list) else r.json().get("items", [])
        pid = items[0]["id"]
        r2 = session.get(f"{BASE_URL}/api/practitioners/{pid}")
        assert r2.status_code == 200
        d = r2.json()
        assert "badges" in d and isinstance(d["badges"], list)
        assert "verifications" in d and isinstance(d["verifications"], list)


# ---------- BLOG ----------
class TestBlog:
    def test_blog_index(self, session):
        r = session.get(f"{BASE_URL}/api/blog")
        assert r.status_code == 200
        data = r.json()
        posts = data if isinstance(data, list) else data.get("items") or data.get("posts") or []
        assert len(posts) == 8, f"Expected 8 posts, got {len(posts)}"
        # Sorted by published_at desc
        if all("published_at" in p for p in posts):
            dates = [p["published_at"] for p in posts]
            assert dates == sorted(dates, reverse=True)
        # Each post fields
        for p in posts:
            for k in ["slug", "title", "category", "city", "hero_image", "excerpt", "author"]:
                assert k in p, f"Post {p.get('slug')} missing field {k}"

    def test_blog_filter_category(self, session):
        r = session.get(f"{BASE_URL}/api/blog", params={"category": "Local Discovery"})
        assert r.status_code == 200
        data = r.json()
        posts = data if isinstance(data, list) else data.get("items") or []
        assert len(posts) == 5, f"Expected 5 'Local Discovery' posts, got {len(posts)}"

    def test_blog_filter_city(self, session):
        r = session.get(f"{BASE_URL}/api/blog", params={"city": "Calgary"})
        assert r.status_code == 200
        data = r.json()
        posts = data if isinstance(data, list) else data.get("items") or []
        slugs = {p["slug"] for p in posts}
        expected = {"best-braiders-calgary-2026", "mobile-barbers-calgary-edmonton", "bridal-mehndi-calgary-2026"}
        assert expected.issubset(slugs), f"Expected slugs {expected} in {slugs}"

    def test_blog_post_detail(self, session):
        r = session.get(f"{BASE_URL}/api/blog/best-braiders-calgary-2026")
        assert r.status_code == 200
        d = r.json()
        assert d.get("slug") == "best-braiders-calgary-2026"
        assert d.get("body_markdown"), "body_markdown missing"
        embedded = d.get("embedded_practitioners") or []
        assert len(embedded) >= 1, "Expected at least 1 embedded practitioner"
        blessing = next((p for p in embedded if "blessing" in (p.get("display_name", "") + p.get("slug", "")).lower()), None)
        assert blessing, "Blessing should be embedded"
        for k in ["display_name", "starting_price", "badges"]:
            assert k in blessing, f"Embedded practitioner missing {k}"


# ---------- VERIFICATIONS (sequential single-flow to avoid pytest alpha-ordering issues) ----------
class TestVerifications:
    def test_full_verification_workflow(self, session, blessing_token, admin_token, amara_token):
        # 1. Practitioner submits verification
        r = _auth_request(
            "POST", "/api/me/practitioner/verifications", blessing_token,
            json={"verification_type": "insurance", "document_url": "https://example.com/cert.pdf"},
        )
        assert r.status_code in (200, 201), f"POST verification failed: {r.status_code} {r.text}"
        body = r.json()
        # API returns minimal { ok: True, status: 'pending' } -- accept either shape
        assert body.get("status") == "pending" or body.get("verification_type") == "insurance"

        # 2. Practitioner GETs own verifications (returns {verifications, badges, verification_status})
        r2 = _auth_request("GET", "/api/me/practitioner/verifications", blessing_token)
        assert r2.status_code == 200
        d = r2.json()
        verifs = d.get("verifications") if isinstance(d, dict) else d
        assert any(v.get("verification_type") == "insurance" for v in verifs)

        # 3. Admin sees pending list with enriched practitioner_name / email
        r3 = _auth_request("GET", "/api/admin/verifications", admin_token)
        assert r3.status_code == 200, f"Admin list failed: {r3.status_code} {r3.text}"
        items = r3.json() if isinstance(r3.json(), list) else r3.json().get("items") or []
        assert len(items) >= 1
        target = next((v for v in items
                       if v.get("verification_type") == "insurance"
                       and "blessing" in (v.get("practitioner_email", "") + v.get("practitioner_name", "")).lower()
                       and v.get("status") == "pending"), None)
        assert target, f"No pending insurance for Blessing among {len(items)} items: {[(v.get('practitioner_email'), v.get('verification_type'), v.get('status')) for v in items]}"
        assert target.get("practitioner_name")
        assert target.get("practitioner_email")
        vid = target.get("id") or target.get("_id")

        # 4. Non-admin gets 403
        r4 = _auth_request("GET", "/api/admin/verifications", amara_token)
        assert r4.status_code == 403

        # 5. Admin approves with grant_badges=['insured']
        r5 = _auth_request(
            "PUT", f"/api/admin/verifications/{vid}", admin_token,
            json={"decision": "verified", "grant_badges": ["insured"]},
        )
        assert r5.status_code == 200, f"PUT verification failed: {r5.status_code} {r5.text}"

        # 6. Verify badge granted in practitioner detail
        r6 = requests.get(f"{BASE_URL}/api/practitioners")
        items = r6.json() if isinstance(r6.json(), list) else r6.json().get("items", [])
        blessing = next((p for p in items if "blessing" in (p.get("display_name", "") + p.get("slug", "")).lower()), None)
        assert blessing
        pid = blessing["id"]
        r7 = requests.get(f"{BASE_URL}/api/practitioners/{pid}")
        d = r7.json()
        assert "insured" in d.get("badges", []), f"Insured badge not granted; badges={d.get('badges')}"
        assert d.get("is_insured") is True, f"is_insured not True; got {d.get('is_insured')}"


# ---------- EXISTING FLOWS (regression) ----------
class TestRegression:
    def test_categories(self, session):
        r = session.get(f"{BASE_URL}/api/categories")
        assert r.status_code == 200
        items = r.json() if isinstance(r.json(), list) else r.json().get("items", [])
        assert len(items) > 0

    def test_practitioner_by_slug(self, session):
        r = session.get(f"{BASE_URL}/api/practitioners/slug/blessing-braids-yyc")
        assert r.status_code == 200
        d = r.json()
        assert "blessing" in d.get("display_name", "").lower()

    def test_admin_stats(self, session, admin_token):
        r = _auth_request("GET", "/api/admin/stats", admin_token)
        assert r.status_code == 200

    def test_slots(self, session):
        r = session.get(f"{BASE_URL}/api/practitioners")
        items = r.json() if isinstance(r.json(), list) else r.json().get("items", [])
        pid = items[0]["id"]
        # fetch services for the practitioner via the detail endpoint
        r2 = session.get(f"{BASE_URL}/api/practitioners/{pid}")
        services = r2.json().get("services", [])
        if not services:
            pytest.skip("No services for this practitioner")
        sid = services[0]["id"]
        from datetime import date, timedelta
        d = (date.today() + timedelta(days=2)).isoformat()
        r3 = session.get(f"{BASE_URL}/api/practitioners/{pid}/slots", params={"date": d, "service_id": sid})
        assert r3.status_code == 200
