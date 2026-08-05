# Presentation brief and slide script

Everything you need to give this talk. It has three parts: a short brief of the whole project, a
slide by slide plan with on-slide text and speaker notes, and a Q and A sheet. Figures referenced
live in `figures/`. Suggested length is 12 to 15 minutes on 12 to 14 slides.

---

## Part 1. The brief (read this first)

**The question.** Pain neuroimaging has long described a cortical "pain matrix", anterior insula,
cingulate, and secondary somatosensory cortex. But the pain system is distributed, with major
subcortical and brainstem nodes: thalamus, periaqueductal gray, parabrachial nucleus, rostral
ventromedial medulla. A live question in the field is whether the cortical emphasis in the literature
reflects the real organization of pain, or whether it is amplified by how the literature measures,
reports, and indexes results. Subcortical nuclei are small, deep, and hard to image, so their
coordinates may simply be under-reported. This matters because automated tools that summarize the
literature increasingly define brain networks and are used to localize function, so any bias in the
literature is inherited and amplified by the tools built on it.

**The approach.** Test that bias using the NeuroQuery open dataset. NeuroQuery built its own
coordinate extraction pipeline from full text, independent of the other meta-analytic databases, and
ships the raw tables: peak coordinates, per-study word counts, term frequencies, article metadata,
and a term co-occurrence structure. Four of the five analyses here are pure counting on those tables,
so there is no trained model in the loop and no way for a model's quirks to drive the result. It is a
third, independently built dataset used to check a bias other tools cannot see from within.

**The finding, in one line.** Across every measure the pain literature over-represents cortex, the
imbalance is roughly twofold and it is concentrated specifically at the coordinate reporting stage,
not in whether the field discusses subcortical structures.

**Why it is more than a re-illustration.** Three things: the imbalance appears in a third,
independently extracted database (Idea A); it separates a coordinate reporting effect from a simple
attention effect (Idea C); and the same tool's text-trained map recovers the subcortical signal its
raw coordinates lose (Idea B). Together they place the bias at a specific stage rather than just
restating that cortex looks dominant.

---

## Part 2. Slide by slide

Each block gives the slide title, what to put on the slide, which figure to show, and what to say.
Speaker notes are written so you can read them almost verbatim.

### Slide 1. Title
**On slide:** Representation bias in the pain neuroimaging literature: a test with the NeuroQuery
open dataset. Your name, date.
**Say:** "I looked at whether the cortical dominance we see in pain brain maps is real, or partly an
artifact of how the literature reports its results, using an independent dataset to test it."

### Slide 2. The problem
**On slide (bullets):**
- Pain imaging emphasizes a cortical "pain matrix" (insula, cingulate, S2).
- But pain is distributed: thalamus, PAG, parabrachial, RVM are core nodes.
- Subcortical nuclei are small, deep, hard to image, so their peaks may be under-reported.
- Automated literature tools inherit and amplify whatever bias is in the literature.
**Say:** "The standard picture of pain in the brain is cortical. But the actual pain system runs
through the brainstem and thalamus just as much. The concern is that the deep structures are hard to
image, so the literature may simply report their coordinates less often, and the tools we use to
summarize that literature would then hand us back a map that looks more cortical than the biology
is."

### Slide 3. The idea
**On slide:**
- Use NeuroQuery's raw open data: coordinates, word counts, metadata, term co-occurrence.
- NeuroQuery's coordinate extraction is independent of other databases.
- Four of five analyses are pure counting, no model in the loop.
- Five angles on one question: does the literature over-represent cortex, and where does the bias
  enter.
**Say:** "NeuroQuery is a meta-analysis tool, but I am not using its search box. I am using the raw
tables it ships. That matters because counting coordinates and words in a downloaded file has no
model that can be tricked. And because NeuroQuery extracted its coordinates with its own pipeline, if
I see the same bias here that other tools show, that points to the literature itself rather than to
one tool's code."

### Slide 4. Idea A, the size-fair reporting audit  [core result]
**Figure:** `reporting_forest.png`
**On slide:**
- 484 most pain-relevant studies from NeuroQuery, all their reported peaks.
- Same-size sphere at each of 10 standard pain regions, count studies reporting a peak inside.
- Same radius everywhere, so a region cannot win for being large.
- Cortical reported about twice as often as subcortical (2.05 at 6 mm, p = 0.03).
**How I made it:** "I took NeuroQuery's own text score for the word pain, kept the most pain-specific
3.6 percent of the corpus, that is 484 studies, and pulled every coordinate they reported. Then for
ten a-priori pain regions, five cortical and five subcortical, I put a 6 mm sphere at each and
counted the fraction of studies with a peak inside. Same radius at every region is the key: it takes
size out of the comparison."
**What it shows:** "Red circles are cortical, blue triangles are subcortical. The cortical regions
sit on the right, reported often. The subcortical nuclei sit on the left, reported rarely. The two
dashed lines are the group means, and the cortical mean is about twice the subcortical mean."
**The line to land:** "Look at S1, primary somatosensory cortex. It is large and easy to image, so if
this were just about detectability it should sit with the other cortical regions. Instead it falls
down among the brainstem nuclei. So this is not simply that cortex is easier to scan. It tracks which
structures the pain field chooses to emphasize, the affective and evaluative cortex."

### Slide 5. Idea A robustness
**Figure:** `ratio_by_radius.png` (and optionally the `threshold_sweep.csv` numbers as a small table)
**On slide:**
- Ratio holds across sphere radii: 2.05, 1.69, 1.61, 1.57 at 6, 8, 10, 12 mm.
- Stable near 2.0 whether you take the top 2, 3, or 3.6 percent most pain-specific studies.
- Not a radius artifact, not a threshold artifact.
**Say:** "Two quick robustness checks. Widening the sphere keeps the ratio above one, and it is
strongest at the tightest, most anatomically precise radius. And sweeping how strict I am about
what counts as a pain study, the ratio stays near two across the pain-specific range and only eases
toward 1.7 when I loosen the selection a lot. So the result does not hinge on my choices."

### Slide 6. Idea C, mention versus reporting  [localizes the bias]
**Figure:** `mention_vs_reporting.png`
**On slide:**
- Same 484 studies: how often is each region named in the text, versus reported as a coordinate.
- Subcortex is discussed nearly as much, but reported about half as often.
- Thalamus is the most-mentioned region of all, yet reported near the bottom.
- Mention imbalance 1.62, reporting imbalance 2.02.
**How I made it:** "For the same studies, I counted how often each region is named anywhere in the
text, using a careful synonym list for each region and only counting terms that actually exist in
NeuroQuery's vocabulary, and I checked that no single synonym drives it. Then I compared that mention
rate to the reporting rate from the first analysis."
**What it shows:** "Grey bars are mentions, colored bars are reported coordinates. For the
subcortical regions the grey bar towers over the colored one. Thalamus is the single most mentioned
region in the whole set, above every cortical region, and yet its coordinates are reported near the
bottom."
**The line to land:** "This separates two explanations. It is not that the field ignores subcortex.
The field talks about it constantly. It is specifically that subcortical coordinates get
under-reported. The bias lives at the reporting step, not in what the field pays attention to."

### Slide 7. Idea B, the model recovers the subcortical signal  [the clincher]
**Figure:** `roi_zvalues.png`
**On slide:**
- The one analysis that uses NeuroQuery's trained map, for the single query "pain".
- It predicts a brain map from the text, not just from reported peaks.
- RVM and PAG rank above the cingulate; thalamus matches anterior insula; S1 is negative.
- The subcortical signal is in the text; the coordinates are where it is lost.
**How I made it:** "Here I did use NeuroQuery's model, but in the safest way, one validated word,
pain, read at the same coordinates. The model predicts a whole-brain map from how words co-occur in
the literature, so it draws on the text, not only on reported peaks. I read its value at each region."
**What it shows:** "The descending pain-control nuclei, rostral ventromedial medulla and
periaqueductal gray, come out near the top, above the cingulate. Thalamus sits with anterior insula.
S1 is actually negative, not pain specific, which matches the reporting audit."
**The line to land:** "This is the clincher for the previous slide. Same tool, two outputs. Its raw
coordinates under-report these structures, but its text-trained map puts them near the top. So the
signal linking pain to the brainstem is present in the literature's text. It is the coordinate
reporting step that loses it." *(Caveat to say aloud: this value is a prediction, an association, not
a localization claim, and RVM being highest deserves a little caution.)*

### Slide 8. Idea E, the vocabulary is only mildly cortical
**Figure:** `semantic_anchoring.png`
**On slide:**
- With no model at all: how often does "pain" co-occur with each region's term across the corpus.
- Cortical a little higher than subcortical (1.49).
- Validation: nearest terms to "pain" are painful, nociceptive, noxious, chronic pain; nearest
  anatomy is insula.
**Say:** "The mildest measure, and pure co-occurrence, no model. How often does the word pain show up
in the same paper as each region. As a sanity check, the words closest to pain are exactly what they
should be, and the closest brain region is the insula. Cortical regions co-occur with pain a bit more
than subcortical ones, but only a bit, a ratio of about 1.5. Hold that number for the next slide."

### Slide 9. Idea D, is it improving over time
**Figure:** `year_trend.png`
**On slide:**
- Publication year recovered from PubMed for the 484 studies (2004 to 2017).
- Cortical over subcortical ratio declines weakly (slope -0.44 per year, p = 0.054).
- Before 2016: 2.85. From 2016: 2.48.
- Consistent with a hardware and measurement account, but not decisive; corpus ends 2017.
**Say:** "This is the honest slide. If the bias were purely an old-hardware problem, it should shrink
as scanners improve. There is a weak downward trend, borderline significant, and the ratio is a bit
lower after 2016. So maybe hardware is part of it. But the effect is small and the corpus stops in
2017, before high-field imaging became common, so I cannot settle it. I am showing it because the
honest answer is a partial one."

### Slide 10. Synthesis, the gradient
**Figure:** `convergence_summary.png`
**On slide:**
- Four independent measures, all above one.
- The imbalance grows: co-occurrence 1.49, mentions 1.62, coordinate reporting 2.02 and 2.05.
- Plus: the trained map recovers subcortex.
**The line to land:** "Here is the whole story in one picture. Four independent measures, all showing
cortex over subcortical, but notice they get bigger left to right. In the raw vocabulary the
imbalance is mild. When the field writes about regions it is a little bigger. When it reports
coordinates it doubles. And the model's own map recovers the subcortical structures. So the bias is
small in discussion and large in the coordinate record. It is concentrated at the coordinate
reporting stage, and it is present in a third, independently built dataset."

### Slide 11. What it means, and why it matters
**On slide:**
- The cortical dominance in coordinate summaries of pain is, in substantial part, a reporting effect.
- It is present in an independently extracted database, so it is a property of the literature.
- Subcortical and brainstem nodes (PAG, RVM, thalamus, parabrachial) are underplayed by the
  coordinate record.
- Automated syntheses that define pain networks inherit this, so cortical-dominance claims from them
  should be discounted.
**Say:** "This does not tell you where pain is generated. What it tells you is that the standard tools
for summarizing the pain literature systematically under-report the deep structures, so a map built
from them looks more cortical than the evidence warrants. For anyone using these tools to localize
pain or define its network, that is a caution. And it says the brainstem and thalamic nodes deserve a
closer look than the coordinate record gives them."
**Scope link (adapt to your framing):** "This slots directly into the larger question I care about,
where the subcortical contribution to pain sits. It is an independent line of evidence that the
cortical picture is inflated by measurement and reporting, which is exactly what you would want to
establish before leaning on subcortical structures."

### Slide 12. Limits
**On slide:**
- These measure the literature, not the brain. No claim about where pain is generated.
- Pain studies selected by a single term, contrast-blind (same limit for cortical and subcortical).
- Encoding z (Idea B) is an association, not a significance test.
- Year analysis is underpowered and ends in 2017.
**Say:** "To be clear about what this is not. Every measure here is about the literature, not about
where pain lives. The study selection uses one word and does not distinguish experimental contrasts,
though that limit applies equally to both sides of the comparison. The model value in the recovery
slide is an association, not a formal test. And the time trend is weak. I am confident about the
reporting imbalance and where it sits; I am not making a localization claim."

### Slide 13 (backup). Methods one-pager
**On slide:**
- Data: NeuroQuery open dataset (13,000 studies, own extraction pipeline).
- Selection: top 3.6 percent by NeuroQuery's tf-idf for "pain" = 484 studies.
- Regions: 10 core (5 cortical, 5 subcortical), extended to 16, MNI coordinates from the literature.
- Reporting audit: fixed-radius spheres, Wilson intervals, one-sided Mann-Whitney.
- All code and logged parameters in the repository.

---

## Part 3. Anticipated questions

**"Isn't NeuroQuery biased like every other tool, so of course it agrees?"**
Yes, and that is the design. It draws on the same underlying literature but extracts coordinates with
a different pipeline. Agreement across independent pipelines is what localizes the bias to the
literature rather than to one tool. And Idea B uses NeuroQuery's own bias diagnostically: its map
recovers subcortex, so I am not just taking its output at face value.

**"Couldn't subcortical peaks just be weaker, so this is real biology, not bias?"**
Two things argue against pure detectability. First, S1 is a large, easily imaged cortical region and
it is reported as rarely as the brainstem, which a detectability account cannot explain. Second,
high-field 7T work recovers brainstem pain responses that standard scanners miss. Idea D tests the
hardware account directly and finds at most a weak effect.

**"Why these regions and coordinates?"**
They are standard a-priori pain nodes from the literature, with a fixed sphere radius at each so size
does not matter. I also ran an extended 16-region set to check it is not cherry-picked, and the
result holds on both.

**"Is the encoding z in Idea B a real statistic?"**
It is a rescaled prediction from NeuroQuery's model, good for ranking and association, not a
significance test and not a localization claim. I report it only as an association, and I flag that
the deepest structure, RVM, being highest warrants some caution.

**"You selected pain studies with one word. Isn't that crude?"**
It is contrast-blind and incomplete, yes. But the comparison is internal, cortical versus subcortical
under the exact same selection, so the selection limit applies equally to both and does not create the
gap. The threshold sweep shows the result is stable across how strict the selection is.

**"What would make this stronger?"**
Repeating the reporting audit on a hand-curated database as a fourth independent pipeline, and
extending the year analysis past 2017 into the high-field era.

---

## Figure cheat sheet (one line each)

- `reporting_forest.png` (A): per-region reporting rate, cortical circles versus subcortical
  triangles, with confidence intervals. Made by counting studies with a peak inside a fixed sphere.
- `ratio_by_radius.png` (A): the cortical over subcortical ratio at 6, 8, 10, 12 mm, plus the two
  region sets. Robustness check.
- `mention_vs_reporting.png` (C): grey mention bars versus colored reporting bars per region. Made by
  counting text mentions and comparing to reporting.
- `roi_zvalues.png` (B): NeuroQuery's encoding value for "pain" at each region. Made from the trained
  map. Shows RVM and PAG high.
- `semantic_anchoring.png` (E): co-occurrence of each region term with "pain". Pure counting.
- `year_trend.png` (D): reporting ratio by publication year with a weighted trend line.
- `convergence_summary.png` (synthesis): the four measures as a gradient, discussion on the left,
  coordinate reporting on the right.

## Suggested timing

Slides 1 to 3 in two minutes. Slides 4 to 5 (Idea A) in three minutes, this is the core. Slides 6 to
7 (C then B) in three minutes, this is the argument. Slides 8 to 9 (E, D) in two minutes. Slides 10
to 12 in three minutes. Leave two minutes for questions.

If you only have five slides: title, Idea A (slide 4), Idea C (slide 6), Idea B (slide 7), synthesis
(slide 10). That path alone makes the whole argument.
