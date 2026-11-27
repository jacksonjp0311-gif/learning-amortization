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
4. **GitHub rendering of `whitepaper.md` was not checked visually** in a browser. The PDF is the canonical version.
5. **Statistics.** Only percentile bootstrap intervals are implemented. BCa and studentized intervals, and the Wilcoxon alternative, are mentioned but not implemented. With few seeds the intervals are descriptive only.
6. **The synthetic example is tiny** (6 primitives, Z₁₆, depth ≤ 5). It demonstrates the accounting, not any empirical claim.
