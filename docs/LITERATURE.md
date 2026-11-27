# Literature check and citation verification

Checked on 2026-11-26. Each entry in `paper/refs.bib` was checked against a primary
metadata source: the Crossref record for the DOI, the arXiv API record, or the
publisher's or proceedings page. The table shows which source confirmed the title,
authors and year, and what the paper is cited for.

| Key | Work | Verified via | Cited for |
|---|---|---|---|
| thrun1998learning | Thrun & Pratt (eds.), *Learning to Learn*, 1998 | Crossref DOI 10.1007/978-1-4615-5529-2 | Classic learning-to-learn source |
| caruana1997multitask | Caruana, *Multitask Learning*, Mach. Learn. 28(1):41–75, 1997 | Crossref DOI 10.1023/A:1007379606734 | Shared inductive bias |
| baxter2000model | Baxter, *A Model of Inductive Bias Learning*, JAIR 12:149–198, 2000 | Crossref DOI 10.1613/jair.731 | Theory of bias learning |
| hospedales2022meta | Hospedales et al., *Meta-Learning in Neural Networks: A Survey*, TPAMI 44(9):5149–5169, 2022 | Crossref DOI + Edinburgh Research Explorer record | Meta-learning survey |
| finn2017maml | Finn, Abbeel & Levine, MAML, ICML 2017 | arXiv 1703.03400 | Modern meta-learning |
| lopezpaz2017gem | Lopez-Paz & Ranzato, *Gradient Episodic Memory for Continual Learning*, NeurIPS 2017 | arXiv 1706.08840 | BWT/FWT accuracy metrics |
| diazrodriguez2018dont | Díaz-Rodríguez, Lomonaco, Filliat & Maltoni, *Don't forget, there is more than forgetting*, NeurIPS 2018 CL workshop | arXiv 1810.13166 | Resource-aware CL criteria (closest prior art) |
| chaudhry2018rwalk | Chaudhry et al., *Riemannian Walk…*, ECCV 2018, LNCS pp. 556–572 | Crossref DOI 10.1007/978-3-030-01252-6_33 | Intransigence |
| chaudhry2019agem | Chaudhry et al., *Efficient Lifelong Learning with A-GEM*, ICLR 2019 | arXiv 1812.00420 | Learning-curve area (LCA) |
| wolczyk2021continual | Wołczyk et al., *Continual World*, NeurIPS 2021 | arXiv 2105.10919 + NeurIPS paper PDF (FT definition read from Sec. 4.1) | AUC forward transfer; Prop. 5 |
| veniat2021efficient | Veniat, Denoyer & Ranzato, ICLR 2021 | arXiv 2012.12631 | CTrL transfer benchmark |
| chen2018lifelong | Chen & Liu, *Lifelong Machine Learning*, 2nd ed., 2018 | Crossref DOI 10.1007/978-3-031-01581-6 | Lifelong-learning survey |
| taylor2009transfer | Taylor & Stone, JMLR 10(56):1633–1685, 2009 | jmlr.org page | Time-to-threshold, transfer ratio |
| fikes1972learning | Fikes, Hart & Nilsson, AIJ 3:251–288, 1972 | Crossref DOI | Macro-operators (MACROPS) |
| mitchell1986ebg | Mitchell, Keller & Kedar-Cabelli, Mach. Learn. 1(1):47–80, 1986 | Crossref DOI 10.1007/BF00116250 | Explanation-based generalisation |
| laird1986chunking | Laird, Rosenbloom & Newell, Mach. Learn. 1(1):11–46, 1986 | Crossref DOI 10.1007/BF00116249 | Chunking |
| minton1990quantitative | Minton, AIJ 42(2–3):363–391, 1990 | Crossref DOI | Utility problem |
| tambe1990expensive | Tambe, Newell & Rosenbloom, Mach. Learn. 5(3):299–348, 1990 | Crossref DOI 10.1007/BF00117107 | Expensive chunks |
| ellis2021dreamcoder | Ellis et al., *DreamCoder*, PLDI 2021, pp. 835–850 | Crossref DOI 10.1145/3453483.3454080 (+ arXiv 2006.08381) | Library learning |
| bowers2023stitch | Bowers et al., *Top-Down Synthesis for Library Learning*, PACMPL 7(POPL):1182–1213, 2023 | Crossref DOI 10.1145/3571234 | Stitch |
| grand2024lilo | Grand et al., *LILO*, ICLR 2024 | arXiv 2310.19791 | LILO |
| gershman2014amortized | Gershman & Goodman, *Amortized Inference in Probabilistic Reasoning*, CogSci 2014 | eScholarship record | Amortized inference |
| wenliang2020amortised | Wenliang et al., *Amortised Learning by Wake-Sleep*, ICML 2020, PMLR 119:10236–10247 | PMLR page | Name clash with "amortised learning" |
| schwartz2020green | Schwartz et al., *Green AI*, CACM 63(12):54–63, 2020 | Crossref DOI 10.1145/3381831 | Reporting computational cost |
| hernandez2020measuring | Hernandez & Brown, 2020 | arXiv 2005.04305 | Compute to a fixed performance level |
| dehghani2022efficiency | Dehghani et al., *The Efficiency Misnomer*, ICLR 2022 | arXiv 2110.12894 | Cost indicators disagree |
| chollet2019measure | Chollet, *On the Measure of Intelligence*, 2019 | arXiv 1911.01547 | Skill-acquisition efficiency |
| dietterich1998approximate | Dietterich, Neural Comput. 10(7):1895–1923, 1998 | Crossref DOI | Paired tests |
| efron1993bootstrap | Efron & Tibshirani, *An Introduction to the Bootstrap*, 1993 | Crossref DOI 10.1007/978-1-4899-4541-9 | Bootstrap |
| agarwal2021deep | Agarwal et al., *…Statistical Precipice*, NeurIPS 2021 | arXiv 2108.13264 | Reporting with few seeds |

Venues for the arXiv-verified conference papers were confirmed from the arXiv comment field
(MAML: "ICML 2017"; GEM: "Published at NIPS 2017"; A-GEM: "ICLR 2019"; LILO: "ICLR 2024
camera-ready"; Agarwal et al.: "Outstanding Paper Award at NeurIPS 2021"), from the NeurIPS
proceedings PDF (Continual World), from the ICLR 2021 virtual-conference page (Veniat et al.),
from the workshop paper page (Díaz-Rodríguez et al., NeurIPS 2018 Continual Learning workshop)
and from a web search (Dehghani et al., ICLR 2022). Page numbers are given only where a primary
record confirmed them.

## Is "learning amortization" already established?

We searched the web and the literature above for the phrase "learning amortization"
and for metrics combining (a) cost at matched accuracy, (b) a sequence-level savings
ratio and (c) full lifecycle costs. We found no established metric under this name.
Nearby terms mean other things. *Amortized inference* (Gershman & Goodman 2014) and
*amortised learning* (Wenliang et al. 2020) name algorithms that reuse computation,
not cross-task evaluation metrics. The ingredients are well established:

- time-to-threshold and the transfer ratio (Taylor & Stone 2009);
- AUC forward transfer (Wołczyk et al. 2021), which is exactly an amortization ratio
  over training steps (paper, Prop. 5);
- resource-aware continual-learning criteria (Díaz-Rodríguez et al. 2018);
- compute to a fixed performance level (Hernandez & Brown 2020);
- the utility problem of speedup learning (Minton 1990).

The paper therefore presents its contribution as a synthesis and a measurement
protocol. It does not claim a new concept. This search cannot rule out an
unindexed or very recent use of the phrase.
