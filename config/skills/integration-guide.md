# Skill Filtering Integration Guide

## Quick Start

Add this section to your orchestrator's system prompt (e.g., Tech Lead):

---

## Available Skills Filter

Before presenting skills to subagents or yourself, apply these filters:

### Step 1: Load Registry
Read `/config/skills/registry.yaml`

### Step 2: Apply Filters
For each skill, check:

1. **If `granted_agents` exists:** Only listed agents can use it
2. **Else if in `blocked_agents`:** Agent cannot use it  
3. **Otherwise:** Skill is available

### Current Restrictions

| Skill | Blocked From | Reason |
|-------|--------------|--------|
| writing-plans | qwen-plan-agent | Generates full code; plan agent should use metacode only |

### Example Decision Table

| Agent | Requesting Skill | Allowed? |
|-------|------------------|----------|
| qwen-plan-agent | writing-plans | ❌ NO — blocked |
| qwen-plan-agent | brainstorming | ✅ YES — no restrictions |
| build-agent | writing-plans | ✅ YES — not blocked |
| build-agent | any-skill | ✅ YES — no restrictions |

---

## Verification Checklist

When an agent requests a skill:

- [ ] Check if skill has `granted_agents` restriction
- [ ] If yes, verify requesting agent is in the list
- [ ] Check if skill has `blocked_agents` containing requester
- [ ] If blocked, deny and explain why (reference the reason field)
- [ ] Otherwise, allow

## Denial Message Template

```
The requested skill "[skill-name]" is not available to this agent.

Reason: [reason from registry]

Available alternatives: [list 1-2 similar unrestricted skills]
```

Example:
```
The requested skill "writing-plans" is not available to this agent.

Reason: Plan agent should provide architectural guidance using metacode only. 
This skill generates complete implementation code which doesn't follow project 
conventions and pollutes build agent context.

Available alternatives: Use inline architectural descriptions with metacode comments,
or dispatch build-agent for detailed implementation planning.
```
