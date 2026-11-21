# Routing Examples

Worked before/after examples for every destination in the routing table in [SKILL.md](../SKILL.md). One language (Ruby); port freely. Each example shows the comment, where its fact goes, and what the code looks like afterwards.

## Tautology → delete

```ruby
# Set the batch size to 50        →  BATCH = 50
BATCH = 50
```

Nothing to save: the code states the fact.

## Name carries it

```ruby
# Number of times we retry a flaky call
3.times { resp = attempt(endpoint) }
```

```ruby
MAX_RETRIES = 3
MAX_RETRIES.times { resp = attempt(endpoint) }
```

The comment's fact — what the `3` means — moves into the name.

## Extracted method carries it

```ruby
def import(records)
  # Normalize the vendor records
  records.each do |r|
    r.transform_keys!(&:to_sym)
    r[:email] = r[:email].to_s.downcase
  end
  store(records)
end
```

```ruby
def import(records)
  records.each { |r| normalize(r) }
  store(records)
end

def normalize(record)
  record.transform_keys!(&:to_sym)
  record[:email] = record[:email].to_s.downcase
end
```

The block's purpose — which the comment had to state — becomes the method's name, and `import` reads as its table of contents.

## The value belongs in a config file

```ruby
# Vendor API timeout — ops asked for 30s
VENDOR_TIMEOUT = 30
```

The comment was pointing at the real problem: a deployment setting living in source code. The value moves to `config/initializers/vendor.rb`, where comments are allowed:

```ruby
# Vendor API timeout — ops asked for 30s
Vendor.timeout = 30
```

## A test carries it

```ruby
# Prices are always in cents; never floats
def price_for(order)
  (order.total * 100).round
end
```

Two facts, two homes — "cents" moves into the name, "never floats" into a test:

```ruby
def price_cents(order)
  (order.total * 100).round
end
```

```ruby
it "returns integer cents, never a float" do
  expect(price_cents(orders(:one))).to be_a(Integer)
end
```

## A task carries it (excuse)

```ruby
# TODO: remove the manual slice when the vendor fixes pagination
records = fetch_all.first(BATCH)
```

```ruby
records = fetch_all.first(BATCH)
```

The code stays, uncommented, only after `tasks/vendor-pagination.md` exists — the fix-task template is in [artifact-templates.md](artifact-templates.md). An unrecorded excuse is a lost bug report.

## An ADR carries it

```ruby
# The legacy v1 endpoint stays until Billing migrates off its reader
def fetch_all
  LegacyApi.v1.jobs
end
```

```ruby
def fetch_all
  LegacyApi.v1.jobs
end
```

Plus `docs/adr/0007-legacy-v1-jobs-endpoint.md`:

```markdown
# Jobs imports read the legacy v1 endpoint

Billing still reads job records from the v1 schema; switching to v2 before
their reader migrates would desync their exports. `fetch_all` stays on the
legacy v1 endpoint until that migration lands.
```

The qualification rule for ADRs is in [artifact-templates.md](artifact-templates.md).

## A document carries it

```ruby
# Usage: ApiClient.new(token).fetch_batch(50) — raises TimeoutError after 30s
class ApiClient
```

The class carries no prose. The usage lives in the module's document (`app/README.md`, or the project's usage guide):

````markdown
# ApiClient

Fetches batches of vendor records.

```ruby
client = ApiClient.new(token)
client.fetch_batch(50)
```

`fetch_batch` raises `TimeoutError` when the vendor does not answer within 30s.
````

In a project whose convention is doc comments (YARD, rustdoc, godoc), the API usage goes into the doc comment instead of a separate file — see *Doc comments* in [SKILL.md](../SKILL.md).
