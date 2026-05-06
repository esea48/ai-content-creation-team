# Prompt Comparison: SRH Content Templates

## Summary

This document compares current and proposed prompt templates for SRH University content, and reflects on what we learned about prompt quality and data grounding through the process.

The core finding: the more relevant reference material we provide to the model, the better and more specific the output. A vanilla GPT prompt produces generic, low-uniqueness content. Guided prompts with structured Content Requirements and Style Rules — anchored to PRIMARY and SECONDARY knowledge bases — produced noticeably more SRH-specific, brand-native results.

We observed this directly through three iterations of a Classical Music blog post: without data references, the output was generic. As we added structure, knowledge base grounding, and tighter style rules, the content became progressively more differentiated and SRH-native.

---

## Classical Music Blog Post: Three Iterations

### Generic (No prompt structure, no data)

**Prompt used:**
```
You are writing as an industry analyst for SRH University, focused on higher education in Europe. Write a blog about the Classical Music program.

Required structure:
- Opening section that frames the topic in the current market context
- Market trends section with at least 2 specific trends from the secondary research layer
- Competitor positioning section that explains how other institutions or providers are responding
- Customer pain points section that addresses specific frustrations or unmet needs
- Market gap section that identifies what is missing in the current landscape
- Closing section that links the insight back to SRH's positioning where relevant
```

**Output sample:**
> *"Classical music education in Europe sits at a critical inflection point... the field is now being reshaped by structural changes in higher education, shifting labor markets, and evolving audience behaviors."*

The generic output is well-researched and analytically structured — it reads like a credible industry report. But it has no SRH identity whatsoever. It cites external research, references the Bologna Process, and maps the competitive landscape in detail, yet SRH only appears in the final paragraph as an afterthought. The writing is confident but could belong to any institution, consultancy, or think tank.

**What's missing:** Any SRH-specific facts, programme details, or brand voice. The institution is a footnote, not the author.

---

### Version 1 (Guided prompt, basic knowledge base reference)

**Prompt used:**
```
You are writing as an industry analyst for SRH University, focused on higher education and applied AI programmes in Europe.

Required structure:
- Opening section that frames the topic in the current market context
- Market trends section with at least 2 specific trends from the secondary research layer
- Competitor positioning section that explains how other institutions or providers are responding
- Customer pain points section that addresses specific frustrations or unmet needs
- Market gap section that identifies what is missing in the current landscape
- Closing section that links the insight back to SRH's positioning where relevant

Brand requirements:
{source_rules}
{brand_voice_rules}
- Language: {language_label}
- Tone: {tone_label}
- Voice: {voice_label}
- Keep the analysis specific, credible, useful, and ready for publication.
- Make the analysis feel informed, current, and publication-ready.
```

**Output sample:**
> *"As global interest in classical music continues to rise, educational institutions are presented with a unique opportunity to innovate their offerings... SRH University stands out in the landscape of higher education by integrating practical applications into its curriculum."*

Version 1 moves in the right direction. It follows the required structure — market trends, competitor positioning, pain points, market gap — and connects each section back to SRH. It reads more like an institutional blog than a third-party report. However, it still leans heavily on analyst framing and generic language. Phrases like "innovate their offerings" and "thrive in today's competitive job market" appear without specific SRH proof points to back them up.

**What improved:** SRH is present throughout, not just at the end. Structure is clear and publication-ready.  
**What's still missing:** Concrete SRH facts, named programmes, specific outcomes, and a distinctive editorial voice.

---

### Version 2 (Stronger prompt, tighter style rules, differentiation guidance)

**Prompt used:**
```
You are a content strategist for SRH University.

Use the PRIMARY knowledge base as the source of truth for SRH facts.
Use the SECONDARY knowledge base for market context, competitor signals, and audience pain points.

Write a blog post that feels strategic, credible, and clearly tied to SRH's positioning in the market.

Task:
Write about: [topic]
Audience: [audience]
Tone: [tone]
Language: [language]
Word count: [word_count]

Required structure:
- Open with a specific market trend, challenge, or audience need
- Show SRH's point of view on that issue
- Include 2 to 3 body sections with concrete SRH facts and proof points
- Include a short competitor or market contrast section
- Close with a clear takeaway that reinforces SRH's positioning

Content requirements:
- Use both knowledge bases, but keep SRH facts grounded in PRIMARY
- Include concrete examples, not vague claims
- Make the differentiation explicit
- Show why SRH is a better fit than a generic alternative
- Use named facts, programme details, partnerships, or outcomes where relevant

Style rules:
- Avoid generic marketing language such as "cutting-edge," "world-class," or "innovative"
- Avoid filler openings like "In today's fast-changing world"
- Prefer clear, direct, human language
- Write like SRH, not like a generic higher-education blog

Brand requirements:
{source_rules}
{brand_voice_rules}
- Language: {language_label}
- Tone: {tone_label}
- Voice: {voice_label}
- Make the piece feel informed, practical, and distinctively SRH
- Use the SECONDARY knowledge base to sharpen contrast, not to dominate the article
```

**Output sample:**
> *"At SRH University, we recognize the critical need for a curriculum that bridges classical music with contemporary industry demands... With over 9,500 students from more than 140 countries, SRH stands out as an inclusive and diverse institution."*

Version 2 is the most grounded of the three. It opens with a market framing but quickly shifts to SRH's point of view, and grounds that perspective in real data — student numbers, programme structure, alumni outcomes, and competitive contrast with Berlin's public universities. The competitive section is notably sharper: it positions SRH against traditional conservatories and theory-heavy public institutions by name, rather than speaking in generalities.

**What improved:** Real SRH facts throughout, sharper competitive contrast, more confident institutional voice, concrete alumni and outcome references.  
**What's still missing:** Named alumni examples; a few filler phrases ("transformative journey," "dynamic music environment") still remain.

---

## Prompt Iteration Scores: Version 1 vs Version 2

*Note: Generic output is excluded from this comparison as it contains no SRH-specific data or brand grounding.*

| Template | Version 1 Brand Score | Version 2 Brand Score | Version 1 Uniqueness | Version 2 Uniqueness | Main Gap |
|---|---:|---:|---:|---:|---|
| Blog Post | 7/10 | 8.5/10 | 6.5/10 | 8.5/10 | Version 1 reads like a standard analyst blog; Version 2 feels more SRH-led |
| Newsletter | 8.5/10 | 9/10 | 7.5/10 | 8.5/10 | Already the strongest template; Version 2 mainly reduces generic drift |
| Program Description | 7/10 | 8.5/10 | 6/10 | 8/10 | Version 1 reads too brochure-like; Version 2 is more human and brand-native |

---

## Key Takeaways

**What worked**
- Adding explicit Content Requirements and Style Rules had the biggest impact on output quality — telling the model what to include *and* what to avoid
- Grounding prompts in PRIMARY vs SECONDARY knowledge bases kept SRH facts accurate while allowing market context to support rather than dominate
- Concrete anti-patterns in the style rules (e.g. "avoid 'world-class'" or "avoid filler openings") were more effective than abstract tone guidance

**What we'd improve next**
- Getting a real market perspective — ideally from prospective students or recruiters — to validate whether the output actually resonates
- If stakeholders can provide concrete examples of content they love or hate, we can incorporate those as few-shot examples to further improve output consistency
