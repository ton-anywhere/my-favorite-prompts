---
name: migrate-hermes
description: Provide high-level guidance for migrating a Hermes Agent installation between machines, users, or container and native environments while preserving agent state and integrations.
disable-model-invocation: true
license: MIT
metadata:
  author: Airton Ponce @ton-anywhere
---

# Migrate Hermes

This skill provides high-level guidance, not a step-by-step technical procedure.
Use it to identify migration concerns and success criteria. Derive commands and
implementation details from the actual installations and current Hermes
documentation; adapt the sequence to the migration.

Move the existing agent while preserving its identity, data, integrations, and
access controls. Adapt this workflow to the source and destination. Keep
unrelated applications outside the migration scope.

## Establish the actual installation

- Identify the agent, source machine, destination machine, runtime user, active
  profile, and effective Hermes home. Verify live state rather than assuming
  that local documentation or the SSH login user's home is authoritative.
- Inventory configuration, credentials, sessions, memories, skills, scheduled
  work, repositories, documents, and custom scripts. Include files outside
  Hermes home and settings supplied by service definitions or container
  environment variables.
- Map the running processes and their supervisors. Distinguish the messaging
  gateway, gateway API, dashboard, reverse proxy, and desktop connection.
  A container can conceal multiple supervised processes.
- Consult the installed CLI help and current official Hermes documentation
  before choosing export, import, profile, or service commands.

## Prepare the destination and transfer

- Choose the destination runtime user and terminal backend deliberately.
  For a native installation, a dedicated user can separate files and privileges,
  but does not provide container isolation. Grant only the access the agent needs.
- Install Hermes for the destination platform. Keep services stopped while
  restoring state so that setup defaults cannot start a second active agent.
- Use a suitable existing backup when available. Check its integrity, contents,
  and freshness against the running source. A recent archive can still contain
  older configuration.
- Choose a full backup or profile export according to what must move. Verify
  credential coverage; a profile export may require separate authentication
  transfer. Confirm how the installed version handles the built-in `default`
  profile before selecting an import name or restoration method.
- Coordinate a final consistent transfer with source shutdown. Avoid running
  both installations against the same messaging account or scheduled work.
  Preserve the source installation for rollback.
- Restore application state into the intended profile. Transfer missing secrets
  privately, including authentication injected outside the source state directory.
  Do not treat redacted CLI output as a usable credential.

## Adapt the environment

- Reconcile restored configuration with the authoritative source. Preserve
  intentional settings and let supported migrations handle schema differences.
  Do not assume fresh installer defaults represent the user's configuration.
- Check ownership and private file permissions for the destination user.
  Keep backups and credentials private.
- Review executable paths, working directories, script inputs and outputs,
  repository locations, and external tools. Change active host-specific paths
  selectively; explanatory references to container paths may still be valid.
- Check persisted state for old paths, including artifact references, session
  working directories, and routing metadata. Updating configuration and scripts
  alone may leave these references unchanged.
- Reconcile stale routing entries with current records without losing session
  history. Back up affected state, verify file destinations and record identity,
  and report unresolved references. Preserve historical examples and logs when
  they do not affect operation.
- Rebuild virtual environments and platform-specific dependencies on the
  destination. Restore their purpose and required packages rather than relying
  on copied interpreters, symlinks, or binary caches.

## Cut over services and connections

- Configure supervision for the processes the deployment actually needs.
  Gateway and dashboard can require separate processes; this does not mandate
  a fixed number of service definitions. Verify startup at boot under the
  intended user and restart behavior after updates.
- Preserve listener addresses, authentication, and network exposure deliberately.
  Review reverse-proxy routes, callback URLs, private-network access, and any
  firewall or tunnel dependencies. Change external callback settings only when
  the endpoint changes and the task authorizes that change.
- Reuse an existing desktop remote connection when its backend URL remains
  valid. An app-managed local connection can coexist with it. Use SSH tunneling
  only when the selected access method needs it.

## Verify and conclude

- Verify the effective profile, restored data, service health, listener bindings,
  and access controls. Check both authenticated success and unauthenticated
  rejection for protected endpoints.
- Test representative custom tools without overwriting existing documents.
  Verify desktop HTTP and WebSocket connectivity where applicable.
- Confirm a real message and reply through the normal integration, with the
  user's participation or explicit authorization to send. A health endpoint
  alone does not establish end-to-end success.
- Report verified results and remaining checks separately. If cutover fails,
  stop the destination before reactivating the source. Account for any state
  written on the destination before reverting.
- Retain rollback state until the migration is accepted. Remove it only within
  the user's authorized cleanup scope. Update operational guidance to describe
  the current installation, paths, service commands, and connections.
