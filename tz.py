import datetime
import zoneinfo

UTC = zoneinfo.ZoneInfo("UTC")
CET = zoneinfo.ZoneInfo("CET")
PT = zoneinfo.ZoneInfo("Europe/Lisbon")
ES = zoneinfo.ZoneInfo("Europe/Madrid")

utc = datetime.datetime.now(tz=UTC)
cet = utc.astimezone(CET)
pt = utc.astimezone(PT)
es = utc.astimezone(ES)


print(f"UTC: {utc}")
print(f"CET: {cet}")
print(f" PT: {pt}")
print(f" ES: {es}")
