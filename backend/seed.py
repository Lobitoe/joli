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
    {"email": "blessing@tryjoli.com", "password": "Pass123!", "name": "Blessing Adeyemi", "role": "practitioner"},
    {"email": "kofi@tryjoli.com", "password": "Pass123!", "name": "Kofi Mensah", "role": "practitioner"},
    {"email": "linh@tryjoli.com", "password": "Pass123!", "name": "Linh Tran", "role": "practitioner"},
    {"email": "priya@tryjoli.com", "password": "Pass123!", "name": "Priya Sharma", "role": "practitioner"},
    {"email": "fatima@tryjoli.com", "password": "Pass123!", "name": "Fatima Khan", "role": "practitioner"},
    {"email": "amara@tryjoli.com", "password": "Pass123!", "name": "Amara Okonkwo", "role": "client"},
    {"email": "daniel@tryjoli.com", "password": "Pass123!", "name": "Daniel Brown", "role": "client"},
]


PRACTITIONER_PROFILES = {
    "blessing@tryjoli.com": {
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
    "kofi@tryjoli.com": {
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
    "linh@tryjoli.com": {
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
    "priya@tryjoli.com": {
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
    "fatima@tryjoli.com": {
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
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@tryjoli.com")
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
    client = await db.users.find_one({"email": "amara@tryjoli.com"})
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


async def seed_verifications_and_badges(db):
    """Seed verification status and badges for the demo practitioners."""
    # Map: email -> (verified_types, badges, is_insured)
    profile_setup = {
        "blessing@tryjoli.com": (["government_id"], ["top_rated", "community_endorsed"], False),
        "kofi@tryjoli.com": (["government_id", "trade_certificate"], ["certified_barber", "top_rated"], True),
        "linh@tryjoli.com": (["government_id", "insurance"], ["insured", "top_rated"], True),
        "priya@tryjoli.com": (["government_id"], ["top_rated", "community_endorsed"], False),
        "fatima@tryjoli.com": (["government_id"], ["community_endorsed"], False),
    }
    for email, (verifs, badges, insured) in profile_setup.items():
        user = await db.users.find_one({"email": email})
        if not user:
            continue
        prac = await db.practitioners.find_one({"user_id": user["id"]})
        if not prac:
            continue
        # Verifications
        for vtype in verifs:
            existing = await db.practitioner_verifications.find_one({"practitioner_id": prac["id"], "verification_type": vtype})
            if existing:
                continue
            await db.practitioner_verifications.insert_one({
                "id": str(uuid.uuid4()),
                "practitioner_id": prac["id"],
                "verification_type": vtype,
                "document_url": "https://example.com/seed-doc.pdf",
                "document_expiry": None,
                "status": "verified",
                "verified_by": "system_seed",
                "verified_at": utcnow_iso(),
                "rejection_reason": None,
                "created_at": utcnow_iso(),
                "updated_at": utcnow_iso(),
            })
        # Badges
        for btype in badges:
            existing = await db.practitioner_badges.find_one({"practitioner_id": prac["id"], "badge_type": btype})
            if existing:
                continue
            await db.practitioner_badges.insert_one({
                "id": str(uuid.uuid4()),
                "practitioner_id": prac["id"],
                "badge_type": btype,
                "is_active": True,
                "granted_at": utcnow_iso(),
                "expires_at": None,
            })
        # Roll-up status on practitioner doc
        await db.practitioners.update_one(
            {"id": prac["id"]},
            {"$set": {"verification_status": "verified", "is_insured": insured}}
        )


BLOG_POSTS = [
    {
        "slug": "best-braiders-calgary-2026",
        "title": "10 Best Braiders in Calgary (2026 Edition)",
        "category": "Local Discovery",
        "city": "Calgary",
        "hero_image": "https://images.unsplash.com/photo-1605497788044-5a32c7078486?crop=entropy&cs=srgb&fm=jpg&q=85&w=1600",
        "author": "Joli Editorial",
        "excerpt": "From knotless braids to feed-in cornrows, here are the Calgary braiders our community trusts in 2026 — with prices, styles, and how to book.",
        "embed_practitioner_emails": ["blessing@tryjoli.com"],
        "body": """# 10 Best Braiders in Calgary (2026 Edition)

If you've been doom-scrolling Instagram looking for a braider who actually knows your texture, takes their time, and doesn't ghost your DMs — this list is for you. We sourced the names from WhatsApp groups, church recommendations, and our own clients across the NE, NW, SE and SW.

## How we picked them

Every braider on this list:

- Has at least 3 years of dedicated braiding work
- Specializes in protective styles for textured hair (4a–4c, type 3, locs)
- Books transparently with structured availability — no "DM for price"
- Maintains a consistent quality bar on real client work, not stock photos

## What you'll pay in Calgary in 2026

- **Knotless braids (mid-back):** $220–$320
- **Knotless braids (waist / hip length):** $300–$420
- **Box braids (medium):** $200–$280
- **Cornrows (straight back):** $80–$120
- **Cornrows (feed-in design):** $150–$210
- **Passion / Senegalese twists:** $250–$360
- **Loc retwist:** $90–$160

> Tip: A 25% deposit is now standard for protective styles in Calgary — it locks your 5-to-7-hour slot and weeds out flaky bookings. If a braider doesn't ask for one, it's usually a sign their schedule is chaotic.

## The braiders

### 1. Blessing's Braids YYC — NE Calgary

Nigerian-Canadian braider with 4+ years specializing in knotless braids, box braids, and feed-in cornrows. Home studio in NE Calgary near Saddle Ridge. Soft-tension work that won't break your edges.

## Want to book one of them?

Joli is the easiest way to lock down an appointment — see real portfolios by style category, real prices, and put down a deposit in under 60 seconds.""",
    },
    {
        "slug": "mobile-barbers-calgary-edmonton",
        "title": "Mobile Barbers in Calgary & Edmonton: Where They Are and What They Charge",
        "category": "Local Discovery",
        "city": "Calgary",
        "hero_image": "https://images.unsplash.com/photo-1599351431202-1e0f0137899a?crop=entropy&cs=srgb&fm=jpg&q=85&w=1600",
        "author": "Joli Editorial",
        "excerpt": "Mobile barbers who actually understand Black, African and South Asian hair textures — bringing the chair to your door across Calgary and Edmonton.",
        "embed_practitioner_emails": ["kofi@tryjoli.com"],
        "body": """# Mobile Barbers in Calgary & Edmonton

Skin fades, designs, waves, beard sculpts — at your door. Here's who's actually doing the work in 2026.

## Why mobile?

The best barbers for textured hair in Calgary almost always started in shops, then went mobile once their book filled up. You get the same skill at your kitchen counter for the same price (sometimes less, because they're not paying chair rent).

## Typical mobile barber pricing

- **Skin fade (standard):** $45–$60
- **Skin fade + beard:** $65–$85
- **Hair design / line art:** +$15–$30 on top of cut
- **Waves treatment + cut:** $55–$70
- **Kids cut (under 12):** $25–$35

## Featured: Kofi Cuts Mobile

Kofi runs a tight 25 km radius across YYC — downtown, NE, NW, SE. Bookings come with a 24-hour cancellation policy because no-shows on mobile cost double (you waste the slot AND the drive). Book through his Joli link to lock in.""",
    },
    {
        "slug": "nail-techs-home-studios-edmonton",
        "title": "Nail Techs With Home Studios in Edmonton: The 2026 Map",
        "category": "Local Discovery",
        "city": "Edmonton",
        "hero_image": "https://images.unsplash.com/photo-1632345031435-8727f6897d53?crop=entropy&cs=srgb&fm=jpg&q=85&w=1600",
        "author": "Joli Editorial",
        "excerpt": "Forget walk-in salons. Edmonton's most talented nail techs work out of cozy home studios — by appointment only, and worth every minute of the wait.",
        "embed_practitioner_emails": ["linh@tryjoli.com"],
        "body": """# Nail Techs With Home Studios in Edmonton

The best nail art in YEG isn't in a strip-mall salon — it's in a Mill Woods spare bedroom with a ring light and a Bluetooth speaker.

## What home studios get right

- **Time** — one client at a time, no rushed cuticles
- **Personalization** — the tech remembers your shape, your allergies, your wedding date
- **Price** — usually $10–$20 less than a salon for the same gel set

## Pricing snapshot

- **Gel manicure:** $50–$70
- **Acrylic full set (short):** $70–$90
- **Acrylic full set (long):** $90–$130
- **Dip powder:** $65–$80
- **Full set with custom nail art:** $100–$140
- **3D / chrome / encapsulated art:** $120–$180

## Featured: Linh Nails Studio

Linh runs a biweekly book that closes 3 weeks out. Joli now shows her real availability — no more "are you open Saturday?" DM threads.""",
    },
    {
        "slug": "bridal-mehndi-calgary-2026",
        "title": "Bridal Mehndi Artists in Calgary: A 2026 Booking Guide",
        "category": "Local Discovery",
        "city": "Calgary",
        "hero_image": "https://images.unsplash.com/photo-1623217509141-6f735087b50c?crop=entropy&cs=srgb&fm=jpg&q=85&w=1600",
        "author": "Joli Editorial",
        "excerpt": "From Arabic to Indian traditional to Indo-Arabic fusion — Calgary's bridal mehndi artists, what they charge, and how far ahead to book.",
        "embed_practitioner_emails": ["priya@tryjoli.com"],
        "body": """# Bridal Mehndi Artists in Calgary

For a Hindu, Sikh, or Muslim wedding, bridal mehndi is a multi-hour event in itself. Here's how to book the right artist without stress.

## How far ahead to book

- **Bridal mehndi:** 4–6 months ahead for peak season (May–September)
- **Reception or sangeet mehndi:** 6–8 weeks ahead
- **Party mehndi:** 1–2 weeks usually fine

## What you'll pay

- **Bridal mehndi (hands + feet):** $350–$500
- **Party mehndi (one hand):** $60–$80
- **Party mehndi (both hands):** $100–$140
- **Multi-event bridal package (mehndi + ceremony + reception):** $1,200–$1,800

## Trials matter

A bridal trial ($150–$200) lets you preview your final design, test the henna paste on your skin, and lock in style direction. Most artists require one.

## Featured: Priya Bridal Studio

Priya specializes in Indo-Arabic fusion mehndi and bridal makeup. 6 years experience across Calgary's South Asian wedding circuit.""",
    },
    {
        "slug": "eyebrow-threading-edmonton-mill-woods",
        "title": "Eyebrow Threading in Mill Woods, Edmonton: Where to Go in 2026",
        "category": "Local Discovery",
        "city": "Edmonton",
        "hero_image": "https://images.unsplash.com/photo-1571875257727-256c39da42af?crop=entropy&cs=srgb&fm=jpg&q=85&w=1600",
        "author": "Joli Editorial",
        "excerpt": "The threading specialists Mill Woods residents actually recommend — fast, precise, and under $20 for brows.",
        "embed_practitioner_emails": ["fatima@tryjoli.com"],
        "body": """# Eyebrow Threading in Mill Woods, Edmonton

You don't need to drive across the city for a 10-minute brow shape. Mill Woods has at least a dozen home-studio threading specialists who'll get you in and out under 20 minutes.

## What threading costs in Mill Woods

- **Eyebrow threading:** $15–$18
- **Upper lip threading:** $8–$10
- **Full face threading:** $35–$45

## Featured: Fatima Threading & Brows

Fatima runs a tidy home studio in Mill Woods. Walk-ins are welcome with an appointment, and her sterilization standards are non-negotiable (a real concern with threading).""",
    },
    {
        "slug": "knotless-braids-styles-guide",
        "title": "Knotless Braids in 2026: Styles, Lengths, Prices and Care",
        "category": "Style Guide",
        "city": None,
        "hero_image": "https://images.unsplash.com/photo-1572955304332-bf714bd49add?crop=entropy&cs=srgb&fm=jpg&q=85&w=1600",
        "author": "Joli Editorial",
        "excerpt": "Everything you need to know before booking your next knotless install — length, parting, tension, take-down, and how to keep them looking fresh for 6 weeks.",
        "embed_practitioner_emails": ["blessing@tryjoli.com"],
        "body": """# Knotless Braids: The 2026 Guide

Knotless braids are the dominant protective style of the late 2020s for a reason — less tension on your scalp than traditional box braids, more natural movement, and a finish that doesn't scream "fresh install" for the first 48 hours.

## Lengths and what they cost

- **Shoulder length:** $220–$280 · 4–5 hours
- **Mid-back:** $260–$340 · 5–6 hours
- **Waist length:** $300–$380 · 6–7 hours
- **Hip / butt length:** $360–$440 · 7–9 hours

## Care between appointments

1. Wrap with a satin scarf or silk bonnet every night, no exceptions
2. Light edge oil every 2-3 days — don't drown your scalp
3. Refresh wash every 2-3 weeks with diluted shampoo + a precision applicator bottle
4. Take down at 6-8 weeks, never longer — your edges will thank you

## Booking on Joli

When you book a knotless install on Joli, the system blocks out the full duration (including a 30-minute break) so your braider's day is protected. Deposit is 25% — the rest is settled at the appointment in card, e-transfer or cash.""",
    },
    {
        "slug": "fade-styles-explained",
        "title": "Fade Styles Explained: Skin, Taper, Drop and Burst",
        "category": "Style Guide",
        "city": None,
        "hero_image": "https://images.unsplash.com/photo-1503951914875-452162b0f3f1?crop=entropy&cs=srgb&fm=jpg&q=85&w=1600",
        "author": "Joli Editorial",
        "excerpt": "If you don't know the difference between a low skin and a mid drop fade, your barber will pick one for you. This guide helps you ask for what you want.",
        "embed_practitioner_emails": ["kofi@tryjoli.com"],
        "body": """# Fade Styles Explained

The fade you ask for and the fade you get are often two different cuts. Here's the actual vocabulary.

## Skin fade

Hair tapers to literal skin at the bottom (0 guard, then a razor finish). Bold, clean, requires a touch-up every 7-10 days to stay sharp.

## Taper fade

Hair tapers but doesn't go to skin — usually finishes at a 1 or 0.5 guard. Softer look, lasts 2-3 weeks before it grows out.

## Drop fade

The fade arcs down toward the back of the head rather than running level. Pairs well with longer top styles.

## Burst fade

The fade radiates outward from behind the ear in a semicircle. Mohawk-friendly.

## Pair with

- **Line-up / edge-up:** sharp the hairline and beard line ($15-$25 add-on)
- **Hair design:** custom shapes shaved into the side ($20-$50 add-on)
- **Waves treatment:** for textured hair, the brush + durag set after the cut keeps your pattern crisp

## Book a barber on Joli

Filter by "barber" + your city to see real portfolio examples of every fade style, with each barber's price.""",
    },
    {
        "slug": "joli-direct-booking-link-guide",
        "title": "How to Use Your Joli Direct Link to Book More Clients (and Pay Zero Commission)",
        "category": "Practitioner Education",
        "city": None,
        "hero_image": "https://images.unsplash.com/photo-1521322800607-8c38375eef04?crop=entropy&cs=srgb&fm=jpg&q=85&w=1600",
        "author": "Joli Editorial",
        "excerpt": "Your Joli direct link is the most valuable piece of digital real estate you own as a practitioner. Here's how to actually use it.",
        "embed_practitioner_emails": [],
        "body": """# Your Joli Direct Link: A Practitioner's Guide

Every practitioner on Joli gets a unique URL — `tryjoli.com/p/your-name`. Anyone who books through it pays you full price, forever. Joli takes 0% commission on direct-link bookings, ever.

## Where to put your link

1. **Instagram bio** — the single highest-converting placement. Replace your Linktree or carrd. Pin a story highlight called "Book"
2. **WhatsApp status & business profile** — under "Website"
3. **TikTok bio** — same idea, same conversion
4. **Email signature** — for the bridal MUAs and barbers who do consultations
5. **Business cards & door magnet** (for home studios) — QR code straight to your link

## Why it works

When someone DMs you "how do I book?", you don't write back a long explanation. You send one link. They land on a page with your real portfolio, real prices, and a deposit-locked booking flow. The whole conversation collapses into 90 seconds.

## Don't mix your sources

If you direct existing clients to your Joli link, those bookings stay 0% commission. If you only push the marketplace browse page, Joli's 10% only kicks in on the *first* booking from any new client we sourced for you — every booking after that is 0% too. Either way, your repeat business is yours.""",
    },
]


async def seed_blog_posts(db):
    if await db.blog_posts.count_documents({}) > 0:
        return
    for i, p in enumerate(BLOG_POSTS):
        embed_ids = []
        for email in p.get("embed_practitioner_emails", []):
            u = await db.users.find_one({"email": email})
            if u:
                prac = await db.practitioners.find_one({"user_id": u["id"]})
                if prac:
                    embed_ids.append(prac["id"])
        published_at = (datetime.now(timezone.utc) - timedelta(days=(len(BLOG_POSTS) - i) * 3)).isoformat()
        await db.blog_posts.insert_one({
            "id": str(uuid.uuid4()),
            "slug": p["slug"],
            "title": p["title"],
            "excerpt": p["excerpt"],
            "body_markdown": p["body"],
            "category": p["category"],
            "city": p.get("city"),
            "hero_image": p["hero_image"],
            "author": p["author"],
            "embedded_practitioner_ids": embed_ids,
            "is_published": True,
            "published_at": published_at,
            "created_at": utcnow_iso(),
        })


async def run_all_seeds(db):
    await seed_admin(db)
    await seed_categories(db)
    await seed_users_and_practitioners(db)
    await seed_sample_reviews(db)
    await seed_verifications_and_badges(db)
    await seed_blog_posts(db)
