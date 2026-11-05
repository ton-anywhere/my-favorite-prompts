#!/usr/bin/env -S node --experimental-strip-types
// Scan node:test / Vitest / Jest examples for more than one assertion call.
//
// Usage:
//   node --experimental-strip-types skills/verify-specs/scripts/ts/expectation_count_audit.ts test/example.test.ts
//   node --experimental-strip-types skills/verify-specs/scripts/ts/expectation_count_audit.ts --all
import { examples, specFiles } from "./spec_examples.ts";

// assert(...), assert.equal(...), t.assert.ok(...), expect(...)
const ASSERTION = /\b(?:assert(?:\.\w+)?|expect)\s*\(/g;

let total = 0;
let fileCount = 0;
for (const file of specFiles(process.argv.slice(2))) {
	const hits = examples(file).flatMap((example) => {
		const count = example.body.match(ASSERTION)?.length ?? 0;
		return count > 1
			? [`  Line ${String(example.line).padEnd(4)} [?] ${example.display.padEnd(72)}  assertion calls: ${count}`]
			: [];
	});
	if (hits.length === 0) continue;
	console.log(`${file}\n${hits.join("\n")}\n`);
	total += hits.length;
	fileCount += 1;
}
console.log(`Summary: ${total} multi-assertion example(s) across ${fileCount} file(s)`);
console.log("Note: candidates require reviewer judgment; this does not replace the full verify-specs review.");
