/**
 * Test-only module resolution hook.
 *
 * Node's ESM loader requires explicit file extensions, import attributes for JSON, and
 * knows nothing about the `@/*` path alias, while the application source uses all three
 * because that is what Next.js and TypeScript expect. This hook bridges the gap so
 * `node --test` can execute the TypeScript modules directly (via Node's built-in type
 * stripping) without adding a bundler, a transpiler, or a dependency — and without
 * changing how the app itself imports modules.
 */

import { existsSync } from "node:fs";
import { registerHooks } from "node:module";
import { fileURLToPath, pathToFileURL } from "node:url";
import path from "node:path";

const WEB_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const HAS_EXTENSION = /\.[cm]?[jt]sx?$|\.json$/;

function resolveCandidate(specifier, parentURL) {
  // `@/lib/x` → `<web root>/lib/x`
  const base = specifier.startsWith("@/")
    ? pathToFileURL(path.join(WEB_ROOT, specifier.slice(2))).href
    : specifier;

  const isFileLike = base.startsWith(".") || base.startsWith("/") || base.startsWith("file:");
  if (!isFileLike) return undefined;

  const url = base.startsWith("file:") ? new URL(base) : new URL(base, parentURL);

  if (HAS_EXTENSION.test(url.pathname)) {
    return existsSync(fileURLToPath(url)) ? url : undefined;
  }

  for (const suffix of [".ts", ".tsx", "/index.ts"]) {
    const candidate = new URL(url.href + suffix);
    if (existsSync(fileURLToPath(candidate))) return candidate;
  }

  return undefined;
}

registerHooks({
  resolve(specifier, context, nextResolve) {
    const url = resolveCandidate(specifier, context.parentURL);
    if (!url) return nextResolve(specifier, context);

    // JSON modules need an explicit import attribute that the app source omits,
    // because the bundler supplies it instead.
    if (url.pathname.endsWith(".json")) {
      return { url: url.href, shortCircuit: true, format: "json", importAttributes: { type: "json" } };
    }

    return { url: url.href, shortCircuit: true };
  },
});
