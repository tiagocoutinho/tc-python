from pathlib import Path
from collections import defaultdict
from v4l2capture import Video_device as Video


all_dev_paths = Path("/dev").rglob("video*")
all_devs = ((path, Video(str(path))) for path in all_dev_paths)
buses = defaultdict(list)
for path, dev in all_devs:
    driver, card, bus, caps = dev.get_info()
    buses[bus].append((path, dev, driver, card, bus, caps))

for bus, devs in buses.items():
    dev = min(devs)
    print(dev)

