from pydantic import BaseModel


class ManualReviewRequest(BaseModel):
    repo_url: str
    pr_number: int = 0
    head_sha: str = "HEAD"
    base_sha: str = "HEAD~1"
