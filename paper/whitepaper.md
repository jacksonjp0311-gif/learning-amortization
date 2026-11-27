# Learning Amortization: Measuring Whether Learning Makes Future Learning Cheaper

**James Jackson** · Working paper v0.1 · November 2026 · [PDF](whitepaper.pdf) (canonical; this Markdown is generated from the LaTeX source by `scripts/build_markdown.py`)

## Abstract

A learning system that accumulates knowledge is not necessarily a system that gets better at learning. We make the distinction measurable. *Learning amortization* compares the *total* cost a continual learner pays to reach a fixed accuracy target on every task of a sequence with the cost paid by a reference learner on the same sequence: $A_n = 1 - C_{\text{continual}}(n)/C_{\text{reference}}(n)$. Costs are charged over the whole lifecycle of what is learned: acquisition, verification, storage, retrieval, maintenance and execution, plus any one-time setup. We give formal definitions and prove the basic properties of the metric: its range and sign, unit invariance (and the precise sense in which it is *not* invariant), an exact weighted-average form, an additive decomposition into cost components, its asymptotic limit and a closed-form break-even point. We show that the AUC-based forward-transfer metric of Continual World is exactly an amortization ratio whose cost is training steps averaged over all accuracy thresholds, which places the proposal inside existing transfer metrics instead of beside them. We separate first-order amortization (past learning pays for future learning) from second-order evidence of learning to learn (the savings themselves grow with experience), specify paired-seed estimators, confidence intervals, exact tests and censoring bounds, and list the controls and pitfalls that decide whether a positive $A_n$ means anything. A small open-source reference implementation reproduces every quantity, and a clearly labelled synthetic example shows the metric detecting both genuine amortization and the classical “utility problem” in which a growing library makes learning *more* expensive. The motivating application is PacketLM, a non-transformer sparse-binary learner; this paper reports *no* PacketLM results and gives only a planned evaluation protocol.

## 1. Introduction

The central question behind this paper is simple to state: *does a system become better at learning as a consequence of having learned?* Two easier questions are often answered in its place. The first is whether the system knows more after training, which any memory satisfies. The second is whether it is more accurate on a new task straight away (zero-shot forward transfer), which can be bought with an expensive lookup or a large pre-built library whose cost is never charged.

We argue that the right currency for the central question is *cost at matched accuracy*, summed over everything the system has to do to make prior learning usable. Speedup-learning research found decades ago that learned macro-operators, explanation-based rules and chunks can make a problem solver slower, because matching and maintaining a growing store costs more than it saves (Minton 1990; Tambe, Newell, and Rosenbloom 1990). Modern library-learning systems (Ellis et al. 2021; Bowers et al. 2023; Grand et al. 2024) and continual learners face the same trade-off. A metric that ignores storage, retrieval and maintenance can report progress when there is none.

**Contributions.**

This is a measurement paper; it proposes no learning algorithm and makes no empirical claim about any real system.

1.  A **full-lifecycle cost functional** with an explicit accuracy-matching rule (cost-to-target), declared prices and an attribution rule for costs between tasks (Section 3).

2.  The **learning-amortization** family: cumulative $A_n$, marginal $a_i$, asymptotic $A_\infty$ and break-even $n^\star$, with proofs of their properties (Section 4).

3.  An **exact link to forward transfer**: Continual World’s FT metric is an amortization ratio over training steps averaged across accuracy thresholds (Proposition 5).

4.  A separation of **first-order amortization from second-order learning to learn**, via novelty stratification, fork-and-discard probe curves and trend tests (Section 5).

5.  An **estimation and control protocol** with paired seeds, intervals, exact tests and censoring bounds (Sections 6, 7 and 8), and a **reference implementation** with a synthetic worked example (Section 9).

## 2. Related work and novelty assessment

**Learning to learn and meta-learning.**

The idea that experience with earlier tasks should improve learning of later ones is old and well developed. It appears in the edited volume of Thrun and Pratt (1998), in multitask learning (Caruana 1997), in Baxter’s theory of inductive-bias learning (Baxter 2000), and in modern meta-learning (Finn, Abbeel, and Levine 2017; Hospedales et al. 2022). These works mostly measure gains in accuracy or sample efficiency on new tasks; they rarely charge the cost of keeping and consulting what was learned.

**Continual-learning metrics.**

Lopez-Paz and Ranzato (2017) define backward transfer (BWT) and forward transfer (FWT) from an accuracy matrix $R_{j,i}$, the test accuracy on task $i$ after training on task $j$. FWT measures zero-shot accuracy on task $i$ just before it is trained, relative to a random-initialisation baseline. It is an accuracy quantity and carries no cost. Dı́az-Rodrı́guez et al. (2018) add efficiency criteria, including model-size efficiency, sample-storage efficiency and computational efficiency, and combine them with accuracy-based ones in a weighted score. That work is the closest prior art we found for charging resources in continual learning. As far as we can tell, it does not define cost at matched accuracy or a sequence-level savings ratio. Chaudhry et al. (2018) introduce intransigence (inability to learn new tasks), and Chaudhry et al. (2019) introduce the learning-curve area (LCA) as a measure of how quickly a learner acquires new tasks. Wołczyk et al. (2021) measure forward transfer as the normalised area between a continual learner’s training curve and a from-scratch reference; Proposition 5 shows that this is a special case of the ratio studied here. Veniat, Denoyer, and Ranzato (2021) probe several kinds of transfer and report them together with how fast the model grows in size. Chen and Liu (2018) survey lifelong learning more broadly.

**Transfer metrics in reinforcement learning.**

Taylor and Stone (2009) list jumpstart, asymptotic performance, total reward, the transfer ratio and *time to threshold*. Time to threshold is exactly a per-task cost-to-target when cost is measured in samples, and the transfer ratio is an area ratio. Our per-task quantity $a_i$ (Definition 6) generalises time-to-threshold reduction to a multi-component cost.

**Speedup learning and the utility problem.**

Learned macro-operators (Fikes, Hart, and Nilsson 1972), explanation-based generalisation (Mitchell, Keller, and Kedar-Cabelli 1986) and Soar’s chunking (Laird, Rosenbloom, and Newell 1986) all aim to make future problem solving cheaper. Minton (1990) measured the utility of a learned control rule as its average savings times its application frequency minus its average match cost, and showed that unrestricted learning can slow the solver down. Tambe, Newell, and Rosenbloom (1990) traced the same effect to expensive chunks. Our component decomposition (Proposition 2) is the sequence-level analogue of Minton’s utility, extended to storage, maintenance and verification.

**Library learning.**

DreamCoder (Ellis et al. 2021) grows a library of reusable functions and a recognition model that guides search, and reports that solving more tasks makes later tasks easier to solve. Stitch (Bowers et al. 2023) makes library compression far faster, and LILO (Grand et al. 2024) combines LLM-guided synthesis with Stitch compression and automatic documentation. These systems are the natural home for amortization measurements, but their reported metrics are mostly tasks solved and search time under a budget, without a full-lifecycle cost accounting at matched accuracy.

**Amortized inference and “amortised learning”.**

In probabilistic inference, amortization means reusing past computation so that future inferences are cheaper. Gershman and Goodman (2014) argue that people cache and reuse sub-inferences. Wenliang et al. (2020) use the name *amortised learning* for a wake-sleep method that learns to predict maximum-likelihood parameter updates. These usages are close in spirit, since earlier computation pays for later computation, but they name algorithms, not a cross-task evaluation metric. To avoid confusion, we always say *learning amortization* and always mean the metric $A_n$.

**Efficiency accounting.**

Schwartz et al. (2020) argue for reporting the computational price of results. Hernandez and Brown (2020) measure algorithmic progress as the training compute needed to reach a *fixed* performance level (AlexNet-level ImageNet accuracy), which is the same cost-at-matched-accuracy principle we use. Dehghani et al. (2022) show that different cost indicators (FLOPs, parameters, throughput) can rank models differently, which motivates our per-resource reporting rule (Proposition 1(iii)). Chollet (2019) defines intelligence as skill-acquisition efficiency relative to priors and experience. $A_n$ is a much narrower, operational quantity, but it shares the view that efficiency of acquisition, not skill alone, is what should be measured.

**Novelty assessment.**

We searched for the phrase “learning amortization” and for metrics that combine cost-at-matched-accuracy, a sequence-level savings ratio and full lifecycle costs. We found no established metric under this name. The ingredients are not new: time-to-threshold (Taylor and Stone 2009), area-based forward transfer (Wołczyk et al. 2021), resource-aware continual-learning criteria (Dı́az-Rodrı́guez et al. 2018), compute to a fixed performance level (Hernandez and Brown 2020), and the utility analysis of speedup learning (Minton 1990). Our contribution is therefore a *synthesis and a protocol*. It has one definition that charges every lifecycle cost at matched accuracy, proofs of the properties needed to interpret it, an exact reduction showing how an established forward-transfer metric fits inside it, and a control and statistics protocol aimed at separating learning to learn from accumulation. We make no stronger novelty claim.

## 3. Formal setup

<div id="def:protocol" class="definition">

**Definition 1** (Task sequence and protocol). A seed $s$ determines, through a fixed generator, a task sequence $\mathcal{T}^{(s)} = (T_1,\dots,T_N)$. Each task $T_i$ provides an interaction source (examples, teaching turns, oracle queries) and a *sealed* evaluation set $E_i$ that no learner reads. A learner $L$ has a state $M$ (memory, library, parameters). A *continual* learner starts task $i$ from the state $M_{i-1}$ left by task $i-1$, starting from an initial state $M_0$. A *reference* learner $R$ runs on the same $\mathcal{T}^{(s)}$ under a protocol specified in Section 7; the default reference resets its state to $M_0$ before every task.

</div>

<div id="def:cost" class="definition">

**Definition 2** (Cost functional). Let $\mathcal{K}= \lbrace \mathrm{acq},\mathrm{ver},\mathrm{sto},\mathrm{ret},\mathrm{mnt},\mathrm{exe}\rbrace$ be the cost components and $\mathcal{R}$ a finite set of measured resources (e.g. primitive operations, CPU-seconds, byte-seconds of storage, oracle queries, teacher turns). For task index $i\in\lbrace 0,\dots,N\rbrace$, component $k$ and resource $r$, let $q_{i,k,r}\ge 0$ be the measured amount. Index $i=0$ collects one-time costs paid before $T_1$. Given a price vector $w\in\mathbb{R}_{\ge 0}^{\mathcal{R}}$ *declared before the experiment*,

$$
\tag{1}
c_{i,k} = \sum_{r\in\mathcal{R}} w_r\, q_{i,k,r}, \qquad c_i = \sum_{k\in\mathcal{K}} c_{i,k}.
$$

*Attribution rule.* Every cost incurred from the moment the learner is ready to accept $T_i$ until the moment it is ready to accept $T_{i+1}$ is charged to $i$; costs before $T_1$ are charged to $0$. Thus post-task consolidation, deduplication and checkpointing are charged to the task that triggered them. Experimenter-side evaluation on $E_i$ is not charged. The learner’s own execution to produce answers for $E_i$ is charged as $c_{i,\mathrm{exe}}$.

</div>

The components have the following meanings. *Acquisition* covers search, candidate generation, parameter updates and interaction with the teacher or oracle. *Verification* covers checking candidates against evidence, consistency checks and re-verification after corrections or retractions. *Storage* is the holding cost of the state, measured in a resource such as byte-seconds, $\int |M(t)|\,dt$ over the task’s interval, so a library that is never used still costs something. *Retrieval* covers indexing, lookup and matching of stored items, which is Minton’s match cost. *Maintenance* covers consolidation, compression, deduplication, dependency propagation, invalidation and checkpoint I/O. *Execution* is running the acquired capability.

<div id="def:ctt" class="definition">

**Definition 3** (Cost-to-target). Fix, before the experiment, an accuracy target $\alpha_i\in(0,1]$ and a budget $B_i>0$ for every task. Let $\mathrm{acc}_i(L,t)$ be the accuracy on $E_i$ of the hypothesis $L$ has committed to after spending cost $t$ on $T_i$. The learning phase of $T_i$ ends at a time $\tau_i(L)$ defined in one of two ways, declared in advance:

- *anytime learners*: $\tau_i(L) = \min\bigl(B_i,\ \inf\lbrace t\ge 0: \mathrm{acc}_i(L,t)\ge \alpha_i\rbrace \bigr)$, where the experimenter evaluates checkpoints on $E_i$ without feeding any result back to the learner;

- *self-stopping learners*: $\tau_i(L)=\min(B_i,\sigma_i)$, where $\sigma_i$ is the moment the learner commits by its own criterion.

$c_i(L)$ is the total cost charged to $i$ by Definition 2: the cost up to $\tau_i$ plus the post-task costs (consolidation, maintenance, execution on $E_i$) the attribution rule assigns to $i$. The censoring indicator is $\delta_i(L)=\mathbf{1}[\mathrm{acc}_i(L,\tau_i)<\alpha_i]$.

</div>

<div class="remark">

*Remark 1* (Accuracy matching). A task’s cost counts as *matched* for an arm only if $\delta_i=0$. Cost-to-target makes accuracies comparable by construction. The alternative, a fixed budget with an equivalence test on accuracy (e.g. two one-sided tests with a declared margin), is also valid but must be declared in advance. Comparing costs at different accuracies is not valid.

</div>

<div id="def:cum" class="definition">

**Definition 4** (Cumulative cost). $C_L(n) = \sum_{i=0}^{n} c_i(L)$ for $n=0,\dots,N$.

</div>

<div id="def:A" class="definition">

**Definition 5** (Learning amortization). For a learner $L$, a reference $R$ and a horizon $1\le n\le N$ with $C_R(n)>0$,

$$
\tag{2}
\boxed{\;A_n(L\,\Vert \,R) \;=\; 1-\frac{C_L(n)}{C_R(n)}\;}
$$

We write $A_n$ when $L$ and $R$ are clear from context. $A_n>0$ means $L$ paid less than $R$ in total to reach the same targets on the first $n$ tasks.

</div>

<div id="def:marg" class="definition">

**Definition 6** (Marginal and asymptotic amortization). For $i\ge 1$ with $c_i(R)>0$, the marginal amortization is $a_i = 1 - c_i(L)/c_i(R)$, and we set $a_0 = 1-c_0(L)/c_0(R)$ when $c_0(R)>0$. The asymptotic amortization is $A_\infty = \lim_{n\to\infty} A_n$ when the limit exists. The tail-window estimator with window $k$ is

$$
A^{(k)}_N = 1-\frac{\sum_{i=N-k+1}^{N} c_i(L)}{\sum_{i=N-k+1}^{N} c_i(R)}.
$$

</div>

<div id="def:be" class="definition">

**Definition 7** (Break-even point). $n^\star = \min\lbrace n\in\lbrace 1,\dots,N\rbrace : A_m>0 \text{ for all } m\in\lbrace n,\dots,N\rbrace \rbrace$, and $n^\star$ is undefined if $A_N\le 0$. Requiring positivity on the rest of the horizon prevents a temporary crossing from being reported as break-even.

</div>

## 4. Properties

All proofs are short and given inline. Each property has an executable check in `tests/`.

<div id="prop:basic" class="proposition">

**Proposition 1** (Basic properties). Let $C_R(n)>0$.

(i) *Range and sign.* $A_n\le 1$, with equality if and only if $C_L(n)=0$, and $A_n$ is unbounded below. $A_n>0$, $=0$ or $<0$ according as $C_L(n)<$, $=$ or $>C_R(n)$.

(ii) *Unit invariance.* Replacing $w$ by $\lambda w$ for any $\lambda>0$ leaves $A_n$ unchanged. In particular, with a single resource, $A_n$ does not depend on the unit.

(iii) *No invariance to relative prices.* With two or more resources, changing the *relative* prices can change the sign of $A_n$. Results must therefore be reported per resource as well as for the declared $w$.

(iv) *Log form and asymmetry.* With $\ell_n = \log C_R(n) - \log C_L(n)$ (for $C_L(n)>0$), $A_n = 1-e^{-\ell_n}$. Moreover $\ell_n(R\Vert L)=-\ell_n(L\Vert R)$, whereas $A_n(R\Vert L) = -A_n(L\Vert R)/(1-A_n(L\Vert R))$.

(v) *Weighted average.* Let $P=\lbrace i\le n: c_i(R)>0\rbrace$ and $Z=\lbrace i\le n: c_i(R)=0\rbrace$. Then

$$
\tag{3}
A_n = \sum_{i\in P}\omega_i\, a_i \;-\; \sum_{i\in Z}\frac{c_i(L)}{C_R(n)},\qquad \omega_i = \frac{c_i(R)}{C_R(n)},\quad \sum_{i\in P}\omega_i = 1 .
$$

In the common case $c_0(R)=0$ (a reference with no setup), the learner’s whole setup cost enters through the second sum as a pure penalty. If $Z=\varnothing$, then $A_n$ is exactly the $\omega$-weighted mean of the marginal amortizations.

</div>

<div class="proof">

*Proof.* (i) Costs are non-negative, so $C_L(n)/C_R(n)\ge 0$, and the ratio is $0$ only when $C_L(n)=0$. Letting $C_L(n)\to\infty$ shows that $A_n$ is unbounded below. The sign statement follows by rearranging the definition. (ii) Both cumulative costs are linear in $w$ by (1), so the common factor $\lambda$ cancels. (iii) Consider one task, $c_0=0$ and two resources (operations and memory). Let $L$ use $(1,10)$ and $R$ use $(10,0)$. With prices $(1,0.1)$, $A_1 = 1-2/10 = 0.8$. With prices $(1,10)$, $A_1 = 1-101/10 = -9.1$. (iv) $C_L/C_R = e^{-\ell_n}$. Swapping the arms gives $1-C_R/C_L = 1-1/(1-A_n)$. (v) $1-\frac{C_L(n)}{C_R(n)} = \sum_{i\le n} \frac{c_i(R)-c_i(L)}{C_R(n)}$. For $i\in P$ the summand equals $\frac{c_i(R)}{C_R(n)}\bigl(1-\frac{c_i(L)}{c_i(R)}\bigr)=\omega_i a_i$, and for $i\in Z$ it equals $-c_i(L)/C_R(n)$. Finally $\sum_{i\in P}c_i(R)=C_R(n)$. ◻

</div>

Item (v) shows that cumulative amortization weights each task by its *reference* cost, so hard tasks dominate. This is deliberate, because it reports savings in the currency actually spent. An unweighted mean of $a_i$, as used for FT by Wołczyk et al. (2021), answers a different question and should be labelled as such. Because of (iv), averages of $A$ across seeds should be taken on the $\ell$ scale or as ratios of sums, never as unweighted arithmetic means of per-seed $A$ values.

<div id="prop:decomp" class="proposition">

**Proposition 2** (Component decomposition). Write $C_{L,k}(n)=\sum_{i\le n}c_{i,k}(L)$ and similarly for $R$. Then

$$
\tag{4}
A_n = \sum_{k\in\mathcal{K}} D_{n,k},\qquad D_{n,k} = \frac{C_{R,k}(n)-C_{L,k}(n)}{C_R(n)} .
$$

</div>

<div class="proof">

*Proof.* $C_R(n)-C_L(n) = \sum_k \bigl(C_{R,k}(n)-C_{L,k}(n)\bigr)$. Divide by $C_R(n)$. ◻

</div>

<div id="cor:utility" class="corollary">

**Corollary 1** (Utility condition). Partition $\mathcal{K}$ into components on which $L$ saves ($D_{n,k}\ge 0$) and overheads ($D_{n,k}<0$). Then $A_n>0$ if and only if the total savings exceed the total overheads:

$$
\sum_{k: D_{n,k}\ge 0}\bigl(C_{R,k}-C_{L,k}\bigr) \;>\; \sum_{k: D_{n,k}<0}\bigl(C_{L,k}-C_{R,k}\bigr).
$$

A memoryless reference typically has $C_{R,\mathrm{ret}}=C_{R,\mathrm{mnt}}=0$, so for a library learner retrieval and maintenance enter only as overheads. This is Minton’s utility problem (Minton 1990) at the scale of a whole sequence.

</div>

<div id="prop:asym" class="proposition">

**Proposition 3** (Asymptotic limit). Suppose $c_0(L),c_0(R)<\infty$ and the per-task averages converge: $\frac1n\sum_{i=1}^n c_i(L)\to\gamma_L$ and $\frac1n\sum_{i=1}^n c_i(R)\to\gamma_R>0$. Then

$$
A_\infty = \lim_{n\to\infty}A_n = 1-\frac{\gamma_L}{\gamma_R}.
$$

</div>

<div class="proof">

*Proof.* $\frac{C_L(n)}{C_R(n)} = \frac{c_0(L)/n + \frac1n\sum_{i=1}^n c_i(L)}{c_0(R)/n+\frac1n\sum_{i=1}^n c_i(R)}\to\frac{\gamma_L}{\gamma_R}$, since the denominator tends to $\gamma_R>0$. ◻

</div>

One-time costs vanish from $A_\infty$. A system with an enormous pre-built library can therefore look excellent asymptotically while never repaying its setup within any realistic horizon. $A_\infty$ or $A^{(k)}_N$ must always be reported together with $A_N$ at the actual horizon and with $n^\star$.

<div id="prop:be" class="proposition">

**Proposition 4** (Break-even under constant costs). Let $c_0(L)=c_0(R)+\Delta_0$ with $c_0(R)\ge 0$ and $c_0(L)\ge 0$, and for $i\ge1$ let $c_i(R)=\gamma>0$ and $c_i(L)=\gamma-\delta$ with $0<\delta\le\gamma$. Then

$$
A_n = \frac{n\delta-\Delta_0}{c_0(R)+n\gamma},
$$

which is non-decreasing in $n$ when $\Delta_0\ge 0$ and tends to $\delta/\gamma$. Consequently $n^\star = \lfloor \Delta_0/\delta\rfloor+1$ if $\Delta_0\ge 0$ and $n^\star=1$ if $\Delta_0<0$ (for $N\ge n^\star$).

</div>

<div class="proof">

*Proof.* $1-\frac{c_0(R)+\Delta_0+n(\gamma-\delta)}{c_0(R)+n\gamma} = \frac{n\delta-\Delta_0}{c_0(R)+n\gamma}$. Its derivative in $n$ has the sign of $\delta c_0(R)+\gamma\Delta_0$, which is $\ge 0$ when $\Delta_0\ge0$. So when $\Delta_0\ge 0$, $A_n>0$ exactly when $n>\Delta_0/\delta$ and positivity then persists, giving the first integer above $\Delta_0/\delta$. When $\Delta_0<0$ the numerator is positive for all $n\ge1$. ◻

</div>

### 4.1 Relation to forward transfer

Let a learning curve on a task be $p_0,\dots,p_{D-1}\in[0,1]$, the performance after $k$ units of training cost, with budget $D$. Define the first-hit cost $t(\alpha)=\min\lbrace k: p_k\ge\alpha\rbrace$ (or $D$ if the target is never reached), the normalised area $\mathrm{AUC}=\frac1D\sum_k p_k$, and

$$
I(p) = \int_0^1 \min\bigl(t(\alpha),D\bigr)\,d\alpha ,
$$

the cost-to-target averaged uniformly over all targets $\alpha$ and censored at the budget.

<div id="prop:ft" class="proposition">

**Proposition 5** (Forward transfer is an amortization ratio). If $p$ is non-decreasing, then (i) $\mathrm{AUC} = 1 - I(p)/D$. Hence (ii), for non-decreasing $p$ (continual) and $p^b$ (reference) with $\mathrm{AUC}^b<1$, the Continual World forward transfer (Wołczyk et al. 2021) satisfies

$$
\mathrm{FT} = \frac{\mathrm{AUC}-\mathrm{AUC}^b}{1-\mathrm{AUC}^b} = 1-\frac{I(p)}{I(p^b)} .
$$

</div>

<div class="proof">

*Proof.* (i) $p_k = \int_0^1 \mathbf{1}[p_k\ge\alpha]\,d\alpha$, so $\sum_k p_k = \int_0^1 \bigl|\lbrace k: p_k\ge\alpha\rbrace \bigr|\,d\alpha$. For a non-decreasing curve, $\lbrace k:p_k\ge\alpha\rbrace =\lbrace t(\alpha),\dots,D-1\rbrace$, which has $D-\min(t(\alpha),D)$ elements. Dividing by $D$ gives the claim. (ii) By (i), $\mathrm{AUC}-\mathrm{AUC}^b = (I(p^b)-I(p))/D$ and $1-\mathrm{AUC}^b = I(p^b)/D>0$. ◻

</div>

The same proof works in continuous time, which is the form used by Wołczyk et al. (2021). For a non-decreasing $p:[0,\Delta]\to[0,1]$, Tonelli’s theorem gives $\int_0^\Delta p(t)\,dt=\int_0^1 \bigl(\Delta-\min(t(\alpha),\Delta)\bigr)\,d\alpha$ with $t(\alpha)=\inf\lbrace t:p(t)\ge\alpha\rbrace$. FT is thus learning amortization for a single task in which cost is training steps only, the target is averaged over $[0,1]$ instead of fixed, costs are censored at the budget, and tasks are then averaged without weights. $A_n$ keeps the ratio form but fixes a declared target, charges every lifecycle component and aggregates by cost. For curves that rise and then collapse, AUC and $I$ disagree. The test suite includes a counterexample, so monotonicity (or a running maximum) must be stated whenever this correspondence is used. By contrast, GEM’s FWT (Lopez-Paz and Ranzato 2017) is a zero-shot accuracy difference. Positive FWT is neither necessary nor sufficient for $A_n>0$: a learner can be accurate zero-shot only through an expensive retrieval, or have zero zero-shot accuracy and still learn each new task cheaply.

## 5. First-order amortization versus learning to learn

### 5.1 Two different claims

$A_n>0$ is a *first-order* claim: what was learned earlier pays for part of what is learned later. That can happen without the learning process improving at all, for example when later tasks repeat earlier ones and the learner retrieves stored answers. The stronger, *second-order* claim is that the learner’s capacity to acquire genuinely new capabilities grows with experience. The three instruments below target the second claim.

<div id="def:novel" class="definition">

**Definition 8** (Novelty-stratified amortization). Before running, the generator labels each task *novel* or *familiar* by a criterion that does not depend on outcomes. A task is novel, for instance, if its solution is not equivalent to any solution of an earlier task and it uses relations or entities withheld from earlier tasks. With $\mathcal{N}$ the novel tasks among the first $n$,

$$
A_n^{\mathrm{nov}} = 1-\frac{c_0(L)+\sum_{i\in\mathcal{N}}c_i(L)}{c_0(R)+\sum_{i\in\mathcal{N}}c_i(R)}.
$$

Both arms’ full setup costs are kept. When $c_0(L)\ge c_0(R)$, the usual case for a learner that ships with or builds a library, this charges the whole extra setup to the novel tasks and is conservative for the learner.

</div>

<div id="def:probe" class="definition">

**Definition 9** (Fork-and-discard probe curve). Fix sealed probe tasks $P_1,\dots,P_m$ that never enter any learner’s state. After task $k$ of the sequence, copy the state $M_k$, solve each probe from the copy, record the cost-to-target $c_{P_j}(M_k)$, then discard the copy. The probe amortization is

$$
\Pi(k) = 1-\frac{\sum_j c_{P_j}(M_k)}{\sum_j c_{P_j}(M_0)} .
$$

</div>

Because the probes are discarded, $\Pi(k)$ measures how cheap *new* learning has become at stage $k$ without contaminating the sequence. Evidence for learning to learn is a $\Pi(k)$ that rises with $k$ on probes that are novel by the criterion of Definition 8.

### 5.2 Trend test

Let $\ell_{s,i} = \log c_i^{(s)}(R)-\log c_i^{(s)}(L)$ be the per-task log ratio in seed $s$, and $\bar\ell_i$ its mean over seeds. The trend $\beta$ is the ordinary least-squares slope of $\bar\ell_i$ on $i$, with a bootstrap interval obtained by resampling seeds. A positive $\beta$ means the per-task savings grow along the sequence, which is the signature of compounding. $\beta\approx 0$ with $A_n>0$ means a fixed advantage, for example a useful initial library. $\beta$ measures growth in *relative* savings. If later tasks are harder for the reference while $L$’s absolute cost stays flat, $\beta>0$ even though $L$’s learning has not accelerated in absolute terms. $\beta$ must therefore be read alongside absolute per-task costs, $\Pi(k)$ and the order-shuffled control.

## 6. Estimation and inference

### 6.1 Design

Run $S$ independent seeds. Within a seed, every arm sees the same task sequence, the same splits and the same sealed sets, which makes the design *paired*. Let $X_s = C_L^{(s)}(n)$ and $Y_s = C_R^{(s)}(n)$. Before running, fix and record the following: $\alpha_i$, $B_i$, $w$, the generator, $S$, $n$, the novelty criterion, the primary comparison and the analysis code version. Where possible, use deterministic operation counts as the primary cost, and wall-clock time on pinned cores, with repetitions, as a secondary cost.

### 6.2 Estimators, intervals and tests

The population quantity is $A_n = 1-\mathbb{E}X/\mathbb{E}Y$, the savings on the total spent by a population of runs. Its plug-in estimator is the ratio of means,

$$
\tag{5}
\hat A_n = 1-\frac{\sum_s X_s}{\sum_s Y_s},
$$

which is consistent by the strong law of large numbers and continuity of $(x,y)\mapsto 1-x/y$ at $(\mathbb{E}X,\mathbb{E}Y)$ with $\mathbb{E}Y>0$. The mean of per-seed $A$ values estimates a different quantity, $1-\mathbb{E}[X/Y]$, and is distorted by the asymmetry noted in Proposition 1(iv). We do not use it. As a robustness check we also report the geometric form $1-\exp(-\bar\ell)$ with $\bar\ell = \frac1S\sum_s \ell_s$ and $\ell_s=\log Y_s-\log X_s$.

*Delta-method standard error.* With $\hat\rho = \bar X/\bar Y$ and residuals $d_s = X_s-\hat\rho Y_s$ (which sum to zero),

$$
\tag{6}
\widehat{\mathrm{SE}}(\hat A_n) = \frac{1}{\bar Y}\sqrt{\frac{1}{S(S-1)}\sum_{s=1}^S d_s^2 } .
$$

*Paired bootstrap.* Resample whole seeds with replacement, using the same indices for both arms, recompute (5), and report percentile intervals (Efron and Tibshirani 1993). For small $S$, treat intervals as descriptive and report every per-seed value, following Agarwal et al. (2021).

*Exact test.* Under $H_0$, the distribution of $\ell_s$ is symmetric about $0$ (no amortization). The sign-flip permutation test uses $|\bar\ell|$ and enumerates all $2^S$ sign patterns. The smallest attainable two-sided $p$-value is $2/2^S$, so $S\ge 6$ seeds are needed before $p<0.05$ is even possible. The Wilcoxon signed-rank test on $\ell_s$ is an alternative. Across several controls, correct for multiplicity (e.g. Holm). On paired designs and the dangers of naive $t$-tests over resampled splits, see Dietterich (1998).

### 6.3 Censoring

A censored task (Definition 3) is recorded at the cost actually spent: the budget, or the stopping cost of a committed hypothesis that missed the target. Reaching the target in the same run would have required at least that much, so the recorded cost is a *lower* bound on the true cost-to-target.

<div id="prop:cens" class="proposition">

**Proposition 6** (Censoring bounds). Let $\tilde C_L,\tilde C_R$ be the recorded and $C_L\ge\tilde C_L$, $C_R\ge\tilde C_R$ the true cumulative costs. If only $L$ has censored tasks ($C_R=\tilde C_R$), the recorded $\tilde A_n$ is an *upper* bound on $A_n$ (optimistic). If only $R$ has censored tasks, $\tilde A_n$ is a *lower* bound (pessimistic). If both do, the direction is undetermined.

</div>

<div class="proof">

*Proof.* $A_n$ is decreasing in $C_L$ and increasing in $C_R$ for $C_R>0$. ◻

</div>

Censoring counts per arm must be reported. Dropping censored tasks from the analysis is selection on the outcome, and is not allowed.

## 7. Required controls

Each control is a reference $R$ in $A_n(L\Vert R)$ and answers one question. Table 1 lists them.

<div id="tab:controls">

| Control            | What changes                                                                  | What $A_n(L\Vert \text{control})>0$ shows                                           |
|:-------------------|:------------------------------------------------------------------------------|:------------------------------------------------------------------------------------|
| Empty-memory       | State reset to $M_0$ before every task                                        | Carried-over state pays for itself (default reference)                              |
| Frozen             | State frozen after a warm-up of $w_0$ tasks                                   | Continued learning helps beyond the initial library (evaluate on tasks after $w_0$) |
| Primitive-only     | Acquired procedures disabled; facts kept                                      | Reuse of *procedures*, not only stored facts, drives savings                        |
| Shuffled-evidence  | Same volume of experience with evidence–label pairing permuted                | Savings depend on the *content* of experience, not its volume or caching artefacts  |
| Symbolic reference | Efficient indexed symbolic implementation of the same tasks                   | $L$ is competitive in absolute terms, not only against itself                       |
| Geometry-disabled  | Geometric activation and pruning replaced by exhaustive or indexed operations | Savings are attributable to the geometric (Bitwork) mechanism                       |
| Order-shuffled     | Same tasks, randomised order                                                  | Savings are not an artefact of a hand-ordered curriculum                            |
| Exact-repeat cache | Pure memoisation of identical tasks                                           | Upper bound on what caching alone achieves; $L$ must beat it on novel tasks         |

Controls. The first six come from the PacketLM qualification plan; the last two are additions recommended here. All arms run the same frozen engine source, identified by its hash.

</div>

## 8. Pitfalls

1.  **Cached results mistaken for capability.** Overlapping or repeated tasks give large $A_n$ through retrieval alone. *Mitigation:* use $A_n^{\mathrm{nov}}$, $\Pi(k)$ and the exact-repeat cache control.

2.  **Leakage.** Sealed sets read by the learner, probes written into its state, or a library seeded from evaluation material all invalidate the result. *Mitigation:* hash the sealed sets, use fork-and-discard probes, and log the provenance of every stored item.

3.  **Post-hoc thresholds and prices.** Choosing $\alpha$, $B$ or $w$ after seeing results can manufacture a positive $A_n$. *Mitigation:* pre-register them and report the curve $\alpha\mapsto A_n(\alpha)$ and the per-resource results as sensitivity analyses.

4.  **Unpriced costs.** Omitting storage, retrieval, maintenance, verification or setup hides the utility problem (Corollary 1). Teacher effort in interactive teaching is a resource and must be counted, for example as teacher turns.

5.  **Developer improvements counted as learning.** Changing engine code between tasks moves cost from the learner to the developer. *Mitigation:* freeze the engine source and run all arms on the same hash.

6.  **Weak references.** A deliberately slow baseline inflates $A_n$. *Mitigation:* include the symbolic reference and report absolute costs.

7.  **Description length mistaken for cost.** A shorter program is not necessarily cheaper to find, verify or run. Measure operations.

8.  **Aggregation errors.** Averaging $A$ values across seeds, or mixing weighted and unweighted task averages, changes the estimand (Proposition 1(iv)–(v)).

9.  **Dropping failures.** Removing censored tasks or failed seeds is selection on the outcome (Proposition 6).

## 9. Reference implementation and a synthetic worked example

The package `amortization/` implements every quantity above. It includes cost logs with declared prices (Definition 2), $A_n$, $a_i$, $A^{(k)}_N$, $n^\star$, the decomposition (4), the estimator (5), the standard error (6), the paired bootstrap, the exact sign-flip test, the trend $\beta$, $A_n^{\mathrm{nov}}$, $\Pi(k)$, and the functions used to check Proposition 5. Each proposition has a test.

**The example is synthetic.**

The following numbers come from a toy program-search world written for this paper. They say nothing about PacketLM or any other real system. Inputs are $\mathbb{Z}_{16}$ and there are six fixed primitive maps. Each task is a hidden map given by 10 training pairs, with 6 sealed test inputs. A learner enumerates compositions breadth-first up to depth 5, commits to the first one consistent with the training pairs, and succeeds if it is exactly correct on the sealed inputs ($\alpha=1$). The *base* arm is empty-memory. The *library* arm stores each correct solution and offers it as an extra building block on later tasks, a much simplified version of DreamCoder’s library. Costs are counted operations, not simulated. Acquisition is one operation per computed output, verification is one per training comparison, retrieval is one per library fetch, storage is $0.01$ per stored cell per task, maintenance is one per cell compared during deduplication, and execution is one per sealed input. In the *compositional* curriculum, each target composes two earlier targets or primitives, so reuse is possible. In the *unrelated* curriculum, targets are independent depth-3 compositions of primitives. We used $S=20$ seeds, $N=12$ tasks and $10^4$ bootstrap resamples. The run takes about three seconds and is reproduced by `python examples/synthetic_toy.py`.

<div id="tab:toy">

|                                                              |                   Compositional |                       Unrelated |
|:-------------------------------------------------------------|--------------------------------:|--------------------------------:|
| $\hat A_{12}$ (ratio of means)                               |                         $0.917$ |                        $-2.261$ |
| 95% paired bootstrap CI                                      |               $[0.869,\ 0.941]$ |             $[-2.539,\ -1.975]$ |
| Delta-method SE                                              |                         $0.017$ |                         $0.147$ |
| Sign-flip $p$ ($10^5$ Monte Carlo draws)                     |                      $<10^{-4}$ |                      $<10^{-4}$ |
| Tail window $A^{(4)}_{12}$ (seed-mean costs)                 |                         $0.933$ |                        $-4.306$ |
| Break-even $n^\star$ (seed-mean costs)                       |                             $2$ |                            none |
| Trend $\beta$ \[95% CI\]                                     |         $0.147\ [0.103, 0.193]$ |       $-0.137\ [-0.154,-0.119]$ |
| Censored tasks, base / library (of 240)                      |                      $12$ / $0$ |                       $1$ / $1$ |
| $D_{\mathrm{acq}}$ / $D_{\mathrm{ver}}$                      |               $0.847$ / $0.078$ |             $-1.993$ / $-0.140$ |
| $D_{\mathrm{ret}}$ / $D_{\mathrm{mnt}}$ / $D_{\mathrm{sto}}$ | $-0.002$ / $-0.005$ / $-0.0001$ | $-0.091$ / $-0.037$ / $-0.0004$ |

SYNTHETIC toy example (not PacketLM). The component contributions $D_k$ (Proposition 2) are computed on seed-mean costs and sum exactly to $\hat A_{12}$ (a ratio of means equals a ratio of seed-mean costs). Execution contributes $0$ in both curricula.

</div>

<figure id="fig:toy">
<img src="figures/synthetic_curve.png" />
<figcaption>SYNTHETIC. <span class="math inline"><em>A</em><sub><em>n</em></sub></span> on seed-mean costs for the two curricula. The same library mechanism amortizes strongly when tasks compose and is strongly <em>negative</em> when they do not.</figcaption>
</figure>

**Reading the example.**

In the compositional curriculum, $A_{12}$ is large and the trend is positive. The decomposition shows that the savings are almost entirely in acquisition, with small overheads from retrieval, maintenance and storage. The base arm exceeds its budget on 12 of 240 tasks, so by Proposition 6 the reported $\hat A_{12}$ is a lower bound. In the unrelated curriculum the library cannot help, because every stored entry enlarges the branching factor. $A_{12}$ is about $-2.3$, the trend is negative, and break-even never occurs. This is a minimal instance of the utility problem (Corollary 1). The example also illustrates Section 5. A positive $\beta$ here comes from tasks that are built to reuse earlier solutions, which is first-order reuse. On its own it would not establish learning to learn without novel probes.

## 10. Planned evaluation on PacketLM

PacketLM (<https://github.com/jacksonjp0311-gif/PacketLM>) is a non-transformer learner built on sparse binary (“Bitwork”) representations, with persistent memory, acquired constructions and acquired relational procedures. **No PacketLM result is reported here.** The planned protocol follows its G46–G48 qualification plan and has five parts.

1.  *Instrumentation.* Count candidate evaluations, primitive bit operations, bytes held, retrieval probes, retraction and dependency propagation steps, checkpoint I/O and teacher turns. Map each count to a component of $\mathcal{K}$.

2.  *Arms.* Run the continual engine and the controls of Table 1 on one frozen engine hash, with $S\ge 10$ seeds and a randomised curriculum of unfamiliar relation names, entities and withheld graphs.

3.  *Primary endpoint.* $\hat A_N$ against the empty-memory reference, with novelty-stratified $A^{\mathrm{nov}}_N$ and the probe curve $\Pi(k)$ as the learning-to-learn endpoints. Report the per-resource results and censoring counts.

4.  *Pre-registration.* Before any run, commit $\alpha_i$, $B_i$, $w$, the generator and the analysis code to the repository.

5.  *Reporting.* Publish negative results with the same prominence as positive ones.

## 11. Limitations

$A_n$ depends on declared prices, targets and budgets. We make this explicit rather than removing it, and sensitivity analyses are mandatory. It compares two learners on one task distribution; it is not a measure of general intelligence. Cost-to-target needs a well-defined accuracy, which is harder for open-ended language behaviour than for the structured tasks considered here. Charging storage by holding time is one reasonable convention among several, and others are possible. The novelty criterion is supplied by the experimenter and can be mis-specified. Finally, the worked example is tiny and synthetic by design.

## 12. Conclusion

Learning amortization asks whether past learning pays for future learning once every lifecycle cost is charged at matched accuracy. The metric is simple, but interpreting it needs the properties proved here, especially weighting, asymmetry, asymptotics, break-even and censoring bounds. It also needs controls that separate reuse of real capability from caching, and a second-order analysis that separates learning to learn from accumulation. We offer it as a measurement protocol to be falsified in practice.

**Acknowledgements.**

Prepared with the help of an AI research assistant for the literature check, drafting and code. The author is responsible for the content.

**License.**

Text © 2026 James Jackson, licensed under CC BY 4.0. Code is MIT-licensed.

## Appendix A. Notation

|                                       |                                                                          |
|:--------------------------------------|:-------------------------------------------------------------------------|
| $T_i$, $E_i$                          | task $i$ and its sealed evaluation set                                   |
| $c_{i,k}$, $c_i$                      | cost of component $k$ on task $i$; total cost of task $i$ ($i=0$: setup) |
| $C_L(n)$, $C_R(n)$                    | cumulative cost of learner and reference through task $n$                |
| $A_n$, $a_i$, $A_\infty$, $A^{(k)}_N$ | cumulative, marginal, asymptotic and tail-window amortization            |
| $n^\star$                             | break-even point (Definition 7)                                          |
| $D_{n,k}$                             | contribution of component $k$ (Proposition 2)                            |
| $\alpha_i$, $B_i$, $\delta_i$         | accuracy target, budget, censoring indicator                             |
| $\ell_n$, $\ell_s$, $\beta$           | log cost ratio; per-seed log ratio; trend slope                          |
| $\Pi(k)$                              | fork-and-discard probe amortization (Definition 9)                       |
| $w$                                   | declared price vector over resources $\mathcal{R}$                       |

## References

<div id="refs" class="references csl-bib-body hanging-indent" entry-spacing="0">

<div id="ref-agarwal2021deep" class="csl-entry">

Agarwal, Rishabh, Max Schwarzer, Pablo Samuel Castro, Aaron Courville, and Marc G. Bellemare. 2021. “Deep Reinforcement Learning at the Edge of the Statistical Precipice.” In *Advances in Neural Information Processing Systems 34 (NeurIPS)*. <https://arxiv.org/abs/2108.13264>.

</div>

<div id="ref-baxter2000model" class="csl-entry">

Baxter, Jonathan. 2000. “A Model of Inductive Bias Learning.” *Journal of Artificial Intelligence Research* 12: 149–98. <https://doi.org/10.1613/jair.731>.

</div>

<div id="ref-bowers2023stitch" class="csl-entry">

Bowers, Matthew, Theo X. Olausson, Lionel Wong, Gabriel Grand, Joshua B. Tenenbaum, Kevin Ellis, and Armando Solar-Lezama. 2023. “Top-down Synthesis for Library Learning.” *Proceedings of the ACM on Programming Languages* 7 (POPL): 1182–1213. <https://doi.org/10.1145/3571234>.

</div>

<div id="ref-caruana1997multitask" class="csl-entry">

Caruana, Rich. 1997. “Multitask Learning.” *Machine Learning* 28 (1): 41–75. <https://doi.org/10.1023/A:1007379606734>.

</div>

<div id="ref-chaudhry2018rwalk" class="csl-entry">

Chaudhry, Arslan, Puneet K. Dokania, Thalaiyasingam Ajanthan, and Philip H. S. Torr. 2018. “Riemannian Walk for Incremental Learning: Understanding Forgetting and Intransigence.” In *Computer Vision – ECCV 2018*, 556–72. Lecture Notes in Computer Science. Springer. <https://doi.org/10.1007/978-3-030-01252-6_33>.

</div>

<div id="ref-chaudhry2019agem" class="csl-entry">

Chaudhry, Arslan, Marc’Aurelio Ranzato, Marcus Rohrbach, and Mohamed Elhoseiny. 2019. “Efficient Lifelong Learning with A-GEM.” In *International Conference on Learning Representations (ICLR)*. <https://arxiv.org/abs/1812.00420>.

</div>

<div id="ref-chen2018lifelong" class="csl-entry">

Chen, Zhiyuan, and Bing Liu. 2018. *Lifelong Machine Learning*. 2nd ed. Synthesis Lectures on Artificial Intelligence and Machine Learning. Morgan & Claypool / Springer. <https://doi.org/10.1007/978-3-031-01581-6>.

</div>

<div id="ref-chollet2019measure" class="csl-entry">

Chollet, François. 2019. “On the Measure of Intelligence.” <https://arxiv.org/abs/1911.01547>.

</div>

<div id="ref-dehghani2022efficiency" class="csl-entry">

Dehghani, Mostafa, Anurag Arnab, Lucas Beyer, Ashish Vaswani, and Yi Tay. 2022. “The Efficiency Misnomer.” In *International Conference on Learning Representations (ICLR)*. <https://arxiv.org/abs/2110.12894>.

</div>

<div id="ref-dietterich1998approximate" class="csl-entry">

Dietterich, Thomas G. 1998. “Approximate Statistical Tests for Comparing Supervised Classification Learning Algorithms.” *Neural Computation* 10 (7): 1895–1923. <https://doi.org/10.1162/089976698300017197>.

</div>

<div id="ref-diazrodriguez2018dont" class="csl-entry">

Dı́az-Rodrı́guez, Natalia, Vincenzo Lomonaco, David Filliat, and Davide Maltoni. 2018. “Don’t Forget, There Is More Than Forgetting: New Metrics for Continual Learning.” In *NeurIPS 2018 Workshop on Continual Learning*. <https://arxiv.org/abs/1810.13166>.

</div>

<div id="ref-efron1993bootstrap" class="csl-entry">

Efron, Bradley, and Robert J. Tibshirani. 1993. *An Introduction to the Bootstrap*. Chapman & Hall (reissued by Springer US). <https://doi.org/10.1007/978-1-4899-4541-9>.

</div>

<div id="ref-ellis2021dreamcoder" class="csl-entry">

Ellis, Kevin, Catherine Wong, Maxwell Nye, Mathias Sablé-Meyer, Lucas Morales, Luke Hewitt, Luc Cary, Armando Solar-Lezama, and Joshua B. Tenenbaum. 2021. “DreamCoder: Bootstrapping Inductive Program Synthesis with Wake-Sleep Library Learning.” In *Proceedings of the 42nd ACM SIGPLAN International Conference on Programming Language Design and Implementation (PLDI)*, 835–50. <https://doi.org/10.1145/3453483.3454080>.

</div>

<div id="ref-fikes1972learning" class="csl-entry">

Fikes, Richard E., Peter E. Hart, and Nils J. Nilsson. 1972. “Learning and Executing Generalized Robot Plans.” *Artificial Intelligence* 3: 251–88. <https://doi.org/10.1016/0004-3702(72)90051-3>.

</div>

<div id="ref-finn2017maml" class="csl-entry">

Finn, Chelsea, Pieter Abbeel, and Sergey Levine. 2017. “Model-Agnostic Meta-Learning for Fast Adaptation of Deep Networks.” In *Proceedings of the 34th International Conference on Machine Learning (ICML)*, 70:1126–35. PMLR. <https://arxiv.org/abs/1703.03400>.

</div>

<div id="ref-gershman2014amortized" class="csl-entry">

Gershman, Samuel J., and Noah D. Goodman. 2014. “Amortized Inference in Probabilistic Reasoning.” In *Proceedings of the 36th Annual Meeting of the Cognitive Science Society (CogSci)*. <https://escholarship.org/uc/item/34j1h7k5>.

</div>

<div id="ref-grand2024lilo" class="csl-entry">

Grand, Gabriel, Lionel Wong, Matthew Bowers, Theo X. Olausson, Muxin Liu, Joshua B. Tenenbaum, and Jacob Andreas. 2024. “LILO: Learning Interpretable Libraries by Compressing and Documenting Code.” In *International Conference on Learning Representations (ICLR)*. <https://arxiv.org/abs/2310.19791>.

</div>

<div id="ref-hernandez2020measuring" class="csl-entry">

Hernandez, Danny, and Tom B. Brown. 2020. “Measuring the Algorithmic Efficiency of Neural Networks.” <https://arxiv.org/abs/2005.04305>.

</div>

<div id="ref-hospedales2022meta" class="csl-entry">

Hospedales, Timothy M., Antreas Antoniou, Paul Micaelli, and Amos J. Storkey. 2022. “Meta-Learning in Neural Networks: A Survey.” *IEEE Transactions on Pattern Analysis and Machine Intelligence* 44 (9): 5149–69. <https://doi.org/10.1109/TPAMI.2021.3079209>.

</div>

<div id="ref-laird1986chunking" class="csl-entry">

Laird, John E., Paul S. Rosenbloom, and Allen Newell. 1986. “Chunking in Soar: The Anatomy of a General Learning Mechanism.” *Machine Learning* 1 (1): 11–46. <https://doi.org/10.1007/BF00116249>.

</div>

<div id="ref-lopezpaz2017gem" class="csl-entry">

Lopez-Paz, David, and Marc’Aurelio Ranzato. 2017. “Gradient Episodic Memory for Continual Learning.” In *Advances in Neural Information Processing Systems 30 (NeurIPS)*. <https://arxiv.org/abs/1706.08840>.

</div>

<div id="ref-minton1990quantitative" class="csl-entry">

Minton, Steven. 1990. “Quantitative Results Concerning the Utility of Explanation-Based Learning.” *Artificial Intelligence* 42 (2–3): 363–91. <https://doi.org/10.1016/0004-3702(90)90059-9>.

</div>

<div id="ref-mitchell1986ebg" class="csl-entry">

Mitchell, Tom M., Richard M. Keller, and Smadar T. Kedar-Cabelli. 1986. “Explanation-Based Generalization: A Unifying View.” *Machine Learning* 1 (1): 47–80. <https://doi.org/10.1007/BF00116250>.

</div>

<div id="ref-schwartz2020green" class="csl-entry">

Schwartz, Roy, Jesse Dodge, Noah A. Smith, and Oren Etzioni. 2020. “Green AI.” *Communications of the ACM* 63 (12): 54–63. <https://doi.org/10.1145/3381831>.

</div>

<div id="ref-tambe1990expensive" class="csl-entry">

Tambe, Milind, Allen Newell, and Paul S. Rosenbloom. 1990. “The Problem of Expensive Chunks and Its Solution by Restricting Expressiveness.” *Machine Learning* 5 (3): 299–348. <https://doi.org/10.1007/BF00117107>.

</div>

<div id="ref-taylor2009transfer" class="csl-entry">

Taylor, Matthew E., and Peter Stone. 2009. “Transfer Learning for Reinforcement Learning Domains: A Survey.” *Journal of Machine Learning Research* 10 (56): 1633–85. <https://jmlr.org/papers/v10/taylor09a.html>.

</div>

<div id="ref-thrun1998learning" class="csl-entry">

Thrun, Sebastian, and Lorien Pratt, eds. 1998. *Learning to Learn*. Boston, MA: Springer US (originally Kluwer Academic Publishers). <https://doi.org/10.1007/978-1-4615-5529-2>.

</div>

<div id="ref-veniat2021efficient" class="csl-entry">

Veniat, Tom, Ludovic Denoyer, and Marc’Aurelio Ranzato. 2021. “Efficient Continual Learning with Modular Networks and Task-Driven Priors.” In *International Conference on Learning Representations (ICLR)*. <https://arxiv.org/abs/2012.12631>.

</div>

<div id="ref-wenliang2020amortised" class="csl-entry">

Wenliang, Li, Theodore Moskovitz, Heishiro Kanagawa, and Maneesh Sahani. 2020. “Amortised Learning by Wake-Sleep.” In *Proceedings of the 37th International Conference on Machine Learning (ICML)*, 119:10236–47. PMLR. <https://proceedings.mlr.press/v119/wenliang20a.html>.

</div>

<div id="ref-wolczyk2021continual" class="csl-entry">

Wołczyk, Maciej, Michał Zając, Razvan Pascanu, Łukasz Kuciński, and Piotr Miłoś. 2021. “Continual World: A Robotic Benchmark for Continual Reinforcement Learning.” In *Advances in Neural Information Processing Systems 34 (NeurIPS)*. <https://arxiv.org/abs/2105.10919>.

</div>

</div>
