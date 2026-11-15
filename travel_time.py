"""Navigator travel-time formatting. No Streamlit dependencies."""
import math

from i18n import t

SOL_MINUTES = 24.6597 * 60  # Martian day (sol) in minutes


def format_duration(minutes):
    """90.4 -> '1 h 30 min'; 0.4 -> '< 1 min'; 3000 -> '2 d 1 h 0 min'."""
    if not math.isfinite(minutes) or minutes < 0:
        return "—"
    total = int(round(minutes))
    if total == 0:
        return f"< 1 {t('unit.min')}" if minutes > 0 else f"0 {t('unit.min')}"
    days, rest = divmod(total, 24 * 60)
    hours, mins = divmod(rest, 60)

    parts = []
    if days:
        parts.append(f"{days} {t('unit.d')}")
    if days or hours:
        parts.append(f"{hours} {t('unit.h')}")
    parts.append(f"{mins} {t('unit.min')}")
    return " ".join(parts)


def sols(minutes):
    """Duration in Martian sols."""
    return minutes / SOL_MINUTES
