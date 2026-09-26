This are the following areas the should be covered in this skill:
OBS: Texting can be expanded and refined. Sections must be mantained.

# Cirurgical precision
focus on clear and minimal orientation with cirurgical precision

# Prompt engineering
what can be improved in the system prompt / context files (user & project AGENTS) / user prompts to improve the results
is there any conflicting guidance of what is in the context?

# Harness settings
what can be done using the respective harness to make the performance better. 
ex: disabling skills, disabling tools, disabling system prompt, appending a system prompt.
too many tools available

# Harness engineering
if something cannot be fixed using prompt engineering or the available harness settings, make explicit the harness limitations and bring some implementation ideas for extensions or patches inside that harness.

If it's not possible, changing to another harness could be the solution. You can suggest that.

# Model settings
Verify the current sampling params being sent on the request. Are they correct? Temperature is too high? What are the model card recommendations? Should we put repetition penalties to avoid loops? 

If the ai model is being hosted locally, verify the params that are being served. Are they customized or it's the model default configs? 

Use hugging face cli or mcp if needed.

# Model limitations
Do not immediatly disquality the small model being babysitted.
You must first explore adjustments using `prompt engineering`, `harness settings`, `harness engineering` and model settings before stating it's a model limitation. Smaller models are constantly getting better. They can do a lot when properly babysitted.c
