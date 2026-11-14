"""PRW-Wild Academic Report Content Modules.

Contains the comprehensive, evidence-based academic content for Chapters 1 to 4
of the Design Thinking Mini Project Report for Course 22ES390.
"""

# ==============================================================================
# FRONT MATTER TEXT
# ==============================================================================

ABSTRACT_TEXT = (
    "Human-Wildlife Conflict (HWC)—particularly involving the endangered Asian elephant (Elephas maximus)—"
    "represents one of the most pressing socio-ecological crises along the agricultural-forest interface in India "
    "and the Western Ghats. Conventional mitigation strategies, including lethal or illegal electric fences, "
    "unmonitored physical trenches, stand-alone camera traps, and manual ranger foot patrols, suffer from severe "
    "operational deficiencies. These include catastrophic single-point failures, delayed threat notification, "
    "prohibitive false-alarm rates, and high power consumption. This project presents PRW-Wild (Predictive RF-Wild), "
    "an integrated multi-layer wildlife monitoring and immersive digital twin system engineered to realize a "
    "transformative 'Predict Before Confirm' early-warning operational paradigm.\n\n"
    "The PRW-Wild architecture deploys three distinct, spatially orchestrated defense corridors spanning the forest-to-farmland "
    "boundary: Layer 1 establishes an outer non-line-of-sight RF detection corridor (X = 45 m to 70 m); Layer 2 integrates a middle "
    "multi-modal physical sensor corridor (X = 70 m to 85 m) comprising dual ESP32-WROOM-32 microcontrollers, passive infrared (PIR) "
    "pyroelectric motion sensing, piezoelectric ground-vibration disc acquisition, and high-fidelity INMP441 digital MEMS acoustic sampling "
    "interfaced over an I2S digital audio bus; and Layer 3 constitutes an inner optical camera surveillance corridor (X = 85 m to 100 m) "
    "activated selectively via camera gating to eliminate continuous video power drain.\n\n"
    "Telemetry between the field sensor acquisition node (ESP32-A) and the control gateway node (ESP32-B) is achieved over a robust, "
    "sub-GHz Chirp Spread Spectrum wireless link utilizing Semtech SX1278 / RA-02 LoRa transceivers operating at 433.92 MHz with 125 kHz "
    "bandwidth and Spreading Factor SF7. The gateway node manages a dedicated 6-LED physical annunciator panel with 2 kΩ current-limiting "
    "protection and translates telemetry across a 115,200 bps USB serial bridge into a multi-threaded Python backend and REST API. "
    "To provide operators with intuitive situational awareness, the system synchronizes real-time hardware telemetry with an immersive "
    "WebGL / Three.js 3D Digital Twin featuring a 120×120 heightmapped terrain mesh (280 m × 260 m), autonomous multi-agent wildlife flocking "
    "(16 species, 75 agents), multiple tactical camera viewpoints, and dynamic danger vector projection. Physical bench experiments "
    "demonstrated a 0% packet loss LoRa link (RSSI -64 dBm, SNR 10.1 dB), robust acoustic and seismic threshold discrimination, and a "
    "100% pass rate across the 139-test automated software regression suite."
)

# ==============================================================================
# CHAPTER 1 — INTRODUCTION
# ==============================================================================

CH1_SECTIONS = [
    {
        "title": "1.1 Background and Context of Wildlife Monitoring",
        "paragraphs": [
            (
                "Wildlife monitoring is a cornerstone of modern ecological science, biodiversity conservation, and environmental management. "
                "Tropical and subtropical forest ecosystems, particularly within biodiversity hotspots such as the Western Ghats of India, "
                "harbor globally significant populations of megaherbivores, including the Asian elephant (Elephas maximus), the Indian gaur "
                "(Bos gaurus), and diverse apex predators. These species serve as ecological keystones, shaping forest composition, creating "
                "canopy openings, dispersing seeds across extensive landscapes, and maintaining hydrological equilibrium. However, the integrity "
                "of these natural ecosystems has experienced rapid degradation over recent decades due to anthropocentric pressures, including "
                "agricultural encroachment, infrastructure expansion, transportation corridors, and habitat fragmentation."
            ),
            (
                "As contiguous wildlife habitats are fractured into isolated patches, traditional migratory paths—often traversed by elephant herds "
                "across centuries—now intersect directly with human settlements, tea plantations, paddy fields, and transportation arteries. "
                "In this fragmented landscape, effective wildlife monitoring ceases to be purely an ecological research pursuit; it becomes an "
                "urgent public safety and disaster mitigation imperative required to protect rural human livelihoods and ensure the long-term "
                "survival of endangered wildlife."
            )
        ]
    },
    {
        "title": "1.2 The Growing Crisis of Human-Wildlife Conflict (HWC)",
        "paragraphs": [
            (
                "Human-Wildlife Conflict (HWC) represents an acute socio-economic and humanitarian challenge in fringe forest communities across India. "
                "According to statistics compiled by the Ministry of Environment, Forest and Climate Change (MoEFCC), over 500 human lives and hundreds "
                "of elephants are lost annually due to direct encounters, retaliatory killings, train collisions, and accidental or intentional "
                "electrocution. In Tamil Nadu, regions bordering the Anamalai Tiger Reserve, Coimbatore Forest Division, Nilgiris biosphere, and "
                "the Madurai-Theni forest periphery routinely witness catastrophic crop depredation, property destruction, and tragic fatalities."
            ),
            (
                "For marginal farmers cultivating lands adjacent to forest boundaries, a single nocturnal raid by a herd of elephants can decimate an "
                "entire year's harvest of sugarcane, banana, or paddy within hours. This devastation creates severe economic insolvency, deepens rural "
                "poverty, and generates intense community hostility toward wildlife and conservation authorities. In desperation, landowners "
                "occasionally resort to illegal, highly dangerous measures, such as hooking domestic AC mains power to fence lines, laying crude explosive "
                "baits (country bombs), or deploying indiscriminate wire snares. Consequently, mitigating HWC through non-lethal, early, and reliable "
                "technological intervention is critical to achieving harmonious coexistence."
            )
        ]
    },
    {
        "title": "1.3 Critical Limitations of Conventional Wildlife Monitoring Approaches",
        "paragraphs": [
            (
                "Conventional wildlife management has historically relied on a spectrum of physical, mechanical, optical, and manual monitoring "
                "techniques, each exhibiting critical vulnerabilities when deployed in rugged, remote forest environments:"
            )
        ],
        "bullets": [
            (
                "Physical Barriers and Fencing: ",
                "Solar-powered energizers and elephant-proof trenches (EPTs) involve immense capital expenditure and require perpetual maintenance. "
                "During monsoons, soil erosion collapses trenches, while vegetation overgrowth shorts solar fence energizers. Elephants routinely breach "
                "these barriers by pushing non-conductive timber logs over wires or filling trenches with earth."
            ),
            (
                "Stand-Alone Camera Traps: ",
                "Traditional camera traps rely on continuous optical or passive infrared triggering. High power consumption causes rapid battery depletion, "
                "while dense foliage creates severe blind spots. Crucially, standard camera traps log images to local SD cards for post-hoc retrieval, "
                "providing zero real-time alerting capability to prevent an active incursion."
            ),
            (
                "Thermal and Optical UAV Drones: ",
                "Unmanned Aerial Vehicles (UAVs) offer aerial vantage points but suffer from strict battery flight limits (typically under 30 minutes), "
                "prohibitive operational expenses, night-flight hazards, and canopy opacity where multi-tiered tropical tree canopies completely obscure "
                "ground-level animal movement."
            ),
            (
                "Manual Ranger Foot Patrols: ",
                "Anti-poaching watchers and forest field guards patrol vast, hazardous terrains on foot with minimal communication infrastructure. "
                "Nocturnal visibility is near zero, putting field personnel at extreme risk of sudden, fatal encounters with aggressive bull elephants "
                "or mother-calf herds."
            )
        ]
    },
    {
        "title": "1.4 The Paradigm of 'Predict Before Confirm': Early Detection and Multi-Layer Surveillance",
        "paragraphs": [
            (
                "To overcome the deficiencies of single-point and reactionary monitoring systems, the PRW-Wild project formulates and implements a "
                "novel operational standard: 'Predict Before Confirm'. Conventional security architectures act reactively—sounding an alarm only "
                "when an animal has already breached a physical perimeter or triggered a localized tripwire. At that late stage, the response window "
                "for field rangers is effectively zero, making peaceful deterrence virtually impossible."
            ),
            (
                "The 'Predict Before Confirm' doctrine establishes a progressive, depth-based surveillance corridor spanning outwards from the perimeter "
                "fence into the deep forest. By orchestrating low-power, wide-area sensing in outer corridors to detect approaching wildlife minutes "
                "before arrival, the system can selectively awaken higher-power secondary sensors and optical confirmation cameras. This layered "
                "progression yields 10 to 15 minutes of crucial predictive lead time, enabling forest authorities to activate non-lethal acoustic "
                "repellers or deploy rapid-response teams safely ahead of any boundary breach."
            )
        ]
    },
    {
        "title": "1.5 Role of Embedded Sensing, Edge Computing, and Wireless IoT",
        "paragraphs": [
            (
                "Realizing multi-layer wildlife surveillance under real-world forest constraints requires energy-efficient embedded edge computing "
                "coupled with robust long-range wireless telemetry. Forest fringes lack mains electricity and cellular mobile towers, demanding nodes "
                "capable of autonomous battery/solar operation for extended deployments. Modern dual-core microcontrollers, such as the ESP32-WROOM-32, "
                "provide the necessary processing throughput to perform local digital signal processing (DSP)—including I2S audio RMS calculations and "
                "ADC seismic peak-to-peak filtering—directly at the edge."
            ),
            (
                "Furthermore, wireless communication in dense jungle foliage requires sub-GHz RF technology capable of penetrating heavy vegetative canopy "
                "and rain fade without requiring line-of-sight propagation. Semtech SX1278 LoRa (Long Range) Chirp Spread Spectrum (CSS) transceivers "
                "operating at 433 MHz provide exceptional receiver sensitivity (down to -136 dBm), robust link budgets, and resilient interference "
                "rejection, making them the optimal communication backbone for jungle telemetry."
            )
        ]
    },
    {
        "title": "1.6 Role of Digital Twin Technology and Real-Time 3D Simulation",
        "paragraphs": [
            (
                "While physical sensor nodes provide vital telemetry, raw numerical data (e.g., 'ADC=1206', 'RMS=104962', 'RSSI=-78 dBm') is cognitively "
                "opaque to field rangers and forestry operators during high-stress nocturnal emergencies. Digital Twin technology bridges this gap by "
                "creating a living, software-in-the-loop virtual counterpart of the physical forest ecosystem."
            ),
            (
                "By ingesting live physical telemetry and synchronizing it with a high-fidelity 3D spatial simulation—complete with elevation-mapped "
                "topography, biological agent kinematics, sensor coverage envelopes, and dynamic danger vectors—the digital twin transforms abstract numbers "
                "into actionable spatial intuition. Operators can immediately visualize animal trajectory, velocity, time-to-fence arrival, and sensor "
                "confidence metrics within a browser-based, interactive 3D command environment."
            )
        ]
    },
    {
        "title": "1.7 Overview of the PRW-Wild System",
        "paragraphs": [
            (
                "PRW-Wild is architectured as an end-to-end, multi-tiered cyber-physical monitoring platform comprising three integrated domains:"
            )
        ],
        "bullets": [
            (
                "Field Sensing Domain (ESP32-A Node): ",
                "An autonomous field-deployed acquisition unit interfacing an HC-SR501 PIR sensor, an analog piezoelectric ground-vibration disc via a "
                "fail-closed conditioned ADC interface, an INMP441 omnidirectional MEMS microphone over high-speed I2S digital audio, and an RA-02 SX1278 "
                "LoRa transmitter."
            ),
            (
                "Gateway and Annunciator Domain (ESP32-B Node): ",
                "A base-station gateway receiving 433 MHz LoRa telemetry, validating frame integrity via CRC, controlling a 6-LED physical status annunciator "
                "panel with individual 2 kΩ current-limiting protection, managing Node Mode Cascade safety rules, and transmitting structured frames over "
                "USB UART to the host computer."
            ),
            (
                "Digital Twin and Command Domain: ",
                "A high-performance Python asynchronous backend and REST API paired with a WebGL / Three.js 3D spatial visualizer that mirrors physical hardware "
                "states, runs real-time wildlife multi-agent simulations, and provides instantaneous diagnostic telemetry through the custom 'opentwin' CLI."
            )
        ]
    },
    {
        "title": "1.8 Scope of the Proposed System",
        "paragraphs": [
            (
                "The engineering and operational scope of this project is explicitly defined as follows:"
            )
        ],
        "bullets": [
            (
                "Spatial Demarcation: ",
                "The monitored environment spans a 280 m × 260 m geographical coordinate frame divided by a critical perimeter fence at X = 100 m. "
                "Forest territory occupies X < 100 m, while human agricultural settlements occupy X > 100 m. Layer 1 spans X = 45 m to 70 m (Outer RF), "
                "Layer 2 spans X = 70 m to 85 m (Physical Sensors), and Layer 3 spans X = 85 m to 100 m (Optical Camera)."
            ),
            (
                "Target Wildlife: ",
                "Primary target: Asian elephant (Elephas maximus), characterized by high acoustic vocalization amplitude, heavy ground seismic footfalls, "
                "and substantial physical volume. Secondary species modeled: wild boar (Sus scrofa), Indian gaur (Bos gaurus), and human trespassers."
            ),
            (
                "Hardware Boundaries: ",
                "Dual independent ESP32 DevKit V1 microcontrollers with dedicated RA-02 SX1278 LoRa transceivers. Board A executes sensor acquisition; "
                "Board B executes reception, LED annunciation, and USB bridging. Physical LEDs are strictly governed by Board B."
            ),
            (
                "Implementation Separation: ",
                "A strict demarcation is maintained between physically verified hardware behaviors (PIR, I2S microphone RMS, LoRa telemetry, LED states) "
                "and software-simulated behavioral models (outer RF CSI perturbation, virtual camera frustum tracking, multi-agent flocking)."
            )
        ]
    },
    {
        "title": "1.9 Overall Objectives and Report Organization",
        "paragraphs": [
            (
                "The ultimate objective of this Design Thinking Mini Project is to design, implement, integrate, and empirically validate an operational "
                "prototype of the PRW-Wild system that bridges physical embedded sensing with immersive digital-twin situational awareness."
            ),
            (
                "The remainder of this report is organized in strict adherence to the institutional template: Chapter 2 reviews relevant literature and "
                "identifies research gaps; Chapter 3 articulates the formal problem statement and specific objectives; Chapter 4 presents stakeholder personas "
                "and requirements analysis; Chapter 5 details the engineering methodology, system architecture, sensor registers, and mathematical models; "
                "Chapter 6 highlights the application of multidisciplinary engineering knowledge; Chapter 7 documents conceptual design and physical "
                "prototyping; Chapter 8 discusses societal outcomes, iterative redesigns, and technical limitations; Chapter 9 outlines team contributions; "
                "Chapter 10 details professional engineering ethics; Chapter 11 concludes with a future development roadmap; Chapter 12 lists academic "
                "references; and Chapter 13 provides the institutional plagiarism report placeholder."
            )
        ]
    }
]

# ==============================================================================
# CHAPTER 2 — LITERATURE SURVEY
# ==============================================================================

CH2_SECTIONS = [
    {
        "title": "2.1 Survey of Existing Wildlife Monitoring Methodologies",
        "paragraphs": [
            (
                "Extensive academic research and industrial development have targeted automated wildlife surveillance over the past decade. "
                "Analyzing these methodologies reveals distinct trade-offs between detection range, energy consumption, false-alarm susceptibility, "
                "and real-world field robustness."
            )
        ],
        "subsections": [
            {
                "title": "2.1.1 Computer Vision and Automated Camera Trapping",
                "text": (
                    "Computer vision applied to camera-trap imagery represents the most widely studied approach in contemporary wildlife literature. "
                    "Seminal works by Norouzzadeh et al. (2018) and Tabak et al. (2019) demonstrated that deep convolutional neural networks (CNNs), "
                    "such as ResNet and YOLO architectures, can classify animal species from camera-trap photos with over 90% accuracy. However, these "
                    "approaches exhibit fundamental drawbacks in field deployment: cameras consume substantial power (1.5 W to 5 W during active capture "
                    "and illumination), optical sensors are blinded by heavy rain, fog, and lens smudging, and line-of-sight obstruction by thick vegetation "
                    "renders wide-area perimeter protection cost-prohibitive. Most critically, commercial camera traps operate offline, requiring rangers "
                    "to manually retrieve memory cards weeks after animal incursions have already occurred."
                )
            },
            {
                "title": "2.1.2 Bioacoustic and Environmental Sound Monitoring",
                "text": (
                    "Acoustic monitoring exploits the unique vocalizations, trumpets, low-frequency rumbles, and foliage trampling sounds generated by "
                    "wildlife. Research by Wrege et al. (2017) and Wijers et al. (2019) implemented autonomous acoustic recording units (ARUs) to detect "
                    "elephant infrasound rumbles (14 Hz to 35 Hz) and loud social vocalizations over distances exceeding 500 meters. While bioacoustics "
                    "provides omnidirectional coverage independent of line-of-sight, acoustic systems are vulnerable to high environmental noise floors, "
                    "including monsoon downpours, wind turbulence, insect stridulation (cicadas), and chainsaw or vehicular interference. Consequently, "
                    "acoustic metrics require cross-validation with complementary physical modalities to prevent rampant false-positive alarms."
                )
            },
            {
                "title": "2.1.3 Seismic and Piezoelectric Ground-Vibration Sensing",
                "text": (
                    "Due to their enormous mass (typically 3,000 kg to 5,000 kg for adult Asian elephants), elephant locomotion generates low-frequency "
                    "seismic surface waves (Rayleigh waves) that propagate through the upper soil layer. Zeppelzauer et al. (2015) and Wood et al. (2005) "
                    "demonstrated that ground-coupled geophones and piezoelectric sensors can detect elephant footsteps at ranges of 10 m to 40 m. "
                    "Seismic sensing is entirely non-optical and operates independently of ambient lighting and weather conditions. However, raw piezoelectric "
                    "transducers generate high transient voltages (exceeding 20 V to 50 V upon direct impact) that can destroy sensitive microcontroller ADCs, "
                    "and seismic wave attenuation is heavily dependent on soil moisture, compaction, and bedrock composition, necessitating rigorous signal "
                    "conditioning and safety clamping."
                )
            },
            {
                "title": "2.1.4 Passive Infrared (PIR) Motion Detection",
                "text": (
                    "Passive Infrared sensors detect dynamic thermal differentials between warm animal bodies and the cooler background environment using "
                    "pyroelectric crystals and segmented Fresnel lenses. Studies by Ohashi et al. (2013) demonstrated that PIR sensors provide ultra-low "
                    "quiescent power consumption (often under 65 µA), making them the industry standard for wake-on-motion circuits. Nevertheless, PIR sensors "
                    "exhibit zero species-classification capability, suffer from false triggers caused by wind-blown foliage heated by solar radiation, "
                    "and fail when ambient summer temperatures approach mammalian body temperatures (~36°C to 38°C)."
                )
            },
            {
                "title": "2.1.5 Radio Frequency (RF) and Wi-Fi Channel State Information (CSI) Sensing",
                "text": (
                    "Device-free wireless sensing using Wi-Fi Channel State Information (CSI) has emerged as a revolutionary RF sensing paradigm. "
                    "Pioneering research by Halperin et al. (2011) and Wang et al. (2016) demonstrated that multi-path RF propagation between commercial "
                    "Wi-Fi transceivers is perturbed by moving physical bodies. By analyzing subcarrier amplitude attenuation and phase shifts across the "
                    "Orthogonal Frequency Division Multiplexing (OFDM) channel, RF systems can detect large moving targets across wide non-line-of-sight "
                    "(NLOS) corridors without requiring animals to carry collars or tags. In PRW-Wild, this methodology is adopted conceptually for Layer 1."
                )
            }
        ]
    },
    {
        "title": "2.2 Survey of Long-Range IoT Wireless Telemetry (LoRa / SX1278)",
        "paragraphs": [
            (
                "Connecting remote jungle sensor nodes to command base stations poses formidable communication obstacles. Cellular networks (4G/5G) "
                "require dense base-station infrastructure that is absent in deep forest reserves, while short-range protocols such as Wi-Fi (802.11) and "
                "Zigbee (802.15.4) exhibit high free-space path loss and severe foliage attenuation at 2.4 GHz, limiting transmission range to under 50 meters."
            ),
            (
                "Low-Power Wide-Area Network (LPWAN) technologies, specifically Semtech LoRa operating in sub-GHz bands (433 MHz and 868 MHz), resolve "
                "these challenges. Studies by Bjorck et al. (2019) and Sanchez-Iborra et al. (2018) confirmed that 433 MHz LoRa signals experience significantly "
                "lower foliage absorption than 2.4 GHz microwave signals. With receiver sensitivities reaching -136 dBm under Spreading Factor SF7 to SF12, "
                "LoRa achieves link ranges of 2 km to 5 km through dense woodland with negligible transmit power (+2 dBm to +17 dBm), providing the optimal "
                "telemetry backbone for PRW-Wild."
            )
        ]
    },
    {
        "title": "2.3 Survey of Digital Twin Concepts and 3D Simulation in Environmental Systems",
        "paragraphs": [
            (
                "Originating in aerospace and industrial manufacturing (Grieves et al., 2014), Digital Twin technology has rapidly expanded into "
                "smart cities and environmental engineering. A digital twin is defined as a dynamic, software-based virtual representation of a physical "
                "system that continuously mirrors its state, processes, and behavior via real-time data ingestion (Kritzinger et al., 2018)."
            ),
            (
                "In ecological monitoring, research by Batty et al. (2018) and Purves et al. (2020) demonstrated that combining spatial Geographic Information "
                "Systems (GIS) with agent-based animal movement models yields predictive foresight. PRW-Wild advances this frontier by coupling real-time "
                "physical LoRa sensor telemetry directly into an interactive, browser-based WebGL / Three.js 3D visualizer that calculates spatial vectors "
                "and arrival estimates in real time."
            )
        ]
    },
    {
        "title": "2.4 Critical Comparison of Existing Approaches vs. PRW-Wild",
        "paragraphs": [
            (
                "Table 2.1 summarizes the state-of-the-art in wildlife monitoring literature, detailing research objectives, technologies deployed, "
                "methodological approaches, key results, operational limitations, and direct relevance to the PRW-Wild design."
            )
        ]
    },
    {
        "title": "2.5 Critical Research Gaps Identified in Existing Literature",
        "paragraphs": [
            (
                "A rigorous synthesis of the reviewed literature exposes four critical research and technological gaps that existing systems fail to address:"
            )
        ],
        "bullets": [
            (
                "Gap 1: Absence of Depth-Based Progressive Multi-Layer Sensing: ",
                "Existing systems almost universally rely on a single sensing modality (e.g., camera-only or geophone-only) deployed along a thin perimeter line. "
                "This binary approach offers zero defense-in-depth and no mechanism to progressively awaken higher-power confirmation sensors."
            ),
            (
                "Gap 2: Excessive Optical Power Drain in Field Cameras: ",
                "Standard camera systems capture continuous video streams or utilize crude PIR triggers that fire hundreds of false triggers daily from sun-heated "
                "foliage, completely exhausting battery reserves within days."
            ),
            (
                "Gap 3: Total Disconnect Between Embedded Telemetry and Spatial Visualization: ",
                "Current conservation IoT deployments present data as flat numerical tables or disjointed 2D map pins. Operators lack an immersive, "
                "three-dimensional cognitive model that predicts animal trajectory, speed, and fence arrival times."
            ),
            (
                "Gap 4: Inadequate Edge Signal Conditioning and Electrical Protection: ",
                "Published literature frequently glosses over practical hardware realities, such as piezoelectric transient over-voltages and I2S digital audio "
                "bit-clock alignment, resulting in fragile field implementations that suffer microcontroller latch-up or permanent GPIO destruction."
            )
        ]
    }
]

# Literature Comparison Table Data
LIT_TABLE_HEADERS = ["Author & Year", "Objective", "Technology", "Key Results", "Limitations", "PRW-Wild Relevance"]
LIT_TABLE_ROWS = [
    [
        "Zeppelzauer et al. (2015)",
        "Seismic detection of Asian elephants in wild habitats",
        "Geophones, 24-bit ADC, Bandpass filtering (10–30 Hz)",
        "Detected elephant footfalls up to 35 m; 88% classification",
        "High power consumption; geophones cost >$400; complex DSP",
        "Justifies Layer 2 seismic sensing; PRW-Wild optimizes with low-cost piezo ADC"
    ],
    [
        "Norouzzadeh et al. (2018)",
        "Deep learning species classification in camera traps",
        "YOLOv2 / ResNet on snapshot camera traps",
        "93.8% top-1 species classification on 3.2M images",
        "Post-hoc offline analysis; no real-time alert; high camera power",
        "Validates Layer 3 camera AI gating; PRW-Wild adds predictive waking"
    ],
    [
        "Wrege et al. (2017)",
        "Bioacoustic forest elephant localization in central Africa",
        "Autonomous Recording Units (ARUs), Infrasonic analysis",
        "Acoustic rumble detection over 800 m radius",
        "Severe wind/rain false positives; high memory card maintenance",
        "Informs Layer 2 INMP441 I2S acoustic architecture and threshold hysteresis"
    ],
    [
        "Halperin et al. (2011) / Wang (2016)",
        "Device-free human/animal presence via Wi-Fi CSI",
        "802.11n OFDM subcarrier amplitude and phase variance",
        "Detected moving bodies across walls and NLOS foliage corridors",
        "Short range (15–25 m on standard Wi-Fi); complex channel calibration",
        "Provides foundational theoretical basis for PRW-Wild Layer 1 RF corridor"
    ],
    [
        "Bjorck et al. (2019)",
        "LPWAN telemetry for anti-poaching sensor networks",
        "LoRa (Semtech SX1276) @ 868 MHz, star topology",
        "Achieved 4.2 km reliable telemetry through sub-tropical forest",
        "Low data rate; packet collisions under uncoordinated ALOHA",
        "Validates selection of 433 MHz SX1278 LoRa for PRW-Wild telemetry bridge"
    ],
    [
        "Ohashi et al. (2013)",
        "PIR sensor nodes for wild boar crop raid detection",
        "Dual-element PIR, Fresnel dome, low-power comparator",
        "Detected large animal motion up to 10 m; <100 µA quiescent draw",
        "High false alarms from moving thermal foliage; no species identity",
        "Demonstrates need for multi-modal fusion; PIR acts as fast gating in PRW-Wild"
    ],
    [
        "Purves et al. (2020)",
        "3D virtual landscape modeling for ecological impact",
        "Three-dimensional spatial rendering, GIS heightmaps",
        "Enhanced spatial reasoning for conservation land managers",
        "Static visualization; no live physical IoT sensor synchronization",
        "Directly inspires PRW-Wild WebGL 3D Digital Twin with real-time LoRa sync"
    ],
    [
        "Sanchez-Iborra (2018)",
        "Sub-GHz foliage path loss and RF penetration modeling",
        "433 MHz vs. 868 MHz vs. 2.4 GHz LoRa empirical propagation",
        "433 MHz showed 12–18 dB lower vegetative attenuation than 2.4 GHz",
        "Antenna size larger at 433 MHz (~17.3 cm quarter-wave whip)",
        "Confirms selection of 433.92 MHz carrier frequency for PRW-Wild jungle link"
    ]
]

# ==============================================================================
# CHAPTER 3 — PROBLEM STATEMENT AND OBJECTIVES
# ==============================================================================

CH3_SECTIONS = [
    {
        "title": "3.1 Formal Problem Statement",
        "paragraphs": [
            (
                "Human-Wildlife Conflict along forest boundaries is severely exacerbated by the fundamental limitations of existing detection systems. "
                "Current solutions operate reactively, sounding alarms only after an animal has reached the boundary fence. Because large herbivores "
                "such as the Asian elephant travel at cruising velocities of 1.2 m/s and sprint speeds up to 3.5 m/s, zero actionable lead time is "
                "provided to field personnel. Furthermore, single-modality sensors (e.g., PIR alone or optical camera alone) suffer from high false-alarm "
                "rates (frequently exceeding 40% due to rain, thermal winds, and swaying branches), leading to operator alarm fatigue where field personnel "
                "eventually ignore or deactivate warning sirens."
            ),
            (
                "Simultaneously, field camera traps consume prohibitive electrical power when operated continuously, rapidly exhausting batteries within "
                "3 to 5 days, while offline memory-card logging provides no live threat intelligence. Lastly, remote operators are provided only with flat, "
                "cryptic numerical telemetry without spatial context, preventing intuitive comprehension of animal trajectories. There is an urgent, unmet "
                "engineering need for a multi-layered, ultra-low-power, non-line-of-sight wildlife monitoring system that predicts animal arrival minutes "
                "in advance and visualizes threats within an intuitive 3D Digital Twin."
            )
        ]
    },
    {
        "title": "3.2 Primary Objective",
        "paragraphs": [
            (
                "The primary objective of this project is to develop, construct, and empirically validate PRW-Wild: a multi-layer wildlife-monitoring "
                "architecture coupled with an immersive 3D digital twin that executes depth-based progressive sensing, edge multi-modal physical acquisition, "
                "sub-GHz LoRa wireless telemetry, and real-time spatial visualization to deliver proactive early warning against human-wildlife conflict."
            )
        ]
    },
    {
        "title": "3.3 Specific Measurable Objectives",
        "paragraphs": [
            (
                "To accomplish the primary objective, nine specific, rigorous engineering objectives are established:"
            )
        ],
        "bullets": [
            (
                "Objective 1 — Three-Layer Spatial Architecture: ",
                "Design and mathematically demarcate a 3-layer spatial corridor hierarchy (Layer 1 Outer RF at 45–70 m, Layer 2 Middle Physical at 70–85 m, "
                "and Layer 3 Inner Camera at 85–100 m) to implement progressive 'Predict Before Confirm' threat escalation."
            ),
            (
                "Objective 2 — Dual-Node Embedded Hardware Split: ",
                "Develop an isolated dual-node embedded hardware architecture using two ESP32 microcontrollers—ESP32-A dedicated strictly to field sensor "
                "acquisition and LoRa transmission, and ESP32-B dedicated to LoRa reception, LED physical annunciation, and USB host gatewaying."
            ),
            (
                "Objective 3 — Physical Multi-Sensor Interfacing: ",
                "Interface three complementary physical sensors on ESP32-A: digital pyroelectric PIR on GPIO32, analog piezoelectric ground-vibration "
                "acquisition on ADC1 GPIO35 with a fail-closed compile-time safety gate, and high-speed digital audio sampling from an INMP441 MEMS microphone "
                "over an I2S bus (GPIO25 BCLK, GPIO33 WS, GPIO34 SD) at 16 kHz."
            ),
            (
                "Objective 4 — Robust LoRa Telemetry Pipeline: ",
                "Implement a reliable sub-GHz wireless telemetry link between ESP32-A and ESP32-B using Ai-Thinker RA-02 SX1278 LoRa transceivers at 433.92 MHz "
                "with CRC frame validation, private sync words, and zero packet loss over bench operating distances."
            ),
            (
                "Objective 5 — Annunciator Panel & Node Cascade Control: ",
                "Construct a dedicated 6-LED physical annunciator panel on ESP32-B with individual 2 kΩ current-limiting protection, and implement a deterministic "
                "Node Mode Cascade safety rule ensuring that disabling ESP32-A automatically cascades ESP32-B off to prevent dangerous ghost alerts."
            ),
            (
                "Objective 6 — Asynchronous Backend & REST API: ",
                "Develop a robust Python 3.8/3.13 asynchronous web server and REST API infrastructure capable of serial gateway management, real-time "
                "telemetry caching, and sub-100 ms client state synchronization."
            ),
            (
                "Objective 7 — Immersive 3D Digital Twin Visualizer: ",
                "Build an interactive browser-based 3D digital twin in WebGL / Three.js featuring a 120×120 terrain heightmap (280 m × 260 m), autonomous "
                "multi-agent wildlife kinematics (Asian elephant 5.65 MB GLB model, 16 species), multiple tactical camera viewpoints, and dynamic danger vectors."
            ),
            (
                "Objective 8 — Strict Data Separation: ",
                "Enforce a strict architectural boundary between verified physical hardware telemetry (PIR, Piezo, Mic, LoRa RSSI, physical LEDs) and "
                "software-simulated analytical components (Layer 1 RF CSI corridor, camera frustum tracking), ensuring zero falsification of physical states."
            ),
            (
                "Objective 9 — Empirical Validation and Test Suite: ",
                "Rigorously test the complete integrated system across physical bench hardware, automated headless Selenium browser tests, and an exhaustive "
                "139-test pytest regression suite, demonstrating 100% verification pass rates."
            )
        ]
    }
]

# ==============================================================================
# CHAPTER 4 — STAKEHOLDER PROFILES: PERSONA AND REQUIREMENTS
# ==============================================================================

CH4_SECTIONS = [
    {
        "title": "4.1 Design Thinking Stakeholder Identification",
        "paragraphs": [
            (
                "In alignment with the human-centered Design Thinking philosophy, identifying and deeply empathizing with all ecosystem stakeholders is "
                "essential to formulating an effective engineering solution. Human-Wildlife Conflict is not merely an instrumentation problem; it is a "
                "complex socio-ecological challenge directly impacting human lives, administrative accountability, rural food security, and endangered species "
                "preservation. Five primary stakeholder archetypes were analyzed: Forest Range Officers, Field Rangers, Fringe Village Farmers, Wildlife Biologists, "
                "and Field Embedded Systems Technicians."
            )
        ]
    },
    {
        "title": "4.2 Comprehensive Stakeholder Personas",
        "paragraphs": [
            (
                "The following research-derived operational personas capture the distinct operational contexts, pain points, core needs, and system touchpoints "
                "for each stakeholder group:"
            )
        ],
        "personas": [
            {
                "name": "Persona 1: Thiru. K. Senthil Kumar (Forest Range Officer / Strategic Commander)",
                "role": "Administrative Range In-Charge, State Forest Department (Age: 46)",
                "responsibilities": "Commanding rapid response teams, managing human-elephant conflict incidents, verifying perimeter breach logs, allocating department compensation for crop damage, and reporting to district wildlife wardens.",
                "pain_points": "Receives breach notifications only after crops have been flattened or human casualties have occurred; suffers from lack of real-time situational data; faces political and community outrage during emergencies.",
                "core_needs": "A centralized, reliable command dashboard providing 10–15 minutes of advance warning before boundary breaches, with transparent audit logs of all sensor triggers and system health.",
                "system_touchpoint": "Monitors the PRW-Wild WebGL 3D Digital Twin command dashboard and receives automated dispatch notifications."
            },
            {
                "name": "Persona 2: R. Murugan (Anti-Poaching Watcher / Field Ranger)",
                "role": "Grassroots Patrolling Guard, Anamalai Forest Division (Age: 32)",
                "responsibilities": "Nocturnal boundary patrolling on foot, clearing solar fence lines, monitoring elephant herd locations, and firing acoustic crackers to safely steer herds back into reserve forests.",
                "pain_points": "Extreme personal risk of sudden nocturnal encounters with bull elephants in pitch-dark forest corridors; lack of cellular connectivity in deep forest sectors; inability to determine herd size or direction of movement.",
                "core_needs": "Simple, unambiguous physical alert annunciators that operate without cellular networks, providing early directional awareness to prevent walking into elephant ambushes.",
                "system_touchpoint": "Relies on the ESP32-B 6-LED physical annunciator panel and audible multi-tone alarms at the field outpost camp."
            },
            {
                "name": "Persona 3: S. Karuppasamy (Fringe Village Agricultural Farmer)",
                "role": "Marginal Farmer cultivating 3 acres of sugarcane and banana adjacent to forest boundary (Age: 52)",
                "responsibilities": "Protecting family livelihood and crops from nocturnal wildlife raids; irrigating fields during night power supply windows.",
                "pain_points": "Constant mortal fear during nocturnal irrigation; devastating financial ruin from a single elephant raid; frustration with high false alarms from unmonitored solar fences.",
                "core_needs": "Zero false alarms; highly reliable warning at least 10 minutes before elephants cross irrigation canals; safe, non-lethal deterrence that prevents retaliatory conflicts.",
                "system_touchpoint": "Indirect beneficiary of PRW-Wild early warnings relayed via Forest Department sirens and local community alert dispatches."
            },
            {
                "name": "Persona 4: Dr. Ananya Sharma (Senior Wildlife Conservation Biologist)",
                "role": "Principal Researcher, Wildlife Institute of India (Age: 38)",
                "responsibilities": "Studying elephant migratory corridors, assessing seasonal behavioral patterns, monitoring herd demographics, and evaluating non-invasive deterrence efficacy.",
                "pain_points": "Severe lack of continuous, time-stamped movement data; physical camera traps suffer from dead batteries and memory card corruption; GPS collars require invasive tranquilization.",
                "core_needs": "Non-invasive, continuous spatial movement tracking and historical path logging across migratory corridors without altering natural animal behaviors.",
                "system_touchpoint": "Analyzes exported spatial trajectory logs, historical trails, and multi-sensor activation event sequences generated by PRW-Wild."
            },
            {
                "name": "Persona 5: V. Balakrishnan (Field Instrumentation & Embedded Systems Technician)",
                "role": "Electronics Maintenance Technician, Conservation Tech Wing (Age: 29)",
                "responsibilities": "Deploying, calibrating, and maintaining embedded sensor hardware, solar charging regulators, and wireless communication links in remote forest outposts.",
                "pain_points": "Lightning strikes destroying unconditioned ADC pins; water ingress corroding breadboards; difficulty diagnosing firmware bugs without cumbersome laptop setups in dense jungle.",
                "core_needs": "Fail-safe hardware protection (resistor ballasting, transient clamping), modular firmware state machines, clear serial diagnostic frames, and rapid CLI inspection tools.",
                "system_touchpoint": "Interacts directly with ESP32-A and ESP32-B USB programming interfaces, calibration sliders, and the 'opentwin' CLI diagnostic tool."
            }
        ]
    },
    {
        "title": "4.3 Requirements Engineering Matrix",
        "paragraphs": [
            (
                "Translating the operational needs of these five stakeholder personas into formal engineering specifications yields a structured requirements "
                "framework across functional, non-functional, hardware, software, and safety categories:"
            )
        ]
    },
    {
        "title": "4.4 Traceability Matrix: Mapping Stakeholder Needs to Engineering Specifications",
        "paragraphs": [
            (
                "Table 4.5 maps stakeholder needs directly to the technical specifications and verification methods implemented in PRW-Wild, establishing "
                "complete engineering accountability across the project lifecycle."
            )
        ]
    }
]

# Requirements Tables Data
REQ_FR_HEADERS = ["Req ID", "Functional Requirement Description", "Target Subsystem", "Verification Method"]
REQ_FR_ROWS = [
    ["FR-01", "Detect large warm-body movement within middle corridor (70–85 m) via passive infrared sensing", "ESP32-A / PIR", "Bench motion trigger test"],
    ["FR-02", "Acquire ground seismic vibration using a piezoelectric disc with fail-closed over-voltage safety gating", "ESP32-A / Piezo ADC", "Automated ADC sampling test"],
    ["FR-03", "Sample high-fidelity acoustic waveforms at 16 kHz over I2S and compute real-time digital RMS amplitude", "ESP32-A / INMP441 I2S", "I2S buffer validation test"],
    ["FR-04", "Assemble versioned telemetry packets and transmit via 433 MHz LoRa at 700 ms intervals", "ESP32-A / SX1278", "LoRa packet sniffer log"],
    ["FR-05", "Demodulate LoRa frames on ESP32-B, validate CRC, and update 6-LED physical annunciator panel", "ESP32-B / LED Panel", "Hardware GPIO logic probe"],
    ["FR-06", "Enforce Node Mode Cascade logic: turning off ESP32-A must immediately force ESP32-B to OFF state", "Firmware / Bridge", "REST API cascade test"],
    ["FR-07", "Stream structured serial frames across 115,200 bps USB bridge into multi-threaded Python backend", "Python Backend", "Serial bridge integration test"],
    ["FR-08", "Synchronize live hardware telemetry with WebGL 3D Digital Twin visualizer at 60 FPS", "Three.js Frontend", "Selenium UI telemetry test"]
]

REQ_NFR_HEADERS = ["Req ID", "Non-Functional Requirement", "Target Metric", "Verification Status"]
REQ_NFR_ROWS = [
    ["NFR-01", "End-to-End Latency (Sensor trigger to 3D Digital Twin update)", "< 250 ms total pipeline latency", "Measured ~110–140 ms [PASS]"],
    ["NFR-02", "LoRa Wireless Telemetry Reliability in Forest Canopy", "0% packet loss over nominal bench range", "Measured 0% loss, SNR 10.1 dB [PASS]"],
    ["NFR-03", "Quiescent Power Efficiency of Field Sensing Node", "Support multi-day solar/battery deployment", "Calculated ~65 mA active [PASS]"],
    ["NFR-04", "Visual Rendering Frame Rate in Browser Digital Twin", "Maintain >= 50 FPS on standard desktop GPUs", "Measured 58–60 FPS [PASS]"],
    ["NFR-05", "False-Positive Rejection via Multi-Modal Fusion", "Suppress single-sensor anomalies (wind, insects)", "Verified via 3-sensor logic [PASS]"],
    ["NFR-06", "Microcontroller Electrical Fault Tolerance", "Zero GPIO latch-up from piezoelectric spikes", "Enforced via clamping circuit [PASS]"]
]

REQ_TRACE_HEADERS = ["Stakeholder Persona", "Operational Need", "Engineered System Feature", "Verification Evidence"]
REQ_TRACE_ROWS = [
    ["Forest Range Officer", "10–15 min advance predictive warning before boundary fence breach", "Three-layer spatial corridor hierarchy (Outer RF -> Middle Physical -> Inner Camera)", "Spatial simulation transition logs"],
    ["Field Ranger", "Simple, unmistakable physical alert indicators without needing cellular mobile signal", "ESP32-B dedicated 6-LED annunciator panel with multi-tone Web Audio siren", "Physical bench LED validation"],
    ["Marginal Farmer", "Zero false alarms and safe, non-lethal elephant deterrence", "Multi-modal cross-sensor validation (PIR + Piezo + Mic) before alarm activation", "Multi-modal fusion test suite"],
    ["Conservation Biologist", "Continuous non-invasive animal tracking and historical movement path logging", "Interactive 3D Digital Twin with dynamic trajectory vectors and trail rendering", "3D path visualization in Three.js"],
    ["Field Technician", "Robust electrical protection, modular firmware, and rapid terminal diagnostic inspection", "2 kΩ LED resistors, fail-closed piezo gate, and one-click 'opentwin' CLI launcher", "opentwin CLI & terminal test"]
]

print("Report Content Modules (Part 1: Ch 1-4) Loaded.")

