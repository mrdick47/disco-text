from datetime import datetime


def format_timestamp(dt: datetime, use_24h: bool) -> str:
    local_dt = dt
    if local_dt.tzinfo is not None:
        local_dt = dt.astimezone()

    month = local_dt.month
    day = local_dt.day
    year = local_dt.year

    if use_24h:
        time_str = f"{local_dt.hour}:{local_dt.minute:02d}"
    else:
        hour = local_dt.hour % 12 or 12
        ampm = "AM" if local_dt.hour < 12 else "PM"
        time_str = f"{hour}:{local_dt.minute:02d} {ampm}"

    return f"{month}/{day}/{year} {time_str}"
