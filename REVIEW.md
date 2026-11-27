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

