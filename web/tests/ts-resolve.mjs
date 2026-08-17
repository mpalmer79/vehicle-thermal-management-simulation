/**
 * Test-only module resolution hook.
 *
 * Node's ESM loader requires explicit file extensions, while the application source
 * uses the extensionless relative imports that Next.js and TypeScript expect. This hook
 * bridges the two so `node --test` can execute the TypeScript modules directly (via
 * Node's built-in type stripping) without adding a bundler, a transpiler, or a
 * dependency, and without changing how the app itself imports modules.
 */

import { existsSync } from "node:fs";
import { registerHooks } from "node:module";
import { fileURLToPath } from "node:url";

const HAS_EXTENSION = /\.[cm]?[jt]sx?$|\.json$/;

registerHooks({
  resolve(specifier, context, nextResolve) {
    const relative = specifier.startsWith(".") || specifier.startsWith("/");
    if (relative && !HAS_EXTENSION.test(specifier) && context.parentURL) {
      for (const suffix of [".ts", ".tsx", "/index.ts"]) {
        const candidate = new URL(specifier + suffix, context.parentURL);
        if (existsSync(fileURLToPath(candidate))) {
          return { url: candidate.href, shortCircuit: true };
        }
      }
    }
    return nextResolve(specifier, context);
  },
});
