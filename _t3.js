const fs = require("fs");
const src = fs.readFileSync("static/tools.js", "utf8");
const start = src.indexOf("function readGroup");
const end = src.indexOf("const TOOLS");
eval(src.slice(start, end));
console.log("N:", normalizeFnPowers("\\sin^2x"));
console.log("L:", la2plain("\\sin^2x", { unevaluated: true }));
console.log("L:", la2plain("\\sin^{2}x", { unevaluated: true }));
