from fastapi import APIRouter, HTTPException, Query

from db import (
    fetch_detections,
    fetch_detections_summary,
    fetch_detections_today,
    fetch_inventory,
    fetch_item,
    fetch_item_summary,
    fetch_movements,
    fetch_staff,
    fetch_stats,
)

router = APIRouter(prefix="/api", tags=["Inventory API"])


@router.get("/inventory")
def get_inventory():
    return fetch_inventory()


@router.get("/movements")
def get_movements(
    limit: int = Query(200, ge=1, le=1000),
    staff_name: str = Query(""),
):
    return fetch_movements(limit, staff_name)


@router.get("/stats")
def get_stats():
    return fetch_stats()


@router.get("/search")
def search_inventory(
    q: str = Query("", alias="q"),
    query: str = Query("", alias="query"),
):
    return fetch_inventory(q or query)


@router.get("/items/{item_id}")
def get_item(item_id: int):
    item = fetch_item(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.get("/item-summary")
def get_item_summary(name: str = Query(..., min_length=1)):
    summary = fetch_item_summary(name)
    if summary is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return summary


@router.get("/detections")
def get_detections(limit: int = Query(100, ge=1, le=1000)):
    return fetch_detections(limit)


@router.get("/detections/summary")
def get_detections_summary():
    return fetch_detections_summary()


@router.get("/detections/today")
def get_detections_today():
    return fetch_detections_today()


@router.get("/staff")
def get_staff_list():
    return fetch_staff()
