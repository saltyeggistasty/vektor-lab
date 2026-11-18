const fs = require("fs");
const src = fs.readFileSync("static/tools.js", "utf8");
const start = src.indexOf("function readGroup");
const end = src.indexOf("const TOOLS");
eval(src.slice(start, end));
const cases = [
  ["\\sin^2x", "uneval"],
  ["\\sin^{2}x", "uneval"],
  ["\\sin^2(x)", "uneval"],
  ["\\sin^2 2x", "uneval"],
  ["\\sin^2\\left(x^2\\right)", "uneval"],
  ["\\ln^2 x", "uneval"],
  ["\\arcsin^2 x", "uneval"],
  ["\\sin^{-1}(1)", "uneval"],
  ["\\sin 2x", "uneval"],
  ["\\cos^3 x", "uneval"],
  ["e^{\\sin^2 x}", "uneval"],
];
for (const [la] of cases) {
  const out = la2plain(la, { unevaluated: true });
  console.log(la.padEnd(26), "->", out);
}
