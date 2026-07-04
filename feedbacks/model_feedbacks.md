
## Models Feedbacks

Model (Agent)
Qwen 3 Coder 30B MoE Q8 (build agent)
Date: 8/05/2026
It was very very instable, difficult to steer, couldn't handle code reviews well, deleted a bunch of review files when received a review saying it had to clean .bak files it created previously.
Very bad experience overall. will change for another more grounded model.

Model (Agent)
GLM 4.7 flash  (build agent)
Date: 10/05/2026
Many tool call errors. Was not able to conclude the task.

Gemma 4 MoE Q8 (gemma build agent)
Date: 11/05/2026
It performed the adjustments from reviews, but it failed to load relevant skills even at low temps(0.15) and 0.8 top_p. Because of that, it couldn't stop introducing new issues to the code. Seems interesting for some live coding, coding assisting, but not useful for reliable agentic coding

Gemma 4 31B (Dense - build agent)
28/06/2026
Outputting `$\rightarrow$` instead of `->` because it was trained onLaTeX format. I need to parse them or use a formatter on the output. Regex?
