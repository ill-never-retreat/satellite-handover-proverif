"""Deterministic functional checks; these are not a cryptographic proof."""
from pathlib import Path
import json, hmac, hashlib, math
import evaluate as e
import sys
out=e.ROOT/("recorded_results" if "--recorded" in sys.argv else "reproduced_results")
checks={}
ns=e.moduli(160,3)
pairs=[e.residue(n,128,s) for n,s in zip(ns,e.IDS)]
rs,etas=zip(*pairs)
c=e.crt(rs,ns); wire=c.to_bytes(60,"big")
checks["CRT_roundtrip"]=all(c%n==r for n,r in zip(ns,rs))
root=bytes(range(16)); rid2=(2).to_bytes(13,"big")
sk=e.session_key(root,etas[0],e.EXP,e.IDR,e.IDS[0])
ct,tg=e.seal(sk,b"handover",wire+e.IDR,e.PAYLOAD)
checks["valid_decryption"]=e.open_message(sk,b"handover",wire+e.IDR,ct,tg)==e.PAYLOAD
def rejected(key,header,ct,tg):
 try: e.open_message(key,b"handover",header,ct,tg)
 except ValueError: return True
 return False
checks["tampered_ciphertext_rejected"]=rejected(sk,wire+e.IDR,ct[:-1]+bytes([ct[-1]^1]),tg)
checks["tampered_MAC_rejected"]=rejected(sk,wire+e.IDR,ct,tg[:-1]+bytes([tg[-1]^1]))
# A credential holder knows its own session master and can re-MAC a changed header.
# The target must derive a DIFFERENT master for the substituted router identity.
ct2,tg2=e.seal(sk,b"handover",wire+rid2,e.PAYLOAD)
target2=e.session_key(root,etas[0],e.EXP,rid2,e.IDS[0])
checks["credential_holder_retagged_identity_rejected"]=rejected(target2,wire+rid2,ct2,tg2)
old=e.kdf(root,b"session"+etas[0]+e.EXP)
oldct,oldtg=e.seal(old,b"handover",wire+rid2,e.PAYLOAD)
checks["negative_control_unbound_identity_accepts"]=e.open_message(old,b"handover",wire+rid2,oldct,oldtg)==e.PAYLOAD
ek,mk=e.traffic_keys(sk)
checks["separate_traffic_keys"]=ek!=mk[:16]
checks["different_target_changes_master"]=sk!=e.session_key(root,etas[0],e.EXP,e.IDR,e.IDS[1])

# Independently construct the specified satellite-downlink MAC input. This
# prevents a matching but incorrectly ordered sender/receiver pair from passing.
def flip_last(value):
 return value[:-1]+bytes([value[-1]^1])

def downlink_rejected(key,nonce,cts,tags,router_message,label=b"satellite-down"):
 try: e.open_message(key,label,nonce,cts,tags,router_message)
 except ValueError: return True
 return False

downlink_checks={name:True for name in (
 "satellite_downlink_specified_MAC_order", "satellite_downlink_valid_decryption",
 "router_downlink_bundle_consistent", "satellite_downlink_nonce_tamper_rejected",
 "satellite_downlink_ciphertext_tamper_rejected", "satellite_downlink_router_ciphertext_tamper_rejected",
 "satellite_downlink_router_MAC_tamper_rejected", "satellite_downlink_MAC_tamper_rejected",
 "satellite_downlink_old_order_rejected", "satellite_downlink_role_substitution_rejected")}
downlink_configurations=0
for tagbits in (128,80):
 for m in (2,3,4,5,6,8,10,16):
  moduli=e.moduli(tagbits+32,m)
  ltks=[bytes([i+1])*16 for i in range(m)]
  kr,ks=bytes([31])*16,bytes([47])*16
  token,keys,(nonce,cts,tags,ctr,tagr)=e.prepare(moduli,tagbits,ltks,kr,ks)
  mr=ctr+tagr
  _,mk=e.traffic_keys(ks)
  expected=hmac.digest(mk,e.PREFIX+b"satellite-down"+nonce+cts+mr,"sha256")[:20]
  downlink_checks["satellite_downlink_specified_MAC_order"] &= hmac.compare_digest(tags,expected)
  sat_plain=e.open_message(ks,b"satellite-down",nonce,cts,tags,mr)
  downlink_checks["satellite_downlink_valid_decryption"] &= sat_plain[:13]==e.IDR and len(sat_plain)==29
  router_plain=e.open_message(kr,b"router-down",b"",ctr,tagr)
  wire=token.to_bytes(m*(tagbits+32)//8,"big")
  expected_bundle=nonce+wire+e.EXP+b"".join(sid+key for sid,key in zip(e.IDS,keys))+sat_plain[13:]
  downlink_checks["router_downlink_bundle_consistent"] &= router_plain==expected_bundle
  downlink_checks["satellite_downlink_nonce_tamper_rejected"] &= downlink_rejected(ks,flip_last(nonce),cts,tags,mr)
  downlink_checks["satellite_downlink_ciphertext_tamper_rejected"] &= downlink_rejected(ks,nonce,flip_last(cts),tags,mr)
  downlink_checks["satellite_downlink_router_ciphertext_tamper_rejected"] &= downlink_rejected(ks,nonce,cts,tags,flip_last(ctr)+tagr)
  downlink_checks["satellite_downlink_router_MAC_tamper_rejected"] &= downlink_rejected(ks,nonce,cts,tags,ctr+flip_last(tagr))
  downlink_checks["satellite_downlink_MAC_tamper_rejected"] &= downlink_rejected(ks,nonce,cts,flip_last(tags),mr)
  old_tag=hmac.digest(mk,e.PREFIX+b"satellite-down"+nonce+mr+cts,"sha256")[:20]
  downlink_checks["satellite_downlink_old_order_rejected"] &= downlink_rejected(ks,nonce,cts,old_tag,mr)
  downlink_checks["satellite_downlink_role_substitution_rejected"] &= downlink_rejected(ks,nonce,cts,tags,mr,b"router-down")
  downlink_configurations+=1
checks.update(downlink_checks)
cost=e.cost(3,160)
checks["principal_costs"]=all(cost[k]==v for k,v in {"token_bits":480,"ho_control_bits":872,"phaseII_bits":4152,"prepare_bits":5264,"router_cache_bits":1208}.items())
state=e.state_checks()
checks["state_invariant"]=state["max_acceptances_per_tuple"]==1
checks["negative_state_controls_fail"]=state["negative_control_nonatomic_accepts"]==2 and state["negative_control_cache_lost_on_reboot"]==2
result=json.loads((out/"results.json").read_text())
tests=[]
for cell in result["simulation"]:
 p=cell["analytic_fallback_rate"]; n=cell["episodes"]; k=round(cell["fallback_rate"]*n)
 probs=[math.exp(math.lgamma(n+1)-math.lgamma(i+1)-math.lgamma(n-i+1)+i*math.log(p)+(n-i)*math.log1p(-p)) for i in range(n+1)]
 pv=min(1.0,2*min(math.fsum(probs[:k+1]),math.fsum(probs[k:])))
 tests.append({"m":cell["m"],"a":cell["candidate_available_probability"],"p_loss":cell["packet_loss"],
  "observed_fallbacks":k,"expected_fallbacks":n*p,"exact_equal_tail_p":pv})
checks["fallback_formula_not_rejected_familywise_005"]=min(t["exact_equal_tail_p"] for t in tests)>=.05/len(tests)
report={"checks":checks,"all_pass":all(checks.values()),"satellite_downlink_configurations":downlink_configurations,"state_rerun":state,"exact_binomial_tests":tests,"familywise_threshold":.05/len(tests),
 "interpretation":"Passing checks validate selected implementation properties, not ResHide hardness, arbitrary parser safety, or a full protocol proof."}
(e.OUT/"functional_checks.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print(json.dumps(report,indent=2))
assert report["all_pass"]
