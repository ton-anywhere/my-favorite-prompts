---
name: create-prd
description: Use when the owner asks for a product requirements document (PRD) for a new product, MVP, or feature whose scope is not yet settled (/create-prd <idea>).
disable-model-invocation: true
license: Apache-2.0 (see LICENSE)
metadata:
  author: Airton Ponce @ton-anywhere
  source: https://github.com/snarktank/ai-dev-tasks/blob/main/create-prd.md
  fork: https://github.com/ton-anywhere/ai-dev-tasks
  original-author: Ryan Carson @snarktank
  modified: Rewritten by Airton Ponce from the Apache-2.0 original (codebase audit, INVEST validation, deferred-phase and data-dependency sections).
---

# Rule: Generating a Product Requirements Document (PRD)

## Goal

To guide an AI assistant in creating a detailed Product Requirements Document (PRD) in Markdown format, based on an initial user prompt. The PRD should be clear, actionable, and suitable for a junior developer to understand and implement the feature.

## Process

1.  **Receive Initial Prompt:** The user provides a brief description or request for a new feature or functionality.
2.  **Audit Current State:** Before asking any questions, read the existing codebase to understand current infrastructure, tech stack, and architectural decisions already in place. Check `docker-compose.yml`, `Gemfile`/`package.json`, config files, and any existing docs. This prevents the PRD from describing infra or constraints that contradict what's already built. *For greenfield projects with no existing code: skip the audit, but ensure the PRD's Technical Considerations section captures the key tech stack choices (framework, database, hosting) as decisions to be made or confirmed — don't leave them implicit.*
3.  **Ask Clarifying Questions:** Before writing the PRD, the AI *must* ask only the most essential clarifying questions needed to write a clear PRD. Limit questions to 3-5 critical gaps in understanding. The goal is to understand the "what" and "why" of the feature, not necessarily the "how" (which the developer will figure out). Make sure to provide options in letter/number lists so I can respond easily with my selections.
4.  **Generate PRD:** Based on the initial prompt and the user's answers to the clarifying questions, generate a PRD using the structure outlined below.
5.  **INVEST Validation:** Before saving, review every Functional Requirement against the INVEST checklist and fix any violations:
    - **Independent**: Can this requirement be implemented and tested without depending on another unfinished requirement?
    - **Negotiable**: Does it describe the *outcome* (what the user needs), not the *mechanism* (how to build it)? Avoid prescribing implementation details unless they are firm architectural decisions.
    - **Valuable**: Does it deliver value on its own, or does it only have value when bundled with several others?
    - **Estimable**: Is it specific enough to estimate? (i.e., does it name data sources, expected volumes, formats, or interfaces where relevant?)
    - **Small**: Can it be delivered in a single iteration? If not, split it.
    - **Testable**: Is there a clear, observable way to verify it's done?
6.  **Save PRD:** Save the generated document as `prd-[feature-name].md` inside the `/tasks` directory.

## Clarifying Questions (Guidelines)

Ask only the most critical questions needed to write a clear PRD. Focus on areas where the initial prompt is ambiguous or missing essential context. Common areas that may need clarification:

*   **Problem/Goal:** If unclear - "What problem does this feature solve for the user?"
*   **Core Functionality:** If vague - "What are the key actions a user should be able to perform?"
*   **Scope/Boundaries:** If broad - "Are there any specific things this feature *should not* do?"
*   **Success Criteria:** If unstated - "How will we know when this feature is successfully implemented?"
*   **Data Scope:** If the feature involves external data - "What data sources are involved? Which languages, translations, APIs, or datasets must be supported in the MVP vs. later?"

**Important:** Only ask questions when the answer isn't reasonably inferable from the initial prompt. Prioritize questions that would significantly impact the PRD's clarity.

### Formatting Requirements

- **Number all questions** (1, 2, 3, etc.)
- **List options for each question as A, B, C, D, etc.** for easy reference
- Make it simple for the user to respond with selections like "1A, 2C, 3B"

### Example Format

```
1. What is the primary goal of this feature?
   A. Improve user onboarding experience
   B. Increase user retention
   C. Reduce support burden
   D. Generate additional revenue

2. Who is the target user for this feature?
   A. New users only
   B. Existing users only
   C. All users
   D. Admin users only

3. What is the expected timeline for this feature?
   A. Urgent (1-2 weeks)
   B. High priority (3-4 weeks)
   C. Standard (1-2 months)
   D. Future consideration (3+ months)
```

## PRD Structure

The generated PRD should include the following sections:

1.  **Introduction/Overview:** Briefly describe the feature and the problem it solves. State the goal.
2.  **Goals:** List the specific, measurable objectives for this feature.
3.  **User Stories:** Detail the user narratives describing feature usage and benefits.
4.  **Functional Requirements:** List the specific functionalities the feature must have. Use clear, concise language (e.g., "The system must allow users to upload a profile picture."). Number these requirements. Each requirement must describe the *outcome*, not prescribe the implementation mechanism.
5.  **Non-Goals (Out of Scope):** Clearly state what this feature will *not* include to manage scope.
6.  **Deferred to Future Phase:** List requirements that are intentionally out of scope for the MVP but planned for later. Include a one-line rationale for each deferral (e.g., "SQLite compatibility — deferred to mobile phase; current web app targets PostgreSQL only").
7.  **Data & External Dependencies:** For any feature that ingests, syncs, or depends on external data, enumerate: source name, URL or API endpoint, data format (CSV/JSON/etc.), relevant fields/schema, expected volume, and any licensing considerations. Leave blank if not applicable.
8.  **Design Considerations (Optional):** Link to mockups, describe UI/UX requirements, or mention relevant components/styles if applicable.
9.  **Technical Considerations (Optional):** Mention any known technical constraints, dependencies, or suggestions (e.g., "Should integrate with the existing Auth module"). For each technical decision, note whether it is **MVP-critical** or **deferrable**.
10. **Success Metrics:** How will the success of this feature be measured? (e.g., "Increase user engagement by 10%", "Reduce support tickets related to X").
11. **Open Questions:** List any remaining questions or areas needing further clarification.

## Target Audience

Assume the primary reader of the PRD is a **junior developer**. Therefore, requirements should be explicit, unambiguous, and avoid jargon where possible. Provide enough detail for them to understand the feature's purpose and core logic.

## Output

*   **Format:** Markdown (`.md`)
*   **Location:** `/tasks/`
*   **Filename:** `prd-[feature-name].md`

## Final instructions

1. Do NOT start implementing the PRD
2. Audit the current codebase state before asking questions
3. Make sure to ask the user clarifying questions
4. Take the user's answers to the clarifying questions and improve the PRD
5. Run the INVEST validation pass before saving — fix any requirements that fail
