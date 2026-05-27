from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

# 1. Crear una fecha sin zona horaria (ejemplo: 25 de diciembre a las 10:00 AM)
fecha_naive = datetime(2026, 12, 25, 10, 0, 0)

# 2. Localizar al sistema que esta fecha "pertenece" a la zona horaria de Venezuela
fecha_ven = fecha_naive.replace(tzinfo=timezone(timedelta(hours=-4)))

print(f" Fecha y hora, sin zona horaria: {fecha_naive}")
print(f" Fecha y hora, con zona horaria venezolana: {fecha_ven}")
print(f" Fecha y hora actual, sin zona horaria: {datetime.now()}")
print(f" Fecha y hora actual, con zona horaria UTC: {datetime.now(timezone.utc)}")
print(f" Fecha y hora actual, con zona horaria venezolana: {datetime.now(timezone(timedelta(hours=-4)))}")
