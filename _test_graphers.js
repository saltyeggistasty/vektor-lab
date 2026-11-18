/* Tes math core graphers.js — jalankan: node _test_graphers.js */
"use strict";
global.window = {};
require("G:/vektor-lab(1)/vektor-lab/static/graphers.js");
const T = global.window.__GRAPH_TEST;

let PASS = 0, FAIL = 0;
function check(name, cond, detail) {
  if (cond) { PASS++; console.log("  OK   " + name); }
  else { FAIL++; console.log("  FAIL " + name + "  " + detail); }
}

/* ===== real parser ===== */
const f1 = T.compileReal("x^2 + y^2", ["x", "y"]);
check("x^2+y^2 (3,4) = 25", f1(3, 4) === 25, f1(3, 4));
const f2 = T.compileReal("sin(pi/2)", []);
check("sin(pi/2) = 1", Math.abs(f2() - 1) < 1e-12);
const f3 = T.compileReal("x - y", ["x", "y"]);
check("x-y (5,2) = 3", f3(5, 2) === 3);
const f4 = T.compileReal("sqrt(16) + 2^3", []);
check("sqrt16+2^3 = 12", f4() === 12);
const f5 = T.compileReal("log(e)", []);
check("log(e) = 1", Math.abs(f5() - 1) < 1e-12);
const f6 = T.compileReal("2x + 3y", ["x", "y"]);      // implicit mult
check("implicit 2x+3y (1,2) = 8", f6(1, 2) === 8, f6(1, 2));
const f7 = T.compileReal("-x^2", ["x"]);               // unary
check("unary -x^2 (2) = -4", f7(2) === -4, f7(2));
const f8 = T.compileReal("atan2(y, x)", ["x", "y"]);
check("atan2(1,1) = pi/4", Math.abs(f8(1, 1) - Math.PI / 4) < 1e-12);
let threw = false;
try { T.compileReal("import os", ["x"]); } catch (e) { threw = true; }
check("ident asing -> error fungsi/variabel", threw);

/* ===== complex parser ===== */
const c1 = T.compileComplex("z^2");
const r1 = c1({ re: 0, im: 1 });
check("z^2 di i = -1", r1.re === -1 && Math.abs(r1.im) < 1e-12, JSON.stringify(r1));
const c2 = T.compileComplex("1/z");
const r2 = c2({ re: 2, im: 0 });
check("1/2 = 0.5", Math.abs(r2.re - 0.5) < 1e-12 && Math.abs(r2.im) < 1e-12);
const c3 = T.compileComplex("exp(i*pi)");
const r3 = c3({ re: 1, im: 0 });
check("exp(i pi) = -1", Math.abs(r3.re + 1) < 1e-12 && Math.abs(r3.im) < 1e-12, JSON.stringify(r3));
const c4 = T.compileComplex("z^3 - 1");
const r4 = c4({ re: 1, im: 0 });
check("z^3-1 di 1 = 0", Math.abs(r4.re) < 1e-12 && Math.abs(r4.im) < 1e-12);
const c5 = T.compileComplex("2z + i");
const r5 = c5({ re: 3, im: 0 });
check("implicit 2z+i (3) = 6+i", r5.re === 6 && r5.im === 1, JSON.stringify(r5));
const c6 = T.compileComplex("(z+1)(z-1)");
const r6 = c6({ re: 2, im: 0 });
check("(z+1)(z-1) di 2 = 3", Math.abs(r6.re - 3) < 1e-12, JSON.stringify(r6));
const c7 = T.compileComplex("sqrt(4)");
const r7 = c7({ re: 0, im: 0 });
check("sqrt(4) = 2", r7.re === 2 && Math.abs(r7.im) < 1e-12);
const c8 = T.compileComplex("log(z)");
const r8 = c8({ re: Math.E, im: 0 });
check("log(e) = 1 (real)", Math.abs(r8.re - 1) < 1e-12 && Math.abs(r8.im) < 1e-12);
const c9 = T.compileComplex("sin(z)");
const r9 = c9({ re: 0, im: 0 });
check("sin(0) = 0", Math.abs(r9.re) < 1e-12 && Math.abs(r9.im) < 1e-12);
/* z^2-1 di titik nol: f(i) = -2 */
const c10 = T.compileComplex("z^2 - 1");
const r10 = c10({ re: 0, im: 1 });
check("z^2-1 di i = -2", Math.abs(r10.re + 2) < 1e-12, JSON.stringify(r10));

/* ===== hsv ===== */
const h1 = T.hsv(0, 1, 1);
check("hsv(0,1,1) = merah", h1[0] === 1 && h1[1] === 0 && h1[2] === 0);

console.log(`\nTOTAL: ${PASS} OK, ${FAIL} FAIL`);
process.exit(FAIL ? 1 : 0);
