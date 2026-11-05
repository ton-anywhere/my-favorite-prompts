// Shared by the TypeScript audits: argument handling and `it(...)`/`test(...)` example extraction.
import { existsSync, globSync, readFileSync } from "node:fs";

export type Example = { line: number; desc: string; display: string; body: string };

const EXAMPLE = /^\s*(?:it|test|specify)(?:\.(?:only|skip|todo))?\s*\(\s*(["'`])(.*?)\1/;
const MAX_DESC = 72;
const USAGE = "Usage: condition_word_audit.ts|expectation_count_audit.ts SPEC_FILE [SPEC_FILE ...] | --all";

export function specFiles(args: string[]): string[] {
	if (args.includes("-h") || args.includes("--help")) {
		console.log(USAGE);
		process.exit(0);
	}
	const all = args.includes("--all");
	if (all && args.length > 1) fail("Use either --all or explicit spec file paths, not both.");
	if (!all && args.length === 0) fail(USAGE);
	if (all) {
		return globSync("**/*.{test,spec}.{ts,tsx,mts,js,mjs}", { exclude: (path) => path.includes("node_modules") }).sort();
	}
	const missing = args.filter((path) => !existsSync(path));
	if (missing.length > 0) fail(`Spec file not found: ${missing.join(", ")}`);
	return args;
}

function fail(message: string): never {
	console.error(message);
	process.exit(2);
}

// shortcut: parentheses inside strings or regex literals in the example body skew the depth count;
// upgrade to the TypeScript parser if that produces wrong spans.
export function examples(file: string): Example[] {
	const lines = readFileSync(file, "utf8").split("\n");
	const found: Example[] = [];
	lines.forEach((line, index) => {
		const match = EXAMPLE.exec(line);
		if (!match) return;
		const desc = match[2];
		const display = desc.length > MAX_DESC ? `${desc.slice(0, MAX_DESC - 3)}...` : desc;
		found.push({ line: index + 1, desc, display, body: bodyFrom(lines, index) });
	});
	return found;
}

// The example's call spans from its `it(` line until its parentheses balance.
function bodyFrom(lines: string[], start: number): string {
	let depth = 0;
	const body: string[] = [];
	for (const line of lines.slice(start)) {
		body.push(line);
		for (const char of line) {
			if (char === "(") depth += 1;
			else if (char === ")") depth -= 1;
		}
		if (depth <= 0) break;
	}
	return body.join("\n");
}
