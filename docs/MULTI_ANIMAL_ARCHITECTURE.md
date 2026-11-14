# PRW-Wild Multi-Animal Ecosystem Architecture

**Population:** 60 Active Autonomous Agents  
**Terrain Model:** Analytical Continuous Elevation Grounding  
**Taxonomy:** 6 Native Indian Wildlife Species  
**Framework:** Behavior FSM + Reynolds Flocking + Dynamic Ecological Resource Patches  

---

## 1. 3D Terrain Elevation Grounding

All 3D assets (trees, rocks, ferns, grass tufts, crop parcels, watchtower, fence posts) and all 60 animal agents are mathematically grounded to the continuous sculpted terrain surface using $y = \text{getTerrainElevation}(x, z)$:

$$\begin{aligned}
y_{\text{base}} &= \begin{cases} (100 - x) \times 0.015 & x < 100 \\ -(x - 100) \times 0.005 & x \ge 100 \end{cases} \\
y_{\text{hills}} &= 1.8 \sin(0.065x + 1.2) \cos(0.055z) + 0.75 \sin(0.12x - 0.5) \cos(0.11z + 0.8) + 0.35 \sin(0.22x) \sin(0.19z) \\
y_{\text{corridor}} &= -2.2 \times \max\left(0, 1 - \frac{|z - (100 + 6\sin(0.05x))|}{22}\right)^2 \quad (x < 105) \\
y_{\text{pond1}} &= -2.4 \times \max\left(0, 1 - \frac{\sqrt{(x-75)^2 + (z-140)^2}}{22}\right)^{1.8} \\
y_{\text{pond2}} &= -2.1 \times \max\left(0, 1 - \frac{\sqrt{(x-45)^2 + (z-60)^2}}{18}\right)^{1.8}
\end{aligned}$$

As animals move across the landscape, their Y elevation dynamically adapts to the ground contour:
- Western ridge: $+2.5\text{m}$ to $+4.5\text{m}$
- Forest clearings: $+0.8\text{m}$ to $+1.5\text{m}$
- Ancient corridor valley: $-1.5\text{m}$ to $-2.4\text{m}$
- North & South Pond basins: $-2.1\text{m}$ to $-2.8\text{m}$ (water surface at $y = 0.05\text{m}$)
- Farmland terraces: $-0.2\text{m}$ to $-1.2\text{m}$

---

## 2. Individual Animal Roster & Demographics (60 Agents)

Every animal in the ecosystem has a unique identity, demographic stage, morphology scale, and behavioral role:

### A. Asian Elephants (*Elephas maximus*) — 8 Individuals
- `anim_001`: **Airavata (Lead Tusker)** — Alpha male, scale 1.30×, role: herd_matriarch, task: Corridor migration
- `anim_002`: **Indira (Matriarch)** — Matriarch cow, scale 1.15×, role: herd_matriarch, task: Browsing canopy
- `anim_003`: **Gajendra (Calf)** — Juvenile calf, scale 0.62×, role: boundary_averse, task: Following matriarch
- `anim_004`: **Balarama (Sub-Adult)** — Young bull, scale 0.88×, role: canopy_browser, task: Feeding on mangoes
- `anim_005`: **Kamala (Adult Cow)** — Cow, scale 1.05×, role: pond_drinker, task: Drinking at North Pond
- `anim_006`: **Ravana (Solitary Bull)** — Large tusker, scale 1.35×, role: boundary_prober, task: Probing perimeter fence
- `anim_007`: **Meena (Adult Cow)** — Cow, scale 1.02×, role: boundary_averse, task: Grazing clearing
- `anim_008`: **Chota (Calf)** — Calf, scale 0.60×, role: boundary_averse, task: Playing in corridor mud

### B. Chital / Spotted Deer (*Axis axis*) — 18 Individuals
- Stags: **Chital Stag Alpha** (1.18×, branched antlers), **Chital Stag 02** (1.12×), **Chital Stag Prober** (1.15×, boundary prober), **Chital Stag North** (1.16×)
- Hinds: **Spotted Hind 01–09** (0.95×–1.04×, grazing and drinking)
- Fawns & Yearlings: **Chital Fawn 01–04** (0.55×–0.60×), **Chital Yearling 01** (0.82×)

### C. Sambar Deer (*Rusa unicolor*) — 8 Individuals
- Stags: **Sambar Stag Prime** (1.25×, alpha), **Sambar Stag 02** (1.18×), **Sambar Solitary Prober** (1.20×)
- Cows: **Sambar Cow 01–03** (0.98×–1.02×, browsing shrubs, pond drinking)
- Young: **Sambar Yearling** (0.78×), **Sambar Fawn** (0.60×)

### D. Indian Wild Boar (*Sus scrofa cristatus*) — 12 Individuals
- Boars: **Old Razorback Boar** (1.28×, alpha with tusks), **Boar Scout 01** (0.95×, prober)
- Matrons: **Sow Matron 01–02** (1.00×–1.05×)
- Young: **Boar Sub-Adult 01–02** (0.82×–0.85×), **Piglets 01–06** (0.48×–0.53×)

### E. Gaur / Indian Bison (*Bos gaurus*) — 8 Individuals
- Bulls: **Titan Gaur Bull** (1.35×, muscular ridge, crescent horns), **Gaur Scout Bull** (1.22×, prober)
- Cows: **Gaur Cow 01–04** (1.00×–1.08×, western pasture grazers, pond drinkers)
- Calves: **Gaur Calf 01–02** (0.62×–0.65×)

### F. Bonnet Macaque (*Macaca radiata*) — 8 Individuals
- Troop: **Macaque Alpha Scout** (1.15×), **Macaque Forager 01–03** (0.95×–1.00×), **Macaque Sub-Adult** (0.80×, prober), **Juvenile Macaque 01–03** (0.58×–0.62×)

---

## 3. Dynamic Behavioral FSM & Task Execution

Each agent transitions across 10 distinct states governed by physiological needs (hunger, thirst, fatigue), herd cohesion, and boundary proximity:

1. `GRAZING`: Consumes pasture grass clearing patches.
2. `BROWSING`: Forages in wild mango groves and tall acacia canopy.
3. `DRINKING`: Visually positions at North/South Pond shoreline edges.
4. `RESTING`: Ruminates in the shade of sprawling Banyan trees.
5. `HERD_FOLLOW`: Sub-adults and calves steer towards the group leader.
6. `APPROACHING_BOUNDARY`: 4 designated bold probers approach the perimeter fence ($x \in [75\text{m}, 100\text{m}]$).
7. `TURNING_AWAY`: Deterred by virtual fence acoustic/strobe stimulus, retreats into forest.
8. `CROSSING_BOUNDARY`: High-risk breach towards sugarcane/paddy farm fields.
9. `WALKING`: Gentle wander through corridor riverbed.
10. `EXPLORING`: Roaming across ridge clearings.
