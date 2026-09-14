# Where EXCRE stands after a proper literature check (14 Sep 2026)

Before writing any code I went back and verified every citation in the proposal
and searched for anything published since May that touches the same idea. Short
version: the core idea is still alive, but the window is closing and the paper
cannot be framed the way the proposal frames it. Notes below.

## 1. Citation audit

Most of the proposal's references check out, including the ones I was least
sure about:

| Reference in proposal | Status |
|---|---|
| Council Mode (Wu et al. 2026) | Real. arXiv:2604.02923. Triage -> parallel heterogeneous models -> synthesis. 41.7% relative hallucination reduction on a HaluEval subset, +7.5 on TruthfulQA, 4.2x token cost. |
| T-FIX (Havaldar et al.) | Real. arXiv:2511.04070. Benchmark for expert-aligned explanations, 7 tasks / 3 domains. |
| Lee, Lauscher & Albrecht, LaMAS@AAAI'26 | Real. arXiv:2512.04691 (mechanistic-interpretability agenda for ethical multi-agent LLM systems). |
| ConsensAgent (Pitre et al.) | Real. ACL 2025 Findings. |
| Mirror Loop (DeVilling) | Real. arXiv:2510.21861. |
| Iwanowski & Gahbler 2025 "multi-LLM consensus survey" | Exists but is about consensus of vision models for **object detection** (Applied Sciences 15:12961). The proposal cites it as if it were a survey of multi-LLM reasoning consensus. Needs fixing in the thesis — either recharacterise it honestly or swap in an actual MAD survey. |
| PeerCoT | Shaky. The only trace I can find is an ICLR 2026 workshop item, and the proposal itself lists two different author sets (Schaffer et al. in the references, Chaturvedi et al. in Table 2-1). Until I can pin down the actual paper it should not be treated as a headline baseline. If it stays in the thesis, cite it exactly; if it can't be located, drop it. |

## 2. The uncomfortable finding: we got partially scooped in June

**"The Consistency Illusion: How Multi-Agent Debate Hides Reasoning
Misalignment" (arXiv:2606.08457, June 2026)** introduces CARA (Cross-Agent
Reasoning Alignment): automated metrics for whether agents that agree on an
answer also agree on the reasoning. That is the same observation IMRC is built
on — answer-level consensus can hide reasoning-level disagreement. They also
show a headline result: debate reduces surface contradictions while the
semantic similarity of the reasoning chains actually *drops*.

So the claim in the proposal's gap G2 ("no accepted metric distinguishes
agreement on the answer from agreement on the rationale") is no longer true as
stated, and a reviewer in this area will know it.

What CARA does *not* do — and this is where the thesis lives now:

1. It is purely a post-hoc diagnostic on debate transcripts. The signal never
   feeds back into the decision. EXCRE computes congruence *inside* the loop
   and uses it: in the trust score, in the convergence check, and to gate
   whether the system should answer at all.
2. Two medical QA benchmarks, two backbones from the same family. No maths, no
   commonsense, no legal, no genuinely heterogeneous model mix.
3. No adversarial study. Nobody has shown that a compromised agent that argues
   convincingly for a wrong answer is invisible to answer-agreement but visible
   to a reasoning-congruence gap. That experiment is still ours.
4. Their protocol fix (Grounded Debate Protocol) is prompt-level. The
   schema-validated exchange with evidence weights and a full audit trail is
   still unoccupied territory.

Other close neighbours found in the same sweep, all post-proposal:

- AgentAuditor (arXiv:2602.09341) — builds a "reasoning tree" over agent
  traces and adjudicates at divergence points; targets what they call
  confabulation consensus. Uses training (preference optimisation), which we
  deliberately avoid.
- Reasoning Consensus via weighted DAG aggregation (arXiv:2607.27783) —
  post-hoc, single pass, no exchange between models.
- Disagreement as Data (arXiv:2601.12618) — cosine similarity over traces as
  an analytics tool, education domain.

None of these combine: iterative exchange + heterogeneous models + congruence
as a live decision signal + adversarial validation. That combination is the
paper.

## 3. Is this publishable? Honest answer

Yes, conditionally. Not at a top-tier main conference on accuracy numbers —
that fight is unwinnable (Smit et al. 2024 and Wang et al. showed debate gains
often reduce to sampling effects, and reviewers now demand token-matched
baselines, which flatten most of the reported gains in this literature). And
the proposal's H1 ("beat ReConcile/Council Mode/PeerCoT by >=3pp on 4/7
datasets") is exactly the kind of claim that dies in review: underpowered at
feasible sample sizes and hostage to model/version noise.

What *is* publishable, because it is checkable and nobody has done it:

- **C1.** Reasoning congruence carries information about correctness beyond
  answer agreement and self-reported confidence. (Incremental predictive value,
  measured properly.)
- **C2.** A trust score built on it supports selective prediction: risk-coverage
  curves that beat confidence-only and agreement-only gating.
- **C3.** An adversarial insider that answer-level consensus cannot see produces
  a detectable high-agreement/low-congruence signature. Detection quantified as
  AUROC, clean vs sabotaged.
- **C4.** At matched token budget, schema-structured exchange does not cost
  accuracy relative to free-text debate, and buys machine-checkable audit
  trails. (Even a null result here is a usable finding — it removes the "why
  bother with structure" objection.)

If C1 and C3 hold empirically, this is a solid workshop paper (LaMAS@AAAI,
TrustNLP, or similar) and a plausible Findings short paper at an ACL-family
venue. If they hold *strongly* across four-plus datasets with heterogeneous
models, a Findings long paper is realistic. If they don't hold, the thesis
still stands (a careful negative result with a failure taxonomy is fine for an
MSc), but the paper becomes much harder. The risk is real; better to know now.

Timing matters. CARA appeared in June; this space is moving at a
paper-per-month pace. Every month of delay makes the novelty statement harder
to defend, so the experiments should be running within weeks, not months.

## 4. Architecture or prototype — what is actually the contribution?

The question was: is the contribution the architecture, or a prototype that
beats a benchmark? Neither, and this matters for how everything gets written.

Reviewers do not accept "we designed a framework" as a contribution — designs
are cheap and unfalsifiable. They also will not be impressed by +2pp on GSM8K
from a student budget — accuracy leaderboards belong to the labs. The
contribution is a set of **validated claims** (C1-C4 above). The architecture
is the apparatus that makes the claims testable; the prototype is the
instrument; the benchmarks are the evidence. The IMRC definition, the schema,
and the protocol are contributions only insofar as the claims about them
survive the experiments.

Practical consequence: build the measurement machinery (metrics, statistics,
adversarial harness) with as much care as the framework itself, because that
is what the paper actually rests on. Accuracy vs ReConcile gets reported
honestly, whatever it turns out to be, as a secondary result at matched budget
— it is context, not the headline.

## 5. What changes vs the proposal

- H1 gets reframed: primary hypotheses become C1-C3, accuracy parity/gain
  becomes secondary. (The thesis text can keep the original H1 as stated and
  report against it honestly; the paper leads with the trust claims.)
- Drop PeerCoT as a named baseline unless the citation can be pinned down.
  Council Mode's synthesis step gets approximated as a "central judge"
  baseline since the exact prompts are not public.
- Scope: start with 4 datasets, 5 systems (see the experiment plan), grow to
  the full 7x7 grid only if budget survives contact with reality.
- Related work must cite and position against 2606.08457 (CARA),
  2602.09341, 2607.27783, and 2601.12618. Pretending they don't exist would be
  fatal in review.
