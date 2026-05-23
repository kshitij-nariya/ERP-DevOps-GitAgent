from fastapi import APIRouter, HTTPException

from db.database import get_review, list_reviews

router = APIRouter()


@router.get("")
def reviews(limit: int = 20) -> list[dict]:
    return list_reviews(limit)


@router.get("/latest")
def latest_review() -> dict:
    reviews_list = list_reviews(1)
    if not reviews_list:
        return {}
    return reviews_list[0]


@router.get("/{review_id}")
def review_detail(review_id: int) -> dict:
    review = get_review(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review
