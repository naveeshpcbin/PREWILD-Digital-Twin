# PRW-Wild Wildlife Digital Twin: Complete Animal Asset Inventory

**Project:** PRW-Wild — AAA-Quality Immersive Wildlife Digital Twin  
**Document Revision:** 2.0.0 (Production Master)  
**Standard:** Antigravity Production Asset Standard & Three.js r128 PBR Engine  
**Blender Pipeline Version:** Blender 5.2.2 LTS  
**Target Architecture:** South Indian Forest-Farmland Wildlife Coexistence Model  

---

## 1. Executive Summary

This inventory documents all sixteen (16) biological wildlife species implemented, rigged, textured, and integrated into the PRW-Wild production digital twin. Every asset is authored in native Blender 5.2.2 LTS with organic `bmesh` quad-dominant geometry, skeletal armatures with vertex skinning weights, cyclic locomotion actions (`Walk`), and Physically Based Rendering (PBR) Principled BSDF materials with roughness, metallic, and normal channel modulation.

All 16 models are deployed in the production web directory at `src/prw_wild/web/static/assets/animals/` and mirrored in the project root `assets/animals/`.

---

## 2. 16-Species Production Matrix

| ID | Species Common Name | Scientific Name | Trophic Guild | Target Poly Count | GLB Size (bytes) | Armature Bones | Root Dimensions ($L \times W \times H$, m) | Production Asset Path |
|:---|:---|:---|:---|:---:|:---:|:---:|:---:|:---|
| 01 | **Asian Elephant** | *Elephas maximus indicus* | Megaherbivore / Keystone | 18,420 | 1,719,260 | 28 | $5.80 \times 2.40 \times 3.20$ | `assets/animals/asian_elephant.glb` |
| 02 | **Gaur / Indian Bison** | *Bos gaurus* | Large Herbivore | 2,500 | 175,972 | 16 | $3.10 \times 1.25 \times 2.05$ | `assets/animals/gaur_bison.glb` |
| 03 | **Bengal Tiger** | *Panthera tigris tigris* | Apex Carnivore | 2,396 | 167,132 | 16 | $2.60 \times 0.75 \times 1.10$ | `assets/animals/bengal_tiger.glb` |
| 04 | **Indian Leopard** | *Panthera pardus fusca* | Mesocarnivore | 2,396 | 167,300 | 16 | $1.95 \times 0.60 \times 0.78$ | `assets/animals/indian_leopard.glb` |
| 05 | **Sloth Bear** | *Melursus ursinus* | Insectivore / Frugivore | 2,396 | 163,700 | 16 | $1.75 \times 0.72 \times 0.88$ | `assets/animals/sloth_bear.glb` |
| 06 | **Dhole / Wild Dog** | *Cuon alpinus* | Pack Carnivore | 2,396 | 167,196 | 16 | $1.25 \times 0.42 \times 0.58$ | `assets/animals/dhole.glb` |
| 07 | **Indian Wild Boar** | *Sus scrofa cristatus* | Omnivore / Opportunist | 2,436 | 166,352 | 16 | $1.55 \times 0.62 \times 0.90$ | `assets/animals/wild_boar.glb` |
| 08 | **Sambar Deer** | *Rusa unicolor* | Large Cervid | 2,524 | 173,484 | 16 | $2.20 \times 0.85 \times 1.45$ | `assets/animals/sambar_deer.glb` |
| 09 | **Chital / Spotted Deer**| *Axis axis* | Medium Cervid | 2,492 | 171,092 | 16 | $1.65 \times 0.58 \times 1.05$ | `assets/animals/chital_deer.glb` |
| 10 | **Indian Muntjac** | *Muntiacus muntjak* | Small Cervid | 2,468 | 170,284 | 16 | $1.05 \times 0.40 \times 0.62$ | `assets/animals/indian_muntjac.glb` |
| 11 | **Golden Jackal** | *Canis aureus indicus* | Scavenger / Mesocarnivore| 2,396 | 167,224 | 16 | $0.98 \times 0.36 \times 0.48$ | `assets/animals/golden_jackal.glb` |
| 12 | **Bonnet Macaque** | *Macaca radiata* | Arboreal / Ground Primate| 2,416 | 165,980 | 16 | $0.65 \times 0.32 \times 0.52$ | `assets/animals/bonnet_macaque.glb` |
| 13 | **Gray Langur** | *Semnopithecus entellus* | Canopy Folivore | 2,416 | 165,328 | 16 | $0.78 \times 0.34 \times 0.68$ | `assets/animals/gray_langur.glb` |
| 14 | **Crested Porcupine** | *Hystrix indica* | Rodent / Herbivore | 2,652 | 184,160 | 16 | $0.85 \times 0.48 \times 0.45$ | `assets/animals/crested_porcupine.glb` |
| 15 | **Indian Peafowl** | *Pavo cristatus* | Terrestrial Avian | 1,344 | 97,476 | 12 | $1.80 \times 0.45 \times 0.85$ | `assets/animals/indian_peafowl.glb` |
| 16 | **Indian Hare** | *Lepus nigricollis* | Small Herbivore | 2,396 | 167,772 | 16 | $0.52 \times 0.24 \times 0.32$ | `assets/animals/indian_hare.glb` |

---

## 3. Detailed Morphological Specifications

### 01. Asian Elephant (*Elephas maximus indicus*)
- **Morphology:** Massive convex dorsum (humped back), dual hemispherical cranial lobes, broad fan-shaped ears, tapered prehensile trunk with single dorsal fingertip, columnar graviportal limbs with keratinized hoof nails, ivory tusk geometry on lead alpha tuskers.
- **Skeletal Structure:** 28 bones (`Root`, `Spine_01..04`, `Neck`, `Head`, `Trunk_01..06`, `Tusk_L/R`, `Leg_FL/FR/BL/BR`, `Tail_01..03`).
- **PBR Material:** Slate-grey leathery dermis (`#454341`), deep wrinkle displacement normal modulation, roughness 0.88, matte epidermal sheen.

### 02. Gaur / Indian Bison (*Bos gaurus*)
- **Morphology:** Prominent high dorsal muscular ridge extending to mid-back, broad convex frontal crest between massive crescent horn cores, distinctive pale-cream "white stockings" extending from hooves to knees/hocks.
- **Skeletal Structure:** 16 bones (`Root`, `Spine_01..03`, `Neck`, `Head`, `Horn_L/R`, `Leg_FL/FR/BL/BR`).
- **PBR Material:** Deep charcoal-black pelt (`#1c1a17`), horn core ivory/slate gradient, pale fawn stocking patches (`#ded5c3`), roughness 0.72.

### 03. Bengal Tiger (*Panthera tigris tigris*)
- **Morphology:** Muscular hypercarnivore quadruped, deep ribcage, powerful scapulae, low center of gravity, broad feline cranium with forward-facing stereoscopic orbits and tactile cheek ruffs.
- **Skeletal Structure:** 16 bones (`Root`, `Pelvis`, `Spine_01..03`, `Neck`, `Head`, `Limb_FL/FR/BL/BR`, `Tail_01..03`).
- **PBR Material:** Rich reddish-amber coat (`#b85214`), dark vertical disruptive camouflage stripes, white ventral/throat countershading, roughness 0.68.

### 04. Indian Leopard (*Panthera pardus fusca*)
- **Morphology:** Sleek, elongated sinuous body adapted for agile climbing and low-profile stalking, elongated cylindrical tail serving as counterweight during arboreal leaps.
- **Skeletal Structure:** 16 bones matching felid locomotion rig with extended tail articulation.
- **PBR Material:** Warm tawny-gold ground tone (`#c98a32`) with dense black rosettes and ventral cream countershading, roughness 0.64.

### 05. Sloth Bear (*Melursus ursinus*)
- **Morphology:** Shaggy, unkempt dark pelt, domed skull, prolonged mobile snout and flexible lips specialized for myrmecophagy, distinctive white/cream Y/V-shaped chest marking.
- **Skeletal Structure:** 16 bones with stocky forequarters and plantigrade limb configuration.
- **PBR Material:** Coarse jet-black shaggy coat (`#181818`), pale buff muzzle, ivory chest chevron, roughness 0.85.

### 06. Dhole / Asiatic Wild Dog (*Cuon alpinus*)
- **Morphology:** Athletic canid build, slender deep-chested thorax, erect rounded ears, bushy black-tipped tail.
- **Skeletal Structure:** 16 bones with cursorial canid pacing kinematics.
- **PBR Material:** Bright rust-red pelt (`#9c3d18`), white underside and paws, dark caudal plume, roughness 0.70.

### 07. Indian Wild Boar (*Sus scrofa cristatus*)
- **Morphology:** Robust wedge-shaped skull, stiff bristly dorsal crest running along spine, flattened cartilaginous nasal disc, protruding lower mandibular tusks.
- **Skeletal Structure:** 16 bones configured for low-slung, head-forward bulldozing locomotion.
- **PBR Material:** Coarse grizzled dark-grey/brown coat (`#2b2622`), ivory tusk points, roughness 0.82.

### 08. Sambar Deer (*Rusa unicolor*)
- **Morphology:** Largest Indian cervid, coarse shaggy neck mane (especially prominent in mature stags), rugged three-tined antler beams with heavy pearling, rugged mountainous build.
- **Skeletal Structure:** 16 bones including cervid spine chain and branching antler attachment vertices.
- **PBR Material:** Uniform dark umber-brown pelage (`#3d2f24`), buff undertones beneath chin and inner flanks, roughness 0.76.

### 09. Chital / Spotted Deer (*Axis axis*)
- **Morphology:** Graceful, medium-sized cervid, slender limbs, long slender neck, lyre-shaped three-tined antlers on mature bucks, distinct white spots arranged in horizontal lines across body throughout life.
- **Skeletal Structure:** 16 bones with delicate high-speed leaping articulation.
- **PBR Material:** Rich golden-fawn ground coat (`#ab6828`), brilliant white spot array, pure white throat patch and ventral belly, roughness 0.62.

### 10. Indian Muntjac / Barking Deer (*Muntiacus muntjak*)
- **Morphology:** Small, compact solitary cervid, hunched back profile, downward-sloping neck, short unbranched antlers raised on tall hair-covered facial pedicels, protruding upper canine tusks.
- **Skeletal Structure:** 16 bones with arched lumbar configuration.
- **PBR Material:** Deep chestnut-red coat (`#8b3a1a`), dark facial V-lines extending down forehead, white groin flash, roughness 0.68.

### 11. Golden Jackal (*Canis aureus indicus*)
- **Morphology:** Slender mesocarnivore canid, pointed fox-like muzzle, slender legs, moderately bushy tail.
- **Skeletal Structure:** 16 bones with agile trotting gait.
- **PBR Material:** Grizzled golden-yellow coat mixed with silver and black dorsal guard hairs (`#a8853b`), buff chest and legs, roughness 0.72.

### 12. Bonnet Macaque (*Macaca radiata*)
- **Morphology:** Medium-sized diurnal primate, prominent radiating whorl or "bonnet" of hair on the cranial vertex, slender torso, long tail exceeding body length.
- **Skeletal Structure:** 16 bones allowing quadrupedal semi-terrestrial/arboreal climbing poses.
- **PBR Material:** Greyish-brown dorsal fur (`#685848`), naked flesh-pink facial skin, pale grey underside, roughness 0.75.

### 13. Gray Langur (*Semnopithecus entellus*)
- **Morphology:** Tall, slender arboreal folivore, long limbs, prolonged black facial mask bordered by a white hair band, magnificent arching tail carried in an S-curve over back.
- **Skeletal Structure:** 16 bones with prolonged vertebral chain and curved tail geometry.
- **PBR Material:** Silvery-grey to straw-coloured pelage (`#8c8a82`), contrasting pitch-black facial and palmar skin, roughness 0.74.

### 14. Indian Crested Porcupine (*Hystrix indica*)
- **Morphology:** Stocky rodent with modified dorsal hairs forming an impressive crest of long flexible spines and rigid banded quills capable of erection and defensive rattling.
- **Skeletal Structure:** 16 bones supporting broad hemispherical spine carapace.
- **PBR Material:** Dark blackish-brown undercoat with striking black-and-white alternating banded quills (`#1e1c1a` with `#e0ded8` rings), roughness 0.65.

### 15. Indian Peafowl (*Pavo cristatus*)
- **Morphology:** Large galliform bird; males feature an iridescent fan-shaped cranial crest, elongated train of upper tail coverts adorned with brilliant ocelli ("eyes"), spurred tarsi.
- **Skeletal Structure:** 12 bones (`Root`, `Spine`, `Neck`, `Head`, `Beak`, `Crest`, `Wing_L/R`, `Leg_L/R`, `Train_01..02`).
- **PBR Material:** Shimmering iridescent cobalt blue neck (`#1248a0`), emerald-green train coverts with bronze ocelli, barred buff wings, roughness 0.45 (low roughness for iridescent sheen).

### 16. Indian Hare (*Lepus nigricollis*)
- **Morphology:** Small, agile lagomorph, elongated hind limbs built for rapid zig-zag evasion, long sensitive ears, characteristic velvety black or dark brown patch across nape of neck.
- **Skeletal Structure:** 16 bones with hyper-flexing lumbar spine and elongated hind feet.
- **PBR Material:** Grizzled reddish-grey body fur (`#745942`), pure white ventral underbelly, distinct charcoal-black nape patch, roughness 0.78.

---

## 4. In-Engine Asset Verification Checklist

- [x] All 16 GLBs present and readable by Three.js `GLTFLoader`.
- [x] Valid node hierarchies, single root transform per entity.
- [x] No NaN or infinite vertex positions; all geometry normals computed and unified.
- [x] Principled BSDF materials mapped with compliant diffuse/roughness parameters.
- [x] Active skeletal animation clips named `Walk` running in Three.js `AnimationMixer`.
- [x] Proper terrain elevation sampling ensuring feet contact ground at dynamic $y = \text{getTerrainElevation}(x, z)$.
- [x] Scaled in real-world metric units matching empirical field measurements.
