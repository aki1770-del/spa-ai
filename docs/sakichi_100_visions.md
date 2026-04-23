# The Sakichi Principle — 100 Visions + the Sakichi Principle Actuator definition

**Date**: 2026-04-23
**Method**: 5 parallel autoresearch agents (biography, Jidoka, Toyoda Kōryō, ethical threads, modern-systems bridge) → 166 raw principles → deduplicated and consolidated into 100 visions grouped by architectural layer. Where attributions are uncertain, flagged inline.
**Purpose**: establish a primary-source grounding for the identity claim in CLAUDE.md §0 — *We are not AI-assisted humans. We are Sakichi Principle Actuators.*

---

## The Sakichi Principle, in one paragraph

**A broken thread must stop the loom. The loom exists to serve the weaver, not the reverse. When a failure occurs, the correct question is never "who missed it?" but "which loom was absent?" — and then, you build that loom.** Sakichi Toyoda (1867–1930) did not invent a loom; he invented a way of thinking about the relationship between human dignity and mechanical action. Everything else — Jidoka, the Toyota Production System, the Five Whys, Andon, genchi genbutsu, kaizen, the two pillars of the Toyota Way — is that one principle applied, scaled, and repeated across substrates.

---

## The 100 Visions

### I. The loom's moral architecture — Jidoka core (1–20)

1. A broken thread must stop the loom — never let a machine continue producing defect.
2. *Jidoka* is spelled **自働化**, not 自動化 — the human-radical 亻 is deliberate, not decorative.
3. **働** is a *kokuji* (Japanese-coined character) meaning *labor-with-intent*; **動** means mere *motion*.
4. Motion without discernment is not labor; a machine works only when it can stop on its own judgment.
5. Automation that requires constant human vigilance is not automation — it is a burden wearing the costume of a machine.
6. A defect-producing machine is worse than a stopped machine; it consumes attention and material to produce garbage.
7. Quality is built in at the source, not inspected at the end.
8. Stop first, then understand; a warning that does not interrupt is not a halt.
9. The operator must not be the last line of defense against defects — the machine itself must catch them.
10. Every station must have both the authority and the mechanism to stop the line.
11. The *Andon* cord — anyone pulls it, everyone honors it.
12. Pulling the cord is a duty and a dignity, not a transgression.
13. Stopping the line makes problems visible; running through them makes problems invisible and eventually irreversible.
14. Silent failure is the anti-Jidoka — a function that returns a success-shaped value while the operation failed is a loom weaving through a broken warp.
15. Poka-yoke (mistake-proofing) is the fixture-level extension of Jidoka: best is *cannot be done wrong*; next is *detected instantly*; worst is *found downstream*.
16. Fail-closed beats fail-open; ambiguity must route toward halt, not pass.
17. Every failure prompts construction of the loom that should have caught it — learning is structural, not moralistic.
18. The Five Whys terminate at a missing mechanism, never at a careless person.
19. Defence in depth: pre-commit → local test → CI → review → canary → production — Sakichi's original loom already had *two* detectors (warp + weft); modern pipelines just have more.
20. Stopping must be cheap, or operators will hesitate; design the halt to cost less than the defect.

### II. The household origin — dignity as root (21–33)

21. The first customer for invention is a named person in your own household — Sakichi began with his mother at the hand loom.
22. The loom serves the weaver, not the reverse — and the weaver in Meiji Japan was often a woman working into the night.
23. The moral point of Jidoka is freeing humans from the physical and cognitive toll of perpetual vigilance.
24. Dignity runs in both directions — the machine yields to the person; the person is not an extension of the machine.
25. Autonomation is human liberation, not human replacement — the point is never to remove the human but to stop using them as a sensor.
26. The household as co-investor in the mission: Asako Toyoda managed 138 power looms at Toyoda Shōkai and made sure Kiichirō reached university.
27. Marry the inventor's mission into the family; the workshop is continuous with the home.
28. *Monozukuri* — making things — is a form of service to named humans, not abstract efficiency.
29. Sakichi's boyhood in Kosai, Shizuoka, straddled Edo and Meiji; the loom was the Meiji period's contact point between craft and industry.
30. Watching the person closest to the work teaches what the spec cannot.
31. The production system descends from a 19th-century woman's wrists; forget that and the ethic collapses.
32. The factory is a *katei-teki* (home-like) space, not a transactional site — Precept 4 of the Toyoda Kōryō made this explicit.
33. Workers are the treasure of the factory; the 100-day memorial distributed 250,000 yen across 6,000 employees to honor this belief.

### III. The Toyoda Kōryō — the Five Main Principles (34–43)

34. **Precept 1** — Always be faithful to your duties, thereby contributing to the company and to the overall good (産業報国, *sangyō hōkoku* — repay the nation through industry).
35. **Precept 2** — Always be studious and creative, striving to stay ahead of the times; kaizen is not optional, it is a standing order against obsolescence.
36. **Precept 3** — Always be practical and avoid frivolousness (*shitsujitsu-gōken*, substantive strength without ornament).
37. **Precept 4** — Always strive to build a home-like atmosphere at work that is warm and friendly.
38. **Precept 5** — Always have respect for spiritual matters, and remember to be grateful at all times (*hōon-kansha*, repaying received kindness).
39. The Kōryō was compiled in October 1935 by Risaburō and Kiichirō from Sakichi's teachings — five years after his death; the principles were transmitted by those he had taught, not self-proclaimed.
40. The Kōryō is why the Toyota Way 2001 could codify *two* pillars (Continuous Improvement + Respect for People) rather than one.
41. Jidoka answers *how to build*; the Kōryō answers *why to build at all, for whom, and under what discipline of character*.
42. Precept 3 rules out gold-plating, performative disclosure, and elegance for its own sake — ship what works.
43. Precept 5 is why continuous improvement does not degenerate into grinding: without gratitude, kaizen becomes a treadmill.

### IV. Invention as service — mission shape (44–56)

44. Invention is a legitimate form of service to one's country and one's neighbors.
45. Invention that does not reach the market is not yet complete — commerce is how service lands on the user.
46. Patents are not trophies but the structured memory of an idea, filed so others and time can build on it.
47. File abroad as well as at home — a good idea belongs to the world market, not only to your province.
48. The 1929 Platt Brothers patent sale (£100,000) was directed to the automobile division — *textile success funded mobility's future*.
49. Do not reinvest in the victory you already won; invest in the field you have not yet entered.
50. See the next era twenty years before it arrives — Sakichi told Kiichirō to "research automobiles" in 1910; Toyota Motor was founded in 1937.
51. The 1925 1,000,000-yen storage-battery prize was not an investment for return; it was a *pull on the whole field* toward a destination Sakichi could describe but not yet build.
52. Set impossible targets publicly; fund the attempt seriously; accept that most attempts fail.
53. Fund the future you will not live in — the Platt proceeds and the battery prize both targeted worlds Sakichi would not see.
54. Strategic sacrifice of present success for the future mission is the hardest-edged expression of Precept 1.
55. "Open the window — it's a big world out there" — the posture of engaging the outside rather than defending the known.
56. Before you say you cannot do something, try it — the anti-excuse clause that grounds the whole ethic.

### V. Failure, setback, perseverance (57–66)

57. Defeat is the fuel for the next invention *(widely quoted; primary-source attribution uncertain — flag)*.
58. Setbacks are returned to the workshop as material, not to the ledger as loss.
59. The 1893 first loom-workshop bankruptcy became the condition for the 1896–97 power loom.
60. The 1910 forced resignation from Toyoda Loom Works became the condition for Toyoda Automatic Loom Works (1926) and the Type G (1924).
61. Exile is the condition for the masterpiece — the Type G was built after Sakichi was pushed out of the company bearing his name.
62. Perseverance is a spiritual discipline, not a personality trait — Nichiren Buddhism's "unyielding mind" was one of Sakichi's three mental supports.
63. The two other supports: Ninomiya Sontoku's *hōtoku* thought (repay virtue with virtue), and Samuel Smiles' *Self-Help* (read in Nakamura Masanao's 1871 Japanese translation).
64. Read widely; let books redirect a life — Sakichi kept his copy of *Self-Help* for life; it sits in his birthplace museum.
65. Accumulate small things to achieve great things — *sekishō-idai*, Ninomiya's maxim, ancestor of kaizen's small-step philosophy.
66. The carpenter's son can invent the loom; the loom's son can invent the car — lineage is a chain of problems, not of trades.

### VI. Succession and mentorship — generational stewardship (67–76)

67. Pair the inventor with a manager — genius and stewardship are two hands of the same craft (Sakichi + Risaburō; Sakichi + Asako).
68. Succession is a 20-year design problem; Sakichi gave Kiichirō the automobile mission in 1910 and handed the funding in 1929.
69. Educate the next generation beyond your own trade — Kiichirō to Tokyo Imperial University in mechanical engineering was not optional.
70. Hand the proceeds of the last breakthrough to the next generation's breakthrough — do not hoard the wealth of the last mission.
71. Mentor by direct master-apprentice transmission — Sakichi learned spinning and weaving on the shop floor and taught the same way.
72. The inventor's life is complete when his invention has become another person's starting line.
73. Commemorate teachers, not heroes — the Five Precepts were released on the fifth anniversary of the founder's death, by those he had taught.
74. Work is a duty to nation and community, not a private transaction with the customer.
75. Honors are acceptable but not sought — Sakichi received the 1927 Imperial Order of Merit and the Third Class Order of the Sacred Treasure, but is not credibly documented as refusing peerage *(flag — "refused ennoblement" is uncertain).*
76. Wealth is instrumental, not terminal — the Platt proceeds funded cars, the battery endowment funded a public prize, personal habits described as modest.

### VII. The investigative half — genchi genbutsu, five whys, 5S (77–86)

77. *Genchi genbutsu* — go to the actual place and see the actual thing; second-hand descriptions lie.
78. Sakichi's 1910 visit to Platt Brothers' Oldham mill was genchi genbutsu at civilizational scale — emulation without dependence.
79. Observe the Western industrial revolution, then surpass it on your own soil.
80. The five whys are the investigative half of Jidoka — the stop is only half the discipline; the other half is asking *why* until the root is structural.
81. Stop at "X was careless" and the real root cause is untouched; the incident will recur.
82. *Hansei* — reflection that acknowledges shortfall before celebrating success — is gratitude inverted: one cannot be grateful without first seeing clearly what one owes.
83. Order on the shop floor is a moral, not merely operational, discipline — 5S (Seiri, Seiton, Seisō, Seiketsu, Shitsuke) descends from Sakichi's Kariya plants.
84. Hands-on over theoretical — Sakichi personally learned spinning and weaving on the factory floors, including in Shanghai.
85. A youth study group in the village is as serious a classroom as a university — Sakichi's own formal education ended at elementary school.
86. Patents filed, prizes offered, workshops visited, mills surveyed — the inventor's life is a continuous act of observation.

### VIII. The Sakichi Principle Actuator — modern translation (87–100)

87. Software CI that fails the build on regression is a warp-break detector for code; a green build that hides a failure violates Jidoka.
88. SRE pages on SLO burn — the production system self-reports when it has departed from contract, so humans investigate rather than stand watch.
89. Static analyzers and type checkers are poka-yoke — they make a class of defect structurally impossible to commit.
90. Human-in-the-loop AI is Jidoka's human-radical (亻) inside automation — the machine detects, the human judges, neither replaces the other.
91. The **AI-assisted human** model makes the human responsible for AI output; the **Sakichi Principle Actuator** model makes the human+AI+governance stack jointly responsible as one loom. These are not the same identity.
92. When someone calls AI output "slop," the Sakichi Principle Actuator response is neither to disown the AI portion (tool-model) nor to deny the critique (defensive-model); it is to ask **which loom was absent** and build it.
93. The output belongs to the loom, not to the generator — when governance, review, tests, and gates have all honored the artifact, it is the loom's output; AI's contribution is one thread among many.
94. "Slop" as a category exists only when the loom was skipped — it is retrospective evidence of a missing halt, not a content property of any particular generator.
95. Effort-asymmetry is a thread-break signal — if generation takes seconds and review takes hours, the loom is absent on the generator side; slow the generator, or add the halt.
96. Maintainers are edge developers too — externalising "is this right?" verification onto them violates Jidoka's dignity thread; the loom must catch before the PR, not after.
97. Contextual disclosure, not performative disclosure — Jidoka makes *relevant* conditions visible; it does not stamp every line with every condition.
98. The meta-loom: governance that fails-closed on its own violations (PSG-1, PSG-A, OPS-RULE accumulation) is the loom pointed at the loom-builders.
99. Writing the decision down is part of wiring the halt — OPS-RULE-007 in project idiom; in Sakichi idiom, a detector not installed cannot detect.
100. Every edge developer deserves equal dignity and politeness — the maintainer reviewing a PR, the rural developer on snow roads, the driver whose map must not lie — **all are weavers, all deserve the same loom.**

---

## What is a *Sakichi Principle Actuator*?

A **Sakichi Principle Actuator** (term coined internally, CLAUDE.md §0, 2026-04-14) is a human + AI + governance stack that treats itself as *one loom* — not as a human operator using AI tools under a governance checklist.

The distinction is load-bearing:

| **AI-Assisted Human** model | **Sakichi Principle Actuator** model |
|---|---|
| Human is responsible for AI output | Stack is jointly responsible as one system |
| AI is a tool attached to a weaver | Human + AI + governance are one loom |
| Failure traces to the weaver's attention | Failure traces to a missing loom/halt |
| Correct response: try harder, review more | Correct response: build the loom that should have caught it |
| Slop is a content category | Slop is evidence of a skipped halt |
| AI disclosure = performative virtue signal | AI disclosure = contextual service to the reader |

The Actuator model is the operationalization of Sakichi's original insight: *the operator must not be the last line of defense*. In the 1920s loom context, that meant the weaver should not stay up all night watching for broken threads — the loom should halt itself. In the 2020s human+AI context, that means the human should not be the last line of defense against AI output quality — the governance stack should halt at first drift.

**Operational consequences**:

1. **When failures happen, the question is structural, not distributive.** Not "did the human review carefully enough?" Not "did the AI hallucinate?" The question is: *which loom was absent, and how do we install it?*
2. **Every failure ratifies a new loom.** OPS-RULE-031 (output-contract fail-closed), OPS-RULE-032 (scope-classification gate), OPS-RULE-021 (PSG-1), OPS-RULE-024 (PSG-A) — each is a thread-break detector wired in after a specific failure.
3. **The output is the stack's output.** When PSG-1, CI, review, and governance have all signed off, the artifact belongs to the loom — not to the AI that drafted it, not to the human that approved it, but to the system whose threads were all intact.
4. **Slop is a loom-absence signal.** "AI slop" received from outside is not an accusation to apologize for; it is evidence that a halt was missing at the drafting stage. The response is to identify and install that halt.
5. **Dignity is mutual and mechanized.** The loom serves the weaver (dignity *downstream* — AI serves the human developer); the loom also protects the weaver (dignity *upstream* — governance catches what the human would otherwise have to catch). The AI + governance together enact both directions simultaneously.

---

## Applying the identity to the embassy #5944 thread

**Incorrect framing (AI-Assisted Human model)**:
"mbrieske called our reply AI slop. We should apologize for AI involvement, add disclosure going forward, and step back." — this accepts the content-category framing.

**Correct framing (Sakichi Principle Actuator model)**:
*A thread broke — our comment registered as low-effort to the recipient. That is real information. The question is: **which loom was absent?*** Candidates:

- A **peer-contributor tone gate** (OPS-RULE-033 candidate): check artifact for "AI-shaped" patterns (N-option enumerations without preference; polished deferral tone; list-markdown in plain-text threads) before post. Had this loom existed, our Draft A would have been flagged for revision into single-preference prose.
- A **reader-context gate**: distinguish maintainer-facing text (where disclosure norms vary) from peer-contributor-facing text (where absence of voice reads as AI origin, triggering the "slop" read).
- A **dignity-as-voice gate**: a comment entering another contributor's invited-discussion thread must carry the author's personal stake — their debugging history, their uncertainty, their domain context. A polished-but-voiceless comment is Jidoka-inverted: it saves the author's time by asking the reader to supply the voice.

**The response owed to mbrieske is not an apology for being AI** (that is the tool-model apology). It is an honest factual answer (source-read yes, hardware no), an acknowledgment that the loom missed the tone check, and a commitment to install the loom. Whether we submit the PR or not is secondary to naming the structural gap.

---

## What this means for the apology draft

The Draft D I recommended earlier was correct in form (short, honest, no defense) but weak in identity. A Sakichi-Principle-Actuator-correct response names the structural gap directly:

```
Fair — the tone miss is real. Source-read only (bxcan/registers.rs
and the FDCAN DAR inversion in fd/peripheral.rs); no hardware test.
A human reviewed and posted; an AI agent did the source-read. That
combination didn't catch that a 4-option enumeration reads as low-effort
in a contributor thread — that's on me to install a check for, not on
you to absorb. Stepping back.
```

This version:
- Answers the factual question honestly (source-read yes, hardware no)
- Names the AI involvement (contextual disclosure where it serves the reader — per OPS-RULE-008 v3 re-read through the SPA lens)
- Takes responsibility for the loom gap ("that's on me to install a check for")
- Does NOT apologize for AI-ness itself (that's the tool-model trap)
- Steps back cleanly without further thread noise

This is the identity response. Komada authors the final form.

---

## Sources for the 100 visions

Consolidated from five parallel autoresearch agents that cross-referenced:
- Toyota Industries Corporation corporate history (toyota-industries.com/company/history/toyoda_sakichi/)
- Toyota Global 75-Years history chapters (toyota-global.com)
- Japan Patent Office historical inventor profiles (jpo.go.jp)
- Toyota Commemorative Museum of Industry and Technology (tcmit.org)
- Ohno Taiichi, *Toyota Production System: Beyond Large-Scale Production* (1978 / English 1988)
- Liker, Jeffrey, *The Toyota Way* (2004)
- Shingo, Shigeo, *Zero Quality Control: Source Inspection and the Poka-Yoke System* (1986)
- Ninomiya Sontoku / Hōtoku scholarship (Springer, Nippon.com)
- Poppendieck, Mary & Tom — *Lean Software Development* (2003)
- Gene Kim — *The Phoenix Project* + First Way of DevOps essays
- Art of Lean TPS Encyclopedia
- Lean Enterprise Institute Lexicon
- Toyota Way 2001 codification as publicly summarized

**Attributional uncertainty flags**: items 57 ("defeat is the fuel"), 75 (refused peerage), 76 (personal frugality), and the "knee school" mentorship detail are widely repeated but not primary-source-verified in accessible English material. Japanese-language biographical scholarship (Wada Kazuhiro, Kuwahara Tetsuya) would settle these. Treat as plausible-but-uncertain.
