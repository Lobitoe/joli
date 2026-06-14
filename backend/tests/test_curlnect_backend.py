"""Curlnect backend API tests."""
import os
import pytest
import requests
import uuid

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://spec-to-launch.preview.emergentagent.com").rstrip("/")
API = f"{BASE_URL}/api"

CLIENT_EMAIL = "amara@curlnect.com"
CLIENT_PASS = "Pass123!"
PRAC_EMAIL = "blessing@curlnect.com"
PRAC_PASS = "Pass123!"
ADMIN_EMAIL = "admin@curlnect.com"
ADMIN_PASS = "AdminPass123!"


# --- helpers ---
def _login(email, password):
    r = requests.post(f"{API}/auth/login", json={"email": email, "password": password}, timeout=30)
    assert r.status_code == 200, f"login failed: {r.status_code} {r.text}"
    data = r.json()
    return data["token"], data["user"]


@pytest.fixture(scope="session")
def client_auth():
    token, user = _login(CLIENT_EMAIL, CLIENT_PASS)
    return {"Authorization": f"Bearer {token}"}, user


@pytest.fixture(scope="session")
def prac_auth():
    token, user = _login(PRAC_EMAIL, PRAC_PASS)
    return {"Authorization": f"Bearer {token}"}, user


@pytest.fixture(scope="session")
def admin_auth():
    token, user = _login(ADMIN_EMAIL, ADMIN_PASS)
    return {"Authorization": f"Bearer {token}"}, user


# ---------- Categories ----------
def test_categories_seeded():
    r = requests.get(f"{API}/categories", timeout=30)
    assert r.status_code == 200
    cats = r.json()
    assert isinstance(cats, list) and len(cats) >= 30, f"expected ~44 cats, got {len(cats)}"
    # No mongo _id leaking
    assert all("_id" not in c for c in cats)
    assert all("id" in c and "name" in c for c in cats)


# ---------- Practitioners discovery ----------
def test_list_practitioners():
    r = requests.get(f"{API}/practitioners", timeout=30)
    assert r.status_code == 200
    pracs = r.json()
    assert len(pracs) >= 4
    p = pracs[0]
    for k in ["portfolio_thumbs", "service_count", "starting_price", "display_name", "city"]:
        assert k in p, f"missing field {k}"
    assert all("_id" not in pp for pp in pracs)


def test_filter_practitioners_calgary():
    r = requests.get(f"{API}/practitioners", params={"city": "Calgary"}, timeout=30)
    assert r.status_code == 200
    for p in r.json():
        assert p["city"].lower() == "calgary"


def test_filter_practitioners_calgary_skin_fade():
    r = requests.get(f"{API}/practitioners", params={"city": "Calgary", "category": "Skin Fade"}, timeout=30)
    assert r.status_code == 200
    pracs = r.json()
    # Should narrow to barbers offering Skin Fade in Calgary; expect ≥1 (Kofi)
    assert len(pracs) >= 1, "expected at least 1 practitioner for Calgary + Skin Fade"


def test_practitioner_by_id_enriched():
    r = requests.get(f"{API}/practitioners", timeout=30)
    pid = r.json()[0]["id"]
    r2 = requests.get(f"{API}/practitioners/{pid}", timeout=30)
    assert r2.status_code == 200
    detail = r2.json()
    for k in ["services", "portfolio", "reviews", "availability"]:
        assert k in detail


def test_practitioner_by_slug_kofi():
    r = requests.get(f"{API}/practitioners/slug/kofi-cuts-yyc", timeout=30)
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["direct_booking_slug"] == "kofi-cuts-yyc"
    assert len(d["services"]) >= 1


# ---------- Auth ----------
def test_register_and_email_unique():
    email = f"TEST_{uuid.uuid4().hex[:8]}@curlnect.com"
    payload = {"email": email, "password": "Pass123!", "name": "Test User", "role": "client"}
    r = requests.post(f"{API}/auth/register", json=payload, timeout=30)
    assert r.status_code == 200, r.text
    data = r.json()
    assert "token" in data and data["user"]["email"] == email
    # cookie set
    assert "access_token" in r.cookies or any(c.name == "access_token" for c in r.cookies)
    # duplicate
    r2 = requests.post(f"{API}/auth/register", json=payload, timeout=30)
    assert r2.status_code == 409


def test_login_invalid():
    r = requests.post(f"{API}/auth/login", json={"email": CLIENT_EMAIL, "password": "wrong"}, timeout=30)
    assert r.status_code == 401


def test_me_endpoint(client_auth):
    headers, _ = client_auth
    r = requests.get(f"{API}/auth/me", headers=headers, timeout=30)
    assert r.status_code == 200
    assert r.json()["email"] == CLIENT_EMAIL


# ---------- Slots ----------
def test_slots_endpoint():
    r = requests.get(f"{API}/practitioners/slug/kofi-cuts-yyc", timeout=30)
    prac = r.json()
    pid = prac["id"]
    sid = prac["services"][0]["id"]
    # find a date that matches availability — pick next 14 days, take first non-empty
    from datetime import date, timedelta
    found = False
    for i in range(1, 15):
        d = (date.today() + timedelta(days=i)).isoformat()
        rs = requests.get(f"{API}/practitioners/{pid}/slots", params={"date": d, "service_id": sid}, timeout=30)
        assert rs.status_code == 200
        data = rs.json()
        if data["slots"]:
            found = True
            assert all(":" in s and len(s) == 5 for s in data["slots"])
            break
    assert found, "no slots found for kofi in next 14 days"


# ---------- Bookings & commission ----------
@pytest.fixture(scope="session")
def fresh_client_token():
    """Create a brand-new client to test first-booking commission cleanly."""
    email = f"TEST_book_{uuid.uuid4().hex[:6]}@curlnect.com"
    payload = {"email": email, "password": "Pass123!", "name": "TestBooker", "role": "client"}
    r = requests.post(f"{API}/auth/register", json=payload, timeout=30)
    assert r.status_code == 200
    return {"Authorization": f"Bearer {r.json()['token']}"}, r.json()["user"]


def _pick_booking(slug):
    from datetime import date, timedelta
    r = requests.get(f"{API}/practitioners/slug/{slug}", timeout=30)
    prac = r.json()
    pid = prac["id"]
    sid = prac["services"][0]["id"]
    for i in range(1, 21):
        d = (date.today() + timedelta(days=i)).isoformat()
        rs = requests.get(f"{API}/practitioners/{pid}/slots", params={"date": d, "service_id": sid}, timeout=30)
        slots = rs.json().get("slots", [])
        if slots:
            return pid, sid, d, slots[0]
    raise AssertionError("no slots available")


def test_first_marketplace_booking_commission_10pct(fresh_client_token):
    headers, _ = fresh_client_token
    pid, sid, d, t = _pick_booking("kofi-cuts-yyc")
    body = {
        "practitioner_id": pid, "service_id": sid,
        "booking_date": d, "start_time": t,
        "client_source": "marketplace",
    }
    r = requests.post(f"{API}/bookings", json=body, headers=headers, timeout=30)
    assert r.status_code == 200, r.text
    b = r.json()
    assert b["status"] == "confirmed"
    assert b["deposit_paid"] is True
    assert b["commission_rate"] == 0.10, f"first marketplace booking should be 10%, got {b['commission_rate']}"
    assert b["is_first_marketplace_booking"] is True
    # second booking → 0%
    pid2, sid2, d2, t2 = _pick_booking("kofi-cuts-yyc")
    # pick a different slot/date to avoid conflict
    body2 = dict(body, booking_date=d2, start_time=t2)
    if d2 == d and t2 == t:
        # pick next slot
        from datetime import date, timedelta
        for i in range(2, 30):
            dd = (date.today() + timedelta(days=i)).isoformat()
            rs = requests.get(f"{API}/practitioners/{pid}/slots", params={"date": dd, "service_id": sid}, timeout=30)
            ss = rs.json().get("slots", [])
            if ss:
                body2["booking_date"] = dd
                body2["start_time"] = ss[0]
                break
    r2 = requests.post(f"{API}/bookings", json=body2, headers=headers, timeout=30)
    assert r2.status_code == 200, r2.text
    b2 = r2.json()
    assert b2["commission_rate"] == 0.0, "repeat booking should be 0%"
    assert b2["is_first_marketplace_booking"] is False


def test_direct_link_booking_is_zero_commission():
    # New client, direct_link source
    email = f"TEST_dl_{uuid.uuid4().hex[:6]}@curlnect.com"
    r = requests.post(f"{API}/auth/register",
                      json={"email": email, "password": "Pass123!", "name": "DL", "role": "client"}, timeout=30)
    assert r.status_code == 200
    headers = {"Authorization": f"Bearer {r.json()['token']}"}
    pid, sid, d, t = _pick_booking("blessing-braids-yyc")
    body = {
        "practitioner_id": pid, "service_id": sid,
        "booking_date": d, "start_time": t,
        "client_source": "direct_link",
    }
    rb = requests.post(f"{API}/bookings", json=body, headers=headers, timeout=30)
    assert rb.status_code == 200, rb.text
    b = rb.json()
    assert b["commission_rate"] == 0.0, "direct_link first booking should be 0%"


def test_bookings_list_client_scoped(client_auth):
    headers, user = client_auth
    r = requests.get(f"{API}/bookings", headers=headers, timeout=30)
    assert r.status_code == 200
    for b in r.json():
        assert b["client_id"] == user["id"]


def test_bookings_list_practitioner_scoped(prac_auth):
    headers, _ = prac_auth
    r = requests.get(f"{API}/bookings", headers=headers, timeout=30)
    assert r.status_code == 200


def test_cancel_booking_by_client(fresh_client_token):
    headers, _ = fresh_client_token
    # find one of their bookings
    r = requests.get(f"{API}/bookings", headers=headers, timeout=30)
    bookings = r.json()
    if not bookings:
        pytest.skip("no bookings to cancel")
    bid = bookings[0]["id"]
    r2 = requests.put(f"{API}/bookings/{bid}/status",
                      json={"status": "cancelled_by_client"}, headers=headers, timeout=30)
    assert r2.status_code == 200, r2.text


# ---------- Reviews ----------
def test_review_requires_completed(client_auth):
    headers, _ = client_auth
    # fake booking id should 404
    r = requests.post(f"{API}/reviews",
                      json={"booking_id": "fake", "rating": 5, "text": "x"},
                      headers=headers, timeout=30)
    assert r.status_code in (404, 400)


# ---------- Admin ----------
def test_admin_stats(admin_auth):
    headers, _ = admin_auth
    r = requests.get(f"{API}/admin/stats", headers=headers, timeout=30)
    assert r.status_code == 200, r.text
    s = r.json()
    for k in ["total_practitioners", "total_clients", "gmv", "commission_revenue", "practitioners_by_type", "recent_bookings"]:
        assert k in s


def test_admin_stats_forbidden_for_client(client_auth):
    headers, _ = client_auth
    r = requests.get(f"{API}/admin/stats", headers=headers, timeout=30)
    assert r.status_code == 403


# ---------- Practitioner self-mgmt ----------
def test_prac_services_crud(prac_auth):
    headers, _ = prac_auth
    # list categories first
    cats = requests.get(f"{API}/categories", timeout=30).json()
    cat_id = cats[0]["id"]
    # create
    payload = {"category_id": cat_id, "name": "TEST_temp_svc",
               "price_min": 50.0, "duration_minutes_min": 30}
    r = requests.post(f"{API}/me/services", json=payload, headers=headers, timeout=30)
    assert r.status_code == 200, r.text
    sid = r.json()["id"]
    # list
    rl = requests.get(f"{API}/me/services", headers=headers, timeout=30)
    assert rl.status_code == 200
    assert any(s["id"] == sid for s in rl.json())
    # delete
    rd = requests.delete(f"{API}/me/services/{sid}", headers=headers, timeout=30)
    assert rd.status_code == 200


def test_prac_availability_replace(prac_auth):
    headers, _ = prac_auth
    body = [
        {"day_of_week": 1, "start_time": "09:00", "end_time": "17:00", "is_available": True},
        {"day_of_week": 2, "start_time": "10:00", "end_time": "18:00", "is_available": True},
    ]
    r = requests.put(f"{API}/me/availability", json=body, headers=headers, timeout=30)
    assert r.status_code == 200
    assert r.json()["count"] == 2
