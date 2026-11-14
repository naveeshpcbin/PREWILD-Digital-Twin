import os

# 1. Patch app.js
app_js_path = r"D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\static\app.js"
with open(app_js_path, "r", encoding="utf-8") as f:
    app_text = f.read()

old_configs = """  const SPECIES_VISUAL_CONFIGS = {
    // 12 Distinct Biologically Rigged & Textured Wildlife Variants
    asian_elephant_bull: { scale: 1.0, color: 0x8c8d8f, glb: 'assets/animals/asian_elephant_bull.glb', yOffset: 0.0 },
    asian_elephant_cow: { scale: 0.95, color: 0x828385, glb: 'assets/animals/asian_elephant_cow.glb', yOffset: 0.0 },
    chital_stag: { scale: 1.15, color: 0xc88242, glb: 'assets/animals/chital_stag.glb', yOffset: 0.0 },
    chital_hind: { scale: 1.05, color: 0xc47e3e, glb: 'assets/animals/chital_hind.glb', yOffset: 0.0 },
    sambar_stag: { scale: 1.30, color: 0x5a3e2b, glb: 'assets/animals/sambar_stag.glb', yOffset: 0.0 },
    sambar_cow: { scale: 1.20, color: 0x543a28, glb: 'assets/animals/sambar_cow.glb', yOffset: 0.0 },
    wild_boar_razorback: { scale: 1.05, color: 0x383432, glb: 'assets/animals/wild_boar_razorback.glb', yOffset: 0.0 },
    wild_boar_sow: { scale: 0.95, color: 0x332f2e, glb: 'assets/animals/wild_boar_sow.glb', yOffset: 0.0 },
    gaur_bull: { scale: 1.25, color: 0x241d19, glb: 'assets/animals/gaur_bull.glb', yOffset: 0.0 },
    gaur_cow: { scale: 1.15, color: 0x28201b, glb: 'assets/animals/gaur_cow.glb', yOffset: 0.0 },
    bonnet_macaque_alpha: { scale: 0.90, color: 0x8a7760, glb: 'assets/animals/bonnet_macaque_alpha.glb', yOffset: 0.0 },
    bonnet_macaque_forager: { scale: 0.80, color: 0x82705a, glb: 'assets/animals/bonnet_macaque_forager.glb', yOffset: 0.0 },

    // Base Species Keys for Backward Compatibility
    asian_elephant: { scale: 1.0, color: 0x8c8d8f, glb: 'assets/animals/asian_elephant_production.glb', yOffset: 0.0 },
    chital_deer: { scale: 1.1, color: 0xc88242, glb: 'assets/animals/chital_deer.glb', yOffset: 0.0 },
    sambar_deer: { scale: 1.25, color: 0x5a3e2b, glb: 'assets/animals/sambar_deer.glb', yOffset: 0.0 },
    wild_boar: { scale: 1.0, color: 0x383432, glb: 'assets/animals/wild_boar.glb', yOffset: 0.0 },
    gaur_bison: { scale: 1.2, color: 0x241d19, glb: 'assets/animals/gaur_bison.glb', yOffset: 0.0 },
    bonnet_macaque: { scale: 0.85, color: 0x8a7760, glb: 'assets/animals/bonnet_macaque.glb', yOffset: 0.0 },
  };"""

new_configs = """  const SPECIES_VISUAL_CONFIGS = {
    // 12 Distinct Biologically Rigged & Textured Wildlife Variants
    asian_elephant_bull: { scale: 1.0, color: 0x8c8d8f, glb: 'assets/animals/asian_elephant_bull.glb', yOffset: 0.0 },
    asian_elephant_cow: { scale: 0.95, color: 0x828385, glb: 'assets/animals/asian_elephant_cow.glb', yOffset: 0.0 },
    chital_stag: { scale: 1.15, color: 0xc88242, glb: 'assets/animals/chital_stag.glb', yOffset: 0.0 },
    chital_hind: { scale: 1.05, color: 0xc47e3e, glb: 'assets/animals/chital_hind.glb', yOffset: 0.0 },
    sambar_stag: { scale: 1.30, color: 0x5a3e2b, glb: 'assets/animals/sambar_stag.glb', yOffset: 0.0 },
    sambar_cow: { scale: 1.20, color: 0x543a28, glb: 'assets/animals/sambar_cow.glb', yOffset: 0.0 },
    wild_boar_razorback: { scale: 1.05, color: 0x383432, glb: 'assets/animals/wild_boar_razorback.glb', yOffset: 0.0 },
    wild_boar_sow: { scale: 0.95, color: 0x332f2e, glb: 'assets/animals/wild_boar_sow.glb', yOffset: 0.0 },
    gaur_bull: { scale: 1.25, color: 0x241d19, glb: 'assets/animals/gaur_bull.glb', yOffset: 0.0 },
    gaur_cow: { scale: 1.15, color: 0x28201b, glb: 'assets/animals/gaur_cow.glb', yOffset: 0.0 },
    bonnet_macaque_alpha: { scale: 0.90, color: 0x8a7760, glb: 'assets/animals/bonnet_macaque_alpha.glb', yOffset: 0.0 },
    bonnet_macaque_forager: { scale: 0.80, color: 0x82705a, glb: 'assets/animals/bonnet_macaque_forager.glb', yOffset: 0.0 },

    // All 16 AAA Wildlife Species Production Library
    asian_elephant: { scale: 1.0, color: 0x8c8d8f, glb: 'assets/animals/asian_elephant_production.glb', yOffset: 0.0 },
    gaur_bison: { scale: 1.25, color: 0x241d19, glb: 'assets/animals/gaur_bison.glb', yOffset: 0.0 },
    bengal_tiger: { scale: 1.15, color: 0xd97724, glb: 'assets/animals/bengal_tiger.glb', yOffset: 0.0 },
    indian_leopard: { scale: 0.98, color: 0xe0a638, glb: 'assets/animals/indian_leopard.glb', yOffset: 0.0 },
    sloth_bear: { scale: 1.05, color: 0x1f1e1c, glb: 'assets/animals/sloth_bear.glb', yOffset: 0.0 },
    dhole: { scale: 0.90, color: 0xb84a23, glb: 'assets/animals/dhole.glb', yOffset: 0.0 },
    wild_boar: { scale: 1.0, color: 0x383432, glb: 'assets/animals/wild_boar.glb', yOffset: 0.0 },
    sambar_deer: { scale: 1.25, color: 0x5a3e2b, glb: 'assets/animals/sambar_deer.glb', yOffset: 0.0 },
    chital_deer: { scale: 1.1, color: 0xc88242, glb: 'assets/animals/chital_deer.glb', yOffset: 0.0 },
    indian_muntjac: { scale: 0.82, color: 0xa84824, glb: 'assets/animals/indian_muntjac.glb', yOffset: 0.0 },
    golden_jackal: { scale: 0.80, color: 0xb8884a, glb: 'assets/animals/golden_jackal.glb', yOffset: 0.0 },
    bonnet_macaque: { scale: 0.85, color: 0x8a7760, glb: 'assets/animals/bonnet_macaque.glb', yOffset: 0.0 },
    gray_langur: { scale: 0.88, color: 0xa8b0b8, glb: 'assets/animals/gray_langur.glb', yOffset: 0.0 },
    crested_porcupine: { scale: 0.80, color: 0x2b2826, glb: 'assets/animals/crested_porcupine.glb', yOffset: 0.0 },
    indian_peafowl: { scale: 0.95, color: 0x0c54a8, glb: 'assets/animals/indian_peafowl.glb', yOffset: 0.0 },
    indian_hare: { scale: 0.65, color: 0x9a8068, glb: 'assets/animals/indian_hare.glb', yOffset: 0.0 },
  };"""

assert old_configs in app_text, "old_configs not found in app.js"
app_text = app_text.replace(old_configs, new_configs, 1)

old_counts = """      // Update Species Counts
      const counts = {};
      multiAnimalPopulation.forEach(a => counts[a.species] = (counts[a.species] || 0) + 1);
      document.getElementById('cnt_elephant') && (document.getElementById('cnt_elephant').textContent = counts.asian_elephant || 0);
      document.getElementById('cnt_chital') && (document.getElementById('cnt_chital').textContent = counts.chital_deer || 0);
      document.getElementById('cnt_sambar') && (document.getElementById('cnt_sambar').textContent = counts.sambar_deer || 0);
      document.getElementById('cnt_boar') && (document.getElementById('cnt_boar').textContent = counts.wild_boar || 0);
      document.getElementById('cnt_gaur') && (document.getElementById('cnt_gaur').textContent = counts.gaur_bison || 0);
      document.getElementById('cnt_macaque') && (document.getElementById('cnt_macaque').textContent = counts.bonnet_macaque || 0);"""

new_counts = """      // Update Species Counts across all 16 species
      const counts = {};
      multiAnimalPopulation.forEach(a => counts[a.species] = (counts[a.species] || 0) + 1);
      const allSp = [
        'asian_elephant', 'gaur_bison', 'bengal_tiger', 'indian_leopard',
        'sloth_bear', 'dhole', 'wild_boar', 'sambar_deer',
        'chital_deer', 'indian_muntjac', 'golden_jackal', 'bonnet_macaque',
        'gray_langur', 'crested_porcupine', 'indian_peafowl', 'indian_hare'
      ];
      allSp.forEach(sp => {
        const el = document.getElementById(`cnt_${sp}`);
        if (el) el.textContent = counts[sp] || 0;
      });
      document.getElementById('cnt_elephant') && (document.getElementById('cnt_elephant').textContent = counts.asian_elephant || 0);
      document.getElementById('cnt_chital') && (document.getElementById('cnt_chital').textContent = counts.chital_deer || 0);
      document.getElementById('cnt_sambar') && (document.getElementById('cnt_sambar').textContent = counts.sambar_deer || 0);
      document.getElementById('cnt_boar') && (document.getElementById('cnt_boar').textContent = counts.wild_boar || 0);
      document.getElementById('cnt_gaur') && (document.getElementById('cnt_gaur').textContent = counts.gaur_bison || 0);
      document.getElementById('cnt_macaque') && (document.getElementById('cnt_macaque').textContent = counts.bonnet_macaque || 0);"""

assert old_counts in app_text, "old_counts not found in app.js"
app_text = app_text.replace(old_counts, new_counts, 1)

with open(app_js_path, "w", encoding="utf-8") as f:
    f.write(app_text)

print("SUCCESS: Updated app.js with 16 species visual configs and telemetry counters")

# 2. Patch index.html
html_path = r"D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\static\index.html"
with open(html_path, "r", encoding="utf-8") as f:
    html_text = f.read()

old_roster = """          <!-- Species Distribution Grid -->
          <div class="species-roster-grid" id="speciesRosterGrid">
            <div class="species-chip elephant"><span class="sp-icon">🐘</span> Elephant <strong id="cnt_elephant">8</strong></div>
            <div class="species-chip chital"><span class="sp-icon">🦌</span> Chital <strong id="cnt_chital">18</strong></div>
            <div class="species-chip sambar"><span class="sp-icon">🦌</span> Sambar <strong id="cnt_sambar">8</strong></div>
            <div class="species-chip boar"><span class="sp-icon">🐗</span> Boar <strong id="cnt_boar">12</strong></div>
            <div class="species-chip gaur"><span class="sp-icon">🐂</span> Gaur <strong id="cnt_gaur">6</strong></div>
            <div class="species-chip macaque"><span class="sp-icon">🐒</span> Macaque <strong id="cnt_macaque">8</strong></div>
          </div>"""

new_roster = """          <!-- Species Distribution Grid (16 Distinct Wildlife Species) -->
          <div class="species-roster-grid" id="speciesRosterGrid">
            <div class="species-chip elephant"><span class="sp-icon">🐘</span> Elephant <strong id="cnt_elephant">8</strong></div>
            <div class="species-chip gaur"><span class="sp-icon">🐂</span> Gaur <strong id="cnt_gaur">6</strong></div>
            <div class="species-chip tiger"><span class="sp-icon">🐅</span> Tiger <strong id="cnt_bengal_tiger">2</strong></div>
            <div class="species-chip leopard"><span class="sp-icon">🐆</span> Leopard <strong id="cnt_indian_leopard">1</strong></div>
            <div class="species-chip bear"><span class="sp-icon">🐻</span> Sloth Bear <strong id="cnt_sloth_bear">1</strong></div>
            <div class="species-chip dhole"><span class="sp-icon">🐕</span> Dhole <strong id="cnt_dhole">2</strong></div>
            <div class="species-chip boar"><span class="sp-icon">🐗</span> Boar <strong id="cnt_boar">12</strong></div>
            <div class="species-chip sambar"><span class="sp-icon">🦌</span> Sambar <strong id="cnt_sambar">8</strong></div>
            <div class="species-chip chital"><span class="sp-icon">🦌</span> Chital <strong id="cnt_chital">18</strong></div>
            <div class="species-chip muntjac"><span class="sp-icon">🦌</span> Muntjac <strong id="cnt_indian_muntjac">1</strong></div>
            <div class="species-chip jackal"><span class="sp-icon">🐺</span> Jackal <strong id="cnt_golden_jackal">1</strong></div>
            <div class="species-chip macaque"><span class="sp-icon">🐒</span> Macaque <strong id="cnt_macaque">8</strong></div>
            <div class="species-chip langur"><span class="sp-icon">🐒</span> Langur <strong id="cnt_gray_langur">2</strong></div>
            <div class="species-chip porcupine"><span class="sp-icon">🦔</span> Porcupine <strong id="cnt_crested_porcupine">1</strong></div>
            <div class="species-chip peafowl"><span class="sp-icon">🦚</span> Peafowl <strong id="cnt_indian_peafowl">1</strong></div>
            <div class="species-chip hare"><span class="sp-icon">🐇</span> Hare <strong id="cnt_indian_hare">1</strong></div>
          </div>"""

assert old_roster in html_text, "old_roster not found in index.html"
html_text = html_text.replace(old_roster, new_roster, 1)

old_filter = """          <!-- Individual Animal Directory (60 Distinct Agents) -->
          <div class="animal-directory-section">
            <div class="ec-section-title">INDIVIDUAL ANIMAL DIRECTORY (60 AGENTS)</div>
            <div class="animal-filter-bar">
              <select id="selSpeciesFilter" class="animal-filter-select" onchange="renderIndividualAnimalDirectory()">
                <option value="all">ALL SPECIES (60 AGENTS)</option>
                <option value="asian_elephant">ASIAN ELEPHANTS (8)</option>
                <option value="chital_deer">CHITAL DEER (18)</option>
                <option value="sambar_deer">SAMBAR DEER (8)</option>
                <option value="wild_boar">INDIAN WILD BOAR (12)</option>
                <option value="gaur_bison">GAUR BISON (8)</option>
                <option value="bonnet_macaque">BONNET MACAQUE (8)</option>
              </select>
            </div>"""

new_filter = """          <!-- Individual Animal Directory (74 Distinct Wildlife Agents) -->
          <div class="animal-directory-section">
            <div class="ec-section-title">INDIVIDUAL ANIMAL DIRECTORY (74 AGENTS • 16 SPECIES)</div>
            <div class="animal-filter-bar">
              <select id="selSpeciesFilter" class="animal-filter-select" onchange="renderIndividualAnimalDirectory()">
                <option value="all">ALL SPECIES (74 AGENTS)</option>
                <option value="asian_elephant">ASIAN ELEPHANTS (8)</option>
                <option value="gaur_bison">INDIAN GAUR (8)</option>
                <option value="bengal_tiger">BENGAL TIGERS (2)</option>
                <option value="indian_leopard">INDIAN LEOPARDS (1)</option>
                <option value="sloth_bear">SLOTH BEARS (1)</option>
                <option value="dhole">DHOLES / WILD DOGS (2)</option>
                <option value="wild_boar">INDIAN WILD BOARS (12)</option>
                <option value="sambar_deer">SAMBAR DEER (8)</option>
                <option value="chital_deer">CHITAL DEER (18)</option>
                <option value="indian_muntjac">INDIAN MUNTJAC (1)</option>
                <option value="golden_jackal">GOLDEN JACKALS (1)</option>
                <option value="bonnet_macaque">BONNET MACAQUES (8)</option>
                <option value="gray_langur">GRAY LANGURS (2)</option>
                <option value="crested_porcupine">CRESTED PORCUPINES (1)</option>
                <option value="indian_peafowl">INDIAN PEAFOWL (1)</option>
                <option value="indian_hare">INDIAN HARES (1)</option>
              </select>
            </div>"""

assert old_filter in html_text, "old_filter not found in index.html"
html_text = html_text.replace(old_filter, new_filter, 1)

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_text)

print("SUCCESS: Updated index.html with 16 species chips and directory options")

