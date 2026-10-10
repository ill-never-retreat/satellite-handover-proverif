from pathlib import Path
import argparse,subprocess,json
p=argparse.ArgumentParser();p.add_argument("--proverif",default="proverif");a=p.parse_args()
root=Path(__file__).resolve().parent
out=root/"reproduced_results";out.mkdir(exist_ok=True)
results=[]
for model in sorted((root/"models").glob("*.pv")):
 r=subprocess.run([a.proverif,str(model)],capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=120)
 t=r.stdout+r.stderr
 (out/(model.stem+".result.txt")).write_text(t,encoding="utf-8")
 results.append({"model":model.name,"exit_code":r.returncode,"queries":[x for x in t.splitlines() if x.startswith("RESULT")]})
(out/"results.json").write_text(json.dumps(results,indent=2),encoding="utf-8")
print(json.dumps(results,indent=2))
assert all(r["exit_code"]==0 for r in results)
