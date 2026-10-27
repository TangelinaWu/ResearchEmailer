"""Generate outreach drafts for NYU faculty outside CS/CDS/CBI.

Covers: Tandon ECE, Tandon BME, Tandon MechE/Aerospace, NYU Grossman School
of Medicine (computational), Center for Neural Science (CNS), and Psychology.
All contacts are NYC metropolitan area. Emails scraped from faculty pages Aug 2026.
"""
import os
import re

from contacts_store import load_contacts, save_contacts, upsert
from draft_generator import first_name, safe_filename, position_ask_for_region

DRAFTS_DIR = os.path.join(os.path.dirname(__file__), "..", "drafts")

SENDER = {
    "linkedin": "https://linkedin.com/in/angelina-wu-nyu",
    "github": "https://github.com/TangelinaWu",
}

BODY_TEMPLATE = """Dear {first_name},

My name is Angelina Wu. I'm an undergraduate studying Computer Science & Economics at NYU (Class of 2028). {opening}

I'm currently a software engineering intern at Lea Technologies, where I work on document taxonomy, data validation, and parsing pipelines. I also have hands-on experience scraping, processing, and cleaning data from independent projects, and I'm especially interested in working with ML data. I primarily work in Python, using pandas, regex, and pypdf for parsing and cleaning, and SQL for data storage and querying.

{position_ask}

Thank you for your time and for the work you're doing. I really enjoyed learning about your research. I've attached my resume for your reference.

Best,
Angelina Wu
aw5287@nyu.edu | {linkedin} | {github}
"""

PROFESSORS = [
    # ── Tandon ECE ─────────────────────────────────────────────────────────────
    dict(
        name="Anna Choromanska",
        email="ac5455@nyu.edu",
        email_status="ready",
        profile_url="https://engineering.nyu.edu/faculty/anna-choromanska",
        affiliation="NYU (Tandon ECE)",
        focus_label="Deep Learning Optimization & Continual Learning (Tandon ECE)",
        focus="Studies how neural networks learn and optimize, focusing on landscape-driven "
              "optimization, continual learning, and distributed training; directs the Learning "
              "Systems Laboratory.",
        opening="I read your work on Wake-Sleep Energy Based Models for continual learning and "
                "your GRAWA gradient-based weighted averaging method for distributed training. "
                "The challenge of designing optimization algorithms that account for the actual "
                "geometry of deep learning loss landscapes—rather than treating them as convex—"
                "is fundamental to making ML training both faster and more reliable, and given "
                "my background in data pipelines and ML model evaluation, I'd love to contribute "
                "to your lab's research.",
    ),
    dict(
        name="Sai Qian Zhang",
        email="sai.zhang@nyu.edu",
        email_status="ready",
        profile_url="https://www.saiqianzhang.com/",
        affiliation="NYU (Tandon ECE)",
        focus_label="Efficient AI & Hardware-Software Co-Design for AR/VR (Tandon ECE)",
        focus="Works on algorithm and hardware co-design for efficient deep neural network "
              "implementation, with applications to AR/VR computing and neural network accelerator "
              "design; previously Senior Research Scientist at Meta Reality Labs.",
        opening="I read about your work on algorithm and hardware co-design for efficient deep "
                "neural networks—particularly designing inference pipelines where the algorithm "
                "is shaped around the hardware constraints rather than layered on top. As AR/VR "
                "applications push ML inference onto power-constrained devices, that co-design "
                "approach is exactly the right framing, and given my interest in ML systems and "
                "data pipelines, I'd love to contribute to your lab's work.",
    ),
    dict(
        name="Yao Wang",
        email="yw523@nyu.edu",
        email_status="ready",
        profile_url="https://engineering.nyu.edu/faculty/yao-wang",
        affiliation="NYU (Tandon ECE/BME)",
        focus_label="Video Processing, Medical Imaging & Brain-Speech Decoding (Tandon ECE)",
        focus="Studies image and video processing, video compression, medical imaging, and "
              "ML for health, including reconstructing speech from brain activity signals for "
              "communication assistance.",
        opening="I read about your lab's work reconstructing speech from neural signals—building "
                "ML pipelines that decode intended speech from brain activity to help individuals "
                "with communication disabilities. The challenge of mapping from high-dimensional, "
                "noisy neural recordings to structured language output is a hard data alignment "
                "problem, and given my experience in data pipelines and parsing, I'd love to "
                "contribute to that research.",
    ),
    # ── Tandon BME ─────────────────────────────────────────────────────────────
    dict(
        name="Rose Faghih",
        email="rtf3364@nyu.edu",
        email_status="ready",
        profile_url="https://engineering.nyu.edu/faculty/rose-faghih",
        affiliation="NYU (Tandon BME)",
        focus_label="Biomedical Signal Processing, Wearables & Cognitive Arousal (Tandon BME)",
        focus="Develops computational methods for biomedical signal processing and control, "
              "using wearables to track cognitive arousal, stress, and hormonal dynamics through "
              "physiological signals like skin conductance and eye tracking.",
        opening="I read your PNAS Nexus paper decoding interoceptive awareness through eye "
                "tracking—developing methods to infer how well people perceive their own bodily "
                "signals from observable gaze data. Building inference pipelines that read "
                "internal physiological states from non-invasive external measurements is a "
                "compelling inverse problem, and given my background in data processing and "
                "signal analysis, I'd love to contribute to your Computational Medicine Lab's "
                "work.",
    ),
    dict(
        name="Hao Su",
        email="hs5894@nyu.edu",
        email_status="ready",
        profile_url="https://engineering.nyu.edu/faculty/hao-su",
        affiliation="NYU (Tandon BME)",
        focus_label="Soft Robotics, RL for Exoskeletons & Assistive Devices (Tandon BME)",
        focus="Develops AI-powered exoskeletons and assistive devices using deep reinforcement "
              "learning, with work on sim-to-real transfer for wearable robots that reduce "
              "metabolic cost during walking, running, and stair climbing.",
        opening="I read your Nature study showing that exoskeletons trained with deep "
                "reinforcement learning in simulation achieved 24.3% less energy consumption "
                "during walking when transferred to real hardware. The sim-to-real gap for "
                "physical assistive devices—where failures affect people directly—makes that "
                "result especially significant, and given my interest in ML training pipelines "
                "and data collection, I'd love to contribute to your BIRO Lab's work.",
    ),
    dict(
        name="John-Ross Rizzo",
        email="JohnRoss.Rizzo@nyulangone.org",
        email_status="ready",
        profile_url="https://engineering.nyu.edu/faculty/john-ross-rizzo",
        affiliation="NYU (Tandon BME / Langone)",
        focus_label="Assistive Tech, Computer Vision & Rehabilitation (Tandon BME)",
        focus="Develops assistive technologies for people with blindness, stroke, and acquired "
              "brain injuries, combining miniaturized sensors, computer vision, and AI to enhance "
              "navigation and motor rehabilitation.",
        opening="I read about your Commute Booster app—using optical character recognition to "
                "help visually impaired users navigate NYC subway stations with 97% sign "
                "identification accuracy. Building computer vision systems that are robust enough "
                "to be genuinely useful in the unpredictable real-world conditions of a subway "
                "station, rather than just in controlled benchmarks, is exactly the kind of "
                "applied ML work I'd love to contribute to.",
    ),
    # ── Tandon MechE / Aerospace ────────────────────────────────────────────────
    dict(
        name="Ludovic Righetti",
        email="ludovic.righetti@nyu.edu",
        email_status="ready",
        profile_url="https://engineering.nyu.edu/faculty/ludovic-righetti",
        affiliation="NYU (Tandon MechE/ECE)",
        focus_label="Legged Locomotion, Manipulation & Optimal Control (Tandon MechE)",
        focus="Studies planning and control of movements for autonomous robots with emphasis on "
              "legged locomotion and manipulation, combining optimal control, reinforcement "
              "learning, and societal implications of robotics.",
        opening="I read about your IROS 2023 Best Paper finalist work on Monte Carlo Tree Search "
                "for robot manipulation planning—using MCTS to generate sequences of manipulation "
                "actions for complex tasks rather than relying on hand-engineered controllers. "
                "Applying principled search algorithms to manipulation planning, where the "
                "combinatorial space is huge and physics constraints are hard, is a compelling "
                "challenge, and I'd love to contribute to your Machines in Motion Lab's work.",
    ),
    dict(
        name="Chen Feng",
        email="cfeng@nyu.edu",
        email_status="ready",
        profile_url="https://engineering.nyu.edu/faculty/chen-feng",
        affiliation="NYU (Tandon MechE)",
        focus_label="Robot Perception, Computer Vision & AI for Construction (Tandon MechE)",
        focus="Develops AI systems for robot perception and learning in construction, "
              "manufacturing, and transportation; directs the AI4CE Lab; recent work on "
              "traffic safety analysis and modular construction automation.",
        opening="I read about your SeeUnsafe system—combining language reasoning and visual "
                "intelligence to automatically identify collisions and near-misses in existing "
                "traffic video, which won NYC's Vision Zero Research Award (2025). Building AI "
                "systems that can analyze large archives of unstructured real-world video for "
                "safety signals is exactly the kind of data pipeline and vision problem I'd love "
                "to contribute to, given my background in data processing and ML.",
    ),
    dict(
        name="Maurizio Porfiri",
        email="mporfiri@nyu.edu",
        email_status="ready",
        profile_url="https://engineering.nyu.edu/faculty/maurizio-porfiri",
        affiliation="NYU (Tandon MechE)",
        focus_label="Complex Systems, Network Science & Urban Data (Tandon MechE)",
        focus="Studies collective behavior, complex systems, and network science, with recent "
              "work on urban data center distribution, human migration modeling, and "
              "mechanical stability through behavioral switching.",
        opening="I read your 2026 Nature Cities paper revealing that 97.5% of data centers are "
                "sited inside metropolitan statistical areas, with electricity capacity and "
                "proximity to closed coal plants as key predictors. Building large-scale data "
                "pipelines to map infrastructure distribution and identify siting drivers across "
                "thousands of locations is exactly the kind of data-driven urban science I'd love "
                "to contribute to, given my background in data collection and processing.",
    ),
    # ── NYU Grossman School of Medicine ────────────────────────────────────────
    dict(
        name="Nadav Brandes",
        email="Nadav.Brandes@nyulangone.org",
        email_status="ready",
        profile_url="https://med.nyu.edu/faculty/nadav-brandes",
        affiliation="NYU (Grossman School of Medicine)",
        focus_label="Protein Language Models & Genomic AI (NYU Med)",
        focus="Develops large language models for protein and DNA sequences to predict disease "
              "variant effects and optimize therapeutic genomic sequences; built ProteinBERT "
              "and published genome-wide disease variant prediction in Nature Genetics.",
        opening="I read your Nature Genetics paper on genome-wide prediction of disease variant "
                "effects using a deep protein language model—showing that LLM-style pretraining "
                "on protein sequences transfers remarkably well to predicting the functional "
                "impact of mutations. Applying the same pretraining-and-fine-tuning paradigm "
                "that transformed NLP to biological sequences is one of the most exciting "
                "directions in computational biology, and given my background in ML data "
                "pipelines, I'd love to contribute to your lab's work.",
    ),
    dict(
        name="Souptik Barua",
        email="Souptik.Barua@nyulangone.org",
        email_status="ready",
        profile_url="https://med.nyu.edu/faculty/souptik-barua",
        affiliation="NYU (Grossman School of Medicine)",
        focus_label="Digital Precision Medicine, Wearables & ML for Health (NYU Med)",
        focus="Develops data-driven biomarkers for chronic conditions by combining wearables, "
              "biosensors, and machine learning; current work includes AI for early detection "
              "of cardiometabolic complications in pregnancy.",
        opening="I read about your Digi-Moms project—using wearables and AI to detect early "
                "signs of cardiometabolic complications during pregnancy, funded by the American "
                "Heart Association. Building ML pipelines that extract clinically meaningful "
                "signals from continuous wearable sensor streams is a hard data quality and "
                "feature engineering problem, and given my background in data pipelines and "
                "validation, I'd love to contribute to your digital precision medicine work.",
    ),
    dict(
        name="Zhe Chen",
        email="Zhe.Chen@nyulangone.org",
        email_status="ready",
        profile_url="https://med.nyu.edu/faculty/zhe-s-chen",
        affiliation="NYU (Grossman School of Medicine)",
        focus_label="Computational Neuroscience, NeuroAI & Brain-Machine Interfaces (NYU Med)",
        focus="Combines computational and ML methods with neural recording experiments to study "
              "hippocampal-cortical circuits, working memory, and brain-machine interfaces for "
              "pain and memory treatment.",
        opening="I read your Nature 2026 paper on subspace communication in the hippocampal-"
                "retrosplenial axis—showing that these two brain regions coordinate using "
                "low-dimensional subspaces that preserve task-relevant information across the "
                "connection. Applying dimensionality reduction and subspace analysis to large-"
                "scale neural recordings to find the structure in high-dimensional activity "
                "is exactly the kind of ML-meets-neuroscience work I'd love to contribute to.",
    ),
    dict(
        name="David Fenyö",
        email="David.Fenyo@nyulangone.org",
        email_status="ready",
        profile_url="https://med.nyu.edu/faculty/david-fenyo",
        affiliation="NYU (Grossman School of Medicine)",
        focus_label="Computational Proteomics & Cancer Genomics (NYU Med)",
        focus="Develops computational and statistical methods for proteomics data analysis, "
              "including protein identification via mass spectrometry, cancer progression "
              "mapping, and ML for clinical prediction; directs the Biomedical Informatics "
              "program.",
        opening="I read about your work applying machine learning to clinical prediction in "
                "proteomics—including ML models for glaucoma treatment outcomes and cancer "
                "progression mapping in breast and prostate tissues. Building computational "
                "pipelines that connect high-dimensional mass spectrometry data to clinical "
                "outcomes is a hard feature engineering and validation problem, and given my "
                "background in data parsing and processing pipelines, I'd love to contribute "
                "to your lab's work.",
    ),
    # ── NYU Center for Neural Science (CNS) ────────────────────────────────────
    dict(
        name="David Heeger",
        email="david.heeger@nyu.edu",
        email_status="ready",
        profile_url="https://www.cns.nyu.edu/heegerlab/",
        affiliation="NYU (Center for Neural Science)",
        focus_label="Computational Neuroscience & fMRI Methods (CNS)",
        focus="Develops computational models of visual and auditory perception, attention, and "
              "neural dynamics, using fMRI and computational neuroimaging to test mechanistic "
              "hypotheses about cortical processing.",
        opening="I've been reading about your Normalization Model of neural computation and your "
                "computational neuroimaging work linking fMRI BOLD signals to underlying neural "
                "activity. Building quantitative models that connect brain imaging measurements "
                "to circuit-level computations—rather than treating fMRI as a black-box correlate—"
                "is a rigorous approach that I find really compelling, and given my background "
                "in data pipelines and ML, I'd love to contribute to your lab's research.",
    ),
    dict(
        name="Dora Angelaki",
        email="dora.angelaki@nyu.edu",
        email_status="ready",
        profile_url="https://engineering.nyu.edu/faculty/dora-angelaki",
        affiliation="NYU (Center for Neural Science / Tandon)",
        focus_label="Multisensory Integration, Navigation & Decision Circuits (CNS)",
        focus="Studies how multisensory information is integrated across subcortical and cortical "
              "areas to support spatial navigation, decision-making, and episodic memory, using "
              "naturalistic foraging tasks and large-scale electrophysiology.",
        opening="I've been reading about your lab's use of naturalistic foraging tasks—combining "
                "uncertainty, spatial navigation, decision-making, and episodic memory in a "
                "single behavioral paradigm to study how the brain performs inference under "
                "realistic conditions. Designing behavioral tasks and analysis pipelines that "
                "can reveal the computational structure of navigation circuits requires careful "
                "data engineering, and I'd love to contribute to that work.",
    ),
    dict(
        name="Christine Constantinople",
        email="",
        email_status="needs_lookup",
        profile_url="https://constantinoplelab.com/",
        affiliation="NYU (Center for Neural Science)",
        focus_label="Value-Based Decision Circuits & Orbitofrontal Cortex (CNS)",
        focus="Studies the neural circuits underlying value-based and economic decision-making, "
              "using high-throughput rat behavioral paradigms, large-scale electrophysiology, "
              "optogenetics, and in vivo whole-cell recording.",
        opening="I read about your lab's work on the neural circuits computing and representing "
                "cognitive variables for value-based decision-making—particularly how populations "
                "of neurons in orbitofrontal cortex and striatum encode expected value and track "
                "reward history. Combining large-scale electrophysiology with high-throughput "
                "behavioral training to get the statistical power to test computational models "
                "of decision circuits is exactly the kind of rigorous approach I'd love to "
                "contribute to, given my experience building data analysis pipelines.",
    ),
    # ── NYU Psychology ─────────────────────────────────────────────────────────
    dict(
        name="Todd Gureckis",
        email="todd.gureckis@nyu.edu",
        email_status="ready",
        profile_url="https://todd.gureckislab.org/",
        affiliation="NYU (Psychology)",
        focus_label="Computational Cognition: Active Learning, Curiosity & Reasoning (Psychology)",
        focus="Studies active and self-directed learning, concept learning, decision-making, "
              "and reasoning using computational cognitive models and large-scale behavioral "
              "experiments, including building the ARC behavioral benchmark.",
        opening="I read your 2025 paper building a comprehensive behavioral dataset for the "
                "Abstraction and Reasoning Corpus (ARC)—collecting human response data at scale "
                "to understand where AI systems fail on tasks humans find intuitive. Generating "
                "large-scale behavioral benchmarks that reveal the computational gap between "
                "human and AI reasoning is critical for guiding AI development, and given my "
                "background in data collection and pipeline work, I'd love to contribute to "
                "your lab's research.",
    ),
    dict(
        name="Wei Ji Ma",
        email="weijima@nyu.edu",
        email_status="ready",
        profile_url="https://www.cns.nyu.edu/malab/",
        affiliation="NYU (Psychology / CNS)",
        focus_label="Bayesian Models of Cognition & Decision-Making (Psychology/CNS)",
        focus="Develops Bayesian and probabilistic models of perception, working memory, and "
              "decision-making, testing whether human cognition is well-described by optimal "
              "inference under uncertainty.",
        opening="I've been reading your work on Bayesian models of working memory—particularly "
                "the question of whether human memory errors follow the predictions of optimal "
                "inference under resource constraints, or whether they reflect fundamentally "
                "different computational principles. Using probabilistic modeling to rigorously "
                "test mechanistic hypotheses about cognition, with careful attention to model "
                "comparison and identifiability, is exactly the kind of quantitative approach "
                "I'd love to contribute to.",
    ),
]


def slug(name):
    return "nyu-other-" + re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def main():
    os.makedirs(DRAFTS_DIR, exist_ok=True)
    contacts = load_contacts()

    generated = 0
    needs_lookup = 0
    for prof in PROFESSORS:
        arxiv_id = slug(prof["name"])
        contact = {
            "name": prof["name"],
            "email": prof["email"],
            "email_source": "faculty_page" if prof["email"] else "",
            "affiliation": prof["affiliation"],
            "region": "nyc_tristate",
            "us_verified": "yes",
            "paper_title": prof["focus_label"],
            "arxiv_id": arxiv_id,
            "paper_url": prof["profile_url"],
            "abstract": prof["focus"],
            "status": prof["email_status"],
            "draft_path": "",
        }

        if prof["email_status"] == "ready" and prof["email"]:
            subject = "Undergrad Researcher Interested in Your Work"
            body = BODY_TEMPLATE.format(
                first_name=first_name(prof["name"]),
                opening=prof["opening"],
                position_ask=position_ask_for_region(contact["region"], prof["email"]),
                linkedin=SENDER["linkedin"],
                github=SENDER["github"],
            )
            fname = safe_filename(prof["name"], arxiv_id)
            path = os.path.join(DRAFTS_DIR, fname)
            with open(path, "w", encoding="utf-8") as f:
                f.write(f"TO: {prof['email']}\nSUBJECT: {subject}\n\n{body}")
            contact["draft_path"] = os.path.join("drafts", fname)
            contact["status"] = "drafted"
            generated += 1
        else:
            needs_lookup += 1

        contacts = upsert(contacts, contact)

    save_contacts(contacts)
    print(f"Generated {generated} drafts in {DRAFTS_DIR}/")
    print(f"{needs_lookup} professors still need email lookup.")
    print(f"Total professors: {len(PROFESSORS)}")


if __name__ == "__main__":
    main()
