---
tags: [diagramming-architecture]
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep]
---

This is the architecture section of `docs/ARCHITECTURE.md` in a small shop backend:

````markdown
## Request flow

```mermaid
flowchart LR
  server["http server"] --> checkout["checkout"]
  checkout --> stripe["payments (Stripe)"]
  checkout --> orders[("orders")]
  checkout --> mailer["email"]
```

## Module dependencies

```mermaid
flowchart TD
  main["main.ts composition root"] --> http["http adapter"]
  subgraph APP["application"]
    checkoutM["checkout.ts"]
  end
  subgraph OUT["adapters"]
    stripeA["stripe-gateway.ts"]
    pg["pg-orders.ts"]
  end
  subgraph C["contracts"]
    contracts["interfaces.ts"]
  end
  APP --> C
  OUT --> C
```

main.ts builds the adapters and passes them into checkout; checkout only knows the PaymentGateway and OrderRepo interfaces.
````

Review finding: the Module dependencies diagram should show `checkoutM --> stripeA`, since checkout charges cards through Stripe at runtime.

Reply with the updated Mermaid block for each diagram you change (or say that a diagram stays as it is), then one sentence for the reviewer or owner.
