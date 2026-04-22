from typing import Optional, List, Dict, Any
from datetime import datetime
from dataclasses import dataclass


@dataclass
class UserProfile:
    """User profile domain entity."""
    uid: str
    name: str
    email: Optional[str] = None
    gender: Optional[str] = None
    bloodGroup: Optional[str] = None
    city: Optional[str] = None
    cnic: Optional[str] = None
    phone: Optional[str] = None
    available: bool = True
    mode: str = "patient"  # 'donor' | 'patient'
    role: str = "user"  # 'user' | 'admin'
    themePreference: str = "system"  # 'system' | 'light' | 'dark'
    locationLat: Optional[float] = None
    locationLng: Optional[float] = None
    createdAt: datetime = None
    updatedAt: datetime = None
    
    def __post_init__(self):
        if self.createdAt is None:
            self.createdAt = datetime.utcnow()
        if self.updatedAt is None:
            self.updatedAt = datetime.utcnow()


@dataclass
class BloodRequest:
    """Blood request domain entity."""
    id: str
    createdBy: str
    patientName: str
    requiredBloodGroup: str
    city: str
    gender: Optional[str] = None
    hospital: Optional[str] = None
    locationAddress: Optional[str] = None
    locationLat: Optional[float] = None
    locationLng: Optional[float] = None
    unitsRequired: Optional[int] = None
    neededBy: Optional[datetime] = None
    notes: Optional[str] = None
    requestedTo: Optional[str] = None  # specific donor uid
    status: str = "open"  # 'open' | 'pending' | 'accepted' | 'rejected' | 'fulfilled' | 'cancelled'
    createdAt: datetime = None
    
    def __post_init__(self):
        if self.createdAt is None:
            self.createdAt = datetime.utcnow()


@dataclass
class Donation:
    """Blood donation domain entity."""
    id: str
    userId: str
    requestId: str
    status: str = "pending"  # 'pending' | 'donated' | 'cancelled'
    date: datetime = None
    
    def __post_init__(self):
        if self.date is None:
            self.date = datetime.utcnow()


@dataclass
class Comment:
    """Comment domain entity."""
    id: str
    requestId: str
    uid: str
    text: str
    createdAt: datetime = None
    
    def __post_init__(self):
        if self.createdAt is None:
            self.createdAt = datetime.utcnow()


@dataclass
class MoneyDonation:
    """Money donation domain entity."""
    id: str
    uid: str  # donor
    amount: float
    currency: str = "PKR"
    purpose: Optional[str] = None
    stripePaymentId: Optional[str] = None
    stripeSessionId: Optional[str] = None
    receiptUrl: Optional[str] = None
    createdAt: datetime = None
    
    def __post_init__(self):
        if self.createdAt is None:
            self.createdAt = datetime.utcnow()


@dataclass
class Notification:
    """Notification domain entity."""
    id: str
    uid: str
    type: str
    title: str
    message: str
    data: Optional[Dict[str, Any]] = None
    read: bool = False
    createdAt: datetime = None
    
    def __post_init__(self):
        if self.createdAt is None:
            self.createdAt = datetime.utcnow()


@dataclass
class ChatSession:
    """Chat session domain entity."""
    id: str
    uid: str
    createdAt: datetime = None
    updatedAt: datetime = None
    
    def __post_init__(self):
        if self.createdAt is None:
            self.createdAt = datetime.utcnow()
        if self.updatedAt is None:
            self.updatedAt = datetime.utcnow()


@dataclass
class ChatMessage:
    """Chat message domain entity."""
    id: str
    sessionId: str
    role: str  # 'user' | 'assistant'
    content: str
    attachments: Optional[List[Dict[str, Any]]] = None
    createdAt: datetime = None
    
    def __post_init__(self):
        if self.createdAt is None:
            self.createdAt = datetime.utcnow()


@dataclass
class FileAttachment:
    """File attachment domain entity."""
    id: str
    fileName: str
    fileUrl: str
    fileType: str
    fileSize: int
    uploadedBy: str
    createdAt: datetime = None
    
    def __post_init__(self):
        if self.createdAt is None:
            self.createdAt = datetime.utcnow()


@dataclass
class Organization:
    """Organization domain entity."""
    id: str
    name: str
    type: str  # 'hospital' | 'ngo'
    city: str
    address: Optional[str] = None
    locationLat: Optional[float] = None
    locationLng: Optional[float] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    logoUrl: Optional[str] = None
    verified: bool = False
    createdAt: datetime = None
    updatedAt: datetime = None
    createdBy: str = None
    
    def __post_init__(self):
        if self.createdAt is None:
            self.createdAt = datetime.utcnow()
        if self.updatedAt is None:
            self.updatedAt = datetime.utcnow()


@dataclass
class OrgSubscription:
    """Organization subscription domain entity."""
    orgId: str
    plan: str  # 'basic' | 'premium'
    status: str  # 'active' | 'cancelled' | 'past_due'
    stripeCustomerId: str
    stripeSubscriptionId: str
    currentPeriodStart: datetime
    currentPeriodEnd: datetime
    createdAt: datetime = None
    updatedAt: datetime = None
    
    def __post_init__(self):
        if self.createdAt is None:
            self.createdAt = datetime.utcnow()
        if self.updatedAt is None:
            self.updatedAt = datetime.utcnow()
