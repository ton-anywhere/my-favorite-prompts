#!/usr/bin/env -S node --experimental-strip-types
// Scan node:test / Vitest / Jest example names for BDD structure-smell keywords.
//
// Usage:
//   node --experimental-strip-types skills/verify-specs/scripts/ts/condition_word_audit.ts test/example.test.ts
//   node --experimental-strip-types skills/verify-specs/scripts/ts/condition_word_audit.ts --all
import { examples, specFiles } from "./spec_examples.ts";

const TRIGGERS: Record<string, string> = {
	when: "condition",
	with: "condition",
	without: "condition",
	for: "condition",
	and: "split",
};

let total = 0;
let fileCount = 0;
for (const file of specFiles(process.argv.slice(2))) {
	const hits = examples(file).flatMap((example) => {
		const words = Object.keys(TRIGGERS)
			.filter((word) => new RegExp(`\\b${word}\\b`, "i").test(example.desc))
			.sort();
		if (words.length === 0) return [];
		const kinds = [...new Set(words.map((word) => TRIGGERS[word]))].sort().join("/");
		return [`  Line ${String(example.line).padEnd(4)} [?] ${example.display.padEnd(72)}  ${kinds}: ${words.map((w) => `"${w}"`).join(", ")}`];
	});
	if (hits.length === 0) continue;
	console.log(`${file}\n${hits.join("\n")}\n`);
	total += hits.length;
	fileCount += 1;
}
console.log(`Summary: ${total} candidate(s) across ${fileCount} file(s)`);
console.log("Note: candidates require reviewer judgment; this does not replace the full verify-specs review.");
