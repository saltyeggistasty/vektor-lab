# -*- coding: utf-8 -*-
"""Inject key use dinamis tools.<id>.useN / sims.<id>.useN ke 7 file i18n.

Sumber kebenaran: registry TOOLS di static/tools.js (elemen dipetakan
manual persis 1:1, dicek thd _use_raw.txt). Elemen LaTeX murni = identitas
(sama di semua bahasa); elemen ber-\\text{} Indonesia diterjemahkan per
bahasa lewat peta fragmen. Key yang SUDAH ADA tidak ditimpa.
"""
import io, json, collections

# ---------------------------------------------------------------- source (id)
SRC = collections.OrderedDict()
SRC["tools.integral.use1"] = r"\displaystyle\int_0^{3}\frac{\sin x}{x}\,dx \approx 1.84865"
SRC["tools.integral.use2"] = r"\dfrac{d}{dx}\,x^{3} = 3x^{2},\quad \left.\dfrac{d}{dx}x^{3}\right|_{x=2} = 12"
SRC["tools.integral.use3"] = r"\sum_{x=1}^{5}x^{2} = 55"
SRC["tools.integral.use4"] = r"\displaystyle\int x^2\,dx = \tfrac{x^3}{3} + C"
SRC["tools.integral.use5"] = r"e^{2\ln 4} = 16"
SRC["tools.integral.use6"] = r"\displaystyle\lim_{x\to 0}\frac{\sin x}{x} = 1"
SRC["tools.matrix.use1"] = r"\det\begin{pmatrix}1&2\\3&4\end{pmatrix} = -2"
SRC["tools.matrix.use2"] = r"\operatorname{rank}\begin{pmatrix}1&1\\1&1\end{pmatrix} = 1"
SRC["tools.matrix.use3"] = r"\lambda\,\mathbf{v} = A\,\mathbf{v} \;\Rightarrow\; \begin{pmatrix}1&2\\3&4\end{pmatrix},\ \lambda=-0.372,\ 5.372"
SRC["tools.ode.use1"] = r"y'' + y = \sin(x),\quad y(0)=1,\ y'(0)=0"
SRC["tools.ode.use2"] = r"y' = x \Rightarrow y = \tfrac{x^2}{2} + C"
SRC["tools.ode.use3"] = r"\text{ode eksponensial:}\; y' = -2y \Rightarrow y = Ce^{-2x}"
SRC["tools.stats.use1"] = r"\text{data: } 2,\,4,\,4,\,5,\,7 \Rightarrow \bar{x} = 4.4,\ \sigma_s \approx 1.8166"
SRC["tools.stats.use2"] = r"\tilde{x} = \text{median} = 4"
SRC["tools.thermo.use1"] = r"P\,V = n\,R\,T \;\Rightarrow\; V = \dfrac{nRT}{P}"
SRC["tools.thermo.use2"] = r"\eta_{\text{Carnot}} = 1 - \dfrac{T_c}{T_h} = 1 - \dfrac{400}{600} \approx 33.3\%"
SRC["tools.qm.use1"] = r"\lambda_{\text{de Broglie}} = \dfrac{h}{m\,v}"
SRC["tools.qm.use2"] = r"E = h\,f = \dfrac{h\,c}{\lambda}"
SRC["tools.qm.use3"] = r"K\!E_{\max} = h f - \varphi"
SRC["tools.es.use1"] = r"F = k_e\,\dfrac{q_1 q_2}{r^{2}}"
SRC["tools.es.use2"] = r"E = \dfrac{k_e\,q}{r^{2}}"
SRC["tools.es.use3"] = r"C = \varepsilon_0\,\dfrac{A}{d}"
SRC["tools.rel.use1"] = r"\gamma = \dfrac{1}{\sqrt{1 - v^{2}/c^{2}}},\quad v = 0.5c \Rightarrow \gamma \approx 1.1547"
SRC["tools.rel.use2"] = r"\Delta t = \gamma\,\Delta t_0,\qquad L = \dfrac{L_0}{\gamma}"
SRC["tools.rel.use3"] = r"E = \gamma m_{0}c^{2},\quad K = (\gamma - 1)m_{0}c^{2}"
SRC["tools.proj.use1"] = r"x_{\max} = \dfrac{v_0^{2}\sin 2\theta}{g}"
SRC["tools.proj.use2"] = r"y_{\max} = y_0 + \dfrac{\left(v_0\sin\theta\right)^{2}}{2g}"
SRC["tools.hydro.use1"] = r"P_{\text{gauge}} = \rho\,g\,h"
SRC["tools.hydro.use2"] = r"A_1 v_1 = A_2 v_2"
SRC["tools.hydro.use3"] = r"P_1 + \tfrac{1}{2}\rho v_1^{2} + \rho g h_1 = P_2 + \tfrac{1}{2}\rho v_2^{2} + \rho g h_2"
SRC["tools.complex.use1"] = r"|z| = \sqrt{a^{2}+b^{2}},\qquad \theta = \arctan\dfrac{b}{a}"
SRC["tools.complex.use2"] = r"z = r\,e^{i\theta}"
SRC["tools.complex.use3"] = r"z^{1/n} = \sqrt[n]{r}\,e^{\,i(\theta + 2\pi k)/n}"
SRC["tools.taylor.use1"] = r"e^{x} \approx 1 + x + \dfrac{x^{2}}{2!} + \dfrac{x^{3}}{3!}"
SRC["tools.taylor.use2"] = r"\sin x \approx x - \dfrac{x^{3}}{3!} + \dfrac{x^{5}}{5!}"
SRC["tools.modmath.use1"] = r"a^{b} \bmod n:\;\; 2^{10} \bmod 1000 = 24"
SRC["tools.modmath.use2"] = r"\gcd(12,18) = 6,\quad \operatorname{lcm}(12,18) = 36"
SRC["tools.modmath.use3"] = r"97 \text{ prima},\;\; 360 = 2^{3}\cdot 3^{2}\cdot 5"
SRC["tools.entropy.use1"] = r"H = -\sum_{i} p_{i}\,\log_{2} p_{i}"
SRC["tools.entropy.use2"] = r"\text{koin adil: } H = 1 \text{ bit},\quad H_{\max} = \log_{2} n"
SRC["tools.poly.use1"] = r"p(x) = x^{2} - 5x + 6 \;\Rightarrow\; x_{1}=2,\ x_{2}=3"
SRC["tools.poly.use2"] = r"x^{2} - 5x + 6 = (x-2)(x-3)"
SRC["tools.poly.use3"] = r"\text{derajat bawah 12, koefisien boleh pecahan}"
SRC["tools.heatexp.use1"] = r"Q = m\,c\,\Delta T"
SRC["tools.heatexp.use2"] = r"\Delta L = \alpha\,L_0\,\Delta T"
SRC["tools.heatexp.use3"] = r"Q = m\,L \;\text{(fase ubah tanpa suhu naik)}"
SRC["tools.schwartz.use1"] = r"r_s = \dfrac{2GM}{c^{2}}"
SRC["tools.schwartz.use2"] = r"\left(1 - \dfrac{r_s}{r}\right)^{-1} \;\text{faktor perlambatan waktu}"
SRC["tools.optics.use1"] = r"n_1\sin\theta_1 = n_2\sin\theta_2"
SRC["tools.optics.use2"] = r"\dfrac{1}{f} = \dfrac{1}{d_o} + \dfrac{1}{d_i}"
SRC["tools.optics.use3"] = r"d\,\sin\theta = m\,\lambda \;\text{(interferensi maksimum)}"
SRC["tools.shm.use1"] = r"T = 2\pi\sqrt{\dfrac{m}{k}}"
SRC["tools.shm.use2"] = r"T = 2\pi\sqrt{\dfrac{L}{g}} \;\text{(bandul sederhana)}"
SRC["tools.shm.use3"] = r"E_{\text{energi}} = \tfrac{1}{2}kA^{2}"
SRC["tools.emind.use1"] = r"\varepsilon = N\,\dfrac{d\Phi}{dt}"
SRC["tools.emind.use2"] = r"\dfrac{V_1}{V_2} = \dfrac{N_1}{N_2} \;\text{(trafo ideal)}"
SRC["tools.emind.use3"] = r"\varepsilon = B\,v\,L \;\text{(EMF gerak)}"
SRC["sims.slogistic.use1"] = r"x_{k+1} = r\,x_k(1-x_k),\quad r = 2 \Rightarrow x^{*} = \tfrac{1}{2}"
SRC["sims.slogistic.use2"] = r"r = 3.2 \Rightarrow \text{periode } 2,\quad r > 3.5699 \Rightarrow \text{kacau}"
SRC["sims.slogistic.use3"] = r"\lambda = \ln|r(1-2x)| > 0 \Leftrightarrow \text{kacau}"
SRC["sims.slorenz.use1"] = r"\dot{x} = \sigma(y-x),\quad \dot{y} = x(\rho-z) - y,\quad \dot{z} = xy - \beta z"
SRC["sims.slorenz.use2"] = r"\rho = 28 \Rightarrow \text{atraktor aneh},\quad \rho < 24.74 \Rightarrow \text{titik tetap}"
SRC["sims.sfourier.use1"] = r"f(x) = x \text{ di } [-\pi,\pi] \Rightarrow b_n = \dfrac{2(-1)^{n+1}}{n}"
SRC["sims.sfourier.use2"] = r"x \approx 2\left(\sin x - \tfrac{\sin 2x}{2} + \tfrac{\sin 3x}{3} - \cdots\right)"
SRC["sims.smatrix.use1"] = r"\begin{pmatrix}0&-1\\1&0\end{pmatrix} = \text{rotasi } 90^{\circ},\ \det = 1"
SRC["sims.smatrix.use2"] = r"\det A = \text{faktor skala luas},\quad \lambda = \text{nilai eigen}"
SRC["sims.swalk.use1"] = r"\langle r^{2} \rangle = n\,\ell^{2} \Rightarrow \text{RMS} = \ell\sqrt{n}"
SRC["sims.swalk.use2"] = r"\text{difiusi: } \langle x^{2} \rangle = 2Dt"
SRC["sims.sdblpend.use1"] = r"\ddot{\theta}_1,\ \ddot{\theta}_2 = \text{RK4},\quad \Delta t = 0.002\,\text{s}"
SRC["sims.sdblpend.use2"] = r"\dfrac{\Delta E}{E} \approx 10^{-7} \;\text{(konservasi)}"
SRC["sims.sdrag.use1"] = r"F_d = \tfrac{1}{2}\rho C_d A\,v^{2}"
SRC["sims.sdrag.use2"] = r"x_{\text{vakum}} = \dfrac{v_0^{2}\sin 2\theta}{g}"
SRC["sims.skepler.use1"] = r"T = 2\pi\sqrt{\dfrac{a^{3}}{\mu}} \;\text{(Hukum III Kepler)}"
SRC["sims.skepler.use2"] = r"v^{2} = \mu\left(\dfrac{2}{r} - \dfrac{1}{a}\right) \;\text{(vis-viva)}"
SRC["sims.sslit.use1"] = r"I(y) = \cos^{2}\!\left(\dfrac{\pi d y}{\lambda L}\right) \cdot \mathrm{sinc}^{2}\!\left(\dfrac{\pi a y}{\lambda L}\right)"
SRC["sims.sslit.use2"] = r"\Delta y = \dfrac{\lambda L}{d}"
SRC["sims.sschrod.use1"] = r"i\,\dfrac{\partial \psi}{\partial t} = -\dfrac{1}{2}\dfrac{\partial^{2}\psi}{\partial x^{2}} + V(x)\,\psi"
SRC["sims.sschrod.use2"] = r"\hbar = m = 1,\quad E = \dfrac{k_0^{2}}{2},\quad v = k_0"
SRC["tools.gdomain.use1"] = r"f(z) = \dfrac{1}{z}"
SRC["tools.gdomain.use2"] = r"f(z) = z^{3} - 1"
SRC["tools.gdomain.use3"] = r"f(z) = \exp\left(\tfrac{1}{z}\right)"
SRC["tools.gfractal.use1"] = r"z_{n+1} = z_n^{2} + c"
SRC["tools.gfractal.use2"] = r"c = -0.7269 + 0.1889i\ \text{(dendrite)}"
SRC["tools.gsurf3d.use1"] = r"z = \sin x\,\cos 2y"
SRC["tools.gsurf3d.use2"] = r"\text{bidang singgung: } z = f_0 + f_x\Delta x + f_y\Delta y"
SRC["tools.gfrenet.use1"] = r"\mathbf{T} = \dfrac{\mathbf{r}'}{\|\mathbf{r}'\|},\quad \mathbf{B} = \mathbf{T}\times\mathbf{N}"
SRC["tools.gtrans3d.use1"] = r"A\mathbf{i},\ A\mathbf{j},\ A\mathbf{k} = \text{kolom } A"
SRC["tools.gtrans3d.use2"] = r"\det A = \text{faktor volume}"
SRC["tools.gslope.use1"] = r"y' = x - y"
SRC["tools.gslope.use2"] = r"\text{klik canvas} \Rightarrow \text{solusi RK4}"
SRC["tools.gdist.use1"] = r"P(a \le X \le b) = \text{area di bawah PDF}"
SRC["tools.gdist.use2"] = r"F(x) = P(X \le x)"
SRC["tools.ggraphalgo.use1"] = r"\text{drag node} \Leftrightarrow \text{recompute}"
SRC["tools.gfield.use1"] = r"\mathbf{E} = \sum_i \dfrac{k q_i}{r_i^{2}}\hat{\mathbf{r}}_i"
SRC["tools.gfield.use2"] = r"\text{drag muatan merah/biru!}"
SRC["tools.gpvcycle.use1"] = r"\eta_{\text{Carnot}} = 1 - \dfrac{T_c}{T_h}"
SRC["tools.gpvcycle.use2"] = r"\eta_{\text{Otto}} = 1 - r^{1-\gamma}"
SRC["tools.gising.use1"] = r"H = -J\sum_{\langle i,j \rangle} s_i s_j"
SRC["tools.gising.use2"] = r"T_c \approx 2.269\ J"
SRC["tools.gminkowski.use1"] = r"\text{drag event} \Rightarrow s^{2} = c^{2}t^{2} - x^{2}\ \text{invarian}"
SRC["tools.gfluid.use1"] = r"\text{drag di canvas} \Rightarrow \text{injeksi tinta + kecepatan}"
SRC["tools.ggeodesic.use1"] = r"\dfrac{d^{2}u}{d\varphi^{2}} = \dfrac{3}{2}r_s u^{2} - u"
SRC["tools.ggeodesic.use2"] = r"b < 1.5\,r_s \Rightarrow \text{tertelan}"
SRC["tools.gray.use1"] = r"\dfrac{1}{f} = \dfrac{1}{d_o} + \dfrac{1}{d_i}"
SRC["tools.gray.use2"] = r"f_1 > 0\ \text{konveks},\ f_2 < 0\ \text{konkaf}"

# --------------------------------------------- peta terjemahan fragmen \text{}
# fragmen Indonesia (persis) -> bahasa target; yang tak disebut = identitas
REPL = {
    "english": {
        r"\text{ode eksponensial:}": r"\text{exponential ODE:}",
        r"\text{median}": r"\text{median}",
        r"\text{ prima}": r"\text{ prime}",
        r"\text{koin adil: }": r"\text{fair coin: }",
        r"\text{derajat bawah 12, koefisien boleh pecahan}":
            r"\text{degree below 12, fractional coefficients allowed}",
        r"\text{(fase ubah tanpa suhu naik)}": r"\text{(phase change, no temperature rise)}",
        r"\text{faktor perlambatan waktu}": r"\text{time dilation factor}",
        r"\text{(interferensi maksimum)}": r"\text{(maximum interference)}",
        r"\text{(bandul sederhana)}": r"\text{(simple pendulum)}",
        r"E_{\text{energi}}": r"E_{\text{energy}}",
        r"\text{(trafo ideal)}": r"\text{(ideal transformer)}",
        r"\text{(EMF gerak)}": r"\text{(motional EMF)}",
        r"\text{periode }": r"\text{period }",
        r"\text{kacau}": r"\text{chaos}",
        r"\text{atraktor aneh}": r"\text{strange attractor}",
        r"\text{titik tetap}": r"\text{fixed point}",
        r"\text{ di }": r"\text{ on }",
        r"\text{rotasi }": r"\text{rotation }",
        r"\text{faktor skala luas}": r"\text{area scale factor}",
        r"\text{nilai eigen}": r"\text{eigenvalue}",
        r"\text{difiusi: }": r"\text{diffusion: }",
        r"\text{(konservasi)}": r"\text{(energy conserved)}",
        r"x_{\text{vakum}}": r"x_{\text{vac}}",
        r"\text{(Hukum III Kepler)}": r"\text{(Kepler's Third Law)}",
        r"\text{bidang singgung: }": r"\text{tangent plane: }",
        r"\text{kolom }": r"\text{columns of }",
        r"\text{faktor volume}": r"\text{volume factor}",
        r"\text{klik canvas}": r"\text{click canvas}",
        r"\text{solusi RK4}": r"\text{RK4 solution}",
        r"\text{area di bawah PDF}": r"\text{area under the PDF}",
        r"\text{drag node}": r"\text{drag node}",
        r"\text{recompute}": r"\text{recompute}",
        r"\text{drag muatan merah/biru!}": r"\text{drag the red/blue charges!}",
        r"\text{drag event}": r"\text{drag event}",
        r"\text{invarian}": r"\text{invariant}",
        r"\text{drag di canvas}": r"\text{drag on canvas}",
        r"\text{injeksi tinta + kecepatan}": r"\text{ink + velocity injection}",
        r"\text{tertelan}": r"\text{captured}",
        r"\text{konveks}": r"\text{convex}",
        r"\text{konkaf}": r"\text{concave}",
    },
    "melayu": {
        r"\text{ode eksponensial:}": r"\text{ODE eksponen:}",
        r"\text{ prima}": r"\text{ perdana}",
        r"\text{koin adil: }": r"\text{syiling adil: }",
        r"\text{derajat bawah 12, koefisien boleh pecahan}":
            r"\text{darjah bawah 12, pekali boleh pecahan}",
        r"\text{(fase ubah tanpa suhu naik)}": r"\text{(perubahan fasa, suhu tidak naik)}",
        r"\text{faktor perlambatan waktu}": r"\text{faktor pelambatan masa}",
        r"\text{(interferensi maksimum)}": r"\text{(interferens maksimum)}",
        r"\text{(bandul sederhana)}": r"\text{(bandul ringkas)}",
        r"E_{\text{energi}}": r"E_{\text{tenaga}}",
        r"\text{(trafo ideal)}": r"\text{(pengubah unggul)}",
        r"\text{(EMF gerak)}": r"\text{(EMF gerakan)}",
        r"\text{periode }": r"\text{tempoh }",
        r"\text{atraktor aneh}": r"\text{penarik aneh}",
        r"\text{ di }": r"\text{ pada }",
        r"\text{rotasi }": r"\text{putaran }",
        r"\text{difiusi: }": r"\text{difusi: }",
        r"\text{(konservasi)}": r"\text{(tenaga terpulihara)}",
        r"\text{bidang singgung: }": r"\text{satah sesentuh: }",
        r"\text{kolom }": r"\text{kolum }",
        r"\text{faktor volume}": r"\text{faktor isipadu}",
        r"\text{klik canvas}": r"\text{klik kanvas}",
        r"\text{solusi RK4}": r"\text{penyelesaian RK4}",
        r"\text{area di bawah PDF}": r"\text{luas di bawah PDF}",
        r"\text{drag node}": r"\text{seret nod}",
        r"\text{recompute}": r"\text{kira semula}",
        r"\text{drag muatan merah/biru!}": r"\text{seret cas merah/biru!}",
        r"\text{drag event}": r"\text{seret peristiwa}",
        r"\text{drag di canvas}": r"\text{seret di kanvas}",
        r"\text{injeksi tinta + kecepatan}": r"\text{suntikan dakwat + halaju}",
        r"\text{(dendrite)}": r"\text{(dendrit)}",
        r"\text{konveks}": r"\text{cembung}",
        r"\text{konkaf}": r"\text{cekung}",
    },
    "russia": {
        r"\text{ode eksponensial:}": r"\text{экспоненциальное ОДУ:}",
        r"\text{data: }": r"\text{данные: }",
        r"\text{median}": r"\text{медиана}",
        r"\text{ prima}": r"\text{ простое}",
        r"\text{koin adil: }": r"\text{честная монета: }",
        r"\text{ bit}": r"\text{ бит}",
        r"\text{derajat bawah 12, koefisien boleh pecahan}":
            r"\text{степень ниже 12, коэффициенты могут быть дробными}",
        r"\text{(fase ubah tanpa suhu naik)}": r"\text{(фазовый переход, без нагрева)}",
        r"\text{faktor perlambatan waktu}": r"\text{фактор замедления времени}",
        r"\text{(interferensi maksimum)}": r"\text{(максимум интерференции)}",
        r"\text{(bandul sederhana)}": r"\text{(математический маятник)}",
        r"E_{\text{energi}}": r"E_{\text{энергия}}",
        r"\text{(trafo ideal)}": r"\text{(идеальный трансформатор)}",
        r"\text{(EMF gerak)}": r"\text{(ЭДС движения)}",
        r"\text{periode }": r"\text{период }",
        r"\text{kacau}": r"\text{хаос}",
        r"\text{atraktor aneh}": r"\text{странный аттрактор}",
        r"\text{titik tetap}": r"\text{устойчивая точка}",
        r"\text{ di }": r"\text{ на }",
        r"\text{rotasi }": r"\text{поворот }",
        r"\text{faktor skala luas}": r"\text{масштаб площади}",
        r"\text{nilai eigen}": r"\text{собственное значение}",
        r"\text{difiusi: }": r"\text{диффузия: }",
        r"\text{(konservasi)}": r"\text{(сохранение энергии)}",
        r"x_{\text{vakum}}": r"x_{\text{вакуум}}",
        r"\text{(Hukum III Kepler)}": r"\text{(третий закон Кеплера)}",
        r"\text{(dendrite)}": r"\text{(дендрит)}",
        r"\text{bidang singgung: }": r"\text{касательная плоскость: }",
        r"\text{kolom }": r"\text{столбцы }",
        r"\text{faktor volume}": r"\text{масштаб объёма}",
        r"\text{klik canvas}": r"\text{клик по холсту}",
        r"\text{solusi RK4}": r"\text{решение RK4}",
        r"\text{area di bawah PDF}": r"\text{площадь под PDF}",
        r"\text{drag node}": r"\text{перетащить узел}",
        r"\text{recompute}": r"\text{пересчёт}",
        r"\text{drag muatan merah/biru!}": r"\text{перетащите красный/синий заряд!}",
        r"\text{drag event}": r"\text{перетащите событие}",
        r"\text{invarian}": r"\text{инвариант}",
        r"\text{drag di canvas}": r"\text{перетащите по холсту}",
        r"\text{injeksi tinta + kecepatan}": r"\text{впрыск чернил + скорость}",
        r"\text{tertelan}": r"\text{захвачен}",
        r"\text{konveks}": r"\text{выпуклая}",
        r"\text{konkaf}": r"\text{вогнутая}",
    },
    "ukraina": {
        r"\text{ode eksponensial:}": r"\text{експоненціальне ДР:}",
        r"\text{data: }": r"\text{дані: }",
        r"\text{median}": r"\text{медіана}",
        r"\text{ prima}": r"\text{ просте}",
        r"\text{koin adil: }": r"\text{чесна монета: }",
        r"\text{ bit}": r"\text{ біт}",
        r"\text{derajat bawah 12, koefisien boleh pecahan}":
            r"\text{степінь нижче 12, коефіцієнти можуть бути дробовими}",
        r"\text{(fase ubah tanpa suhu naik)}": r"\text{(фазовий перехід, без нагріву)}",
        r"\text{faktor perlambatan waktu}": r"\text{фактор уповільнення часу}",
        r"\text{(interferensi maksimum)}": r"\text{(максимум інтерференції)}",
        r"\text{(bandul sederhana)}": r"\text{(математичний маятник)}",
        r"E_{\text{energi}}": r"E_{\text{енергія}}",
        r"\text{(trafo ideal)}": r"\text{(ідеальний трансформатор)}",
        r"\text{(EMF gerak)}": r"\text{(ЕДС руху)}",
        r"\text{periode }": r"\text{період }",
        r"\text{kacau}": r"\text{хаос}",
        r"\text{atraktor aneh}": r"\text{дивний атрактор}",
        r"\text{titik tetap}": r"\text{стала точка}",
        r"\text{ di }": r"\text{ на }",
        r"\text{rotasi }": r"\text{обертання }",
        r"\text{faktor skala luas}": r"\text{масштаб площі}",
        r"\text{nilai eigen}": r"\text{власне значення}",
        r"\text{difiusi: }": r"\text{дифузія: }",
        r"\text{(konservasi)}": r"\text{(збереження енергії)}",
        r"x_{\text{vakum}}": r"x_{\text{вакуум}}",
        r"\text{(Hukum III Kepler)}": r"\text{(третій закон Кеплера)}",
        r"\text{(dendrite)}": r"\text{(дендрит)}",
        r"\text{bidang singgung: }": r"\text{дотична площина: }",
        r"\text{kolom }": r"\text{стовпці }",
        r"\text{faktor volume}": r"\text{масштаб об'єму}",
        r"\text{klik canvas}": r"\text{клік по полотну}",
        r"\text{solusi RK4}": r"\text{розв'язок RK4}",
        r"\text{area di bawah PDF}": r"\text{площа під PDF}",
        r"\text{drag node}": r"\text{перетягнути вузол}",
        r"\text{recompute}": r"\text{перерахунок}",
        r"\text{drag muatan merah/biru!}": r"\text{перетягніть червоний/синій заряд!}",
        r"\text{drag event}": r"\text{перетягніть подію}",
        r"\text{invarian}": r"\text{інваріант}",
        r"\text{drag di canvas}": r"\text{перетягніть по полотну}",
        r"\text{injeksi tinta + kecepatan}": r"\text{впорскування чорнил + швидкість}",
        r"\text{tertelan}": r"\text{захоплений}",
        r"\text{konveks}": r"\text{опукла}",
        r"\text{konkaf}": r"\text{увігнута}",
    },
    "arab": {
        r"\text{ode eksponensial:}": r"\text{معادلة تفاضلية أسية:}",
        r"\text{data: }": r"\text{بيانات: }",
        r"\text{median}": r"\text{الوسيط}",
        r"\text{ prima}": r"\text{ أولي}",
        r"\text{koin adil: }": r"\text{عملة عادلة: }",
        r"\text{ bit}": r"\text{ بت}",
        r"\text{derajat bawah 12, koefisien boleh pecahan}":
            r"\text{درجة أقل من 12، المعاملات قد تكون كسورًا}",
        r"\text{(fase ubah tanpa suhu naik)}": r"\text{(تغير الطور دون ارتفاع الحرارة)}",
        r"\text{faktor perlambatan waktu}": r"\text{معامل تباطؤ الزمن}",
        r"\text{(interferensi maksimum)}": r"\text{(تداخل أقصى)}",
        r"\text{(bandul sederhana)}": r"\text{(بندول بسيط)}",
        r"E_{\text{energi}}": r"E_{\text{طاقة}}",
        r"\text{(trafo ideal)}": r"\text{(محول مثالي)}",
        r"\text{(EMF gerak)}": r"\text{(قوة دافعة حركية)}",
        r"\text{periode }": r"\text{دورة }",
        r"\text{kacau}": r"\text{فوضى}",
        r"\text{atraktor aneh}": r"\text{جاذب غريب}",
        r"\text{titik tetap}": r"\text{نقطة ثابتة}",
        r"\text{ di }": r"\text{ على }",
        r"\text{rotasi }": r"\text{دوران }",
        r"\text{faktor skala luas}": r"\text{معامل مقياس المساحة}",
        r"\text{nilai eigen}": r"\text{القيمة الذاتية}",
        r"\text{difiusi: }": r"\text{انتشار: }",
        r"\text{(konservasi)}": r"\text{(انحفاظ الطاقة)}",
        r"x_{\text{vakum}}": r"x_{\text{فراغ}}",
        r"\text{(Hukum III Kepler)}": r"\text{(قانون كيبلر الثالث)}",
        r"\text{(dendrite)}": r"\text{(شجري)}",
        r"\text{bidang singgung: }": r"\text{المستوى المماسي: }",
        r"\text{kolom }": r"\text{أعمدة }",
        r"\text{faktor volume}": r"\text{معامل الحجم}",
        r"\text{klik canvas}": r"\text{انقر على اللوحة}",
        r"\text{solusi RK4}": r"\text{حل RK4}",
        r"\text{area di bawah PDF}": r"\text{المساحة تحت منحنى الكثافة}",
        r"\text{drag node}": r"\text{اسحب العقدة}",
        r"\text{recompute}": r"\text{إعادة الحساب}",
        r"\text{drag muatan merah/biru!}": r"\text{اسحب الشحنة الحمراء/الزرقاء!}",
        r"\text{drag event}": r"\text{اسحب الحدث}",
        r"\text{invarian}": r"\text{ثابت}",
        r"\text{drag di canvas}": r"\text{اسحب على اللوحة}",
        r"\text{injeksi tinta + kecepatan}": r"\text{حقن الحبر + السرعة}",
        r"\text{tertelan}": r"\text{محتجز}",
        r"\text{konveks}": r"\text{محدب}",
        r"\text{konkaf}": r"\text{مقعر}",
    },
}
REPL["irish"] = REPL["english"]   # Irish English -> English

LANGS = ["indonesia", "english", "melayu", "russia", "ukraina", "irish", "arab"]


def apply_repl(src, mp):
    val = src
    for frag in sorted(mp, key=len, reverse=True):   # fragmen terpanjang dulu
        val = val.replace(frag, mp[frag])
    return val


for lang in LANGS:
    path = f"i18n/{lang}.json"
    data = json.load(io.open(path, encoding="utf-8"), object_pairs_hook=collections.OrderedDict)
    mp = REPL.get(lang, {})
    added, kept = 0, 0
    for key in SRC:
        grp, sub, leaf = key.split(".", 2)          # tools/integral/use1
        grp_d = data.setdefault(grp, collections.OrderedDict())
        sub_d = grp_d.setdefault(sub, collections.OrderedDict())
        if leaf in sub_d:
            kept += 1                                # key sudah ada -> jangan ditimpa
            continue
        sub_d[leaf] = SRC[key] if lang == "indonesia" else apply_repl(SRC[key], mp)
        added += 1
    io.open(path, "w", encoding="utf-8").write(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    print(f"{lang:10s} tambah {added:3d} | skip {kept:3d}")

print("total elemen:", len(SRC))
