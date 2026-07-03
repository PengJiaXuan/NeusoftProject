# Gemini Shadow AIME Failure Audit

Source files:
- Raw: `c:\Users\admin\Desktop\Test\hidden_fork\results\runs\formal_shadow_rerun_v1\raw\gemini-3-flash__shadow__aime.json`
- Scored: `c:\Users\admin\Desktop\Test\hidden_fork\results\runs\formal_shadow_rerun_v1\scored\gemini-3-flash__shadow__aime.json`

Headline findings:
- Total items audited: `30`
- Correct items: `0/30`
- Items with any explicit final-answer marker (`Final Answer`, `boxed`, etc.): `0/30`
- Items where the parser extracted a tail integer anyway: `27/30`
- Items with no parseable tail integer at all: `3/30`
- Items whose ending appears abruptly cut off: `30/30`

Category counts:
- `unfinished_no_parseable_integer`: `3`
- `unfinished_tail_integer_misparse`: `27`

Interpretation:
- This is a protocol-level failure, not a simple set of wrong final answers.
- All 30 responses contain reasoning text, but none contain a valid final-answer marker.
- In 27 cases the scorer grabbed an incidental tail integer from unfinished reasoning.
- In 3 cases there was not even a parseable tail integer to grab.

Illustrative examples:
- `AIME_2025_I_1`: parsed `056` vs correct `070`. Tail: `s appearing in the numbers. I'll need to explore the factors of 56 to make sure the values of *b* don't violate the base-b representation.   To find the sum of all integer bases $b`
- `AIME_2025_I_9`: parsed `None` vs correct `062`. Tail: `nal parabola to $(x', y')$ on the rotated one. The next step is to express $x$ and $y$ in terms of $x'$ and $y'$ to find the new equation.   The original parabola $P_1$ is given by`
- `AIME_2025_II_5`: parsed `None` vs correct `336`. Tail: `ed, including noting the nine-point circle $\mathcal{N}$ and that $D, E, F$ lie on it.  Now, I need to investigate the other points on $\mathcal{N}$.   To find the sum $\widehat{DE`

Conclusion:
- The rerun confirms that `Gemini 3 Flash / Shadow / AIME = 0.0` is a real reproduced outcome under the current shadow protocol.
- The immediate cause is not missing capture; it is the absence of valid final integer answers in all 30 saved responses.