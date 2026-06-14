"""Seed data: service categories, sample practitioners, services, portfolio, availability."""
import uuid
from datetime import datetime, timezone, timedelta
from auth import hash_password


# Service category taxonomy (PRD Section 6)
CATEGORIES = [
    # African / Caribbean Hair - Braiding
    {"name": "Knotless Braids", "parent_category": "Braiding", "cultural_context": "african_hair", "icon": "Braid", "display_order": 1},
    {"name": "Box Braids", "parent_category": "Braiding", "cultural_context": "african_hair", "icon": "Braid", "display_order": 2},
    {"name": "Cornrows", "parent_category": "Braiding", "cultural_context": "african_hair", "icon": "Braid", "display_order": 3},
    {"name": "Ghana Weaving", "parent_category": "Braiding", "cultural_context": "african_hair", "icon": "Braid", "display_order": 4},
    {"name": "Crochet Braids", "parent_category": "Braiding", "cultural_context": "african_hair", "icon": "Braid", "display_order": 5},
    {"name": "Passion Twists", "parent_category": "Braiding", "cultural_context": "african_hair", "icon": "Braid", "display_order": 6},
    {"name": "Senegalese Twists", "parent_category": "Braiding", "cultural_context": "african_hair", "icon": "Braid", "display_order": 7},
    {"name": "Faux Locs", "parent_category": "Braiding", "cultural_context": "african_hair", "icon": "Braid", "display_order": 8},
    # Locs
    {"name": "Loc Installation", "parent_category": "Locs", "cultural_context": "african_hair", "icon": "Sprout", "display_order": 10},
    {"name": "Loc Retwist / Maintenance", "parent_category": "Locs", "cultural_context": "african_hair", "icon": "Sprout", "display_order": 11},
    {"name": "Loc Styling", "parent_category": "Locs", "cultural_context": "african_hair", "icon": "Sprout", "display_order": 12},
    # Natural Hair
    {"name": "Silk Press", "parent_category": "Natural Hair", "cultural_context": "african_hair", "icon": "Wind", "display_order": 20},
    {"name": "Wash & Style", "parent_category": "Natural Hair", "cultural_context": "african_hair", "icon": "Wind", "display_order": 21},
    {"name": "Twist Out / Braid Out", "parent_category": "Natural Hair", "cultural_context": "african_hair", "icon": "Wind", "display_order": 22},
    # Weaves & Wigs
    {"name": "Sew-In Weave", "parent_category": "Weaves & Wigs", "cultural_context": "african_hair", "icon": "Layers", "display_order": 30},
    {"name": "Wig Installation", "parent_category": "Weaves & Wigs", "cultural_context": "african_hair", "icon": "Layers", "display_order": 31},
    # Barber
    {"name": "Skin Fade", "parent_category": "Haircuts", "cultural_context": "general", "icon": "Scissors", "display_order": 40},
    {"name": "Taper Fade", "parent_category": "Haircuts", "cultural_context": "general", "icon": "Scissors", "display_order": 41},
    {"name": "Afro Shape / Pick & Cut", "parent_category": "Haircuts", "cultural_context": "african_hair", "icon": "Scissors", "display_order": 42},
    {"name": "Waves (360/540/720)", "parent_category": "Haircuts", "cultural_context": "african_hair", "icon": "Scissors", "display_order": 43},
    {"name": "Line-Up / Edge-Up", "parent_category": "Design & Detail", "cultural_context": "general", "icon": "Scissors", "display_order": 44},
    {"name": "Hair Design / Line Art", "parent_category": "Design & Detail", "cultural_context": "general", "icon": "Scissors", "display_order": 45},
    {"name": "Beard Sculpt / Beard Fade", "parent_category": "Design & Detail", "cultural_context": "general", "icon": "Scissors", "display_order": 46},
    {"name": "Kids Haircut", "parent_category": "Haircuts", "cultural_context": "general", "icon": "Scissors", "display_order": 47},
    # Nails
    {"name": "Gel Manicure", "parent_category": "Nail Treatments", "cultural_context": "general", "icon": "Hand", "display_order": 50},
    {"name": "Acrylic Full Set", "parent_category": "Nail Treatments", "cultural_context": "general", "icon": "Hand", "display_order": 51},
    {"name": "Dip Powder", "parent_category": "Nail Treatments", "cultural_context": "general", "icon": "Hand", "display_order": 52},
    {"name": "Gel Pedicure", "parent_category": "Nail Treatments", "cultural_context": "general", "icon": "Hand", "display_order": 53},
    {"name": "Full Set Nail Art", "parent_category": "Nail Art", "cultural_context": "general", "icon": "Sparkles", "display_order": 54},
    {"name": "3D Nail Art / Chrome", "parent_category": "Nail Art", "cultural_context": "general", "icon": "Sparkles", "display_order": 55},
    {"name": "Cultural / Festival Nail Art", "parent_category": "Nail Art", "cultural_context": "south_asian", "icon": "Sparkles", "display_order": 56},
    # South Asian Beauty - Mehndi
    {"name": "Bridal Mehndi", "parent_category": "Mehndi / Henna", "cultural_context": "south_asian", "icon": "Flower", "display_order": 60},
    {"name": "Party / Event Mehndi", "parent_category": "Mehndi / Henna", "cultural_context": "south_asian", "icon": "Flower", "display_order": 61},
    {"name": "Arabic Design Mehndi", "parent_category": "Mehndi / Henna", "cultural_context": "south_asian", "icon": "Flower", "display_order": 62},
    {"name": "Indian Traditional Mehndi", "parent_category": "Mehndi / Henna", "cultural_context": "south_asian", "icon": "Flower", "display_order": 63},
    # Threading
    {"name": "Eyebrow Threading", "parent_category": "Threading & Hair Removal", "cultural_context": "south_asian", "icon": "Eye", "display_order": 70},
    {"name": "Full Face Threading", "parent_category": "Threading & Hair Removal", "cultural_context": "south_asian", "icon": "Eye", "display_order": 71},
    {"name": "Upper Lip Threading", "parent_category": "Threading & Hair Removal", "cultural_context": "south_asian", "icon": "Eye", "display_order": 72},
    # Bridal South Asian
    {"name": "Bridal Makeup (Ceremony)", "parent_category": "Bridal Makeup & Hair", "cultural_context": "south_asian", "icon": "Crown", "display_order": 80},
    {"name": "Reception Makeup", "parent_category": "Bridal Makeup & Hair", "cultural_context": "south_asian", "icon": "Crown", "display_order": 81},
    {"name": "Bridal Package (Multi-Event)", "parent_category": "Bridal Makeup & Hair", "cultural_context": "south_asian", "icon": "Crown", "display_order": 82},
    {"name": "Bridal Trial", "parent_category": "Bridal Makeup & Hair", "cultural_context": "south_asian", "icon": "Crown", "display_order": 83},
    # General
    {"name": "Event / Party Makeup", "parent_category": "General Makeup", "cultural_context": "general", "icon": "Palette", "display_order": 90},
    {"name": "Lash Extensions", "parent_category": "Lashes", "cultural_context": "general", "icon": "Eye", "display_order": 91},
]


SEED_USERS = [
    {"email": "blessing@curlnect.com", "password": "Pass123!", "name": "Blessing Adeyemi", "role": "practitioner"},
    {"email": "kofi@curlnect.com", "password": "Pass123!", "name": "Kofi Mensah", "role": "practitioner"},
    {"email": "linh@curlnect.com", "password": "Pass123!", "name": "Linh Tran", "role": "practitioner"},
    {"email": "priya@curlnect.com", "password": "Pass123!", "name": "Priya Sharma", "role": "practitioner"},
    {"email": "fatima@curlnect.com", "password": "Pass123!", "name": "Fatima Khan", "role": "practitioner"},
    {"email": "amara@curlnect.com", "password": "Pass123!", "name": "Amara Okonkwo", "role": "client"},
    {"email": "daniel@curlnect.com", "password": "Pass123!", "name": "Daniel Brown", "role": "client"},
]


PRACTITIONER_PROFILES = {
    "blessing@curlnect.com": {
        "display_name": "Blessing's Braids YYC",
        "bio": "Nigerian-Canadian braider with 4+ years specializing in knotless braids, box braids, and feed-in cornrows. Home studio in NE Calgary. I take my time — your scalp will thank you.",
        "practitioner_type": "braider",
        "location_type": "home_studio",
        "service_mode": "clients_come_to_me",
        "city": "Calgary",
        "province": "AB",
        "service_neighbourhoods": ["NE Calgary", "Saddle Ridge", "Falconridge", "Martindale"],
        "service_radius_km": None,
        "accepted_payments": ["card", "etransfer", "cash"],
        "cancellation_policy": "48 hours notice required. Deposit forfeited for late cancellations.",
        "cancellation_notice_hours": 48,
        "direct_booking_slug": "blessing-braids-yyc",
        "instagram_handle": "@blessingbraids.yyc",
        "whatsapp_number": "+1-403-555-0101",
        "languages": ["en", "yo"],
        "profile_photo_url": "https://images.unsplash.com/photo-1572955304332-bf714bd49add?crop=entropy&cs=srgb&fm=jpg&q=85&w=400",
        "categories": ["Knotless Braids", "Box Braids", "Cornrows", "Passion Twists", "Senegalese Twists"],
    },
    "kofi@curlnect.com": {
        "display_name": "Kofi Cuts Mobile",
        "bio": "Mobile barber bringing the shop to your door. Specialist in skin fades, designs, waves and beard sculpting. 3 years on the road across YYC.",
        "practitioner_type": "barber",
        "location_type": "mobile",
        "service_mode": "i_travel_to_clients",
        "city": "Calgary",
        "province": "AB",
        "service_neighbourhoods": ["Downtown", "NW Calgary", "NE Calgary", "SE Calgary"],
        "service_radius_km": 25,
        "accepted_payments": ["card", "etransfer", "cash"],
        "cancellation_policy": "24 hours notice required for mobile bookings. Deposit forfeited otherwise.",
        "cancellation_notice_hours": 24,
        "direct_booking_slug": "kofi-cuts-yyc",
        "instagram_handle": "@kofi.cuts.yyc",
        "whatsapp_number": "+1-403-555-0102",
        "languages": ["en", "tw"],
        "profile_photo_url": "https://images.unsplash.com/photo-1567894340315-735d7c361db0?crop=entropy&cs=srgb&fm=jpg&q=85&w=400",
        "categories": ["Skin Fade", "Taper Fade", "Waves (360/540/720)", "Hair Design / Line Art", "Beard Sculpt / Beard Fade", "Line-Up / Edge-Up", "Kids Haircut"],
    },
    "linh@curlnect.com": {
        "display_name": "Linh Nails Studio",
        "bio": "Nail artist working from a cozy home studio in Edmonton. Gel, acrylic, dip, and intricate hand-painted designs. Biweekly slots fill up fast — book ahead!",
        "practitioner_type": "nail_tech",
        "location_type": "home_studio",
        "service_mode": "clients_come_to_me",
        "city": "Edmonton",
        "province": "AB",
        "service_neighbourhoods": ["Mill Woods", "South Edmonton"],
        "accepted_payments": ["card", "etransfer", "cash"],
        "cancellation_policy": "48 hours notice. Repeated no-shows result in deposit forfeiture.",
        "cancellation_notice_hours": 48,
        "direct_booking_slug": "linh-nails-yeg",
        "instagram_handle": "@linh.nails.yeg",
        "whatsapp_number": "+1-780-555-0103",
        "languages": ["en", "vi"],
        "profile_photo_url": "https://images.unsplash.com/photo-1688583417770-ff6cc18071dc?crop=entropy&cs=srgb&fm=jpg&q=85&w=400",
        "categories": ["Gel Manicure", "Acrylic Full Set", "Dip Powder", "Full Set Nail Art", "3D Nail Art / Chrome"],
    },
    "priya@curlnect.com": {
        "display_name": "Priya Bridal Studio",
        "bio": "Bridal makeup artist & mehndi specialist for South Asian weddings. 6 years creating timeless looks for Hindu, Sikh, and Muslim brides across Alberta.",
        "practitioner_type": "mua",
        "location_type": "mixed",
        "service_mode": "both",
        "city": "Calgary",
        "province": "AB",
        "service_neighbourhoods": ["NE Calgary", "Saddle Ridge", "Cityscape"],
        "service_radius_km": 40,
        "accepted_payments": ["card", "etransfer", "cash"],
        "cancellation_policy": "Bridal: 14 days notice. Deposits non-refundable on bridal packages.",
        "cancellation_notice_hours": 336,
        "direct_booking_slug": "priya-bridal-yyc",
        "instagram_handle": "@priya.bridal.yyc",
        "whatsapp_number": "+1-403-555-0104",
        "languages": ["en", "hi", "pa"],
        "profile_photo_url": "https://images.unsplash.com/photo-1623217509141-6f735087b50c?crop=entropy&cs=srgb&fm=jpg&q=85&w=400",
        "categories": ["Bridal Mehndi", "Bridal Makeup (Ceremony)", "Reception Makeup", "Bridal Package (Multi-Event)", "Bridal Trial", "Party / Event Mehndi"],
    },
    "fatima@curlnect.com": {
        "display_name": "Fatima Threading & Brows",
        "bio": "Threading specialist — eyebrows, full face, upper lip. Quick, precise, hygienic. Home studio in Mill Woods, walk-ins welcome with appointment.",
        "practitioner_type": "threading_specialist",
        "location_type": "home_studio",
        "service_mode": "clients_come_to_me",
        "city": "Edmonton",
        "province": "AB",
        "service_neighbourhoods": ["Mill Woods", "Ellerslie"],
        "accepted_payments": ["etransfer", "cash"],
        "cancellation_policy": "24 hours notice required.",
        "cancellation_notice_hours": 24,
        "direct_booking_slug": "fatima-threading-yeg",
        "instagram_handle": "@fatima.brows.yeg",
        "whatsapp_number": "+1-780-555-0105",
        "languages": ["en", "ur", "pa"],
        "profile_photo_url": "https://images.unsplash.com/photo-1593351799227-75df2026356b?crop=entropy&cs=srgb&fm=jpg&q=85&w=400",
        "categories": ["Eyebrow Threading", "Full Face Threading", "Upper Lip Threading"],
    },
}


SERVICE_TEMPLATES = {
    "Knotless Braids": [("Knotless Braids — Shoulder Length", 220, 240, 240, 300), ("Knotless Braids — Waist Length", 300, 320, 300, 360), ("Knotless Braids — Hip Length", 350, 380, 360, 420)],
    "Box Braids": [("Box Braids — Medium, Mid-back", 250, 280, 300, 360), ("Box Braids — Jumbo, Shoulder", 180, 200, 180, 240)],
    "Cornrows": [("Cornrows — Straight Back", 80, 100, 90, 120), ("Cornrows — Feed-in Design", 150, 180, 150, 210)],
    "Passion Twists": [("Passion Twists — Mid-back", 240, 280, 300, 360)],
    "Senegalese Twists": [("Senegalese Twists — Mid-back", 250, 280, 300, 360)],
    "Skin Fade": [("Skin Fade — Standard", 45, 55, 45, 60), ("Skin Fade + Beard", 65, 75, 60, 75)],
    "Taper Fade": [("Taper Fade", 40, 50, 45, 60)],
    "Waves (360/540/720)": [("Waves Treatment + Cut", 55, 65, 60, 75)],
    "Hair Design / Line Art": [("Custom Hair Design", 25, 50, 20, 45)],
    "Beard Sculpt / Beard Fade": [("Beard Sculpt", 25, 35, 30, 45)],
    "Line-Up / Edge-Up": [("Line-Up Only", 20, 25, 15, 25)],
    "Afro Shape / Pick & Cut": [("Afro Shape", 40, 50, 45, 60)],
    "Kids Haircut": [("Kids Haircut (under 12)", 25, 30, 30, 45)],
    "Gel Manicure": [("Gel Manicure", 50, 60, 60, 75)],
    "Acrylic Full Set": [("Acrylic Full Set — Short", 70, 80, 90, 120), ("Acrylic Full Set — Long", 90, 110, 120, 150)],
    "Dip Powder": [("Dip Powder Manicure", 65, 75, 75, 90)],
    "Full Set Nail Art": [("Full Set + Custom Nail Art", 100, 130, 120, 150)],
    "3D Nail Art / Chrome": [("3D / Chrome / Encapsulated Art", 120, 150, 120, 180)],
    "Bridal Mehndi": [("Bridal Mehndi — Hands + Feet", 350, 500, 240, 360)],
    "Party / Event Mehndi": [("Party Mehndi — One Hand", 60, 80, 30, 45), ("Party Mehndi — Both Hands", 100, 140, 60, 90)],
    "Bridal Makeup (Ceremony)": [("Bridal Makeup — Ceremony", 350, 450, 120, 180)],
    "Reception Makeup": [("Reception Makeup", 250, 350, 90, 150)],
    "Bridal Package (Multi-Event)": [("Bridal Package — Mehndi+Ceremony+Reception", 1200, 1800, 480, 720)],
    "Bridal Trial": [("Bridal Trial Session", 150, 200, 90, 120)],
    "Eyebrow Threading": [("Eyebrow Threading", 15, 18, 15, 20)],
    "Full Face Threading": [("Full Face Threading", 35, 45, 30, 45)],
    "Upper Lip Threading": [("Upper Lip Threading", 8, 10, 5, 10)],
}


# Curated Unsplash portfolio images per category type
PORTFOLIO_IMAGES = {
    "braider": [
        "https://images.unsplash.com/photo-1572955304332-bf714bd49add?crop=entropy&cs=srgb&fm=jpg&q=85&w=800",
        "https://images.unsplash.com/photo-1605497788044-5a32c7078486?crop=entropy&cs=srgb&fm=jpg&q=85&w=800",
        "https://images.unsplash.com/photo-1580618864180-f6d7d39b8ff6?crop=entropy&cs=srgb&fm=jpg&q=85&w=800",
        "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?crop=entropy&cs=srgb&fm=jpg&q=85&w=800",
        "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?crop=entropy&cs=srgb&fm=jpg&q=85&w=800",
        "https://images.unsplash.com/photo-1601049541289-9b1b7bbbfe19?crop=entropy&cs=srgb&fm=jpg&q=85&w=800",
    ],
    "barber": [
        "https://images.unsplash.com/photo-1567894340315-735d7c361db0?crop=entropy&cs=srgb&fm=jpg&q=85&w=800",
        "https://images.unsplash.com/photo-1503951914875-452162b0f3f1?crop=entropy&cs=srgb&fm=jpg&q=85&w=800",
        "https://images.unsplash.com/photo-1599351431202-1e0f0137899a?crop=entropy&cs=srgb&fm=jpg&q=85&w=800",
        "https://images.unsplash.com/photo-1585747860715-2ba37e788b70?crop=entropy&cs=srgb&fm=jpg&q=85&w=800",
        "https://images.unsplash.com/photo-1622286342621-4bd786c2447c?crop=entropy&cs=srgb&fm=jpg&q=85&w=800",
        "https://images.unsplash.com/photo-1521322800607-8c38375eef04?crop=entropy&cs=srgb&fm=jpg&q=85&w=800",
    ],
    "nail_tech": [
        "https://images.unsplash.com/photo-1688583417770-ff6cc18071dc?crop=entropy&cs=srgb&fm=jpg&q=85&w=800",
        "https://images.unsplash.com/photo-1632345031435-8727f6897d53?crop=entropy&cs=srgb&fm=jpg&q=85&w=800",
        "https://images.unsplash.com/photo-1607779097040-26e80aa78e66?crop=entropy&cs=srgb&fm=jpg&q=85&w=800",
        "https://images.unsplash.com/photo-1604654894610-df63bc536371?crop=entropy&cs=srgb&fm=jpg&q=85&w=800",
        "https://images.unsplash.com/photo-1604902396830-aca29e19b067?crop=entropy&cs=srgb&fm=jpg&q=85&w=800",
        "https://images.unsplash.com/photo-1610992015732-2449b76344bc?crop=entropy&cs=srgb&fm=jpg&q=85&w=800",
    ],
    "mua": [
        "https://images.unsplash.com/photo-1623217509141-6f735087b50c?crop=entropy&cs=srgb&fm=jpg&q=85&w=800",
        "https://images.unsplash.com/photo-1610207844405-78d535f59a48?crop=entropy&cs=srgb&fm=jpg&q=85&w=800",
        "https://images.unsplash.com/photo-1606216794074-735e91aa2c92?crop=entropy&cs=srgb&fm=jpg&q=85&w=800",
        "https://images.unsplash.com/photo-1593696140826-c58b021acf8b?crop=entropy&cs=srgb&fm=jpg&q=85&w=800",
        "https://images.unsplash.com/photo-1591129841117-3adfd313e34f?crop=entropy&cs=srgb&fm=jpg&q=85&w=800",
        "https://images.unsplash.com/photo-1594744803329-e58b31de8bf5?crop=entropy&cs=srgb&fm=jpg&q=85&w=800",
    ],
    "threading_specialist": [
        "https://images.unsplash.com/photo-1487412947147-5cebf100ffc2?crop=entropy&cs=srgb&fm=jpg&q=85&w=800",
        "https://images.unsplash.com/photo-1571875257727-256c39da42af?crop=entropy&cs=srgb&fm=jpg&q=85&w=800",
        "https://images.unsplash.com/photo-1583241800698-9c2e2bd0e0eb?crop=entropy&cs=srgb&fm=jpg&q=85&w=800",
        "https://images.unsplash.com/photo-1616394584738-fc6e612e71b9?crop=entropy&cs=srgb&fm=jpg&q=85&w=800",
    ],
}


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


async def seed_categories(db):
    if await db.service_categories.count_documents({}) > 0:
        return
    docs = []
    for c in CATEGORIES:
        docs.append({"id": str(uuid.uuid4()), "is_active": True, **c})
    await db.service_categories.insert_many(docs)


async def seed_users_and_practitioners(db):
    # Users
    for u in SEED_USERS:
        existing = await db.users.find_one({"email": u["email"]})
        if existing:
            continue
        user_doc = {
            "id": str(uuid.uuid4()),
            "email": u["email"],
            "password_hash": hash_password(u["password"]),
            "name": u["name"],
            "role": u["role"],
            "created_at": utcnow_iso(),
        }
        await db.users.insert_one(user_doc)

    # Practitioner profiles
    for email, prof in PRACTITIONER_PROFILES.items():
        user = await db.users.find_one({"email": email})
        if not user:
            continue
        existing = await db.practitioners.find_one({"user_id": user["id"]})
        if existing:
            continue
        prac_id = str(uuid.uuid4())
        doc = {
            "id": prac_id,
            "user_id": user["id"],
            "display_name": prof["display_name"],
            "bio": prof["bio"],
            "profile_photo_url": prof.get("profile_photo_url"),
            "practitioner_type": prof["practitioner_type"],
            "location_type": prof["location_type"],
            "service_mode": prof["service_mode"],
            "address": None,
            "city": prof["city"],
            "province": prof["province"],
            "service_neighbourhoods": prof.get("service_neighbourhoods", []),
            "service_radius_km": prof.get("service_radius_km"),
            "accepted_payments": prof["accepted_payments"],
            "cancellation_policy": prof["cancellation_policy"],
            "cancellation_notice_hours": prof["cancellation_notice_hours"],
            "direct_booking_slug": prof["direct_booking_slug"],
            "is_premium": False,
            "is_featured": True,
            "instagram_handle": prof.get("instagram_handle"),
            "whatsapp_number": prof.get("whatsapp_number"),
            "languages": prof.get("languages", ["en"]),
            "avg_rating": 4.8,
            "total_reviews": 0,
            "created_at": utcnow_iso(),
            "updated_at": utcnow_iso(),
        }
        await db.practitioners.insert_one(doc)

        # Build service list
        cat_docs = await db.service_categories.find({"name": {"$in": prof["categories"]}}).to_list(100)
        cat_by_name = {c["name"]: c for c in cat_docs}
        ptype = prof["practitioner_type"]
        portfolio_pool = PORTFOLIO_IMAGES.get(ptype, [])
        portfolio_idx = 0

        for cat_name in prof["categories"]:
            cat = cat_by_name.get(cat_name)
            if not cat:
                continue
            tpl = SERVICE_TEMPLATES.get(cat_name, [(cat_name, 50, 80, 60, 90)])
            for (svc_name, pmin, pmax, dmin, dmax) in tpl:
                ref_img = portfolio_pool[portfolio_idx % len(portfolio_pool)] if portfolio_pool else None
                await db.services.insert_one({
                    "id": str(uuid.uuid4()),
                    "practitioner_id": prac_id,
                    "category_id": cat["id"],
                    "category_name": cat_name,
                    "name": svc_name,
                    "description": None,
                    "price_min": pmin,
                    "price_max": pmax,
                    "duration_minutes_min": dmin,
                    "duration_minutes_max": dmax,
                    "reference_photo_url": ref_img,
                    "includes_break": dmin >= 240,
                    "break_duration_minutes": 30 if dmin >= 240 else None,
                    "is_active": True,
                    "display_order": 0,
                    "created_at": utcnow_iso(),
                })
            # Portfolio items for this category
            for i in range(2):
                if not portfolio_pool:
                    break
                img = portfolio_pool[portfolio_idx % len(portfolio_pool)]
                portfolio_idx += 1
                await db.portfolio_items.insert_one({
                    "id": str(uuid.uuid4()),
                    "practitioner_id": prac_id,
                    "category_id": cat["id"],
                    "category_name": cat_name,
                    "image_url": img,
                    "caption": f"{cat_name} — recent work",
                    "tags": [cat_name.lower().replace(" ", "-")],
                    "is_featured": i == 0,
                    "imported_from_instagram": False,
                    "created_at": utcnow_iso(),
                    "display_order": i,
                })

        # Availability — Mon-Sat 9am-7pm
        for day in range(0, 6):
            await db.availability.insert_one({
                "id": str(uuid.uuid4()),
                "practitioner_id": prac_id,
                "day_of_week": day,
                "start_time": "09:00",
                "end_time": "19:00",
                "is_available": True,
            })


async def seed_admin(db):
    import os
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@curlnect.com")
    admin_password = os.environ.get("ADMIN_PASSWORD", "AdminPass123!")
    existing = await db.users.find_one({"email": admin_email})
    if existing is None:
        await db.users.insert_one({
            "id": str(uuid.uuid4()),
            "email": admin_email,
            "password_hash": hash_password(admin_password),
            "name": "Admin",
            "role": "admin",
            "created_at": utcnow_iso(),
        })
    else:
        from auth import verify_password
        if not verify_password(admin_password, existing["password_hash"]):
            await db.users.update_one(
                {"email": admin_email},
                {"$set": {"password_hash": hash_password(admin_password)}},
            )


async def seed_sample_reviews(db):
    if await db.reviews.count_documents({}) > 0:
        return
    practitioners = await db.practitioners.find({}).to_list(20)
    client = await db.users.find_one({"email": "amara@curlnect.com"})
    if not client:
        return
    sample_texts = [
        ("Absolutely the best. Took her time, scalp didn't hurt at all, braids look perfect. Will definitely rebook.", 5),
        ("Loved the experience! Communication was on point and the result speaks for itself.", 5),
        ("Great work, very welcoming home studio. Highly recommended.", 5),
        ("Professional, talented and so kind. My friends keep asking who did my hair.", 4),
    ]
    for prac in practitioners:
        for i, (txt, rating) in enumerate(sample_texts[:3]):
            await db.reviews.insert_one({
                "id": str(uuid.uuid4()),
                "booking_id": None,
                "client_id": client["id"],
                "client_name": "Amara O.",
                "practitioner_id": prac["id"],
                "rating": rating,
                "text": txt,
                "client_photo_urls": [],
                "is_visible": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=7 * (i + 1))).isoformat(),
            })
        # Update aggregate
        revs = await db.reviews.find({"practitioner_id": prac["id"]}).to_list(100)
        if revs:
            avg = sum(r["rating"] for r in revs) / len(revs)
            await db.practitioners.update_one(
                {"id": prac["id"]},
                {"$set": {"avg_rating": round(avg, 2), "total_reviews": len(revs)}},
            )


async def run_all_seeds(db):
    await seed_admin(db)
    await seed_categories(db)
    await seed_users_and_practitioners(db)
    await seed_sample_reviews(db)
