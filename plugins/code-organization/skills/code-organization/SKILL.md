---
name: code-organization
description: Decide where a function belongs — local to a feature, or extracted into a helper, formatter, validator, service, repository, or domain module — and which file it goes in. Use when about to create a new helper/util/service file, when extracting or deduplicating logic, when the same logic appears in a second place, or when asked where a function should live. Do NOT use for bug fixes, styling, or new isolated feature code with no shared logic.
---

# Code Organization

Optimize for **discoverability, responsibility, and maintainability — not maximum reuse.**
A reusable function nobody can find is not a successful abstraction.

## 0. Scope discipline (applies first)

- Only reorganize code the current task already touches.
- Duplicated code found nearby is not a reason to refactor it now — mention it, don't fix it.
- Never restructure folders or introduce a new architectural pattern unless explicitly asked.
- Preserve behavior. Extraction is a move, not a rewrite.

## 1. The extraction rule

Keep logic where it is by default. **Extract on the second caller, not the first.**

Extract only when BOTH hold:

1. Either it is already used by 2+ unrelated features, **or** the operation is generic and stable independent of any feature (date math, currency formatting, email validation); and
2. it stays free of feature-specific state after extraction — no UI context, no feature controllers, no global mutable state, no feature models.

If (1) is true but nothing reuses it yet, keep it local. If unsure, keep it local.

Not reasons to extract: the function is long, the file is large, it *could* be reused someday, it is only a few lines.

If the extracted function needs feature-specific arguments just to satisfy one caller, extraction is wrong.

## 2. Pick the right abstraction

| Category | Signal | Example |
|---|---|---|
| Helper | small, pure, generic computation | `calculateDistance()`, `daysBetween()` |
| Formatter | data → display output | `formatCurrency()`, `formatDateTime()` |
| Validator | input or domain validation | `isValidEmail()`, `validateOrder()` |
| Service | talks to APIs, SDKs, device, app state, or several repositories | `syncOrdersFromServer()` |
| Repository | data access and persistence | `getOrders()`, `saveOrder()` |
| Domain | a meaningful business rule | `calculateTreatmentEligibility()` |

Two frequent mistakes:

- Anything that needs a network/database/SDK dependency is a **service or repository**, never a helper.
- A business rule stays in the domain/model/use-case layer even when it is reusable. Reusable ≠ helper.

## 3. Where the file goes

Inspect the existing tree first and follow it. Consistency with the current codebase beats a cleaner pattern.

Default mapping when the project has no strong convention:

```
helper / formatter / validator  →  shared (or common) utilities layer, one file per domain
service                         →  services layer
repository                      →  data layer
domain rule                     →  domain / model / use-case layer for that feature
feature-local                   →  beside the screen, controller, or module that uses it
```

Stack examples:

- **Flutter/Dart** — `lib/shared/helpers/<domain>_helper.dart`, `lib/services/<domain>_service.dart`, `lib/data/repositories/<domain>_repository.dart`, `lib/domain/<feature>/`
- **Frappe/ERPNext (Python)** — generic utils in `<app>/<app>/utils/<domain>.py`, whitelisted endpoints in `<app>/<app>/api/<domain>.py`, business rules in the DocType controller that owns the document. Never put business rules in `utils/`.
- **JS/TS** — `src/lib/<domain>.ts`, `src/services/`, `src/repositories/`, feature-local files inside the feature folder.

**New file threshold:** create a new file only when it will hold 3+ related functions. For a single function, put it in the nearest existing module that already owns that responsibility.

Name by responsibility, not implementation: `date_helper`, `currency_formatter`, `order_repository`, `email_validator`. Avoid `utils`, `common`, `misc`, `general_helper`, `functions` — and avoid near-duplicates like `date_helper` + `date_utils` + `datetime_helper` in the same project.

Never let one file collect unrelated responsibilities (formatting + validation + uploads + device info). If that has happened, split by responsibility — but only if the task already touches that file.

## 4. Search before creating anything

Run all three before writing a new file:

```bash
rg -n "functionName|similar_name"          # same or similar name
rg -n "format|isValid|calculate|parse" <shared-dir>/   # equivalent logic elsewhere
ls <shared-dir> <services-dir> <repositories-dir>      # who already owns this responsibility
```

If an existing module already owns the responsibility, extend it instead of creating a new one.

## 5. Dependency direction

```
Feature  →  Service / Repository / Domain  →  Shared helper
```

Shared code must never import feature code (controllers, screens, feature models). If extraction would create a back-edge or a cycle, the design is wrong — pass the value in as a parameter instead.

Keep the public API minimal: meaningful parameter and return types, no internal details exposed.

## 6. Finish the move

After extracting:

1. Update every call site — `rg -n "<oldFunctionName>"` must return only the new definition and its callers.
2. Delete the old implementation. Do not leave both unless backward compatibility genuinely requires it.
3. Run the project's checks: analyzer/linter, formatter, and the test suite (e.g. `flutter analyze && dart format`, `bench run-tests --app <app>`, `npm run lint && npm test`).
4. Add a unit test if the extracted function is pure — that is the main payoff of extraction.

## 7. Cross-project sharing

Do not promote code into a shared package until 2+ projects actually consume it and its API has stopped changing. Duplication across repos is cheaper than a premature shared package.

## Gate before creating or extracting

- [ ] Does an equivalent function or module already exist?
- [ ] Is there a real second caller, or is it clearly generic and stable?
- [ ] Can it be free of feature-specific state?
- [ ] Is this the right category — helper vs service vs repository vs domain?

If any answer is no, leave the logic where it is.
