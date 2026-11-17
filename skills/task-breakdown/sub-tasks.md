# Sub-Task Specificity Rules

Sub-tasks must be concrete enough for a developer new to this codebase to implement without additional research. Apply these rules:

- **External data tasks** must include: source URL, file format, relevant field/column names, expected output volume, and any format-specific quirks (e.g., index-based arrays, separate key mapping files). A task like "parse KJV CSV" is not acceptable — "download `t_kjv.csv` from [URL], columns: `b` (book number), `c` (chapter), `v` (verse), `t` (text), join with `key_english.csv` for book names" is.
- **Service/class tasks** must name the file path, the public interface (method signatures and return types where non-obvious), and any singleton/lifecycle constraints.
- **Database tasks** must name every column with its type, nullability, and index strategy.
- **Test sub-tasks** come before the code they test and name the test file and each test's name and assertion.
- **Verification sub-tasks** must state the exact command to run and the expected observable output (e.g., `Verse.by_language("en").count` ≈ 31,102). Every sub-task ends with such a `_Verify:_` line.
- **Every file is named by its path.** "The config test file" is not acceptable; `test/config.test.ts` is.
- **Tasks that depend on unresolved external information** must be marked `⚠️ BLOCKED` with a clear description of what needs to be known before implementation can begin.
