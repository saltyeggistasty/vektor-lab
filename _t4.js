const fs = require("fs");
const src = fs.readFileSync("static/tools.js", "utf8");
const start = src.indexOf("function readGroup");
const end = src.indexOf("const TOOLS");
eval(src.slice(start, end));
const cases = [
  "\\sin^2x", "\\sin^{2}x", "\\sin^2(x)", "\\sin^2 2x",
  "\\sin^2\\left(x^2\\right)", "\\ln^2 x", "\\arcsin^2 x",
  "\\sin^{-1}(1)", "\\sin 2x", "\\cos^3 x", "e^{\\sin^2 x}",
  "\\sec^3 x", "\\tan^2 x", "\\int_0^{\\pi}\\sin^2x\\,dx",
];
for (const la of cases) {
  const out = la2plain(la, { unevaluated: true });
  console.log(la.padEnd(34), "->", out);
}
