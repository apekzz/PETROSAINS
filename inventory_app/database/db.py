"""Compatibility wrappers. All SQL lives in sql.py."""

from sql import (  # noqa: F401
    check_db,
    clear_check_in_out,
    clear_staff_embeddings,
    close_boot_connection,
    bootstrap_database,
    connect_and_prepare,
    ensure_tables,
    export_table_snapshots,
    fetch_detections,
    fetch_detections_summary,
    fetch_detections_today,
    fetch_inventory,
    fetch_inventory_embeddings,
    fetch_item_summary,
    fetch_item,
    fetch_movements,
    fetch_staff,
    fetch_staff_embeddings,
    fetch_stats,
    get_db,
    get_staff,
    insert_check_in_out,
    insert_staff,
    normalize_item_name,
    record_yolo_capture,
    replace_inventory_embeddings,
    restore_empty_tables_from_snapshots,
    refresh_main_inventory,
    save_inventory_embedding,
    save_object_embedding,
)


def init_schema(clear_non_inventory=False, seed=True):
    """Boot helper — create missing tables only. Never seeds or overwrites."""
    bootstrap_database()
    return True
