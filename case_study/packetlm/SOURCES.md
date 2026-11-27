# PacketLM case study: data and sources

Everything in Section 10 of the paper, and the numbers derived in Section 11, comes from
the files listed here. Nothing was re-run for this paper; the cost logs were only copied
(and gzipped) and re-analysed with the pinned instrument.

- **Source repository:** https://github.com/jacksonjp0311-gif/PacketLM
- **Branch / commit:** `g44-canonical-engine` at `8994490`
  ("G57b registered results ..."), read-only clone.
- **Instrument:** this repository's `amortization/metric.py` and `amortization/stats.py`,
  unchanged since `70297af` (tag `instrument-v1`).
- **Reproduce:** `python case_study/packetlm/reproduce.py` (about 25 s). It recomputes 42
  contrasts with 5000-resample paired bootstrap intervals, 9 scaling ratios with PacketLM's
  registered bootstrap, and the derived numbers of Section 11, and compares each with the
  value printed in the source. PacketLM's docs round the instrument's 4-decimal report a
  second time, so a tolerance of half a unit in the printed place plus 0.00005 is used.

## Cost logs (`data/*_total.csv.gz`)

Columns `arm,seed,task,component,resource,amount,censored`, resource `cpu_total_s`.
Arms ending in `+maint` include the teacher's maintenance calls. A task is censored when
not every sealed reply on it was correct.

| file | source path at 8994490 | sha256 of the uncompressed source (first 16 hex) |
|---|---|---|
| `data/g51_comp_total.csv.gz` | `docs/evidence/g51/comp_total.csv` | `d145cb691bc01ec4` |
| `data/g51_unrel_total.csv.gz` | `docs/evidence/g51/unrel_total.csv` | `b02150ebc121a1b5` |
| `data/g53_comp_total.csv.gz` | `docs/evidence/g53/comp_total.csv` | `e568196e49dce095` |
| `data/g53_unrel_total.csv.gz` | `docs/evidence/g53/unrel_total.csv` | `df1f33c183bbee56` |
| `data/g54_comp_total.csv.gz` | `docs/evidence/g54/comp_total.csv` | `6cc7350cc45778ec` |
| `data/g54_unrel_total.csv.gz` | `docs/evidence/g54/unrel_total.csv` | `5d80049c6cd08e84` |
| `data/g56_comp_total.csv.gz` | `docs/evidence/g56/comp_total.csv` | `f1f84d535e8ead1c` |
| `data/g56_unrel_total.csv.gz` | `docs/evidence/g56/unrel_total.csv` | `484826259cdab8ae` |
| `data/g57_comp_total.csv.gz` | `docs/evidence/g57/comp_total.csv` | `aac025f9bf1e332c` |
| `data/g57_unrel_total.csv.gz` | `docs/evidence/g57/unrel_total.csv` | `4357f925c676f911` |
| `data/g57b_comp_total.csv.gz` | `docs/evidence/g57b/comp_total.csv` | `d696472a0d3ba571` |
| `data/g57b_unrel_total.csv.gz` | `docs/evidence/g57b/unrel_total.csv` | `34207dbb50f677a4` |

## Part S run summaries (`data/g57_scale_runs.csv`, `data/g57b_scale_runs.csv`)

One row per (arm, N, seed), extracted without change from `docs/evidence/g57/scale/s*_n*_*.json`
(seeds 221–227, arms Xs/Xi) and `docs/evidence/g57b/scale/s*_n*_*.json` (seeds 231–237, arms
Xs/Xi/Xj): `mean_task_cpu_s`, `amort_task_cpu_s` (G57b only), `known`, `reply_stream_sha256`.

## Documents quoted (not copied)

| document | used for |
|---|---|
| `docs/G51.md` | G51 design, results tables, decision rules L1–L4, maintenance share (65%), trend −0.049/task, misreading correction |
| `docs/G53.md` | G53 profile (scan/search), `--bounded` mechanism and results |
| `docs/G54.md` | `--lean` mechanism, results, rule S (f0 = 25.9 ms, processes, above-floor work, structural share) |
| `docs/G55.md` | the failed registered run (failure preservation) |
| `docs/G56.md` | long-lived protocol, equal-charging decision, primary and secondary contrasts, maintenance share 77% |
| `docs/G57.md` | `--indexed`, results, maintenance 12.46 → 2.72 s, part S design and rule F, reporting rules |
| `docs/G57b.md` | `--incremental`, part S results (§6a), L1/L3 (§6b), comp scan profile (§6c), material and flat rules |
| `docs/LA_EXPORT.md` | how PacketLM maps its logs to the instrument's CSV, cost boundary |
| `docs/RESEARCH_LEDGER.md` | timeline cross-check |
| `VERIFY_cdb4828.md` (branch `verify-cdb4828`) | G51 reproduction; finding G1 (A read as a log ratio) |
| `VERIFY_050bebd.md` (branch `verify-050bebd`) | G53 reproduction; `--bounded` exactness (1,400 sessions) |
| `VERIFY_3e2783c.md` (branch `verify-3e2783c`) | G54 reproduction (13 values); `--lean` not exact in general |
| `VERIFY_d6cbcf3.md` (branch `verify-d6cbcf3`) | G56 reproduction (20 values, 77 hashes); long-lived protocol exactness |
| `VERIFY_35bda6b.md` (branch `verify-35bda6b`) | G57 reproduction (18 contrasts); 47,105-call differential; part S Low 1 |
| `VERIFY_8994490.md` (branch `verify-8994490` @ `9bd3569`) | G57b: no High/Medium; 210,907-call differential, 0 differences; 16/16 contrasts and part S exact; 7-seed part S rerun hash-identical (Xj R1k_16000 2.62 [2.44, 2.83]); Lows 1–3 (partial index-guard coverage; deferred but fail-closed detection; amortized R1k_16000 3.96 → 4.23 if the redundant validation is charged) |

