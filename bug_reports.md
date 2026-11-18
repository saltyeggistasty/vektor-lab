# Bug Report: Calculus operators in the input are mishandled (Integrals & Limits tool)

## Summary
When the input field already contains a calculus operation in LaTeX
(e.g. `\int x dx`), the app handles it inconsistently:
- `\int` appears to be evaluated once by the parser and then applied AGAIN
  by the selected mode, giving silently wrong answers.
- `\frac{d}{dx}` is not recognised as a derivative at all and fails with
  "Unknown symbols: d, dx".
- Definite mode has separate Lower/Upper bound fields that can conflict
  with bounds written in the editor.
Wrong answers are returned with no warning, which is the most serious part.
Because the cause is probably in shared parsing logic, EVERY operator and
mode must be audited, not just the ones observed below.

## Environment
- Local Flask app at 127.0.0.1:5000 ("Nabla Workspace")
- Tool: Integrals & Limits (other tools exist via "Select Tool"; see audit scope)
- Input: math editor field producing LaTeX. Its context menu (Insert matrix,
  Insert, Mode, Font style, Color, Background color, Cut/Copy/Paste) looks like
  MathLive; VERIFY by checking the frontend source.
- Modes: Definite Integral, Indefinite Integral, Limit, Derivative (d/dx),
  Finite sum (Σ), Exponential & Log
- Extra fields: Lower bound a, Upper bound b (Definite), Derivative order n
  (1-12), Evaluation point x (optional)

## Observations so far
| # | Input (LaTeX)        | Mode       | Extra fields        | Observed            | Expected                          |
|---|----------------------|------------|---------------------|---------------------|-----------------------------------|
| 1 | `\int_1^2 x dx`      | Indefinite | none                | 3x/2 + C            | x²/2 + C (or a mode-mismatch warning) |
| 2 | `\int x dx`          | Indefinite | none                | x³/6 + C            | x²/2 + C                          |
| 3 | `\int_1^2 x dx`      | Definite   | a=0, b=3            | 4.5                 | 3/2 (editor bounds) or a conflict warning |
| 4 | `\frac{d}{dx} x^3`   | Derivative | order/point greyed  | Error: "Unknown symbols: d, dx" | 3x²                  |

Reproduction: paste the LaTeX into the Function f(x) field, select the mode,
click Compute. Likely not paste-specific. Likely affects many other inputs.

## Analysis

### Observations 1 and 2: double integration (strong evidence)
Both wrong answers equal the correct answer integrated a second time
with respect to x:
- x²/2 integrated again = x³/6   (matches #2)
- 3/2 (definite result) integrated again = 3x/2   (matches #1)
So the limits are NOT leaking into the integrand; the integral is performed twice.

### Observation 3: ambiguous, three explanations all give 4.5
- (a) Editor bounds ignored, integrand x, fields used: ∫₀³ x dx = 4.5
- (b) Integrand already integrated once (x²/2): ∫₀³ x²/2 dx = 27/6 = 4.5
- (c) Parser first evaluated `\int_1^2 x dx` = 3/2, then the mode integrated
  the constant 3/2 over 0..3: 3/2 × 3 = 4.5
(b) and (c) are consistent with the double-integration hypothesis and with #1.
Do not conclude from #3 that the editor bounds were "ignored".

### Observation 4: parser does not recognise `\frac{d}{dx}`
The parser reads it as an ordinary fraction d / dx × x³, and symbol
validation rejects `d` and `dx`. This CONTRADICTS the earlier prediction
that it would double-apply and return 6x. Operator support is therefore
inconsistent: `\int` is parsed and evaluated, `\frac{d}{dx}` is not parsed
as an operator. `\lim`, `\sum`, `\prod`, `\partial` and all others must be
tested individually. Never assume one operator behaves like another.

## Hypotheses (most likely first)
1. **Parser evaluates the integral, then the mode handler integrates again.**
   The LaTeX-to-SymPy step (latex2sympy / latex2sympy2 / sympy parse_latex)
   turns `\int x dx` into an evaluated result (x²/2), and the handler calls
   `integrate(expr, x)` on it. Look for: `integrate(parse(latex), x)`.
2. **Input wrapped in a template.** The backend or frontend may build
   `\int {user_input} dx`, producing `\int \int x dx dx`. Check the exact
   string sent in the request and the exact string passed to the parser.
3. **Parser auto-evaluates some operators.** Integrals (and possibly limits
   and sums) are evaluated during parsing, while derivatives are not
   recognised. Any mode that re-applies the operation double-applies it.
4. **Two code paths both run.** One path handles operators detected in the
   LaTeX, another handles the dropdown mode, for the same request.

## Second issue: two conflicting sources of bounds
The editor can contain bounds (`\int_1^2`) and Definite mode also shows
Lower/Upper bound fields. When they disagree, the result is wrong or
confusing with no warning. Expected: pre-fill and lock the fields from the
editor bounds, hide them when the editor already has bounds, or warn on conflict.

## Third issue: possible placeholder values
In Derivative mode, "Derivative order" (1) and "Evaluation point" (2) look
greyed out. Confirm whether they are placeholders or real values, and whether
placeholder text is submitted when the field is empty. (A default evaluation
point of 2 being submitted would silently change results.)

---

# NEW: Exhaustive operator audit

## Rules for the AI (read first)
1. **Enumerate from the code, not from this report.** Before testing, build an
   inventory of every operator and input path the app supports by reading:
   (a) the editor's Insert submenu and any toolbar/virtual keyboard definitions,
   (b) every LaTeX command the parser/preprocessor recognises or special-cases,
   (c) every mode handler and its extra fields in the backend,
   (d) the example-usage rows. Anything found in code that is not listed below
   must be added to the audit. This list is a minimum, not a ceiling.
2. **Reproduce before fixing.** Write each test, run it against the current code,
   and record the actual output BEFORE changing any code.
3. **Never edit an expected value to match the output.** Expected values below
   come from mathematics. If one seems wrong, flag it in the report instead.
4. **Classify every test result** as one of:
   - PASS: correct result
   - PASS-WARN: explicit, accurate warning or error message instead of a result
   - FAIL-VISIBLE: crash, stack trace, or confusing error for valid input
   - FAIL-SILENT: wrong result with no warning (highest severity)
5. **Report coverage honestly.** At the end, output a coverage table listing
   every operator, mode, field and menu item found in the code, with the tests
   run and the classification. Anything not tested must be listed as NOT TESTED
   with a reason. Do not omit rows.

## Audit scope
- Every mode in the Integrals & Limits tool.
- Every other tool reachable from "Select Tool" that uses the same editor,
  parser, or validation (matrix operations, etc.). Test them with the same
  operator-in-input approach and list which ones share code with this tool.

## Canary design: detect zero, one, or two applications
Choose inputs where applying the operation 0, 1, or 2 times gives three
DIFFERENT answers, so double application cannot hide behind a coincidence
(as it did in observation 3). Prefer these over inputs like `x`:

| Input          | Operation   | 0 times | 1 time (correct) | 2 times      |
|----------------|-------------|---------|------------------|--------------|
| `\int x^2 dx`  | indefinite  | x²      | x³/3 + C         | x⁴/12 + C    |
| `\frac{d}{dx} x^3` | derivative | x³  | 3x²              | 6x           |
| `\frac{d}{dx} x^4` | derivative | x⁴  | 4x³              | 12x²         |
| `\int_0^3 x^2 dx` | definite | x²      | 9                | 0 (integrating a constant then evaluating) or 27/2 depending on order; record actual |

For definite integrals with conflicting bounds, use this diagnostic:
`\int_1^2 x dx`, Definite, a=0, b=1:
- 1/2   → bounds fields used, integrand x (editor bounds ignored)
- 3/2   → editor bounds used correctly
- 1/6   → integrand integrated twice over 0..1
- 3/2 × 1 = 3/2 is ALSO the "parser evaluated first, then integrated the
  constant over 0..1" result, so it collides with the correct answer; add a
  second run with a=0, b=2 (editor-bounds-correct = 3/2; constant-integrated
  = 3) to separate them.

## Mode × input-type matrix (generate programmatically)
Rows = what is typed in the editor. Columns = selected mode, including any new
"Auto" mode. Run EVERY cell. Do not sample.

Rows (input types):
- R1 plain expression, no operator: `x^2`
- R2 `\int x^2 dx`
- R3 `\int_0^3 x^2 dx`
- R4 `\frac{d}{dx} x^3`
- R5 `\frac{d^2}{dx^2} x^3`
- R6 `\lim_{x\to 0} \frac{\sin x}{x}`
- R7 `\sum_{i=1}^{5} i^2`
- R8 `\prod_{i=1}^{5} i`
- R9 `e^x` and `\ln x` (plain exp/log expressions)
- R10 matrix (via Insert matrix)
- R11 empty input
- R12 two operators combined: `\int \frac{d}{dx} x^3 dx`, `\frac{d}{dx}\int x^2 dx`

Columns (modes): Definite, Indefinite, Limit, Derivative, Finite sum,
Exponential & Log, Auto (if added).

Pass criteria per cell: the app either (1) computes the input's OWN operator
exactly once with the correct result, or (2) gives an explicit mismatch
message. Any other output is FAIL. For plain expressions (R1, R9) in each mode,
the expected behaviour is the mode's own operation applied once to the
expression (e.g. R1 in Derivative → 2x).

## Detailed tests per operator family

### A. Integrals
- `\int x dx` → x²/2 + C
- `\int x^2 dx` → x³/3 + C
- `\int \frac{1}{x} dx` → ln|x| + C (SymPy may return log(x) + C; document
  and accept either only if the choice is deliberate)
- `\int e^x dx` → e^x + C
- `\int \sin x dx` → -cos x + C
- `\int_1^2 x dx` → 3/2
- `\int_{-1}^{1} x dx` → 0
- `\int_2^1 x dx` → -3/2 (reversed bounds)
- `\int_0^0 x dx` → 0
- `\int_0^3 \frac{\sin x}{x} dx` → ≈ 1.84865 (existing example row; has no
  elementary antiderivative, so check the numeric fallback)
- Improper: `\int_0^\infty e^{-x} dx` → 1; `\int_{-\infty}^{\infty} e^{-x^2} dx`
  → √π; `\int_0^1 \frac{1}{x} dx` → diverges (must NOT return a finite number
  or crash)
- Symbolic bounds: `\int_a^b x dx` → (b²-a²)/2
- Other variables: `\int t dt` → t²/2 + C; `\int y dy`
- Multiple variables: `\int xy dx` → x²y/2 + C (y treated as constant)
- Spacing/tokenisation: the editor may emit `xdx` with no space. Test
  `\int xdx`, `\int x^2dx`, `\int e^xdx`, `\int \sin xdx`, `\int x\,dx`,
  `\int x \mathrm{d}x`, `\int x\ dx`. None may produce an "unknown symbol xdx"
  error or a wrong result.
- Missing differential: `\int x` → clear warning, not a crash or a guess.
- Multiple integrals and contour: `\iint`, `\iiint`, `\oint` → computed
  correctly or explicit "unsupported" message.
- Nested: `\int_0^1 \int_0^x y dy dx` → 1/6 or explicit unsupported message.

### B. Derivatives
- `\frac{d}{dx} x^3` → 3x² (currently errors)
- `\frac{d}{dx}(x^3)` and `\frac{d}{dx}\left(x^3\right)` → 3x²
- `\frac{d x^3}{dx}` → 3x²
- `\frac{d^2}{dx^2} x^3` → 6x
- `\frac{d^n}{dx^n}` with the order field: order 3 of x^3 → 6; order 4 → 0;
  order 12 of x^12 → 479001600
- Different notation: `\frac{\mathrm{d}}{\mathrm{d}x} x^3`, `\frac{dy}{dx}`
  with y a defined function, `\frac{d}{dt} t^3`, `f'(x)`, `f''(x)`, `\dot{x}`
  (each either supported or an explicit unsupported message)
- Partial: `\frac{\partial}{\partial x} x^2 y` → 2xy;
  `\frac{\partial^2}{\partial x \partial y} x^2 y` → 2x
- Evaluation point: `\frac{d}{dx} x^3` at x=2 → 12 (existing example row);
  `\left.\frac{d}{dx} x^3\right|_{x=2}` typed in the editor → 12
- Evaluation where the derivative is undefined: `|x|` at x=0, `1/x` at x=0 →
  clear message, not a crash or a silent number
- Chain/product/quotient: `\frac{d}{dx}\sin(x^2)` → 2x cos(x²);
  `\frac{d}{dx} x e^x` → e^x(x+1); `\frac{d}{dx}\frac{x}{x+1}` → 1/(x+1)²
- Order field boundaries: empty, 0, 1, 12, 13, -1, 1.5, "abc" → valid range
  accepted, everything else rejected with a clear message. Also test when the
  order is set in the field AND in the editor (`\frac{d^2}{dx^2}` with order=3):
  conflict must be handled (same issue as conflicting bounds).

### C. Limits
- `\lim_{x\to 0} \frac{\sin x}{x}` → 1
- `\lim_{x\to 2} x^2` → 4
- `\lim_{x\to 0} \frac{1-\cos x}{x^2}` → 1/2
- `\lim_{x\to\infty} \frac{1}{x}` → 0
- `\lim_{x\to\infty} \left(1+\frac{1}{x}\right)^x` → e
- One-sided: `\lim_{x\to 0^+} \frac{1}{x}` → ∞; `\lim_{x\to 0^-} \frac{1}{x}` → -∞
- Two-sided limit that does not exist: `\lim_{x\to 0} \frac{1}{x}` → "does not
  exist" (SymPy defaults to the right-hand limit and returns ∞; a bare ∞ here
  is FAIL-SILENT unless the app deliberately documents that choice)
- Other variables: `\lim_{n\to\infty} \frac{1}{n}` → 0, `\lim_{t\to 1} t^2`
- Notation variants: `\lim_{x \rightarrow 0}`, `\lim\limits_{x\to 0}`,
  `\lim_{x\to 0}` with the body in parentheses
- Does the Limit mode have extra fields (point, direction)? Test fields vs
  editor conflicts as with bounds.

### D. Sums and products
- `\sum_{x=1}^{5} x^2` → 55 (existing example row)
- `\sum_{i=1}^{4} i` → 10. IMPORTANT: confirm `i` is an index, not the
  imaginary unit; also test `\sum_{k=1}^{4} k`, `\sum_{n=1}^{4} n`
- `\sum_{i=1}^{3} 2^i` → 14
- Symbolic upper bound: `\sum_{k=1}^{n} k` → n(n+1)/2
- Infinite: `\sum_{n=1}^{\infty} \frac{1}{n^2}` → π²/6;
  `\sum_{n=0}^{\infty} \left(\frac{1}{2}\right)^n` → 2;
  `\sum_{n=1}^{\infty} \frac{1}{n}` → diverges
- Empty/reversed range: `\sum_{i=5}^{1} i`. Standard math: empty sum = 0.
  SymPy's `.doit()` uses the Karr convention and returns -9. This is a
  deliberate-choice test: decide, document, and show a note if it differs
  from the standard convention.
- Single term: `\sum_{i=3}^{3} i` → 3
- Index variable same as the function's variable (`x`) and different (`i`, `k`)
- Products: `\prod_{i=1}^{5} i` → 120; `\prod_{k=1}^{n} k` → n! (or explicit
  unsupported)
- Nested sums: `\sum_{i=1}^{2}\sum_{j=1}^{2} ij` → 9

### E. Exponentials, logarithms, roots, trig (functions inside every operation)
These are functions, not operators, but they appear inside every operator and
must be tested BOTH standalone and inside each of A–D.
- `e^0` → 1; `e^x` as a function; check `e` is Euler's number and not a symbol
  named "e" (`\int e^x dx` must give e^x + C, not e^x/ln(e)-style garbage)
- `\exp(x)`, `e^{2x}`, `e^{-x^2}`
- `\ln e` → 1; `\ln 1` → 0; `\ln 0` → -∞ or "undefined" (not a crash);
  `\ln(-1)` → iπ or "complex result" message
- `\log_2 8` → 3; `\log_{10} 1000` → 3
- Bare `\log 100`: AMBIGUOUS. Base 10 gives 2; natural log gives 4.605.
  Determine what the app does, show which base in the output, and document it.
- `e^{\ln x}` → x; `\ln(e^x)` → x
- `\sqrt{x}`, `\sqrt[3]{8}` → 2, `\sqrt{-1}` → i or message
- Trig: `\sin`, `\cos`, `\tan`, `\sec`, `\csc`, `\cot`, `\arcsin`, `\arctan`,
  `\sin^2 x`, `\sin^{-1} x` (inverse vs reciprocal: document), `\sinh`, `\cosh`
- Radians vs degrees: `\sin(\pi)` → 0 and `\sin(90)` is in radians (document)
- Constants: `\pi`, `\infty`, Euler's e, imaginary unit `i`

### F. Plain expression / evaluate-simplify
- `x+x` → 2x; `(x+1)^2` → behaviour per design (expand or keep); `2x^2`;
  `\frac{1}{2x}`; implicit multiplication `2x`, `xy`, `2(x+1)`; `x\cdot y`;
  `x\times y`; absolute value `|x|` and `\left|x\right|`; factorial `5!` →
  120; `\binom{5}{2}` → 10; piecewise `\begin{cases}...\end{cases}`;
  floor/ceil; Greek letters (`\alpha`, `\theta`) as variables

### G. Matrices and other editor inserts
- `Insert matrix` output (`\begin{pmatrix}`, `\begin{bmatrix}`, etc.) in every
  calculus mode → explicit "unsupported here" message, never a crash
- Every entry under the editor's `Insert` submenu: insert it, press Compute in
  each mode, and classify. Include every symbol, fraction, root, sub/superscript
  and operator entry the menu offers.

## Input channel tests (the same input must behave identically through all)
Run a core subset (A–D canaries) through each channel:
1. Pasting LaTeX text into the field
2. Typing the formula using keyboard shortcuts
3. Inserting via the editor's Insert submenu
4. Clicking the copy button on an example-usage row and pasting it
5. Switching the editor's own Mode (math / text / LaTeX, if present) and
   entering the same formula
6. Reloading the page with a previously entered formula
Also verify the exact LaTeX string the editor emits for each channel and
compare them. Differences (`\mathrm{d}x` vs `dx`, `\,` thin spaces, `\left(`)
are potential parser breakers.

## Editor-generated markup that can break parsing
The editor's Font style, Color and Background color menus can wrap content in
`\mathbf{}`, `\mathit{}`, `\textcolor{}{}`, `\colorbox{}{}`, `\text{}`. Apply
each to part of a valid formula (e.g. color just the `x` in `\int x^2 dx`) and
confirm the result is unchanged. Strip or ignore presentation markup before
parsing.

## Golden tests from the app's own example rows
The example-usage rows are known-answer test cases. Turn each into an automated
test, using the exact LaTeX the copy button produces:
- `\int_0^3 \frac{\sin x}{x} dx` ≈ 1.84865
- `\frac{d}{dx} x^3 = 3x^2` and the version evaluated at x=2 = 12
- `\sum_{x=1}^{5} x^2` = 55
- `\int x^2 dx = x^3/3 + C`
- Any further example rows found when scrolling the examples panel
If an example in the app's own documentation fails, that is FAIL-SILENT or
FAIL-VISIBLE and the highest-priority regression.

## Field and boundary tests (all modes)
- Lower/Upper bound fields: empty, equal, a>b, negative, decimal, `pi`, `-inf`,
  `inf`, symbolic (`a`), text garbage, very large numbers
- Evaluation point: empty (must mean "no evaluation", not 2), 0, negative,
  decimal, symbolic, a point outside the function's domain
- Order n: see Derivative section
- Placeholder vs value: with all optional fields empty, inspect the request
  payload. No placeholder text may be submitted.
- Switching modes with fields filled: stale values from a previous mode must
  not leak into the next computation.

## Output and formatting checks
- "+ C" appears ONLY for indefinite integrals, never on definite results,
  derivatives, limits or sums.
- Definite/limit/sum results are shown without a free variable x.
- "Numeric value" box: matches the symbolic result to at least 6 digits;
  for non-numeric results (like 3x²) it must be blank or clearly labelled, not
  a wrong number.
- Special results are rendered sensibly: ∞, -∞, "does not exist", NaN, complex
  numbers, "diverges", very long expressions.
- Result LaTeX re-parses without errors (round trip).

## Independent oracle and property tests
Compute expected values with an independent path, not the app's own code:
- Build the expected result directly with SymPy using unevaluated objects, for
  example `Integral(x**2, (x, 0, 3)).doit()`, and compare to the app's output.
- Numeric cross-check with mpmath or scipy (`quad`) for integrals and sums.
- Round-trip properties on randomly generated polynomials, trig and exp
  expressions:
  - `diff(app_indefinite_integral(f)) == f`
  - app_definite(f, a, b) == F(b) - F(a)
  - app_derivative(app_indefinite_integral(f)) == f
  - applying the app's operation to a result must not equal applying it to the
    original input (this is the double-application detector)
- Randomise variable names (`x`, `t`, `y`, `u`) and constants to catch
  hard-coded `x` assumptions.

## Robustness and safety
- Malformed LaTeX (unbalanced braces, `\int_`, `\frac{1}`, `\lim_{x\to}`,
  trailing backslash) → friendly error, no stack trace, no hang.
- Very long input and deeply nested expressions → bounded time (timeout) and a
  clear message.
- Expressions that take a long time (`\int_0^1 x^x dx`) → timeout handling.
- Unknown commands (`\foo{x}`) → "unsupported command" naming the command.
- Input-injection check: if the backend uses `sympify`/`eval`, send strings like
  `__import__('os').system('echo hi')` and Python-style text in the field and
  verify they are rejected safely. Even though the app runs locally, treat the
  input as untrusted.
- The "Unknown symbols" validator: confirm it is applied AFTER operator
  extraction, and that `d`, `dx`, `dt`, `\partial`, index variables and bound
  variables are never reported as unknown when part of valid notation.

## Proposed fix
Do not let the parser interpret calculus operators. Add a pre-processing step
that detects operator notation in the LaTeX BEFORE parsing and routes it:
- `\int` / `\int_a^b` -> extract bounds and integrand, parse the integrand
  alone, apply the integral handler once.
- `\frac{d}{dx}` / `\frac{d^n}{dx^n}` / `\partial` forms -> strip the operator,
  parse the body alone, apply the derivative handler once with order n.
- `\lim_{x\to a}` (with one-sided variants), `\sum_{i=a}^{b}` and
  `\prod_{i=a}^{b}` -> same pattern.
- Strip presentation-only markup (colour, font, spacing) before everything.
- Never apply a mode's operation to an expression that already had the same
  operation applied.

Mode design:
A. Add an "Auto" mode as the default; keep the manual modes as overrides.
   Detection order: `\lim` -> `\sum`/`\prod` -> `\frac{d}{d.}`/`\partial` ->
   `\int` with bounds -> `\int` without bounds -> plain evaluate/simplify.
B. If the user manually selects a mode that conflicts with the operator in the
   input, return a clear message ("Input already contains an integral; switch
   to Auto or remove the ∫") instead of computing.
C. Show a "Detected: <operation>" label near the Compute button.
D. Bounds, derivative order and evaluation point: if the editor already
   contains them, take them from the editor and hide or lock the matching
   fields; otherwise use the fields. Never submit placeholder text.
E. Drop "Exponential & Log" as a mode: exp and log are functions usable
   inside any operation. Plain expressions with no operator fall back to evaluate.
F. Whitelist `d`, `dx`, `\partial` and index/bound variables inside operator
   notation so they are never reported as unknown symbols.
G. Make deliberate, documented, user-visible decisions for the ambiguous cases
   found above: bare `\log` base, two-sided limits that do not exist, reversed
   sum ranges, `\sin^{-1}`, degrees vs radians, antiderivative form of 1/x.

## Deliverables expected from the AI
1. The operator inventory it found in the code, with file and line references.
2. A test file covering EVERY row above (parametrised), checked into the repo.
3. A results table for the CURRENT code (before any fix) with each test
   classified PASS / PASS-WARN / FAIL-VISIBLE / FAIL-SILENT.
4. A root-cause statement that says which hypothesis (1-4) was confirmed, with
   the logged evidence (raw payload, parser output before the mode handler,
   expression before and after each solver call).
5. The fix, then the same results table after the fix.
6. The coverage table (see Rule 5), including any operator found in the code
   that this report did not mention.
7. A short list of the deliberate design decisions made for ambiguous cases.

## Acceptance criteria
- All tests above produce the expected values, or a documented, deliberate
  alternative.
- No operation is ever applied twice (the canary and property tests prove it).
- Input/mode mismatches, conflicting bounds/order/point produce a correct
  result or an explicit warning, never a silently wrong answer.
- Zero FAIL-SILENT results in the final table.
- "Unknown symbols" errors never appear for valid operator notation.
- Placeholder text is never submitted as a value.
- Every example-usage row passes as an automated test.
- The coverage table has no unexplained NOT TESTED rows.