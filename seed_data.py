"""
AgroAid – Knowledge Base Seed Data
Populates the database with 5 crops, their symptoms, diseases, treatments, and rules.
Run once: python seed_data.py
"""
from database import get_db, init_db

def seed():
    init_db()
    conn = get_db()
    c = conn.cursor()

    # Clear existing data (in reverse FK order)
    c.executescript('''
        DELETE FROM rule_symptoms;
        DELETE FROM rules;
        DELETE FROM treatments;
        DELETE FROM diseases;
        DELETE FROM symptoms;
        DELETE FROM crops;
    ''')
    conn.commit()

    # ═══════════════════════════════════════════════════════════════════════════
    # 1. MAIZE
    # ═══════════════════════════════════════════════════════════════════════════
    c.execute("INSERT INTO crops (name, description, icon) VALUES (?,?,?)",
              ("Maize", "A staple cereal crop widely grown across sub-Saharan Africa.", "fa-wheat-awn"))
    maize_id = c.lastrowid

    # Symptoms
    syms = [
        ("Gray or tan lesions on leaves", "Rectangular lesions running parallel to leaf veins"),
        ("Lesions with dark borders", "Lesion edges appear dark or brown"),
        ("Premature drying of leaves", "Leaves dry out before the rest of the plant"),
        ("Stunted plant growth", "Plant is noticeably shorter than expected for its age"),
        ("Yellow streaks on leaves", "Bright yellow stripes running along the leaf"),
        ("Necrotic leaf patches", "Dead brown patches scattered across leaves"),
        ("Rotting at stem base", "Soft, discolored rot near the soil level"),
        ("Tunneling damage in stem", "Holes or tunnels visible when stem is split open"),
        ("Sawdust-like frass on stem", "Fine powdery waste produced by boring insects"),
        ("Broken or dead tassels", "Tassels snapped off or completely dead"),
    ]
    maize_sym_ids = {}
    for name, desc in syms:
        c.execute("INSERT INTO symptoms (crop_id, name, description) VALUES (?,?,?)", (maize_id, name, desc))
        maize_sym_ids[name] = c.lastrowid

    # Disease 1 – Gray Leaf Spot
    c.execute("INSERT INTO diseases (crop_id, name, description, severity) VALUES (?,?,?,?)",
              (maize_id, "Gray Leaf Spot", "Fungal disease caused by Cercospora zeae-maydis, causing rectangular gray lesions on maize leaves.", "High"))
    gls_id = c.lastrowid
    for txt, desc, pri in [
        ("Curative", "Apply fungicides containing azoxystrobin or propiconazole at early symptom onset.", 1),
        ("Cultural", "Practice crop rotation with non-host crops for at least one season.", 2),
        ("Cultural", "Remove and destroy infected plant debris after harvest.", 3),
        ("Preventive", "Plant resistant maize varieties when available in your region.", 4),
    ]:
        c.execute("INSERT INTO treatments (disease_id, treatment_type, description, priority) VALUES (?,?,?,?)", (gls_id, txt, desc, pri))

    # Rule for Gray Leaf Spot
    c.execute("INSERT INTO rules (disease_id, confidence_score) VALUES (?,?)", (gls_id, 0.95))
    rule_id = c.lastrowid
    for sym in ["Gray or tan lesions on leaves", "Lesions with dark borders", "Premature drying of leaves"]:
        c.execute("INSERT INTO rule_symptoms (rule_id, symptom_id) VALUES (?,?)", (rule_id, maize_sym_ids[sym]))

    # Alternative rule (partial match)
    c.execute("INSERT INTO rules (disease_id, confidence_score) VALUES (?,?)", (gls_id, 0.80))
    rule_id = c.lastrowid
    for sym in ["Gray or tan lesions on leaves", "Premature drying of leaves"]:
        c.execute("INSERT INTO rule_symptoms (rule_id, symptom_id) VALUES (?,?)", (rule_id, maize_sym_ids[sym]))

    # Disease 2 – Maize Lethal Necrosis
    c.execute("INSERT INTO diseases (crop_id, name, description, severity) VALUES (?,?,?,?)",
              (maize_id, "Maize Lethal Necrosis (MLN)", "Viral disease caused by the co-infection of Maize Chlorotic Mottle Virus and Wheat Streak Mosaic Virus, causing rapid plant death.", "Critical"))
    mln_id = c.lastrowid
    for txt, desc, pri in [
        ("Quarantine", "Destroy affected plants immediately and report to agricultural authorities.", 1),
        ("Chemical", "Control insect vectors (thrips, aphids) using recommended insecticides.", 2),
        ("Cultural", "Use certified disease-free seed from reputable suppliers.", 3),
        ("Preventive", "Plant MLN-tolerant varieties; avoid planting maize in areas with previous MLN outbreaks.", 4),
    ]:
        c.execute("INSERT INTO treatments (disease_id, treatment_type, description, priority) VALUES (?,?,?,?)", (mln_id, txt, desc, pri))

    c.execute("INSERT INTO rules (disease_id, confidence_score) VALUES (?,?)", (mln_id, 0.95))
    rule_id = c.lastrowid
    for sym in ["Stunted plant growth", "Yellow streaks on leaves", "Necrotic leaf patches"]:
        c.execute("INSERT INTO rule_symptoms (rule_id, symptom_id) VALUES (?,?)", (rule_id, maize_sym_ids[sym]))

    # Disease 3 – Stem Borer
    c.execute("INSERT INTO diseases (crop_id, name, description, severity) VALUES (?,?,?,?)",
              (maize_id, "Stem Borer (Busseola fusca)", "Insect pest larvae that bore into maize stalks causing 'dead heart' in young plants and yield loss.", "Moderate"))
    sb_id = c.lastrowid
    for txt, desc, pri in [
        ("Chemical", "Apply granular insecticides (e.g., carbofuran) into the whorl at early infestation.", 1),
        ("Biological", "Release Cotesia sesamiae parasitoids as biological control agents.", 2),
        ("Cultural", "Intercrop maize with Desmodium to repel stem borers (push-pull strategy).", 3),
        ("Preventive", "Plant push-pull border crops such as Napier grass to trap stem borers.", 4),
    ]:
        c.execute("INSERT INTO treatments (disease_id, treatment_type, description, priority) VALUES (?,?,?,?)", (sb_id, txt, desc, pri))

    c.execute("INSERT INTO rules (disease_id, confidence_score) VALUES (?,?)", (sb_id, 0.93))
    rule_id = c.lastrowid
    for sym in ["Tunneling damage in stem", "Sawdust-like frass on stem", "Broken or dead tassels"]:
        c.execute("INSERT INTO rule_symptoms (rule_id, symptom_id) VALUES (?,?)", (rule_id, maize_sym_ids[sym]))

    # Alternative rule
    c.execute("INSERT INTO rules (disease_id, confidence_score) VALUES (?,?)", (sb_id, 0.75))
    rule_id = c.lastrowid
    for sym in ["Tunneling damage in stem", "Rotting at stem base"]:
        c.execute("INSERT INTO rule_symptoms (rule_id, symptom_id) VALUES (?,?)", (rule_id, maize_sym_ids[sym]))

    # ═══════════════════════════════════════════════════════════════════════════
    # 2. TOMATO
    # ═══════════════════════════════════════════════════════════════════════════
    c.execute("INSERT INTO crops (name, description, icon) VALUES (?,?,?)",
              ("Tomato", "A widely grown vegetable crop highly susceptible to fungal and bacterial diseases.", "fa-circle-dot"))
    tomato_id = c.lastrowid

    syms_t = [
        ("Brown/yellow spots on lower leaves", "Circular spots with yellow halo on older leaves"),
        ("Dark concentric rings in spots", "Target-board pattern of rings within lesions"),
        ("Lesions expand rapidly with wet rot", "Spots enlarge quickly in humid conditions with water-soaked centers"),
        ("White mold on leaf underside", "White cottony growth on the underside of leaves"),
        ("Dark water-soaked lesions on fruit", "Large irregular dark patches on ripening fruit"),
        ("Brown streaks on stem", "Longitudinal brown streaking inside the stem when cut"),
        ("Yellowing of lower leaves", "Lower leaves turn yellow and drop"),
        ("Wilting despite adequate water", "Plant wilts even when soil moisture is sufficient"),
        ("Brown vascular tissue", "Inside stem appears brown/tan when cut cross-sectionally"),
        ("Stunted growth and leaf curl", "Young leaves curl inward and overall growth is reduced"),
    ]
    tomato_sym_ids = {}
    for name, desc in syms_t:
        c.execute("INSERT INTO symptoms (crop_id, name, description) VALUES (?,?,?)", (tomato_id, name, desc))
        tomato_sym_ids[name] = c.lastrowid

    # Disease 1 – Early Blight
    c.execute("INSERT INTO diseases (crop_id, name, description, severity) VALUES (?,?,?,?)",
              (tomato_id, "Early Blight", "Fungal disease (Alternaria solani) producing target-like brown spots on tomato leaves, stems, and fruit.", "Moderate"))
    eb_id = c.lastrowid
    for txt, desc, pri in [
        ("Chemical", "Apply copper-based fungicides or mancozeb every 7–10 days during wet weather.", 1),
        ("Cultural", "Remove infected lower leaves immediately to reduce spore spread.", 2),
        ("Cultural", "Avoid overhead irrigation; water at the base of the plant.", 3),
        ("Preventive", "Apply mulch to prevent soil splash and future spore dispersal.", 4),
    ]:
        c.execute("INSERT INTO treatments (disease_id, treatment_type, description, priority) VALUES (?,?,?,?)", (eb_id, txt, desc, pri))

    c.execute("INSERT INTO rules (disease_id, confidence_score) VALUES (?,?)", (eb_id, 0.95))
    rule_id = c.lastrowid
    for sym in ["Brown/yellow spots on lower leaves", "Dark concentric rings in spots"]:
        c.execute("INSERT INTO rule_symptoms (rule_id, symptom_id) VALUES (?,?)", (rule_id, tomato_sym_ids[sym]))

    # Disease 2 – Late Blight
    c.execute("INSERT INTO diseases (crop_id, name, description, severity) VALUES (?,?,?,?)",
              (tomato_id, "Late Blight", "Oomycete disease (Phytophthora infestans) causing rapid destruction of foliage, stems, and fruit under cool, wet conditions.", "Critical"))
    lb_id = c.lastrowid
    for txt, desc, pri in [
        ("Chemical", "Spray systemic fungicides (e.g., metalaxyl + mancozeb) at first sign of symptoms.", 1),
        ("Chemical", "Remove and destroy affected plant parts at least 100 m from the field.", 2),
        ("Preventive", "Plant certified blight-resistant tomato varieties.", 3),
        ("Cultural", "Ensure good air circulation by proper plant spacing and staking.", 4),
    ]:
        c.execute("INSERT INTO treatments (disease_id, treatment_type, description, priority) VALUES (?,?,?,?)", (lb_id, txt, desc, pri))

    c.execute("INSERT INTO rules (disease_id, confidence_score) VALUES (?,?)", (lb_id, 0.95))
    rule_id = c.lastrowid
    for sym in ["Lesions expand rapidly with wet rot", "White mold on leaf underside", "Dark water-soaked lesions on fruit"]:
        c.execute("INSERT INTO rule_symptoms (rule_id, symptom_id) VALUES (?,?)", (rule_id, tomato_sym_ids[sym]))

    # Disease 3 – Fusarium Wilt
    c.execute("INSERT INTO diseases (crop_id, name, description, severity) VALUES (?,?,?,?)",
              (tomato_id, "Fusarium Wilt", "Soil-borne fungal disease (Fusarium oxysporum f. sp. lycopersici) causing vascular wilting and plant death.", "High"))
    fw_id = c.lastrowid
    for txt, desc, pri in [
        ("Cultural", "Remove and destroy wilted plants including roots; do not compost.", 1),
        ("Chemical", "Drench soil with fungicide solution (e.g., thiophanate-methyl) around healthy plants.", 2),
        ("Preventive", "Use Fusarium-resistant (F1 or F2 rated) tomato varieties.", 3),
        ("Cultural", "Practice 4-year crop rotation; avoid planting solanaceous crops in infested soil.", 4),
    ]:
        c.execute("INSERT INTO treatments (disease_id, treatment_type, description, priority) VALUES (?,?,?,?)", (fw_id, txt, desc, pri))

    c.execute("INSERT INTO rules (disease_id, confidence_score) VALUES (?,?)", (fw_id, 0.92))
    rule_id = c.lastrowid
    for sym in ["Wilting despite adequate water", "Brown vascular tissue", "Yellowing of lower leaves"]:
        c.execute("INSERT INTO rule_symptoms (rule_id, symptom_id) VALUES (?,?)", (rule_id, tomato_sym_ids[sym]))

    # ═══════════════════════════════════════════════════════════════════════════
    # 3. BEAN
    # ═══════════════════════════════════════════════════════════════════════════
    c.execute("INSERT INTO crops (name, description, icon) VALUES (?,?,?)",
              ("Bean", "Common bean is a major protein source for smallholder farming households in East Africa.", "fa-leaf"))
    bean_id = c.lastrowid

    syms_b = [
        ("Rust-colored powdery pustules on leaves", "Orange-brown powdery spots on leaf undersides"),
        ("Leaves turn yellow around pustules", "Yellow halo surrounds rusty pustules"),
        ("Premature leaf drop", "Leaves fall off before maturity"),
        ("Angular water-soaked lesions", "Irregular, wet-looking spots bounded by leaf veins"),
        ("Lesions turn gray with yellow border", "Center of spots dries gray, surrounded by yellow"),
        ("Bacterial exudate on lesions", "Sticky bacterial ooze visible on lesion surface in humid conditions"),
        ("Reddish-brown rot at root", "Root surface shows reddish-brown discoloration and decay"),
        ("Stem turns brown and shrivels", "Lower stem darkens and collapses at soil level"),
        ("Poor germination or seedling death", "Seeds fail to germinate or seedlings collapse shortly after emergence"),
        ("White fungal threads at stem base", "White mycelium visible at the base of the stem near soil"),
    ]
    bean_sym_ids = {}
    for name, desc in syms_b:
        c.execute("INSERT INTO symptoms (crop_id, name, description) VALUES (?,?,?)", (bean_id, name, desc))
        bean_sym_ids[name] = c.lastrowid

    # Disease 1 – Bean Rust
    c.execute("INSERT INTO diseases (crop_id, name, description, severity) VALUES (?,?,?,?)",
              (bean_id, "Bean Rust", "Fungal disease (Uromyces appendiculatus) causing rust-colored pustules on leaves, reducing photosynthesis.", "Moderate"))
    br_id = c.lastrowid
    for txt, desc, pri in [
        ("Chemical", "Apply sulfur-based or triazole fungicides at the first sign of rust pustules.", 1),
        ("Cultural", "Plant resistant bean varieties; avoid dense planting that limits air circulation.", 2),
        ("Cultural", "Remove and burn infected plant debris after harvest.", 3),
        ("Preventive", "Avoid overhead irrigation which promotes leaf wetness and rust spread.", 4),
    ]:
        c.execute("INSERT INTO treatments (disease_id, treatment_type, description, priority) VALUES (?,?,?,?)", (br_id, txt, desc, pri))

    c.execute("INSERT INTO rules (disease_id, confidence_score) VALUES (?,?)", (br_id, 0.94))
    rule_id = c.lastrowid
    for sym in ["Rust-colored powdery pustules on leaves", "Leaves turn yellow around pustules", "Premature leaf drop"]:
        c.execute("INSERT INTO rule_symptoms (rule_id, symptom_id) VALUES (?,?)", (rule_id, bean_sym_ids[sym]))

    # Disease 2 – Angular Leaf Spot
    c.execute("INSERT INTO diseases (crop_id, name, description, severity) VALUES (?,?,?,?)",
              (bean_id, "Angular Leaf Spot", "Fungal disease (Pseudocercospora griseola) producing angular gray lesions on leaves, pods, and stems.", "Moderate"))
    als_id = c.lastrowid
    for txt, desc, pri in [
        ("Chemical", "Apply mancozeb or chlorothalonil fungicides preventively during humid weather.", 1),
        ("Cultural", "Use certified disease-free seed; avoid saving seed from infected plants.", 2),
        ("Cultural", "Rotate crops with cereals or root vegetables for at least 2 seasons.", 3),
        ("Preventive", "Select angular leaf spot resistant bean varieties.", 4),
    ]:
        c.execute("INSERT INTO treatments (disease_id, treatment_type, description, priority) VALUES (?,?,?,?)", (als_id, txt, desc, pri))

    c.execute("INSERT INTO rules (disease_id, confidence_score) VALUES (?,?)", (als_id, 0.92))
    rule_id = c.lastrowid
    for sym in ["Angular water-soaked lesions", "Lesions turn gray with yellow border"]:
        c.execute("INSERT INTO rule_symptoms (rule_id, symptom_id) VALUES (?,?)", (rule_id, bean_sym_ids[sym]))

    # Disease 3 – Root Rot
    c.execute("INSERT INTO diseases (crop_id, name, description, severity) VALUES (?,?,?,?)",
              (bean_id, "Root Rot", "Complex of soil-borne fungi (Fusarium, Rhizoctonia, Pythium) causing root decay and plant collapse, especially in poorly drained soils.", "High"))
    rr_id = c.lastrowid
    for txt, desc, pri in [
        ("Cultural", "Improve soil drainage; avoid waterlogging through proper field management.", 1),
        ("Chemical", "Treat seeds with thiram or mancozeb seed dressing before planting.", 2),
        ("Cultural", "Rotate with non-legume crops for 2–3 seasons.", 3),
        ("Preventive", "Select well-draining planting sites; add organic matter to improve soil structure.", 4),
    ]:
        c.execute("INSERT INTO treatments (disease_id, treatment_type, description, priority) VALUES (?,?,?,?)", (rr_id, txt, desc, pri))

    c.execute("INSERT INTO rules (disease_id, confidence_score) VALUES (?,?)", (rr_id, 0.90))
    rule_id = c.lastrowid
    for sym in ["Reddish-brown rot at root", "Stem turns brown and shrivels", "Poor germination or seedling death"]:
        c.execute("INSERT INTO rule_symptoms (rule_id, symptom_id) VALUES (?,?)", (rule_id, bean_sym_ids[sym]))

    # ═══════════════════════════════════════════════════════════════════════════
    # 4. POTATO
    # ═══════════════════════════════════════════════════════════════════════════
    c.execute("INSERT INTO crops (name, description, icon) VALUES (?,?,?)",
              ("Potato", "An important food security crop grown in highland areas, susceptible to several destructive diseases.", "fa-circle"))
    potato_id = c.lastrowid

    syms_p = [
        ("Dark water-soaked lesions on leaves", "Irregular, dark patches that appear water-soaked"),
        ("White cottony growth on leaf underside", "White mold-like growth visible under leaves in humid conditions"),
        ("Brown rot of tubers", "Internal flesh of tuber shows brown, rotted areas"),
        ("Slime oozes from cut tuber", "When tuber is cut, bacterial slime oozes from vascular ring"),
        ("Wilting during cooler parts of day", "Plant wilts even in cool mornings or evenings"),
        ("Black sclerotia on tuber skin", "Small black bodies (sclerotia) adhering to the tuber skin"),
        ("Stem canker at soil level", "Brown canker lesion at the base of the stem near soil"),
        ("Aerial tubers on stem", "Small tubers forming on the stem above the soil surface"),
        ("Leaf roll and yellowing", "Leaves roll upward and turn yellow from tip inward"),
        ("Stunted and spindly shoots", "Shoots are thin, weak, and shorter than normal"),
    ]
    potato_sym_ids = {}
    for name, desc in syms_p:
        c.execute("INSERT INTO symptoms (crop_id, name, description) VALUES (?,?,?)", (potato_id, name, desc))
        potato_sym_ids[name] = c.lastrowid

    # Disease 1 – Late Blight
    c.execute("INSERT INTO diseases (crop_id, name, description, severity) VALUES (?,?,?,?)",
              (potato_id, "Late Blight", "Devastating oomycete disease (Phytophthora infestans) capable of destroying entire fields rapidly in cool, wet conditions.", "Critical"))
    plb_id = c.lastrowid
    for txt, desc, pri in [
        ("Chemical", "Apply metalaxyl-based fungicides immediately at first sign; repeat every 7 days.", 1),
        ("Chemical", "Alternate with protectant fungicides (mancozeb, chlorothalonil) to prevent resistance.", 2),
        ("Cultural", "Hill up potato plants to protect developing tubers from infection.", 3),
        ("Preventive", "Use certified blight-resistant potato varieties and病 disease-free seed tubers.", 4),
    ]:
        c.execute("INSERT INTO treatments (disease_id, treatment_type, description, priority) VALUES (?,?,?,?)", (plb_id, txt, desc, pri))

    c.execute("INSERT INTO rules (disease_id, confidence_score) VALUES (?,?)", (plb_id, 0.96))
    rule_id = c.lastrowid
    for sym in ["Dark water-soaked lesions on leaves", "White cottony growth on leaf underside", "Brown rot of tubers"]:
        c.execute("INSERT INTO rule_symptoms (rule_id, symptom_id) VALUES (?,?)", (rule_id, potato_sym_ids[sym]))

    # Disease 2 – Bacterial Wilt
    c.execute("INSERT INTO diseases (crop_id, name, description, severity) VALUES (?,?,?,?)",
              (potato_id, "Bacterial Wilt", "Soil-borne disease (Ralstonia solanacearum) causing rapid wilting and internal browning of potato tubers.", "High"))
    pbw_id = c.lastrowid
    for txt, desc, pri in [
        ("Quarantine", "Uproot and destroy infected plants; do not leave debris in the field.", 1),
        ("Cultural", "Avoid planting in fields with a history of bacterial wilt; practice 3–4 year rotation.", 2),
        ("Cultural", "Use certified disease-free seed tubers from reliable suppliers.", 3),
        ("Preventive", "Avoid wounding tubers during planting; disinfect cutting tools with bleach between cuts.", 4),
    ]:
        c.execute("INSERT INTO treatments (disease_id, treatment_type, description, priority) VALUES (?,?,?,?)", (pbw_id, txt, desc, pri))

    c.execute("INSERT INTO rules (disease_id, confidence_score) VALUES (?,?)", (pbw_id, 0.93))
    rule_id = c.lastrowid
    for sym in ["Slime oozes from cut tuber", "Wilting during cooler parts of day"]:
        c.execute("INSERT INTO rule_symptoms (rule_id, symptom_id) VALUES (?,?)", (rule_id, potato_sym_ids[sym]))

    # Disease 3 – Black Scurf (Rhizoctonia)
    c.execute("INSERT INTO diseases (crop_id, name, description, severity) VALUES (?,?,?,?)",
              (potato_id, "Black Scurf (Rhizoctonia)", "Fungal disease (Rhizoctonia solani) causing black crusty patches on tubers and stem cankers that reduce plant vigor.", "Moderate"))
    pbs_id = c.lastrowid
    for txt, desc, pri in [
        ("Chemical", "Treat seed tubers with fungicide (e.g., pencycuron or fludioxonil) before planting.", 1),
        ("Cultural", "Plant into warm soil (above 10°C) to encourage rapid emergence and reduce infection window.", 2),
        ("Cultural", "Practice crop rotation; avoid planting potato in the same field consecutively.", 3),
        ("Preventive", "Use certified scurf-free seed tubers; avoid mechanical damage during harvest.", 4),
    ]:
        c.execute("INSERT INTO treatments (disease_id, treatment_type, description, priority) VALUES (?,?,?,?)", (pbs_id, txt, desc, pri))

    c.execute("INSERT INTO rules (disease_id, confidence_score) VALUES (?,?)", (pbs_id, 0.90))
    rule_id = c.lastrowid
    for sym in ["Black sclerotia on tuber skin", "Stem canker at soil level", "Aerial tubers on stem"]:
        c.execute("INSERT INTO rule_symptoms (rule_id, symptom_id) VALUES (?,?)", (rule_id, potato_sym_ids[sym]))

    # ═══════════════════════════════════════════════════════════════════════════
    # 5. BANANA
    # ═══════════════════════════════════════════════════════════════════════════
    c.execute("INSERT INTO crops (name, description, icon) VALUES (?,?,?)",
              ("Banana", "A major cash and food crop in tropical Africa, threatened by destructive fungal and viral diseases.", "fa-angles-up"))
    banana_id = c.lastrowid

    syms_bn = [
        ("Yellowing and wilting of leaves", "Leaves turn yellow, starting from older outer leaves"),
        ("Internal brown discoloration of pseudostem", "Cutting the pseudostem reveals brown/red discoloration in vascular tissue"),
        ("Fruit fails to ripen normally", "Bananas turn prematurely yellow or fail to develop properly"),
        ("Black streaks on leaves", "Dark elongated streaks running along banana leaves"),
        ("Leaf tissue dies from margins inward", "Leaf edges turn brown and die, progressing inward"),
        ("Premature shriveling of fruit", "Fruit withers and shrivels before full development"),
        ("Stunted sucker growth", "New side shoots (suckers) are short and weak"),
        ("Narrow upright leaves", "New leaves are narrow, erect ('bunchy' appearance)"),
        ("Leaf mosaic pattern", "Leaves show a mosaic or mottled pattern of light and dark green"),
        ("Bunch failure or no bunch at all", "Plant fails to produce a bunch or bunch is severely undersized"),
    ]
    banana_sym_ids = {}
    for name, desc in syms_bn:
        c.execute("INSERT INTO symptoms (crop_id, name, description) VALUES (?,?,?)", (banana_id, name, desc))
        banana_sym_ids[name] = c.lastrowid

    # Disease 1 – Fusarium Wilt (Panama Disease)
    c.execute("INSERT INTO diseases (crop_id, name, description, severity) VALUES (?,?,?,?)",
              (banana_id, "Fusarium Wilt (Panama Disease)", "Devastating soil-borne fungal disease (Fusarium oxysporum f. sp. cubense) that colonizes banana vascular tissue causing plant death.", "Critical"))
    bfw_id = c.lastrowid
    for txt, desc, pri in [
        ("Quarantine", "Immediately remove and destroy infected plants; report outbreak to agricultural authorities.", 1),
        ("Cultural", "Use tissue culture plantlets from certified disease-free sources.", 2),
        ("Cultural", "Do not move soil or plant material from infected areas to unaffected fields.", 3),
        ("Preventive", "Plant TR4-resistant banana varieties (e.g., Cavendish alternatives being developed).", 4),
    ]:
        c.execute("INSERT INTO treatments (disease_id, treatment_type, description, priority) VALUES (?,?,?,?)", (bfw_id, txt, desc, pri))

    c.execute("INSERT INTO rules (disease_id, confidence_score) VALUES (?,?)", (bfw_id, 0.95))
    rule_id = c.lastrowid
    for sym in ["Yellowing and wilting of leaves", "Internal brown discoloration of pseudostem", "Fruit fails to ripen normally"]:
        c.execute("INSERT INTO rule_symptoms (rule_id, symptom_id) VALUES (?,?)", (rule_id, banana_sym_ids[sym]))

    # Disease 2 – Black Sigatoka
    c.execute("INSERT INTO diseases (crop_id, name, description, severity) VALUES (?,?,?,?)",
              (banana_id, "Black Sigatoka", "Fungal leaf disease (Mycosphaerella fijiensis) causing extensive leaf death, reducing photosynthesis and fruit production by up to 50%.", "High"))
    bbs_id = c.lastrowid
    for txt, desc, pri in [
        ("Chemical", "Apply systemic fungicides (triazoles, strobilurins) on a strict spray program.", 1),
        ("Cultural", "Remove and dispose of infected leaves to reduce spore load.", 2),
        ("Cultural", "Ensure good drainage and air movement to reduce leaf wetness period.", 3),
        ("Preventive", "Plant Sigatoka-resistant cultivars where available.", 4),
    ]:
        c.execute("INSERT INTO treatments (disease_id, treatment_type, description, priority) VALUES (?,?,?,?)", (bbs_id, txt, desc, pri))

    c.execute("INSERT INTO rules (disease_id, confidence_score) VALUES (?,?)", (bbs_id, 0.93))
    rule_id = c.lastrowid
    for sym in ["Black streaks on leaves", "Leaf tissue dies from margins inward", "Premature shriveling of fruit"]:
        c.execute("INSERT INTO rule_symptoms (rule_id, symptom_id) VALUES (?,?)", (rule_id, banana_sym_ids[sym]))

    # Disease 3 – Banana Bunchy Top Virus (BBTV)
    c.execute("INSERT INTO diseases (crop_id, name, description, severity) VALUES (?,?,?,?)",
              (banana_id, "Banana Bunchy Top Virus (BBTV)", "Viral disease spread by banana aphids causing stunted growth, narrow upright leaves and failure to produce fruit.", "Critical"))
    bbtv_id = c.lastrowid
    for txt, desc, pri in [
        ("Quarantine", "Immediately destroy infected plants (dig up and bury or burn); never compost.", 1),
        ("Chemical", "Control banana aphid (Pentalonia nigronervosa) vectors with systemic insecticides.", 2),
        ("Cultural", "Use BBTV-indexed tissue culture planting material only.", 3),
        ("Preventive", "Inspect new planting material before introducing to disease-free fields.", 4),
    ]:
        c.execute("INSERT INTO treatments (disease_id, treatment_type, description, priority) VALUES (?,?,?,?)", (bbtv_id, txt, desc, pri))

    c.execute("INSERT INTO rules (disease_id, confidence_score) VALUES (?,?)", (bbtv_id, 0.94))
    rule_id = c.lastrowid
    for sym in ["Narrow upright leaves", "Stunted sucker growth", "Bunch failure or no bunch at all", "Leaf mosaic pattern"]:
        c.execute("INSERT INTO rule_symptoms (rule_id, symptom_id) VALUES (?,?)", (rule_id, banana_sym_ids[sym]))

    conn.commit()
    conn.close()
    print("✅ Database seeded successfully with 5 crops, 15 diseases, and associated rules.")

if __name__ == '__main__':
    seed()
