from collections import Counter
from cloggle.templeosrs import load_collection_log

items = load_collection_log("data/templeosrs")
cnt = Counter()
for item in items.values():
    for s in item.sources:
        cnt[s.lower()] += 1

for src, n in cnt.most_common():
    print(f"{src}\t{n}")