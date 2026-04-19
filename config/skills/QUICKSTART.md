# Skill Access Control — Quick Reference

## 📁 Files Created

```
config/skills/
├── registry.yaml        # Master configuration
├── skill_registry.rb    # Verification utility (Ruby)
├── README.md            # Full documentation
└── integration-guide.md # How to integrate with agents
```

## 🔧 Commands

### Audit all restrictions
```bash
ruby config/skills/skill_registry.rb audit
```

### List available skills for an agent
```bash
ruby config/skills/skill_registry.rb list <agent-name>
# Example:
ruby config/skills/skill_registry.rb list qwen-plan-agent
```

### Check if specific skill is allowed
```bash
ruby config/skills/skill_registry.rb check <skill> <agent>
# Example:
ruby config/skills/skill_registry.rb check writing-plans qwen-plan-agent
```

## ➕ Adding Restrictions

Edit `config/skills/registry.yaml`:

```yaml
existing-skill:
  description: "What it does"
  blocked_agents:
    - new-agent-to-block
  reason: "Why this restriction exists"
```

## 🎯 Current State

| Skill | Blocked From |
|-------|-------------|
| writing-plans | qwen-plan-agent |

**All other skills:** Available to everyone

## ✅ Verification Results

```bash
$ ruby config/skills/skill_registry.rb list qwen-plan-agent
Available: 15 skills
Blocked:   writing-plans ❌

$ ruby config/skills/skill_registry.rb check writing-plans build-agent
✅ ALLOWED — Allowed by default
```

## 🔗 Next Steps

1. **Integrate into Tech Lead agent** — Add filtering logic from integration-guide.md
2. **Test with real dispatches** — Verify qwen-plan-agent can't access writing-plans
3. **Add more restrictions as needed** — Edit registry.yaml, run audit to verify
