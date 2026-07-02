from enum import Enum

class PoolCategory(str, Enum):
    ENTERTAINMENT = "Entertainment"
    MUSIC = "Music"
    AI_PRODUCTIVITY = "AI & Productivity"
    CLOUD_STORAGE = "Cloud Storage"
    DESIGN_CREATIVE = "Design & Creative"
    GAMING = "Gaming"
    EDUCATION = "Education & Learning"
    SOFTWARE_DEV = "Software & Developer Tools"
    NEWS = "News & Reading"
    FITNESS = "Fitness & Wellness"
    BUSINESS = "Business & Finance"
    SHOPPING = "Shopping & Memberships"
    OTHER = "Other"


class request_status(str, Enum):
    REQUESTED = 'requested'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'

class pool_role(str,Enum):
    HOST = 'host'
    MEMBER = 'member'
    

