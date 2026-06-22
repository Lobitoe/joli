"""All Pydantic schemas for the Joli API — lifted from the original server.py."""
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, EmailStr, ConfigDict


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    name: str = Field(min_length=1)
    role: Literal["client", "practitioner"]


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    email: str
    name: str
    role: str


class PractitionerUpsertIn(BaseModel):
    display_name: str
    bio: Optional[str] = ""
    profile_photo_url: Optional[str] = None
    practitioner_type: str
    location_type: str
    service_mode: str
    address: Optional[str] = None
    city: str
    province: str
    service_neighbourhoods: List[str] = []
    service_radius_km: Optional[int] = None
    accepted_payments: List[str] = []
    cancellation_policy: Optional[str] = ""
    cancellation_notice_hours: int = 48
    instagram_handle: Optional[str] = None
    whatsapp_number: Optional[str] = None
    languages: List[str] = ["en"]


class ServiceIn(BaseModel):
    category_id: str
    name: str
    description: Optional[str] = None
    price_min: float
    price_max: Optional[float] = None
    duration_minutes_min: int
    duration_minutes_max: Optional[int] = None
    reference_photo_url: Optional[str] = None
    includes_break: bool = False
    break_duration_minutes: Optional[int] = None


class PortfolioItemIn(BaseModel):
    category_id: str
    image_url: str
    caption: Optional[str] = None
    tags: List[str] = []
    is_featured: bool = False


class AvailabilityIn(BaseModel):
    day_of_week: int
    start_time: str
    end_time: str
    is_available: bool = True


class BookingIn(BaseModel):
    practitioner_id: str
    service_id: str
    booking_date: str  # YYYY-MM-DD
    start_time: str  # HH:MM
    service_location: Literal["practitioner_location", "client_location"] = "practitioner_location"
    client_address: Optional[str] = None
    client_notes: Optional[str] = None
    client_source: Literal["marketplace", "direct_link"] = "marketplace"


class BookingStatusIn(BaseModel):
    status: Literal["confirmed", "completed", "cancelled_by_client", "cancelled_by_practitioner", "no_show"]
    practitioner_notes: Optional[str] = None


class ReviewIn(BaseModel):
    booking_id: str
    rating: int = Field(ge=1, le=5)
    text: Optional[str] = None
    client_photo_urls: List[str] = []


class FavoriteIn(BaseModel):
    practitioner_id: str


class VerificationIn(BaseModel):
    verification_type: Literal["government_id", "trade_certificate", "insurance", "selfie", "background_check"]
    document_url: str
    document_expiry: Optional[str] = None


class VerificationDecisionIn(BaseModel):
    decision: Literal["verified", "rejected"]
    rejection_reason: Optional[str] = None
    grant_badges: List[str] = []


class SuspendPractitionerIn(BaseModel):
    suspended: bool
    reason: Optional[str] = None
