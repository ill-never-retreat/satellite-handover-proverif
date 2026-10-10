"""Reproducible software microbenchmarks and explicitly synthetic sensitivity experiments.
Run from the project root. No real credentials or orbital traces are used.
"""
from pathlib import Path
import hashlib, hmac, json, math, os, platform, random, statistics, sys, time
from collections import deque
import cryptography
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "reproduced_results"
OUT.mkdir(parents=True, exist_ok=True)
RNG = random.Random(20260924)
IDR = (1).to_bytes(13, "big")
IDS = [(i+100).to_bytes(13, "big") for i in range(16)]
EXP = (1800000000).to_bytes(4, "big")
SALT = bytes(32)
PREFIX = b"CEE-HO-v1:"
PAYLOAD = bytes(256)

def expand(prk, info, length):
    return hmac.digest(prk, PREFIX + info + b"\x01", "sha256")[:length]

def kdf(key, info, length=16):
    return expand(hmac.digest(SALT, key, "sha256"), info, length)

def traffic_keys(master):
    prk = hmac.digest(SALT, master, "sha256")
    return expand(prk, b"enc", 16), expand(prk, b"mac", 32)

def session_key(key, eta, exp, rid, sid):
    return kdf(key, b"session" + rid + sid + eta + exp)

def encrypt(key, data, iv):
    e = Cipher(algorithms.AES(key), modes.CTR(iv)).encryptor()
    return iv + e.update(data) + e.finalize()

def decrypt(key, ct):
    e = Cipher(algorithms.AES(key), modes.CTR(ct[:16])).decryptor()
    return e.update(ct[16:]) + e.finalize()

def seal(master, label, header, data, trailer=b""):
    ek, mk = traffic_keys(master)
    ct = encrypt(ek, data, os.urandom(16))
    tag = hmac.digest(mk, PREFIX + label + header + ct + trailer, "sha256")[:20]
    return ct, tag

def open_message(master, label, header, ct, tag, trailer=b""):
    ek, mk = traffic_keys(master)
    if not hmac.compare_digest(tag, hmac.digest(mk, PREFIX+label+header+ct+trailer, "sha256")[:20]):
        raise ValueError("MAC")
    return decrypt(ek, ct)

def moduli(bits, m):
    ns = []
    while len(ns) < m:
        n = RNG.getrandbits(bits) | (1 << (bits-1)) | 1
        if all(math.gcd(n, old) == 1 for old in ns):
            ns.append(n)
    return ns

def crt(rs, ns):
    product = math.prod(ns)
    return sum(r * (product//n) * pow(product//n, -1, n) for r,n in zip(rs,ns)) % product

def residue(n, tagbits, sid):
    while True:
        seed = os.urandom(tagbits//8)
        eta = hashlib.sha256(PREFIX+b"recovery"+seed+IDR+sid).digest()[:tagbits//8]
        rho = int.from_bytes(eta+EXP, "big")
        if rho < n:
            return rho, eta

def prepare(ns, tagbits, ltk, kr, ks):
    pairs = [residue(n, tagbits, sid) for n,sid in zip(ns,IDS)]
    rs, etas = zip(*pairs)
    c = crt(rs, ns)
    cwire = c.to_bytes((len(ns)*(tagbits+32)+7)//8, "big")
    keys = [session_key(key, eta, EXP, IDR, sid) for key,eta,sid in zip(ltk,etas,IDS)]
    nr, skj = os.urandom(16), os.urandom(16)
    bundle = cwire+EXP+b"".join(sid+sk for sid,sk in zip(IDS,keys))
    ctr, tagr = seal(kr,b"router-down",b"",nr+bundle+skj)
    # The satellite MAC binds N_R || CT_Sj || M_R, with M_R = CT_R || tag_R.
    cts, tags = seal(ks,b"satellite-down",nr,IDR+skj,ctr+tagr)
    return c, keys, (nr,cts,tags,ctr,tagr)

def timing(fn, loops, batches=9):
    for _ in range(min(loops,20)): fn()
    vals = []
    for _ in range(batches):
        start = time.perf_counter_ns()
        for _ in range(loops): fn()
        vals.append((time.perf_counter_ns()-start)/loops/1000)
    return {"median_us": statistics.median(vals), "min_us":min(vals),"max_us":max(vals),
            "batch_means_us":vals,"loops_per_batch":loops,"batches":batches}

def cost(m,b):
    c = math.ceil(m*b/8)*8
    idbits,nonce,ts,mac,iv,key = 104,128,32,160,128,128
    m1=idbits+nonce+ts+mac
    m2=idbits+m1+mac
    ctr=iv+nonce+c+ts+m*(idbits+key)+key
    mr=ctr+mac
    cts=iv+idbits+key
    md=nonce+cts+mr+mac
    # control excludes service plaintext, includes its required IV
    ho=c+idbits+mac+iv
    return {"m":m,"modulus_bits":b,"token_bits":c,"ho_control_bits":ho,
            "m1_bits":m1,"m2_bits":m2,"mdown_bits":md,"mr_bits":mr,
            "phaseII_bits":md+mr,"prepare_bits":m1+m2+md+mr,
            "router_cache_bits":c+ts+m*(idbits+key),
            "amortized_u1_bits":m1+m2+md+mr+ho,
            "amortized_um_bits":(m1+m2+md+mr)/m+ho,
            "reduction_vs_1864":1-ho/1864}

def state_checks():
    # Exhaustive finite transition abstraction: two credentials, capacity one,
    # expiry=(2,3), integer time 0..5, skew=1, max horizon=3.
    initial=(0, (), (0,0))
    seen={initial}; q=deque([initial]); transitions=0
    exps=(2,3)
    while q:
        now, entries, accepts=q.popleft()
        active=tuple(i for i in entries if now <= exps[i]+1)
        nexts=[]
        if now < 5: nexts.append((now+1,active,accepts))
        # Authenticate, recheck time and compare/insert are one serialized commit.
        for i in range(2):
            if -1 <= exps[i]-now <= 4 and i not in active and len(active)<1:
                aa=list(accepts); aa[i]+=1
                nexts.append((now,tuple(sorted(active+(i,))),tuple(aa)))
        # bad MAC, duplicate, full and expired rejection are no-state-change.
        nexts.append((now,active,accepts))
        for st in nexts:
            transitions+=1
            assert max(st[2]) <= 1
            if st not in seen: seen.add(st); q.append(st)
    # Negative controls expose the intended failures, not security proofs.
    # Both threads observe an empty table before either commits.
    weak_table=set()
    eligible=[0 not in weak_table, 0 not in weak_table]
    weak_accepts=0
    for ready in eligible:
        if ready:
            weak_table.add(0)
            weak_accepts+=1
    assert weak_accepts==2
    # Accept, lose the table on restart, then replay before expiration.
    volatile_table=set()
    restart_without_retention_accepts=0
    for reboot in (False,True):
        if reboot: volatile_table.clear()
        if 0 not in volatile_table:
            volatile_table.add(0)
            restart_without_retention_accepts+=1
    assert restart_without_retention_accepts==2
    return {"states":len(seen),"transitions":transitions,"max_acceptances_per_tuple":1,
            "negative_control_nonatomic_accepts":weak_accepts,
            "negative_control_cache_lost_on_reboot":restart_without_retention_accepts,
            "scope":"finite numerical state abstraction, not ProVerif or unbounded machine proof"}

def simulate(m,a,p,n=20000):
    rng=random.Random(20260924+m*10000+round(a*100)+round(p*1000))
    sizes=cost(m,160)
    hops=[sizes[k] for k in ("m1_bits","m2_bits","mdown_bits","mr_bits")]
    prepbits=preptime=0.0
    interruptions=[]; totals=[]; attempts_total=0; fallbacks=0; refreshes=0
    def preparation():
        bits=elapsed=0.; rounds=0
        while True:
            rounds+=1
            good=True
            for size in hops:
                bits+=size; elapsed+=10+size/1000 # 1 Mbit/s, ms
                if rng.random()<p:
                    elapsed+=50; good=False; break
            if good: return bits,elapsed,rounds
    for _ in range(n):
        pb,pt,rounds=preparation()
        prepbits+=pb; preptime+=pt; refreshes+=rounds-1
        bits=pb; delay=0.; confirmed=False
        for i in range(m):
            if rng.random()>=a: continue
            attempts_total+=1
            bits+=sizes["ho_control_bits"]
            # 256-byte service payload included only in time, not control-bit total.
            delay+=10+(sizes["ho_control_bits"]+2048)/1000
            if rng.random()<p:
                delay+=50; continue
            # Protected return traffic is exogenous liveness, not a HO ack.
            if rng.random()<p:
                delay+=50; continue
            delay+=20
            confirmed=True; break
        if not confirmed:
            fallbacks+=1
            fb,ft,fr=preparation()
            bits+=fb; delay+=ft+20; refreshes+=fr-1
        interruptions.append(delay); totals.append(bits)
    theoretical=(1-a*(1-p)**2)**m
    return {"m":m,"candidate_available_probability":a,"packet_loss":p,"episodes":n,
            "fallback_rate":fallbacks/n,"analytic_fallback_rate":theoretical,
            "mean_attempts":attempts_total/n,"mean_preparation_ms":preptime/n,
            "mean_confirmation_ms_after_trigger":statistics.mean(interruptions),
            "p95_confirmation_ms_after_trigger":sorted(interruptions)[int(.95*n)],
            "mean_total_control_bits":statistics.mean(totals),
            "mean_preparation_control_bits":prepbits/n,"mean_extra_prepare_rounds":refreshes/n}

def main():
    rows=[]; assertions=0
    for tagbits in (128,80):
        for m in (2,3,4,5,6,8,10,16):
            ns=moduli(tagbits+32,m)
            ltks=[os.urandom(16) for _ in ns]
            kr,ks=os.urandom(16),os.urandom(16)
            pairs=[residue(n,tagbits,sid) for n,sid in zip(ns,IDS)]
            rs,etas=zip(*pairs)
            c=crt(rs,ns)
            assert all(c%n==r for n,r in zip(ns,rs)); assertions+=m
            sk=session_key(ltks[0],etas[0],EXP,IDR,IDS[0])
            wire=c.to_bytes(m*(tagbits+32)//8,"big")
            header=wire+IDR
            def router_packet(): return seal(sk,b"handover",header,PAYLOAD)
            ct,tag=router_packet()
            def target():
                rho=c%ns[0]
                eta=rho.to_bytes((tagbits+32)//8,"big")[:-4]
                key=session_key(ltks[0],eta,EXP,IDR,IDS[0])
                return open_message(key,b"handover",header,ct,tag)
            assert target()==PAYLOAD; assertions+=1
            wrong=session_key(ltks[0],etas[0],EXP,(2).to_bytes(13,"big"),IDS[0])
            try: open_message(wrong,b"handover",wire+(2).to_bytes(13,"big"),ct,tag)
            except ValueError: assertions+=1
            else: raise AssertionError("identity substitution")
            row=cost(m,tagbits+32)
            row.update({"tag_bits":tagbits,"mod":timing(lambda:c%ns[0],20000),
                        "crt":timing(lambda:crt(rs,ns),300),
                        "gateway_prepare":timing(lambda:prepare(ns,tagbits,ltks,kr,ks),100),
                        "router_packet":timing(router_packet,1000),
                        "target_accept_crypto":timing(target,1000)})
            rows.append(row)
    sim=[simulate(m,a,p) for m in (2,3,4,5,6,8,10,16)
         for a in (.3,.6,.9) for p in (0.,.05,.10)]
    result={"platform":{"python":sys.version,"os":platform.platform(),"machine":platform.machine(),
             "cpu":"12th Gen Intel Core i9-12900H, 14 cores / 20 logical processors",
             "cryptography":cryptography.__version__,"clock":"perf_counter_ns",
             "payload_bytes":256,"timing":"single-process, 9 batches, batch-mean ranges",
             "limitations":"desktop software, not flight hardware, not network or secure-erasure timing"},
            "benchmark":rows,"state":state_checks(),"assertions":assertions,"simulation":sim,
            "simulation_assumptions":{"seed":20260924,"episodes_per_cell":20000,"link_ms":10,
              "rate_bps":1000000,"timeout_ms":50,"return_ms":20,"clock_cost_included":False,
              "model":"independent candidate availability and packet losses; fresh bundle per episode; online fallback",
              "omits":"orbital traces, link budgets, Doppler, correlated outages, scheduling and competing queues",
              "control_bits":"sum over transmissions on both hops; excludes application payload and return traffic",
              "return_loss":"one exogenous protected-return opportunity per attempt",
              "availability":"fallback assumes a reachable access satellite and GW; active jamming has no finite bound"}}
    (OUT/"results.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps({"benchmark_rows":len(rows),"simulation_cells":len(sim),"assertions":assertions,
                      "state":result["state"]},indent=2))
    for row in rows:
        if row["tag_bits"]==128 and row["m"] in (3,10,16):
            print({k:row[k] for k in ("m","mod","crt","gateway_prepare","ho_control_bits","prepare_bits")})
    for cell in sim:
        if cell["m"]==3 and cell["candidate_available_probability"]==.6: print(cell)

if __name__=="__main__": main()
