"""Restaurant profile. Single source of truth for the location the voice agent
represents. Swap or extend to multi-tenant later (one profile per restaurant)."""
from __future__ import annotations

RESTAURANT = {
    "name": "Hakka Legend",
    "location": "Markham",
    "address": "Markham, ON",
    "phone": "9052945777",          # main line shown on menu
    "phone_display": "905.294.5777",
    "hours": "Monday-Thursday 11am-10pm, Friday-Saturday 11am-11pm, Sunday 12pm-10pm",
    "website": "https://www.hakkalegend.com",
    "cuisine": "Hakka / Indo-Chinese",
}
