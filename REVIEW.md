# Review notes (v0.1)

**Who reviewed.** The same AI assistant that drafted the package did this review, in a
separate adversarial pass after the first push. It was told to re-derive every result
and to treat every claim as wrong until checked. This is *not* an independent human
review. A second reviewer who did not write the package is still recommended before
the paper is cited or circulated.

**Scope.** The derivations in `paper/whitepaper.tex`, the bibliography, whether each
claim is backed by evidence, the README, the build (PDF and Markdown), the tests and
the synthetic example.

## What was checked

| Area | Check | Result |
|---|---|---|
| Propositions 1–6, Corollary 1 | Each proof re-derived by hand. Each proposition has at least one numerical test in `tests/` | All hold. Two needed restating (findings R1, R4) |
| Prop. 1(iii) counterexample | Recomputed: prices (1, 0.1) give 0.8, prices (1, 10) give −9.1 | Correct |
| Prop. 4 break-even | Derivative sign δ·c₀(R) + γ·Δ₀ checked; formula tested for five (Δ₀, δ) pairs, including an exact integer ratio | Correct |
| Prop. 5 (FT link) | Discrete layer-cake identity tested on 200 random monotone curves; counterexample tested for a non-monotone curve | Correct, but stated only in discrete time (R4) |
| Delta-method SE, Eq. (6) | Compared with the bootstrap SD at S = 400 | Agrees within 10% |
| Bootstrap coverage | 200 synthetic replications at S = 40 | Coverage ≥ 0.88 for a nominal 95% interval (test threshold) |
| Sign-flip test | Exact values (2/32 at S = 5); behaviour under the null | Correct |
| Synthetic example | Re-run from scratch; outputs are deterministic; the Table 2 numbers match `examples/results/summary.json`; the components sum to Â₁₂ | Correct |
| Citations | Every bib entry checked against Crossref, arXiv or the publisher (see `docs/LITERATURE.md`) | Two metadata fixes (R10) |
| Claims vs evidence | Searched for any PacketLM number or result claim | None. Section 10 is a plan only |
| Build | `latexmk` clean (no undefined references), Markdown regenerated with cross-references resolved from `.aux`, `CITATION.cff` validated with `cffconvert` | Clean |
| Package | Fresh virtualenv, `pip install -e ".[test,figures]"`, `pytest` | 36 passed |

## Findings and fixes

| # | Severity | Finding | Fix |
|---|---|---|---|
| R1 | **Math** | Prop. 1(v), the weighted-average form, assumed c_i(R) > 0 for every i including the setup index. That fails in the most common case, a reference with no setup (c₀(R) = 0) | Restated for the general case: tasks with c_i(R) = 0 enter as −c_i(L)/C_R(n). New test `test_weighted_average_identity_with_zero_reference_setup` |
| R2 | Math / definitions | Def. 3 mixed two stopping rules (anytime with first hit, and self-stopping) in one formula | Split into two declared regimes. Post-task costs are stated explicitly |
| R3 | Notation | Storage was written with a price w_sto indexed by component, while w is indexed by resource | Storage is now defined as a measured resource (byte-seconds) |
| R4 | Math | Prop. 5 was proved for discrete curves, but Continual World defines AUC by integrals | Continuous-time statement (Tonelli) added |
| R5 | Claim | A^nov was called "conservative for the learner" unconditionally. That holds only when c₀(L) ≥ c₀(R) | Qualified |
| R6 | Interpretation | A positive trend β can come from the reference's tasks getting harder while L's absolute cost stays flat, which is not acceleration | Caveat added. β must be read with absolute costs, Π(k) and the order-shuffled control |
| R7 | **Code bug** | `CostLog` treated an (arm, seed) with no records for a task as having zero cost, so missing data silently counted as free learning | Now raises `ValueError`. Test `test_missing_task_records_are_rejected` |
| R8 | Completeness | Defs. 8–9 (novelty-stratified A, probe curve Π(k)) were in the paper but not in the code | Added `novelty_stratified_amortization` and `probe_amortization`, with tests |
| R9 | Rendering | In the Markdown version, display math inside a list item was indented, which GitHub renders as a code block. The escapes `\{`, `\|` and `\#` are fragile on GitHub | The build script strips indentation in display math and rewrites them as `\lbrace`, `\Vert` and a cardinality bar |
| R10 | Citations | ECCV 2018 LNCS volume number not confirmed by any primary record. Publisher fields for Thrun & Pratt and Efron & Tibshirani did not match Crossref | Volume removed; publishers corrected |
| R11 | Claim strength | The related-work text said Díaz-Rodríguez et al. "do not define" cost at matched accuracy, stated more strongly than one reading supports | Softened to "as far as we can tell" |
| R12 | Claim | Corollary 1 said a memoryless reference "has" zero retrieval and maintenance cost | Changed to "typically has" |
| R13 | Consistency | Before the first push: code docstrings cited section and equation numbers that did not match the PDF | Aligned with the `.aux` labels |
| R14 | README accuracy | README said the base arm "hit its budget" on 12 tasks. Some of those were depth-limit exhaustion | Reworded to "censored (budget or depth limit reached)" |

## Left open

1. **No PacketLM evaluation.** This is deliberate. Section 10 is a protocol, and results should be added only from verified artifacts.
2. **The novelty search is not exhaustive.** It covered web searches and the literature cited. An unindexed or very recent use of "learning amortization" cannot be ruled out.
3. **Moderate-confidence related-work details.** The Veniat et al. description (transfer reported alongside model growth) and the ICLR 2022 venue for Dehghani et al. were confirmed only by secondary pages, not the primary PDFs.
4. **GitHub rendering of `whitepaper.md` was not checked visually** in a browser. The PDF is the canonical version. *(Superseded: the independent review below checked it, found every numbered display equation broken, and fixed the generator; see I2.)*
5. **Statistics.** Only percentile bootstrap intervals are implemented. BCa and studentized intervals, and the Wilcoxon alternative, are mentioned but not implemented. With few seeds the intervals are descriptive only.
6. **The synthetic example is tiny** (6 primitives, Z₁₆, depth ≤ 5). It demonstrates the accounting, not any empirical claim.

## Independent review

**Who reviewed.** A separate AI reviewer that did not draft the package, working from a
fresh clone of `main` at `eac64a4`. It is still not a human review. Everything below
was re-run or re-derived, not taken from the notes above.

**What was re-done.**

| Area | What was done | Result |
|---|---|---|
| Definitions 1–9, Propositions 1–6, Corollary 1 | Every statement and proof re-derived by hand, including the Prop. 1(iii) counterexample, the Prop. 4 derivative sign and floor formula, and the discrete and continuous layer-cake identities of Prop. 5 | All propositions hold as stated. One remark attached to Def. 8 was false (I1) |
| Prop. 5 against the source | Continual World Eq. (2) read in the arXiv PDF (2105.10919v3): FT_i = (AUC_i − AUC_i^b)/(1 − AUC_i^b), averaged over tasks without weights | Matches the paper |
| Citations | 26 of 30 entries checked against primary records: 13 DOIs on Crossref (Minton, Tambe et al., DreamCoder, Stitch, Dietterich, Baxter, Hospedales et al., Caruana, Chaudhry et al. 2018, Fikes et al., Green AI, Laird et al., Mitchell et al.), 11 arXiv records (Continual World, GEM, Díaz-Rodríguez et al., A-GEM, Veniat et al., LILO, Hernandez & Brown, Dehghani et al., Chollet, Agarwal et al., MAML), and the PMLR and JMLR pages for Wenliang et al. and Taylor & Stone. The text claims for GEM's FWT, A-GEM's LCA, Hernandez & Brown's AlexNet-level target and Díaz-Rodríguez et al.'s efficiency criteria were checked in the PDFs | Metadata and attributed claims correct |
| Tests | Fresh venv, `pip install -e ".[test,figures]"`, `pytest -q` | 36 passed before changes, 37 after (one new test) |
| Synthetic example | `python examples/synthetic_toy.py` from a clean clone | Reproduced `summary.json` and Table 2 exactly and deterministically before the fix in I3; re-run after it |
| PDF | Clean `latexmk -pdf` from scratch | No errors, no undefined references or citations |
| GitHub rendering | README and `whitepaper.md` rendered with GitHub's Markdown API and viewed as live github.com pages in headless Chrome | README fine; `whitepaper.md` broken (I2) |

**Findings and fixes.**

| # | Severity | Finding | Fix |
|---|---|---|---|
| I1 | **Major (math)** | Def. 8 claimed that keeping both setup costs makes A^nov conservative whenever c₀(L) ≥ c₀(R). That is false. With equal setups and a learner that is worse on the novel tasks (c₀ = 10 for both, novel costs 100 vs 50), A^nov = −0.833 while the setup-free ratio is −1.0, so including the setup flatters the learner. The exact condition is c₀(L)·X_R ≥ c₀(R)·X_L. Fix R5 above had qualified the claim with the wrong condition | Restated with the exact if-and-only-if condition, noting it always holds when c₀(R) = 0 and that c₀(L) ≥ c₀(R) is not sufficient. New test `test_novelty_setup_conservativeness_condition` checks the counterexample, the c₀(R) = 0 case and the condition on 500 random cases |
| I2 | **Major (rendering)** | In `whitepaper.md` on GitHub, every numbered display equation (Eqs. 1–6, including the boxed definition of A_n) rendered as a broken vertical stack, because `\tag` does not work inside `$$` there. GitHub also applies Markdown backslash escapes inside `$$…$$` and `$…$`, so `\,` and `\;` were eaten and showed up as literal `,` and `;` (visible in the corollary and in several integrals) | `scripts/build_markdown.py` now writes display math as ```` ```math ```` fences, which GitHub passes to MathJax verbatim, with the equation number appended as "(n)". It rewrites inline `\,` as `\thinspace`. The GitHub Markdown API output was checked to confirm the TeX now reaches MathJax unchanged |
| I3 | **Major (protocol, code)** | The synthetic library learner decided what to store by checking the **sealed** test inputs (`if sol is not None and correct`). That breaks the paper's own rule that no learner reads E_i (Def. 1, Def. 3, pitfall 2) and contradicted the script's docstring ("committed solutions are stored"). It mattered in one unrelated-curriculum seed | The learner now stores every committed, training-consistent solution. Re-run: compositional results are unchanged. Unrelated results moved slightly: Â₁₂ −2.261 → −2.280 (CI [−2.549, −1.999]), SE 0.147 → 0.144, A⁽⁴⁾ −4.306 → −4.349, β −0.137 → −0.138 [−0.155, −0.120], D_acq −1.993 → −2.010, D_ver −0.140 → −0.141, D_ret −0.091 → −0.092. Paper Table 2, README, `summary.json`, cost CSVs and the figure were regenerated from the run |
| I4 | Minor (accuracy) | Section 9 said the base arm "exceeds its budget on 12 of 240 tasks" and the README said "budget or depth limit". Instrumenting the run showed the budget is never hit: 11 are depth-5 exhaustion and 1 is a committed program that fails the sealed inputs | Paper and README now give the actual breakdown. `summary.json` gains a `censoring_reasons` field so the breakdown can be reproduced from the artifacts. The lower-bound conclusion still holds by Prop. 6 |
| I5 | Minor (overclaim) | The abstract and README said Continual World's FT is "exactly" an amortization ratio, without the non-decreasing-curve condition that Prop. 5 needs (the test suite has a counterexample) | Condition added in both places |
| I6 | Minor (consistency) | §6.2 said the sign-flip test enumerates all 2^S patterns. The code does that only for S ≤ 16 and uses Monte Carlo above that, as Table 2 (S = 20) does. The text also did not say that the test's null (symmetry of per-seed log ratios) is not the same as the ratio-of-means estimand | Both stated |
| I7 | Minor (precision) | Def. 3 called τᵢ a "time", but it is indexed by cost spent | Worded as a stopping point measured in cost |
| I8 | Minor (code docs) | `metric.py` described c_i as cost "until the learner first meets the target", which leaves out the post-task costs that Def. 2 attributes to task i. `CostRecord.censored` was described as budget exhaustion only | Docstrings aligned with Defs. 2–3 and §6.3 |
| I9 | Cosmetic | `{\'\i}` in `refs.bib` rendered as "Dı́az-Rodrı́guez" (dotless i plus a combining accent) in the Markdown | Changed to `{\'i}` |

**Left open.**

1. The `whitepaper.md` fix was checked through GitHub's Markdown API and a local MathJax render, not on the live page before the push. The README already renders correctly on github.com.
2. Not re-checked against primary records: Thrun & Pratt, Chen & Liu, Efron & Tibshirani and Gershman & Goodman (the escholarship page did not load from the review machine), plus the Minton utility formula, which was taken from the paper's description and agrees with standard secondary accounts.
3. Items 1–3, 5 and 6 of the earlier "Left open" list still stand.


## Review of the v0.2 revision (PacketLM case study and Section 11)

**Who reviewed.** The same AI assistant that wrote the revision, in a separate pass after drafting, told to treat every new number and proof as wrong until checked against the PacketLM sources. This is *not* an independent human review; a second reader who did not write it is still recommended.

**Scope.** New Sections 10 (Empirical case study: PacketLM) and 11 (Methodological lessons, formalized), the revised abstract, contributions, pitfalls 10–12, limitations, conclusion and notation; `amortization/diagnostics.py`; `case_study/packetlm/`; the README case-study section.

**Instrument pin.** `git diff 70297af -- amortization/metric.py amortization/stats.py amortization/transfer.py amortization/__main__.py amortization/__init__.py` is empty. New code is only in `amortization/diagnostics.py`, which nothing in the old modules imports. Tag `instrument-v1` (annotated) names `70297af`. The 37 original tests pass unchanged; the suite is now 49 (9 in `test_diagnostics.py`, 3 in `test_case_study.py`).

### Mathematics

| Item | Check | Result |
|---|---|---|
| Remark 2 (cost ratio $1-A$) | Recomputed from the G51 totals in the cost log: 215.77 s / 55.73 s = 3.872, $A=-2.872$, $\ell=-1.354$, $A(\mathrm B\Vert\mathrm C)=0.742$ | Correct |
| Prop. 7 (chain rule) | Proof re-derived (ratios of sums telescope). Checked numerically on random data and on G57b: Cj‖Ci‖Bi‖Bj reproduces $A(\mathrm{Cj}\Vert\mathrm{Bj})$ to machine precision | Correct. Holds for point estimates only, which the text says |
| Prop. 8 (protocol dependence) | Mediant identity, derivative sign $\nu_LW_R-W_L\nu_R$, limits and sign-flip condition re-derived; tested for monotonicity on a grid and for a sign flip | Correct under its stated model ($\nu$, $W$ independent of $f$). The G54→G56 illustration is labelled qualitative because the long-lived engine also changes $W$ and the seeds differ |
| Prop. 9 (partial identification) | Monotonicity in every coordinate plus connectedness of the box gives the interval; infinite bounds handled by limits; special cases recover Prop. 6. Sharpness tested with 500 random interior points | Correct |
| Cor. 2 (tipping point) | Direct algebra | Correct |
| Prop. 10 (irrelevant-state scaling) | (i) termwise bounds $1\le h(K_{i-1})\le h(K_{n-1})$; (ii) an $\varepsilon$–$M$ argument needing only $r_i\ge r_{\min}$ and $\phi_i\ge\phi_{\min}$; (iii) limit of (i). Bounds tested on a simulated sequence; (ii) illustrated with $h\propto\sqrt n$ | Correct under (A1). **The brief asked for a link between *sublinear* $R$ and positive $A$. The provable statement is stronger and less favourable:** with unbounded knowledge growth and an irreducible per-task cost, *bounded* $R$ is necessary, and sublinear-but-unbounded $R$ is not sufficient. The text says so |
| Prop. 11 (exactness) | Follows from Prop. 7 and from $\delta_i$ being a function of replies | Correct. Wording fixed in review: exactness gives *identical* censoring patterns, not necessarily "accuracy-matched" in the sense of Def. 11 (which needs $\delta_i=0$) |

### Claims against sources

Every number in Sections 10–11 was traced to PacketLM `g44-canonical-engine` at `8994490` or to a `VERIFY_*.md` report (table in `case_study/packetlm/SOURCES.md`). `python case_study/packetlm/reproduce.py` recomputes, with the pinned instrument and 5000 resamples, all 42 $A$ values and intervals quoted, the 9 scaling ratios (with PacketLM's registered bootstrap, reproduced verbatim) and 9 derived numbers. Result: **60/60 match.** PacketLM's docs round the instrument's 4-decimal output a second time (e.g. −2.5605 printed as −2.561), so the tolerance is half a unit in the printed place plus 0.00005.

### Corrections made during this review

| # | Finding | Fix |
|---|---|---|
| V1 | The brief gave G57's $R_{16000}$ as 91.2. G57's registered value is **91.9 [86.5, 95.7]** (seeds 221–227); 91.2 [81.6, 100.0] is the G57 engine re-run inside G57b on seeds 231–237 | Table 5 uses the same-seed G57b values (91.2, 17.48); the caption also gives 91.9 |
| V2 | "252 vs 247" holds for G54, G56 and G57b only. G51 is 252 vs 249, G53 252 vs 251, G57 252 vs 246 | All six stated |
| V3 | G57b.md says "0 censored outside F", but its cost logs mark B's 5 unsolved compositional tasks, and 2 unrelated tasks in every arm, as censored. The doc counts run-limit censoring; the CSV uses the target definition the instrument applies | The paper uses the instrument's (target) definition and says why the compositional $A$ values are lower bounds |
| V4 | The engine does not split CPU into the components of Def. 2, so the four-way cost decomposition cannot be computed with Prop. 2 | Presented as a call-type and profile decomposition, with that caveat stated |
| V5 | A draft said C and P "cost the same within noise" on unrelated tasks. Two intervals (G54 −0.015 [−0.032, −0.003]; G57b −0.020 [−0.037, −0.004]) exclude 0 | Now "differ by at most 2.4%"; all six values added to the reproduction script |
| V6 | The original misreading was "e^2.9 ≈ 18×" (G51.md), not e^2.87 | Quoted exactly |
| V7 | A draft said every persistent arm had 0 wrong qualified answers; the guards cover the library learner (C, plus Cb/Cl etc.), not P in every experiment | Restricted to the library learner |
| V8 | hyperref warnings from math in a section title; one overfull line | `\texorpdfstring`; allowed breaks in the script path |

### Claims that could not be sourced

None of the numbers in the paper are unsourced. Two items are *not* independently verified, and the paper says so: G57b has no verification report among the sources (a verification was reported to be running, but no report was available), and the lock times of registered runs are the experimenter's statements (verify-35bda6b, Low 2).

### Build

`latexmk` clean: 0 undefined references, 0 overfull boxes, 0 warnings other than package-info lines; 23 pages (was 14). Markdown regenerated with `scripts/build_markdown.py`, which now maps remark labels and counts tabularx columns.

**Left open.** The controls of Table 1 beyond empty-memory, primitive-only and frozen, and the second-order instruments of Section 5, have not been run on PacketLM. The model assumptions of Props. 8 and 10 are not tested against data beyond the qualitative checks shown.
