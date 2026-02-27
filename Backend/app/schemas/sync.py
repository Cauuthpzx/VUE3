from pydantic import BaseModel, Field


class SyncRequest(BaseModel):
    base_url: str = Field(
        description="Base URL of the source site (e.g., https://a2u4k.ee88dly.com)"
    )
    cookies: str = Field(
        description="Cookie string for authentication (PHPSESSID + cf_clearance)"
    )
    agent_id: int = Field(
        default=1,
        description="Agent ID to tag synced data",
    )
    data_date: str | None = Field(
        default=None,
        description="Data date (YYYY-MM-DD). Required for all endpoints except members. "
        "Invites uses today if not provided.",
    )
    max_pages: int = Field(
        default=0,
        description="Max pages per endpoint (0 = all pages)",
    )
    endpoints: list[str] | None = Field(
        default=None,
        description="List of endpoints to sync (None = all)",
    )
