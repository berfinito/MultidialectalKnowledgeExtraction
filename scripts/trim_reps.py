import sys, re, pathlib

src = pathlib.Path(sys.argv[1])
dst = pathlib.Path(sys.argv[2])
k = int(sys.argv[3]) if len(sys.argv) > 3 else 15

lines = src.read_text(encoding="utf-8").splitlines()
out = []
count = 0
in_topic = False
for i, line in enumerate(lines):
    if line.startswith("# Representatives "):
        out.append(line)
        out.append("")
        continue 
    if line.startswith("## Topic "):
        count += 1
        in_topic = True
        if count > k:
            break
        out.append(line)
        continue
    if in_topic:
        out.append(line)
dst.write_text("\n".join(out), encoding="utf-8")
print(f"[trim] -> {dst}")