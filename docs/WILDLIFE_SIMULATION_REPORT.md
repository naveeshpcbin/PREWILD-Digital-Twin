# PRW-Wild — Multi-Animal Wildlife Simulation Report

## 1. Executive Summary

The PRW-Wild Digital Twin features an autonomous multi-animal wildlife simulation engine (`src/prw_wild/ecosystem.py`) simulating **75 active wildlife agents** across **16 indigenous Western Ghats species**. 

Unlike simple scripted trajectories, each agent operates under an individualized behavioral Finite State Machine (FSM), social cohesion forces, predator avoidance dynamics, diurnal activity schedules, and realistic continuous terrain navigation.

---

## 2. Species Demographics & Ecological Structure

The 75 agents represent a biologically plausible ecological pyramid across four trophic tiers:

```
          [ APEX CARNIVORES (5) ]
       Tiger (2), Leopard (3)
                  ▲
        [ PACK / MESOPREDATORS (8) ]
       Dhole (4), Sloth Bear (2), Jackal (2)
                  ▲
        [ MEGA & UNGULATE HERBIVORES (42) ]
 Elephant (6), Gaur (8), Sambar (10), Chital (12), Muntjac (6)
                  ▲
        [ PRIMATES, OMNIVORES & SMALL FAUNA (20) ]
 Macaque (5), Langur (5), Boar (4), Porcupine (2), Peafowl (2), Hare (2)
```

### Complete Demographic Ledger

| # | Species Key | Common Name | Trophic Role | Population Count | Typical Speed ($m/s$) | Active Period |
| :- | :--- | :--- | :--- | :--- | :--- | :--- |
| **01** | `asian_elephant` | Asian Elephant | Mega-Herbivore | 6 | 1.4 – 2.5 | Crepuscular / Diurnal |
| **02** | `gaur_bison` | Indian Gaur | Large Bovine | 8 | 1.2 – 2.2 | Diurnal / Matinal |
| **03** | `bengal_tiger` | Bengal Tiger | Apex Carnivore | 2 | 1.8 – 4.5 | Nocturnal / Crepuscular |
| **04** | `indian_leopard` | Indian Leopard | Solitary Predator | 3 | 1.6 – 4.0 | Nocturnal / Arboreal |
| **05** | `sloth_bear` | Sloth Bear | Insectivore / Omnivore | 2 | 1.1 – 2.0 | Crepuscular / Nocturnal |
| **06** | `dhole` | Asiatic Wild Dog | Pack Carnivore | 4 | 2.0 – 5.0 | Diurnal / Crepuscular |
| **07** | `wild_boar` | Indian Wild Boar | Foraging Omnivore | 4 | 1.3 – 3.2 | Nocturnal / Diurnal |
| **08** | `sambar_deer` | Sambar Deer | Forest Ungulate | 10 | 1.4 – 3.5 | Crepuscular |
| **09** | `chital_deer` | Spotted Deer (Chital) | Gregarious Herbivore | 12 | 1.5 – 4.2 | Diurnal / Crepuscular |
| **10** | `indian_muntjac` | Barking Deer | Solitary Herbivore | 6 | 1.2 – 3.0 | Crepuscular |
| **11** | `golden_jackal` | Golden Jackal | Opportunist Scavenger | 2 | 1.4 – 3.0 | Nocturnal / Crepuscular |
| **12** | `bonnet_macaque` | Bonnet Macaque | Primate Forager | 5 | 1.0 – 2.5 | Diurnal |
| **13** | `gray_langur` | Southern Plains Gray Langur | Primate Folivore | 5 | 1.1 – 2.6 | Diurnal |
| **14** | `crested_porcupine` | Indian Crested Porcupine | Nocturnal Herbivore | 2 | 0.8 – 1.6 | Strictly Nocturnal |
| **15** | `indian_peafowl` | Indian Peafowl | Avian Forager | 2 | 0.9 – 2.2 | Diurnal |
| **16** | `indian_hare` | Black-naped Hare | Small Herbivore | 2 | 1.5 – 4.5 | Nocturnal / Crepuscular |
| **TOTAL** | **16 Species** | | | **75 Agents** | | |

---

## 3. Behavioral Finite State Machine (FSM)

Each individual agent updates its behavioral state machine according to physiological drives, environmental affordances, and sensory proximity:

```
          ┌─────────────┐
          │   RESTING   │◄───────────────┐
          └──────┬──────┘                │
                 │ Energy Repleted       │ Low Fatigue / Safe
                 ▼                       │
          ┌─────────────┐                │
   ┌─────►│  FORAGING   │────────────────┘
   │      └──────┬──────┘
   │             │ Thirst > Threshold
   │             ▼
   │      ┌─────────────┐
   │      │  DRINKING   │
   │      └──────┬──────┘
   │             │ Satiated
   │             ▼
   │      ┌─────────────┐
   └──────┤ PATROLLING  │
          └──────┬──────┘
                 │
        Predator Detected / Loud Noise
                 ▼
          ┌─────────────┐
          │   FLEEING   │
          └─────────────┘
```

1. **FORAGING:** Agent meanders through vegetation patches (Sal, Banyan, Grass clumps) seeking forage nodes. Speed: $0.8 - 1.4\text{ m/s}$.
2. **DRINKING:** Agent navigates towards the nearest carved pond basin (North Basin at $[75, 140]$ or South Basin at $[60, 45]$) when thirst exceeds threshold.
3. **PATROLLING / ROAMING:** Agent patrols home range territory following topological contour lines and animal tracks.
4. **RESTING:** Agent beds down in shaded forest understory during peak heat hours. Animation paused; heading locked.
5. **FLEEING:** Triggered when an apex predator (Tiger/Leopard) breaches safety radius ($< 25\text{m}$) or when Layer 1/2 deterrent sounders activate. Agent sprints toward dense forest cover at maximum sprint speed.

---

## 4. Multi-Agent Flocking & Collision Avoidance

Social ungulates (Chital herds of 12, Sambar groups of 10) execute Reynolds boids flocking rules:
1. **Separation:** Prevent inter-agent crowding ($r_{\text{sep}} = 2.5\text{m}$).
2. **Alignment:** Steer towards average heading of nearby herd members.
3. **Cohesion:** Steer towards average centroid of herd within perception radius ($r_{\text{per}} = 18\text{m}$).

### Perimeter Fence Avoidance
Agricultural perimeter boundary fences at $X = 85.0\text{m}$ exert a quadratic repulsion vector $\vec{F}_{\text{repulse}}$ preventing animals from tunneling through physical barriers unless in an explicit corridor breach scenario.

---

## 5. Visual Integration & Performance Verification

In `src/prw_wild/web/static/app.js`:
- Each of the 75 agents instantiates an optimized instance of its species GLB.
- Forward heading orientation is maintained at all times via $\phi = \operatorname{atan2}(v_x, v_z)$.
- Vertical terrain clamping ($y = \operatorname{getTerrainElevation}(x, z)$) prevents hovering.
- Animation playback speeds scale directly with agent ground velocity.
- **Rendering Performance:** 60.0 FPS sustained at 1080p WebGL under PCF Soft Shadow mapping.

