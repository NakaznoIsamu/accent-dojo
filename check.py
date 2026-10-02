import pyopenjtalk,sys
sys.path.insert(0,"/tmp/claude-0/-home-claude/55e828ac-9f06-5499-9bfb-2da9af8dc45a/scratchpad")
from t2 import pitch
for line in open("sentences.txt"):
    lv,*ss=line.strip().split("|")
    for s in ss:
        nj=pyopenjtalk.run_frontend(s)
        print(lv,s)
        print("   ", " ".join(f"{n['string']}[{n['read']}:{n['acc']}]" for n in nj if n['string'] not in "。、"))
        print("   ", pitch(s))
