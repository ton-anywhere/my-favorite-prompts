# Skill Access Control System

## Overview

This directory contains centralized configuration for controlling which skills are available to which agents.

## Files

- `registry.yaml` — Master registry of all skills and their access restrictions

## How It Works

### Default Behavior (Opt-Out Model)

By default, **all skills are available to all agents**. To restrict access:

```yaml
skill-name:
  description: "What this skill does"
  blocked_agents:
    - agent-that-cant-use-this
```

### Special Grants (Opt-In Override)

If you need a skill that ONLY specific agents can use:

```yaml
sensitive-skill:
  description: "Restricted capability"
  granted_agents:
    - build-agent  # Only this agent can use it
```

When `granted_agents` is set, it overrides `blocked_agents` — only listed agents have access.

## Integration Guide

### For Orchestrators / Tech Lead Agents

Before dispatching an agent or presenting available skills, filter using this logic:

```ruby
def get_available_skills(agent_name, registry)
  available = []

  registry.each do |skill_name, config|
    next unless config.is_a?(Hash)

    # Check opt-in restriction first
    if config.key?('granted_agents')
      available << skill_name if config['granted_agents'].include?(agent_name)
      next
    end

    # Check opt-out blocklist
    blocked = Array(config.fetch('blocked_agents', []))
    next if blocked.include?(agent_name)

    # Default: allowed
    available << skill_name
  end

  available.sort
end
```

### Example Usage

**Scenario:** qwen-plan-agent loads and requests available skills

**Result:** All skills EXCEPT `writing-plans`

```ruby
>> get_available_skills("qwen-plan-agent", registry)
=> ["brainstorming", "code-comments", ..., "test-driven-development", ...]
# writing-plans is NOT in the list
```

**Scenario:** build-agent loads

**Result:** ALL skills including `writing-plans`

## Adding a New Skill

1. Add entry to `registry.yaml`:
   ```yaml
   new-skill:
     description: "What it does"
     blocked_agents: []
   ```

2. If restrictions needed, update `blocked_agents` or add `granted_agents`

3. Done — no changes needed anywhere else!

## Adding a New Agent

Nothing! The agent automatically gets access to all unblocked skills.

If you want to restrict what they can use, add them to relevant `blocked_agents` lists in the registry.

## Audit Commands

### See all blocked combinations
```bash
grep -A2 "blocked_agents:" config/skills/registry.yaml | grep -v "^--$" | grep -v "^.$"
```

### Check if specific skill is blocked from agent
```bash
grep -A5 "^writing-plans:" config/skills/registry.yaml
```

## Philosophy

- **Centralized control**: One source of truth for all restrictions
- **Minimal per-agent config**: Agent files stay focused on behavior, not permissions
- **Explicit over implicit**: Hard-coded rules, not model inference
- **Scales gracefully**: O(1) cost per new skill, O(0) per new agent
