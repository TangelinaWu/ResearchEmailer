"""Generate outreach drafts for NYU CS / CDS / Tandon faculty.

Follows the same pattern as generate_cbi_drafts.py but covers the CS department,
Center for Data Science, and Tandon CSE. Emails scraped from profile pages Aug 2026.
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

# Each dict: name, email, email_status ("ready" or "needs_lookup"),
#            profile_url, focus_label, focus, opening
PROFESSORS = [
    # ── A ──────────────────────────────────────────────────────────────────────
    dict(
        name="Boris Aronov",
        email="boris.aronov@nyu.edu",
        email_status="ready",
        profile_url="https://engineering.nyu.edu/faculty/boris-aronov",
        focus_label="Computational Geometry & Discrete Algorithms",
        focus="Develops algorithms for problems in discrete and combinatorial geometry, including "
              "Voronoi diagrams, motion planning, and hyperplane arrangements.",
        opening="I've been reading about your work on range-searching data structures and "
                "geometric algorithms for proximity queries. The interplay between combinatorial "
                "geometry and practical data structure design—where theoretical bounds on simplex "
                "range counting translate into faster nearest-neighbor search—struck me as a great "
                "example of theory with real algorithmic payoff, and I'd love to learn more about "
                "how your lab approaches those problems.",
    ),
    dict(
        name="Ainesh Bakshi",
        email="ab13784@nyu.edu",
        email_status="ready",
        profile_url="https://engineering.nyu.edu/faculty/ainesh-bakshi",
        focus_label="Quantum Algorithms & High-Dimensional Statistics",
        focus="Applies iterative methods and convex hierarchies to understand large quantum systems, "
              "with additional interests in high-dimensional statistics, privacy, and numerical "
              "linear algebra.",
        opening="I read about your recent quantum algorithms work that was highlighted in Quanta "
                "Magazine's Biggest Breakthroughs in Computer Science 2024. The idea of using "
                "convex relaxations to learn the structure of quantum systems—connecting quantum "
                "information theory to the kinds of iterative optimization methods used in classical "
                "ML—struck me as a really elegant bridge, and I'd love to learn more about projects "
                "coming out of your group.",
    ),
    dict(
        name="Marshall Ball",
        email="marshall.ball@cs.nyu.edu",
        email_status="ready",
        profile_url="https://cs.nyu.edu/~mmb586/index.html",
        focus_label="Cryptography & Hardness Amplification",
        focus="Studies foundations of cryptography including hardness amplification, randomness "
              "extraction, and circuit complexity.",
        opening="I've been reading about your work on hardness amplification and randomness "
                "extraction, particularly the connections you draw between cryptographic hardness "
                "and circuit lower bounds. The question of when local hardness can be amplified to "
                "global hardness feels fundamental to both theory and applications in secure "
                "computation, and I'd love to understand more about the open problems your lab "
                "is working on.",
    ),
    dict(
        name="Rosanna Bellini",
        email="rfb7709@nyu.edu",
        email_status="ready",
        profile_url="https://engineering.nyu.edu/faculty/rosanna-bellini",
        focus_label="Tech-Enabled Harm & Digital Safety (HCI + Security)",
        focus="Combines computer security, privacy, and HCI to detect and prevent technology-enabled "
              "harms, with a focus on technology-facilitated abuse and its intersection with law.",
        opening="I read about your work running the Clinic to End Tech Abuse at Cornell Tech and "
                "your contributions to changing New York State consumer protection laws around "
                "biometric authentication in banking apps. Designing both technical protections "
                "and policy interventions for the same harm—using the same empirical findings—is "
                "exactly the kind of research that bridges CS and real-world impact, and I'd love "
                "to learn more about how your lab approaches that.",
    ),
    dict(
        name="Juan Pablo Bello",
        email="jb2843@nyu.edu",
        email_status="ready",
        profile_url="https://engineering.nyu.edu/faculty/juan-pablo-bello",
        focus_label="Machine Listening & Audio ML (MARL)",
        focus="Directs the Music and Audio Research Lab, applying machine learning and signal "
              "processing to sound recognition, music information retrieval, and urban acoustics.",
        opening="I read about your BirdVoxDetect system—developed with Cornell Lab and École "
                "Centrale de Nantes—that uses machine learning to identify migrating bird calls "
                "from acoustic recordings that the human ear would miss. The idea of building a "
                "freely available open-source detection pipeline for conservation research, rather "
                "than a proprietary tool, struck me as a great example of ML being deployed for "
                "real scientific value, and I'd love to contribute to projects like that.",
    ),
    dict(
        name="Aaron Bernstein",
        email="ab3599@nyu.edu",
        email_status="ready",
        profile_url="https://engineering.nyu.edu/faculty/aaron-bernstein",
        focus_label="Graph Algorithms & Dynamic Data Structures",
        focus="Designs and analyzes algorithms for dynamic graphs, sublinear problems, and "
              "approximation, with emphasis on matching, shortest paths, and connectivity.",
        opening="I've been reading about your work on dynamic graph algorithms, particularly the "
                "challenge of maintaining near-optimal matchings as edges are inserted and deleted. "
                "Designing algorithms that amortize across a sequence of updates—rather than "
                "recomputing from scratch—feels like exactly the right frame for data-intensive "
                "systems that need to stay fresh, and I'd love to learn more about the problems "
                "your lab is currently focused on.",
    ),
    dict(
        name="Nir Bitansky",
        email="nb3873@nyu.edu",
        email_status="ready",
        profile_url="https://sites.google.com/site/nirbitansky/",
        focus_label="Foundations of Cryptography & Proof Systems",
        focus="Studies foundations of cryptography including succinct arguments, obfuscation, "
              "leakage resilience, and post-quantum cryptography.",
        opening="I've been reading about your work on succinct non-interactive arguments and "
                "the connections between proof system efficiency and cryptographic hardness "
                "assumptions. Understanding when we can compress the evidence for a computation "
                "into a short proof feels deeply relevant to verifiable ML and privacy-preserving "
                "systems, and I'd love to learn more about the open problems your group is "
                "exploring.",
    ),
    dict(
        name="Emily Black",
        email="",
        email_status="needs_lookup",
        profile_url="https://emblack.github.io/",
        focus_label="Algorithmic Fairness & Responsible AI",
        focus="Works on algorithmic fairness, anti-discrimination, and ML policy, studying how "
              "machine learning systems can perpetuate or amplify societal inequalities.",
        opening="I read about your work at the Center for Responsible AI on auditing ML systems "
                "for fairness and anti-discrimination, particularly your research connecting "
                "technical fairness definitions to legal anti-discrimination frameworks. Bridging "
                "formal ML guarantees with actual legal obligations feels like exactly the right "
                "way to make responsible AI research actionable, and I'd love to contribute to "
                "that work.",
    ),
    dict(
        name="Joseph Bonneau",
        email="",
        email_status="needs_lookup",
        profile_url="http://jbonneau.com/",
        focus_label="Applied Cryptography & Blockchains",
        focus="Researches security engineering and applied cryptography, including transparent "
              "dictionaries, distributed randomness beacons, verifiable lotteries, and "
              "cryptocurrency protocols.",
        opening="I read about your recent IronDict system using polynomial commitments to build "
                "transparent dictionaries with cryptographic verifiability (USENIX Security 2026), "
                "and your Cornucopia work on distributed randomness beacons. Building "
                "cryptographic infrastructure that multiple parties can audit without trusting "
                "any single server is a compelling engineering challenge, and I'd love to "
                "contribute to projects like that.",
    ),
    dict(
        name="Samuel Bowman",
        email="bowman@nyu.edu",
        email_status="ready",
        profile_url="https://sleepinyourhat.github.io/",
        focus_label="AI Safety & LLM Evaluation",
        focus="Studies AI safety, LLM alignment, and evaluation methods, particularly how to "
              "verify complex model behavior and build reliable oversight mechanisms for AI systems.",
        opening="I've been following your work on AI evaluations and scalable oversight—"
                "particularly how we verify model outputs on tasks where ground truth is hard "
                "to establish. The problem of building evaluation frameworks that remain reliable "
                "as models get more capable is fundamental to safe deployment, and given my "
                "experience building data pipelines and validation systems, I'd love to "
                "contribute to that kind of research.",
    ),
    dict(
        name="Joan Bruna",
        email="bruna@cims.nyu.edu",
        email_status="ready",
        profile_url="http://cims.nyu.edu/~bruna",
        focus_label="Mathematical Foundations of ML (Geometry, Optimization, Stats)",
        focus="Studies mathematical foundations of machine learning covering optimization, "
              "representation theory, and statistical aspects, with applications to "
              "geophysics and climate modeling.",
        opening="I've been reading your work on geometric deep learning and the mathematical "
                "theory behind equivariant neural networks—specifically how symmetry constraints "
                "can be built into architectures to improve sample efficiency and generalization. "
                "Coming from a background in data pipelines and ML systems, I find the question of "
                "when inductive biases from geometry actually improve learning outcomes in practice "
                "really compelling, and I'd love to learn more about how your group approaches it.",
    ),
    dict(
        name="Benedikt Bünz",
        email="bb@nyu.edu",
        email_status="ready",
        profile_url="http://bue.nz",
        focus_label="Zero-Knowledge Proofs & Blockchain Protocols",
        focus="Works on applied cryptography and blockchains, with focus on zero-knowledge "
              "proofs, proof systems, and verifiable computation.",
        opening="I've been reading your work on Bulletproofs and recursive zero-knowledge proof "
                "systems—particularly how making proofs shorter and faster to verify unlocks "
                "practical privacy-preserving computation on blockchains. The gap between "
                "cryptographic theory and deployed systems is something I find really interesting, "
                "and I'd love to understand how your lab thinks about closing that gap for "
                "real-world applications.",
    ),
    # ── C ──────────────────────────────────────────────────────────────────────
    dict(
        name="Justin Cappos",
        email="jcappos@nyu.edu",
        email_status="ready",
        profile_url="https://engineering.nyu.edu/faculty/justin-cappos",
        focus_label="Software Supply Chain Security (TUF, in-toto, gittuf)",
        focus="Pioneered software supply chain security, building five Linux Foundation projects "
              "(TUF, in-toto, Uptane, SBOMit, gittuf) deployed by Google, Amazon, and Docker.",
        opening="I read about your gittuf system—which decentralizes Git repository security "
                "so that policy enforcement doesn't depend on trusting a single centralized "
                "platform—and its Distinguished Paper Award at NDSS 2025. The idea that the "
                "software supply chain is only as trustworthy as the weakest link, and building "
                "verifiable policy into the version control layer itself, is a really clean "
                "solution to a systemic problem. I'd love to contribute to projects in your lab.",
    ),
    dict(
        name="Yi-Jen Chiang",
        email="chiang@nyu.edu",
        email_status="ready",
        profile_url="https://engineering.nyu.edu/faculty/yi-jen-chiang",
        focus_label="Data Visualization & Computational Geometry",
        focus="Works on computer graphics, data visualization, and large-scale geometric "
              "computation, including isosurface extraction, volume rendering, and out-of-core "
              "algorithms.",
        opening="I've been reading about your work on scalable visualization of large datasets "
                "and out-of-core algorithms for geometric computation. Designing systems that "
                "can visualize data too large to fit in memory—by carefully controlling which "
                "pieces are loaded when—is exactly the kind of problem I work on in my data "
                "pipeline work, and I'd love to understand how your lab applies those ideas in "
                "a visualization context.",
    ),
    dict(
        name="Kyunghyun Cho",
        email="kyunghyun.cho@nyu.edu",
        email_status="ready",
        profile_url="http://kyunghyuncho.me/",
        focus_label="Machine Learning & Natural Language Processing",
        focus="Works on machine learning, natural language processing, and machine translation, "
              "with recent focus on drug discovery applications and co-directing the Global "
              "Frontier AI Lab with Yann LeCun.",
        opening="I've been following your research on machine learning for drug discovery from "
                "your time at Prescient Design and Genentech, and your return to NYU this year "
                "to co-direct the Global Frontier AI Lab. The intersection of foundation model "
                "research and biological sequence generation is something I'd love to contribute "
                "to, and I'm particularly interested in the data pipeline and ML data curation "
                "challenges that kind of work requires.",
    ),
    dict(
        name="Eunsol Choi",
        email="eunsol@nyu.edu",
        email_status="ready",
        profile_url="https://eunsol.github.io/",
        focus_label="NLP: Knowledge Management, RAG & Multilingual QA",
        focus="Researches how language models manage knowledge—including retrieval-augmented "
              "generation, knowledge editing, and multilingual question-answering across 23 "
              "languages—and how users interact with LLMs effectively.",
        opening="I've been reading your lab's work on retrieval-augmented generation and the "
                "challenge of keeping LLM knowledge fresh as the world changes—particularly your "
                "research on when to edit parametric knowledge versus retrieve from an external "
                "store. That tension is something I think about a lot in my data pipeline work, "
                "where stale data is a constant problem, and I'd love to help investigate it "
                "from the NLP side.",
    ),
    dict(
        name="Sumit Chopra",
        email="sumit@cs.nyu.edu",
        email_status="ready",
        profile_url="https://www.spchopra.net/",
        focus_label="ML for Medical Imaging (MRI Triaging & Multi-Modal Learning)",
        focus="Develops ML models for healthcare with focus on representation learning, applying "
              "them to MRI triaging, multi-modal medical data, and adaptive k-space sampling.",
        opening="I read about your work on End-to-End MR Triaging—learning disease signatures "
                "directly in raw frequency space before image reconstruction—and on MR scanners "
                "with memory that use patient-specific priors to reduce scan times. Designing ML "
                "pipelines that operate on raw measurement data rather than processed images, to "
                "avoid information loss early in the pipeline, is exactly the kind of ML data "
                "challenge I'd love to work on.",
    ),
    dict(
        name="Rumi Chunara",
        email="rumi.chunara@nyu.edu",
        email_status="ready",
        profile_url="https://engineering.nyu.edu/faculty/rumi-chunara",
        focus_label="ML for Public Health & Health Equity",
        focus="Directs the Center for Health Data Science, applying ML to public health equity, "
              "social determinants of health, and environmental disparities using satellite "
              "imagery and clinical data.",
        opening="I read about your lab's work using satellite imagery to map urban green space "
                "and reveal environmental disparities in cities like Karachi—building an AI "
                "system that can translate aerial data into actionable equity metrics. Combining "
                "remote sensing data with public health measurement is a great example of ML "
                "creating genuinely useful population-level insights, and given my experience "
                "in data pipelines, I'd love to contribute to that kind of work.",
    ),
    dict(
        name="Patrick Cousot",
        email="",
        email_status="needs_lookup",
        profile_url="http://cs.nyu.edu/~pcousot/",
        focus_label="Abstract Interpretation & Static Program Analysis",
        focus="Invented abstract interpretation, a foundational framework for static analysis "
              "of programs, and continues to develop it for verification, semantics, and "
              "safety-critical software.",
        opening="I've been reading about abstract interpretation as a framework for sound "
                "static analysis—particularly how it enables automated proofs of program "
                "properties without running the program. The idea that you can approximate "
                "all possible program behaviors conservatively, and still derive useful "
                "guarantees, is one of the most elegant results in CS, and I'd love to "
                "understand the current research frontiers in your lab.",
    ),
    # ── D ──────────────────────────────────────────────────────────────────────
    dict(
        name="Ernest Davis",
        email="",
        email_status="needs_lookup",
        profile_url="http://cs.nyu.edu/cs/faculty/davise/",
        focus_label="AI & Commonsense Reasoning",
        focus="Works on automated commonsense reasoning, knowledge representation, and "
              "benchmarks for evaluating AI systems on everyday knowledge tasks including "
              "the Winograd Schema Challenge.",
        opening="I've been reading your work on commonsense reasoning benchmarks and the "
                "Winograd Schema Challenge—particularly your analysis of where current "
                "language models still systematically fail on physical and social commonsense "
                "that humans find obvious. Building better tests to distinguish genuine "
                "understanding from pattern matching is critical for making AI systems "
                "actually trustworthy, and I'd love to contribute to that work.",
    ),
    dict(
        name="Yevgeniy Dodis",
        email="dodis@cs.nyu.edu",
        email_status="ready",
        profile_url="http://cs.nyu.edu/~dodis/",
        focus_label="Cryptography: Leakage Resilience & Randomness",
        focus="Studies cryptography with focus on leakage-resilient cryptography, random "
              "number generation, cryptography with biometric and noisy data, and secure "
              "group messaging.",
        opening="I've been reading about your work on leakage-resilient cryptography—"
                "specifically how to build secure systems that remain safe even when an "
                "adversary learns partial information about secret keys through side channels. "
                "That problem feels especially relevant as ML models increasingly run on "
                "hardware with known side-channel vulnerabilities, and I'd love to learn "
                "more about the current research directions in your group.",
    ),
    dict(
        name="Greg Durrett",
        email="gdurrett@nyu.edu",
        email_status="ready",
        profile_url="https://gregdurrett.github.io/",
        focus_label="NLP: LLM Reasoning, Factuality & Evaluation",
        focus="Develops methods for using LLMs to reason over knowledge in text, making them "
              "more reliable and evaluating their factuality, including integrating SMT solvers "
              "for formal reasoning and building factuality evaluation models.",
        opening="I read your paper integrating SMT solvers into LLM reasoning chains (NeurIPS "
                "2023) and your follow-up work evaluating factuality in generated text (EMNLP "
                "2024). The idea of combining neural generation with symbolic verification—so "
                "that model outputs can be checked against ground truth rather than just "
                "plausibly sounding correct—is exactly the kind of ML research I'm most "
                "interested in, and I'd love to contribute to your lab's work.",
    ),
    # ── F ──────────────────────────────────────────────────────────────────────
    dict(
        name="Martin Farach-Colton",
        email="martin.farach-colton@nyu.edu",
        email_status="ready",
        profile_url="https://engineering.nyu.edu/faculty/martin-farach-colton",
        focus_label="Data Structures, Graph Algorithms & Streaming",
        focus="Works on theory and practice of data structures for storage systems, graph "
              "algorithms, and streaming algorithms; recently solved a decades-old open "
              "problem in list labeling.",
        opening="I read about your recent breakthrough on the list-labeling problem—achieving "
                "an almost-perfect solution to a question that had been open for decades in "
                "the theory of dynamic data structures. Finding optimal algorithms for "
                "maintaining ordered labels under insertions and deletions has direct "
                "implications for database indexing and file systems, and I'd love to learn "
                "more about the techniques behind that result and what problems your lab "
                "is working on next.",
    ),
    dict(
        name="Rob Fergus",
        email="fergus@cs.nyu.edu",
        email_status="ready",
        profile_url="http://cs.nyu.edu/~fergus/",
        focus_label="Computer Vision & Deep Learning",
        focus="Works on computer vision and computational photography, including self-supervised "
              "learning, video understanding, and vision-language models.",
        opening="I've been following your work on self-supervised visual representation "
                "learning—particularly the line of research showing that contrastive and "
                "non-contrastive methods can learn rich visual features without labels. "
                "Building pretraining objectives that transfer well across diverse downstream "
                "tasks is fundamental to making vision systems practical, and given my interest "
                "in ML data and training pipelines, I'd love to contribute to that work.",
    ),
    dict(
        name="David Fouhey",
        email="david.fouhey@nyu.edu",
        email_status="ready",
        profile_url="https://cs.nyu.edu/~fouhey/",
        focus_label="Learning-Based CV: 3D Reconstruction, Physical Estimation & Science",
        focus="Develops learning-based computer vision systems for estimating physical "
              "properties from images, applied to solar physics, ecology, and 3D reconstruction "
              "from multiple views.",
        opening="I read about your lab's work applying vision methods to solar physics—"
                "synthesizing magnetograms from multiple instruments and predicting solar "
                "activity from image data. Building ML pipelines that translate raw astronomical "
                "observations into physical measurements is exactly the kind of scientific "
                "ML I'm most excited about, and given my background in data parsing and "
                "processing pipelines, I'd love to contribute to that work.",
    ),
    dict(
        name="Juliana Freire",
        email="juliana.freire@nyu.edu",
        email_status="ready",
        profile_url="https://engineering.nyu.edu/faculty/juliana-freire",
        focus_label="Data Management, Analytics & AI for Science",
        focus="Develops methods and systems for trustworthy data analytics, visualization, and "
              "provenance; currently building ML systems to combat wildlife trafficking using "
              "large language models and custom classifiers.",
        opening="I read about your VIDA Center's work building a 'model factory' that "
                "automatically produces custom classifiers to detect illegal animal product "
                "listings in online marketplaces across different platforms and languages. "
                "Designing a pipeline that can scale ML classification to millions of ads "
                "while adapting to new categories and languages is exactly the kind of data "
                "engineering challenge I work on at Lea Technologies, and I'd love to "
                "contribute to that system.",
    ),
    # ── G ──────────────────────────────────────────────────────────────────────
    dict(
        name="Davi Geiger",
        email="",
        email_status="needs_lookup",
        profile_url="http://cs.nyu.edu/cs/faculty/geiger/",
        focus_label="Computer Vision & Computational Neuroscience",
        focus="Studies computer vision and learning, with a focus on computational models "
              "that bridge vision in biological and artificial systems.",
        opening="I've been reading about your work on computational models of visual "
                "perception—particularly approaches that tie vision algorithms to neural "
                "mechanisms, using insights from biological vision to constrain what kinds "
                "of representations artificial systems should learn. That connection between "
                "computational neuroscience and computer vision is something I'd love to "
                "explore, and I'd enjoy learning more about your current projects.",
    ),
    dict(
        name="Benjamin Goldberg",
        email="",
        email_status="needs_lookup",
        profile_url="http://cs.nyu.edu/cs/faculty/goldberg/",
        focus_label="Programming Languages & Compiler Verification",
        focus="Researches programming languages, compiler verification, and optimization, "
              "including provably correct compilation and language runtime systems.",
        opening="I've been reading about your work on compiler correctness—specifically "
                "how to formally verify that an optimizing compiler preserves program "
                "semantics across transformations. Given that ML inference increasingly "
                "depends on highly optimized compiled kernels, the question of when we "
                "can trust those optimizations is more relevant than ever, and I'd love "
                "to learn more about the current problems your lab focuses on.",
    ),
    dict(
        name="Rachel Greenstadt",
        email="greenstadt@nyu.edu",
        email_status="ready",
        profile_url="https://engineering.nyu.edu/faculty/rachel-greenstadt",
        focus_label="Privacy, AI Security & Trustworthy Intelligent Systems",
        focus="Designs trustworthy intelligent systems combining AI, psychology, economics, "
              "data privacy, and security; recently studied propaganda detection in LLMs, "
              "deepfake communities, and ad-blocker effectiveness.",
        opening="I read your 2024 study evaluating large language models on propaganda "
                "detection in news articles—finding that specialized systems significantly "
                "outperform general LLMs at identifying persuasion techniques. That kind of "
                "empirical stress-testing of LLM capabilities against real-world information "
                "quality tasks is exactly the kind of applied AI research I'd love to "
                "contribute to.",
    ),
    dict(
        name="Anupam Gupta",
        email="anupamg@nyu.edu",
        email_status="ready",
        profile_url="https://cs.nyu.edu/~anupamg/",
        focus_label="Approximation Algorithms & Stochastic Optimization",
        focus="Works on approximation algorithms for stochastic and online problems, "
              "metric embeddings, and algorithm design under uncertainty.",
        opening="I've been reading your work on approximation algorithms for stochastic "
                "optimization—particularly the challenge of making good decisions when "
                "inputs are revealed online or drawn from an unknown distribution. Designing "
                "algorithms that are near-optimal in expectation, despite uncertainty, is a "
                "beautiful problem with real applications in operations and ML, and I'd love "
                "to learn more about the research your lab is doing.",
    ),
    # ── H ──────────────────────────────────────────────────────────────────────
    dict(
        name="Eran Halperin",
        email="",
        email_status="needs_lookup",
        profile_url="https://tinyurl.com/4ub7hv6p",
        focus_label="Computational Genomics & ML in Medicine",
        focus="Develops computational methods for genomics and machine learning for medicine, "
              "including genetic association studies, ancestry inference, and clinical "
              "prediction models.",
        opening="I've been reading about your work on computational genomics—particularly "
                "methods for ancestry deconvolution and genetic association studies in "
                "diverse populations. Building ML models that are accurate and equitable "
                "across different ancestral backgrounds requires careful attention to "
                "data quality and representation, which connects directly to my work "
                "in data pipelines, and I'd love to contribute to that research.",
    ),
    dict(
        name="He He",
        email="hhe@nyu.edu",
        email_status="ready",
        profile_url="https://hhexiy.ai/",
        focus_label="LLMs: Understanding, Evaluation & Human-AI Collaboration",
        focus="Studies how large language models work and their potential risks, including "
              "how they generalize to novel scenarios, how to evaluate and oversee complex "
              "model behavior, and how humans remain valuable in automated pipelines.",
        opening="I've been reading your lab's work on LLM oversight and capability evaluation—"
                "particularly the question of how to discover risky behaviors and verify model "
                "outputs on complex tasks where human judgment is required. As someone who "
                "builds data validation systems at a startup, I find the problem of maintaining "
                "reliable quality checks over model outputs really compelling, and I'd love "
                "to contribute to your research.",
    ),
    dict(
        name="Chinmay Hegde",
        email="chinmay.h@nyu.edu",
        email_status="ready",
        profile_url="https://chinmayhegde.github.io/",
        focus_label="ML, AI Safety & Adversarial Robustness (DICE Lab)",
        focus="Runs the DICE Lab, working on machine learning, algorithms, and big data; "
              "recent work on adversarial attacks against concept-erasure in text-to-image "
              "models and deepfake detection.",
        opening="I read your lab's paper showing that concept erasure methods in text-to-image "
                "models can be circumvented through adversarial attacks—demonstrating that "
                "safety filters based on learned concept suppression are more brittle than "
                "they appear. Understanding the gap between apparent robustness and actual "
                "robustness is critical for responsible deployment, and I'd love to contribute "
                "to that research.",
    ),
    dict(
        name="Lisa Hellerstein",
        email="lisa.hellerstein@nyu.edu",
        email_status="ready",
        profile_url="https://engineering.nyu.edu/faculty/lisa-hellerstein",
        focus_label="Theoretical CS: Stochastic Optimization & ML Theory",
        focus="Studies approximation algorithms, stochastic combinatorial optimization, "
              "machine learning theory, and Boolean functions, with focus on algorithmic "
              "solutions for optimization under uncertainty.",
        opening="I've been reading your work on stochastic combinatorial optimization—"
                "particularly algorithms for problems where the input is revealed "
                "sequentially and decisions must be made before all information is known. "
                "That framework appears throughout ML (e.g., online learning and bandit "
                "problems), and I'd love to understand how your lab connects the theoretical "
                "results to applied settings.",
    ),
    # ── I ──────────────────────────────────────────────────────────────────────
    dict(
        name="Pavel Izmailov",
        email="",
        email_status="needs_lookup",
        profile_url="https://izmailovpavel.github.io/",
        focus_label="AI Reasoning, Interpretability & AI for Mathematics",
        focus="Studies problem-solving and reasoning in AI, interpretability of deep learning "
              "models, and AI applications for mathematical discovery, including federal "
              "initiatives for AI in mathematics.",
        opening="I read about your contributions to the NSF-backed initiative for AI tools "
                "in mathematics—particularly using reinforcement learning and formal proof "
                "assistants to help explore and verify mathematical conjectures. Building "
                "AI systems that can assist with genuine mathematical reasoning, not just "
                "pattern matching, is one of the most exciting frontiers in ML, and I'd "
                "love to contribute to that work.",
    ),
    # ── K ──────────────────────────────────────────────────────────────────────
    dict(
        name="Julia Kempe",
        email="kempe@nyu.edu",
        email_status="ready",
        profile_url="https://cims.nyu.edu/~kempe/",
        focus_label="ML Theory: LLM Reasoning, Model Collapse & Mechanistic Interpretability",
        focus="Investigates foundations of reasoning in large AI models, including self-improving "
              "reasoning via RL, model collapse on synthetic data, and mechanistic interpretability "
              "of attention mechanisms.",
        opening="I read your lab's work on model collapse—studying how training on synthetic "
                "data affects model quality and when generation-then-training loops degrade "
                "performance. That question is directly relevant to modern ML pipelines that "
                "increasingly use model-generated data for training, and as someone who works "
                "on data quality and validation, I find the connection between data provenance "
                "and model quality really compelling. I'd love to contribute to your research.",
    ),
    dict(
        name="Sanjeev Khanna",
        email="",
        email_status="needs_lookup",
        profile_url="https://sanjeevkhanna.org/",
        focus_label="Approximation Algorithms & Combinatorial Optimization",
        focus="Works on approximation algorithms, combinatorial optimization, and graph "
              "algorithms, recently joining NYU as a Silver Professor.",
        opening="I've been reading your work on approximation algorithms for graph problems—"
                "particularly the tight approximation ratios you've established for Steiner "
                "tree and related network design problems. Understanding the fundamental limits "
                "of efficient approximation, and where the gap between theory and practice "
                "closes, is something I'd love to explore, and I'd welcome the chance to "
                "learn about the problems your lab is focused on at NYU.",
    ),
    dict(
        name="Subhash Khot",
        email="khot@cs.nyu.edu",
        email_status="ready",
        profile_url="http://cs.nyu.edu/~khot/",
        focus_label="Computational Complexity & Unique Games Conjecture",
        focus="Studies algorithms, computational complexity, and the hardness of approximation; "
              "famous for the Unique Games Conjecture, which has shaped the theory of "
              "NP-hardness of approximation.",
        opening="I've been reading about the Unique Games Conjecture and how it has unified "
                "a large class of inapproximability results—giving a single hypothesis that "
                "explains why so many optimization problems are hard to approximate beyond "
                "certain thresholds. Understanding the boundary between tractable and "
                "intractable problems is foundational to ML algorithm design, and I'd love "
                "to learn more about the research directions your group is exploring.",
    ),
    dict(
        name="Robert Krueger",
        email="rk4815@nyu.edu",
        email_status="ready",
        profile_url="https://kruegert.github.io/",
        focus_label="Biomedical Visualization & Visual Analytics (Cancer Research)",
        focus="Develops scalable visualization and visual analytics techniques for biomedical "
              "imaging and multi-omics data, with focus on cancer research; recently won Award "
              "of Excellence at IEEE VIS for the BioSET system.",
        opening="I read about your BioSET system for analyzing biomarker-based spatial "
                "co-expression in tumor microenvironments, which won the Award of Excellence "
                "at IEEE VIS 2025. Building interactive visual analytics tools that help "
                "biologists understand high-dimensional spatial omics data—where the patterns "
                "are too complex to see in a table—is exactly the kind of bridge between data "
                "engineering and domain science I'd love to contribute to.",
    ),
    # ── L ──────────────────────────────────────────────────────────────────────
    dict(
        name="Yann LeCun",
        email="yann@cs.nyu.edu",
        email_status="ready",
        profile_url="http://yann.lecun.com",
        focus_label="Machine Learning, CV & World Models (JEPA)",
        focus="Pioneered convolutional neural networks and currently advocates for "
              "Joint Embedding Predictive Architectures (JEPA) as the path toward "
              "human-level AI with genuine world models.",
        opening="I've been reading your work on Joint Embedding Predictive Architectures—"
                "particularly the argument that predicting in representation space (rather "
                "than pixel space) gives a richer and more efficient world model than "
                "generative approaches. The debate about what AI systems should be "
                "predicting, and at what level of abstraction, is one of the most "
                "intellectually interesting open questions in ML, and I'd be very "
                "interested in contributing to research in your lab.",
    ),
    dict(
        name="Jinyang Li",
        email="",
        email_status="needs_lookup",
        profile_url="https://jinyangli.github.io/",
        focus_label="ML Systems, Distributed Computing & Graph Neural Networks",
        focus="Works on machine learning systems, distributed and parallel computing, and "
              "database systems, including GNN training systems and distributed storage.",
        opening="I've been reading about your work on distributed ML training systems—"
                "particularly the challenge of efficiently scheduling and parallelizing "
                "GNN training across multiple machines. Designing systems abstractions "
                "that make distributed ML training both scalable and correct is a hard "
                "engineering problem, and given my background in data pipelines and "
                "distributed data processing, I'd love to contribute to that work.",
    ),
    dict(
        name="Allen Liu",
        email="",
        email_status="needs_lookup",
        profile_url="https://aliu42.github.io/",
        focus_label="ML Theory, Language Models & Quantum Information",
        focus="Studies foundations of machine learning and language models, quantum state "
              "learning, and algorithmic robustness, with recent work on model stealing "
              "from language models and quantum Hamiltonian learning.",
        opening="I read your paper on model stealing vulnerabilities in low-rank language "
                "models (ICLR 2026)—showing that knowing the model's architecture enables "
                "efficient extraction of its parameters. That connection between theoretical "
                "ML and practical security is fascinating, and given my experience in ML "
                "pipelines and model evaluation, I'd love to contribute to that line of "
                "work.",
    ),
    dict(
        name="Romain Lopez",
        email="romain.lopez@nyu.edu",
        email_status="ready",
        profile_url="https://romain-lopez.github.io/",
        focus_label="ML for Single-Cell Biology & Computational Genomics",
        focus="Develops probabilistic ML tools for single-cell biology, including deep "
              "generative models (scVI) for cellular heterogeneity, perturbation prediction "
              "via optimal transport, and causal inference methods.",
        opening="I read about your scVI framework for modeling single-cell RNA-seq data and "
                "your more recent work using flow matching and optimal transport to predict "
                "how cells respond to perturbations. Building probabilistic models that can "
                "extrapolate to unseen genetic or chemical interventions is one of the most "
                "exciting applications of ML, and given my background in data pipelines and "
                "ML model evaluation, I'd love to contribute to your lab's work.",
    ),
    # ── M ──────────────────────────────────────────────────────────────────────
    dict(
        name="Fermi Ma",
        email="",
        email_status="needs_lookup",
        profile_url="https://fermima.com/",
        focus_label="Quantum Computing & Cryptography",
        focus="Studies quantum computing and its interplay with cryptography, complexity "
              "theory, and physics, including pseudorandom unitaries and post-quantum security.",
        opening="I've been reading your work on pseudorandom unitaries and quantum "
                "cryptographic security—particularly the question of what computational "
                "assumptions are needed to generate quantum states that look random to "
                "any efficient observer. That boundary between quantum information theory "
                "and classical cryptography is one of the most interesting theoretical "
                "frontiers, and I'd love to learn more about the problems your lab "
                "is working on.",
    ),
    dict(
        name="Damon McCoy",
        email="mccoy@nyu.edu",
        email_status="ready",
        profile_url="https://engineering.nyu.edu/faculty/damon-mccoy",
        focus_label="Cybersecurity for Democracy & Online Platforms",
        focus="Empirically measures security and privacy challenges in technology systems, "
              "co-directing Cybersecurity for Democracy; recent work on election official "
              "harassment on social media and conspiracy ad monetization.",
        opening="I read your Cybersecurity for Democracy study analyzing harassment of state "
                "election officials on Twitter during the 2022 midterms—finding that Arizona's "
                "chief election officer received far more targeted harassment than any counterpart "
                "in other states. Building data collection and NLP pipelines to quantify online "
                "threats to democratic processes at scale is exactly the kind of work I'd want "
                "to contribute to, given my background in data pipelines and scraping.",
    ),
    dict(
        name="Nasir Memon",
        email="memon@nyu.edu",
        email_status="ready",
        profile_url="https://engineering.nyu.edu/faculty/nasir-memon",
        focus_label="Digital Forensics, Biometrics & Deepfake Detection",
        focus="Studies media forensics, biometrics, authentication, and network security, "
              "including facial recognition bias, deepfake detection, and co-founding NYU's "
              "Center for Cyber Security.",
        opening="I read about your lab's work on deepfake detection and facial recognition "
                "bias—particularly the empirical approach of measuring how detection systems "
                "perform across demographic groups. Given that deepfake detection pipelines "
                "depend critically on the quality and diversity of their training data, "
                "and that I work on data pipelines and validation at Lea Technologies, "
                "I'd love to contribute to that research.",
    ),
    dict(
        name="Bhubaneswar Mishra",
        email="",
        email_status="needs_lookup",
        profile_url="http://cs.nyu.edu/cs/faculty/mishra/",
        focus_label="Computational Biology, Bioinformatics & Algorithmic Algebra",
        focus="Works on bioinformatics, algorithmic algebra, robotics, and computational "
              "biology, including genome assembly algorithms and formal methods for "
              "biological systems.",
        opening="I've been reading about your work on algorithmic approaches to genome "
                "assembly and the use of algebraic methods to model biological systems. "
                "Applying theoretical computer science to understand how genomes are "
                "structured and how biological sequences can be efficiently processed "
                "at scale is a compelling challenge, and I'd love to learn more about "
                "the current problems your lab focuses on.",
    ),
    dict(
        name="Mehryar Mohri",
        email="mohri@cs.nyu.edu",
        email_status="ready",
        profile_url="http://cs.nyu.edu/cs/faculty/mohri/",
        focus_label="ML Theory: LLMs, Game Theory & Optimization",
        focus="Studies machine learning theory with recent work on LLM ranking algorithms, "
              "self-improvement methods for LLMs, and swap regret (Best Paper Award EC 2025).",
        opening="I read about your Best Paper at EC 2025 on swap regret and correlated "
                "equilibria—showing how swap regret minimization connects online learning "
                "to game-theoretic equilibrium concepts. That bridge between learning "
                "theory and strategic behavior is one of the most elegant results in "
                "the field, and I'd love to learn more about how your group is applying "
                "similar ideas to LLM training and alignment.",
    ),
    dict(
        name="Christopher Musco",
        email="cmusco@nyu.edu",
        email_status="ready",
        profile_url="https://www.chrismusco.com/",
        focus_label="Randomized Algorithms & Scalable ML Foundations",
        focus="Studies algorithmic foundations of data science and ML, including randomized "
              "sketching, numerical linear algebra, streaming algorithms, and scalable methods "
              "for large-scale data problems.",
        opening="I've been reading your work on randomized sketching for inner product "
                "estimation and spectral approximation—particularly how careful randomized "
                "dimension reduction can preserve the structure needed for downstream ML "
                "tasks while dramatically reducing computation. Designing fast, provably "
                "accurate approximations for expensive linear algebra operations is exactly "
                "the kind of theoretical ML work I'd love to contribute to.",
    ),
    # ── N ──────────────────────────────────────────────────────────────────────
    dict(
        name="Daniel Neill",
        email="daniel.neill@nyu.edu",
        email_status="ready",
        profile_url="http://www.cs.nyu.edu/~neill",
        focus_label="ML for Public Health, Surveillance & Algorithmic Fairness",
        focus="Develops ML methods for disease surveillance, healthcare analytics, algorithmic "
              "fairness auditing, causal inference, and opioid abuse monitoring using spatial "
              "and temporal data.",
        opening="I read about your work on pre-syndromic surveillance—using unstructured "
                "data sources to detect novel bio-threats before they appear in structured "
                "clinical reports. Building NLP and ML pipelines that can identify weak "
                "early signals across heterogeneous data streams is a hard detection problem, "
                "and given my experience with data scraping and parsing pipelines at Lea "
                "Technologies, I'd love to contribute to that kind of research.",
    ),
    # ── O ──────────────────────────────────────────────────────────────────────
    dict(
        name="Michael Overton",
        email="",
        email_status="needs_lookup",
        profile_url="http://cs.nyu.edu/cs/faculty/overton/",
        focus_label="Numerical Analysis, Optimization & Linear Algebra",
        focus="Studies numerical computing and optimization including floating-point "
              "arithmetic, nonsmooth nonconvex optimization, and software for control "
              "and linear algebra.",
        opening="I've been reading your work on nonsmooth nonconvex optimization—"
                "particularly methods for optimizing functions that have kinks or "
                "flat regions, which is exactly what happens with neural network loss "
                "landscapes near saddle points. Rigorous numerical methods that are "
                "robust to these difficulties are foundational to reliable ML training, "
                "and I'd love to learn more about the problems your group is working on.",
    ),
    # ── P ──────────────────────────────────────────────────────────────────────
    dict(
        name="Aurojit Panda",
        email="apanda@cs.nyu.edu",
        email_status="ready",
        profile_url="https://cs.nyu.edu/~apanda/",
        focus_label="Systems & Networking: Reliability & ML Training Infrastructure",
        focus="Studies distributed systems and networking with focus on reliability through "
              "pre-deployment bug detection and fault tolerance; recent work on eBPF "
              "networking and ML training stragglers.",
        opening="I read your OSDI 2025 paper on understanding stragglers in large model "
                "training using what-if analysis—identifying which distributed bottlenecks "
                "are actually limiting training throughput. Diagnosing performance problems "
                "in ML training pipelines at scale is exactly the kind of systems work I'd "
                "love to contribute to, given my experience in data pipelines.",
    ),
    dict(
        name="Daniele Panozzo",
        email="",
        email_status="needs_lookup",
        profile_url="http://cs.nyu.edu/~panozzo/",
        focus_label="Geometry Processing, Computer Graphics & Digital Fabrication",
        focus="Works on geometry processing, computer graphics, and digital fabrication, "
              "including mesh processing algorithms and simulation methods for physically "
              "accurate modeling.",
        opening="I've been reading about your work on geometry processing for digital "
                "fabrication—particularly methods for optimizing 3D mesh representations "
                "so that physical objects can be accurately manufactured from digital "
                "models. That connection between computational geometry and physical "
                "manufacturing is a compelling application of algorithms, and I'd love "
                "to learn more about the current research in your lab.",
    ),
    dict(
        name="Sunoo Park",
        email="sunoo.park@nyu.edu",
        email_status="ready",
        profile_url="https://sunoopark.com",
        focus_label="Security, Privacy, Election Security & AI Policy",
        focus="Investigates security, privacy, and transparency in digital technologies, "
              "with focus on election security, AI watermarking policy, and the legal "
              "risks facing security researchers.",
        opening="I read your work on AI watermarking policy—analyzing the gap between "
                "technical claims about watermark robustness and what policymakers are "
                "actually assuming when they propose watermarking mandates. Bridging "
                "that technical-policy gap rigorously, rather than letting policy outrun "
                "the science, is exactly the kind of research that shapes how AI gets "
                "deployed, and I'd love to contribute to that work.",
    ),
    dict(
        name="Benjamin Peherstorfer",
        email="pehersto@cims.nyu.edu",
        email_status="ready",
        profile_url="https://cims.nyu.edu/~pehersto/",
        focus_label="Scientific Computing: Model Reduction & Uncertainty Quantification",
        focus="Develops nonlinear model reduction and data-driven methods for scientific "
              "simulation, with applications to wildfire modeling, fusion energy, and "
              "digital twins; works on neural Galerkin schemes for PDEs.",
        opening="I read about your work on Neural Galerkin schemes for solving PDEs—"
                "combining deep networks with residual minimization to get accurate "
                "solutions at dramatically reduced cost. Building computational tools "
                "that make accurate physical simulation tractable at scale, like your "
                "wildfire uncertainty quantification work, is a compelling application "
                "of ML to scientific computing, and I'd love to contribute to that research.",
    ),
    dict(
        name="Kenneth Perlin",
        email="kp1@cs.nyu.edu",
        email_status="ready",
        profile_url="http://cs.nyu.edu/~perlin/",
        focus_label="Computer Graphics, VR & Procedural Simulation (Future Reality Lab)",
        focus="Directs the NYU Future Reality Lab, working on computer graphics, virtual "
              "reality, procedural animation, and human-computer interaction; invented "
              "Perlin noise.",
        opening="I've been reading about the NYU Future Reality Lab's work on immersive "
                "collaborative environments and procedural character animation. Building "
                "real-time systems that generate believable behavior procedurally—rather "
                "than hand-animating—is a great example of algorithmic thinking applied "
                "to human experience, and I'd love to learn more about the projects "
                "your lab is working on.",
    ),
    dict(
        name="Lerrel Pinto",
        email="lerrel@nyu.edu",
        email_status="ready",
        profile_url="https://www.lerrelpinto.com/",
        focus_label="Robot Learning & Physical World AI (GRAIL Lab)",
        focus="Directs the GRAIL Lab, building frontier robotics models including Robot Utility "
              "Models for zero-shot deployment in new environments and AnySkin plug-and-play "
              "tactile sensors.",
        opening="I read about your AnySkin tactile sensing system, which provides "
                "plug-and-play skin-like sensing for robotic manipulation without "
                "retraining when the sensor is replaced. Building sensing and learning "
                "systems that transfer across physical variations—rather than overfitting "
                "to specific hardware—is a hard generalization challenge, and I'd love "
                "to contribute to the data collection and model evaluation pipelines "
                "behind your Robot Utility Models work.",
    ),
    # ── R ──────────────────────────────────────────────────────────────────────
    dict(
        name="Rajesh Ranganath",
        email="rajeshr@cims.nyu.edu",
        email_status="ready",
        profile_url="https://cims.nyu.edu/~rajeshr/",
        focus_label="ML for Healthcare: Causal Inference & Probabilistic Models",
        focus="Develops causal, statistical, and probabilistic inference methods for "
              "healthcare, including FastSHAP for efficient interpretability, survival "
              "analysis, and out-of-distribution detection.",
        opening="I read about your FastSHAP system for efficient Shapley value estimation—"
                "making model interpretability tractable at scale by learning to predict "
                "Shapley values directly rather than computing them combinatorially. "
                "Building ML tools that are both accurate and interpretable enough for "
                "clinical use is a hard tradeoff, and I'd love to contribute to the "
                "data pipeline and evaluation work behind those methods.",
    ),
    dict(
        name="Oded Regev",
        email="regev@cims.nyu.edu",
        email_status="ready",
        profile_url="http://www.cims.nyu.edu/~regev/",
        focus_label="Lattice Cryptography (LWE) & ML for Molecular Biology",
        focus="Invented the Learning With Errors problem underlying post-quantum cryptography, "
              "and also develops interpretable ML models for RNA processing and protein-nucleic "
              "acid interactions.",
        opening="I was struck by the breadth of your research—from inventing the LWE problem "
                "that now underpins NIST post-quantum cryptography standards, to building "
                "interpretable machine learning models for RNA processing in your wet lab. "
                "The emphasis on interpretable rather than black-box ML for biological data "
                "is something I find really compelling, and I'd love to contribute to either "
                "direction in your lab.",
    ),
    dict(
        name="Mengye Ren",
        email="mengye@nyu.edu",
        email_status="ready",
        profile_url="https://mengyeren.com/",
        focus_label="Continual Learning, World Models & Agentic AI (Agentic Learning AI Lab)",
        focus="Directs the Agentic Learning AI Lab, developing ML systems that continuously "
              "learn and adapt, including adaptive latent world models (AdaJEPA), temporal "
              "straightening, and self-supervised learning from egocentric video.",
        opening="I read about your AdaJEPA work on adaptive latent world models that update "
                "their internal representation continuously as new experience arrives—rather "
                "than training once on a static dataset. That framework for systems that "
                "genuinely learn from unfolding experience is one of the most interesting "
                "open challenges in ML, and given my interest in ML data pipelines and "
                "continual data processing, I'd love to contribute to that research.",
    ),
    # ── S ──────────────────────────────────────────────────────────────────────
    dict(
        name="Florian Schaefer",
        email="florian.schaefer@nyu.edu",
        email_status="ready",
        profile_url="https://f-t-s.github.io/",
        focus_label="Scientific Computing, Numerical Methods & Computational Statistics",
        focus="Develops information geometric mechanics for structure-preserving numerical "
              "methods, scalable PDE solvers using conditional independence, and multi-agent "
              "optimization algorithms.",
        opening="I read about your work enabling extreme-scale fluid dynamics simulations "
                "exceeding one quadrillion degrees of freedom through information geometric "
                "regularization. Building numerical methods that scale to that regime—"
                "by exploiting geometric structure rather than brute force—is a remarkable "
                "result, and I'd love to learn more about how those techniques connect to "
                "the statistical inference and ML work coming out of your lab.",
    ),
    dict(
        name="Dennis Shasha",
        email="shasha@cs.nyu.edu",
        email_status="ready",
        profile_url="http://cs.nyu.edu/cs/faculty/shasha/",
        focus_label="Database Systems, Time Series & Bioinformatics",
        focus="Studies database systems, time series pattern recognition, biological network "
              "inference, and protein design, with work spanning high-performance database "
              "searching and time series motif discovery.",
        opening="I've been reading about your work on time series pattern discovery—"
                "particularly algorithms that identify recurring motifs in long sequences "
                "without exhaustive pairwise comparison. Efficient similarity search in "
                "time series data is something I work with in ML data pipelines, where "
                "deduplication and anomaly detection require exactly that kind of fast "
                "approximate matching, and I'd love to learn more about your current "
                "research.",
    ),
    dict(
        name="Alan Siegel",
        email="",
        email_status="needs_lookup",
        profile_url="http://cs.nyu.edu/cs/faculty/siegel/",
        focus_label="Algorithm Analysis, VLSI Design & Lower Bounds",
        focus="Studies VLSI design, algorithm analysis, parallel algorithms, and complexity "
              "lower bounds.",
        opening="I've been reading about your work on universal hashing and lower bounds "
                "for data structure problems. Establishing tight lower bounds—showing that "
                "no algorithm can beat a certain runtime—is one of the hardest and most "
                "satisfying results in theory, and I'd love to learn more about the "
                "problems your lab is focused on.",
    ),
    dict(
        name="Claudio Silva",
        email="csilva@nyu.edu",
        email_status="ready",
        profile_url="https://engineering.nyu.edu/faculty/claudio-silva",
        focus_label="Visualization, Urban Computing & Sports Analytics (VIDA)",
        focus="Co-directs the VIDA Center, working on visualization, geometric computing, "
              "urban analytics, and sports analytics; senior technology consultant for "
              "MLB Statcast (Emmy Award 2018).",
        opening="I read about your ARGUS system for debugging intelligent AR task guidance "
                "systems—using visual analytics to help developers understand where AR "
                "assistants fail and why. Building interactive debugging tools for AI "
                "systems, rather than just performance metrics, is a great approach to "
                "making ML applications more interpretable and reliable, and I'd love "
                "to contribute to that work.",
    ),
    dict(
        name="Anirudh Sivaraman",
        email="anirudh@cs.nyu.edu",
        email_status="ready",
        profile_url="https://cs.nyu.edu/~anirudh/",
        focus_label="Programmable Networks, Systems & eBPF",
        focus="Studies computer networks and systems, particularly programmable routers "
              "and eBPF-based network applications; recent work on datacenter distributed "
              "logs and ML training straggler analysis.",
        opening="I read your CoNEXT 2025 paper demystifying performance of eBPF network "
                "applications—identifying why in-kernel packet processing programs sometimes "
                "underperform expectations. Understanding the performance model of programmable "
                "network infrastructure is essential as ML training increasingly depends on "
                "fast interconnects, and I'd love to contribute to research at that "
                "intersection.",
    ),
    dict(
        name="Julia Stoyanovich",
        email="stoyanovich@nyu.edu",
        email_status="ready",
        profile_url="https://engineering.nyu.edu/faculty/julia-stoyanovich",
        focus_label="Responsible AI, Algorithmic Fairness & Data Ethics",
        focus="Directs the Center for Responsible AI, working on responsible AI, data "
              "management, and algorithmic fairness; developed 'nutritional label' "
              "transparency tools for automated decision systems.",
        opening="I read about your work developing 'nutritional label' transparency tools "
                "for automated decision systems—using LinkedIn Recruiter as a case study "
                "to show what algorithmic explainability should actually communicate to "
                "affected users. Making AI system behavior legible to non-experts, without "
                "oversimplifying the technical reality, is a genuinely hard design challenge, "
                "and I'd love to contribute to that research.",
    ),
    dict(
        name="Lakshminarayanan Subramanian",
        email="lakshmi@cs.nyu.edu",
        email_status="ready",
        profile_url="http://cs.nyu.edu/~lakshmi/",
        focus_label="Networks, Distributed Systems & Computing for Development",
        focus="Works on networks, distributed systems, and using computing to address "
              "global development challenges, including healthcare in low-resource settings "
              "and AI for social good.",
        opening="I've been reading about your work applying computing to development "
                "challenges in low-resource settings—particularly mobile health systems "
                "and data pipelines designed for unreliable connectivity. Building robust "
                "data infrastructure for environments that mainstream tools assume away "
                "is a genuinely hard engineering problem, and I'd love to contribute to "
                "that work.",
    ),
    dict(
        name="Torsten Suel",
        email="torsten.suel@nyu.edu",
        email_status="ready",
        profile_url="https://engineering.nyu.edu/faculty/torsten-suel",
        focus_label="Search Engines, Web Mining & Information Retrieval",
        focus="Studies search engines, scalable information retrieval, data compression, "
              "and web mining, including document retrieval optimization, index compression, "
              "and batch query processing.",
        opening="I've been reading about your work on block-max indexes for efficient "
                "top-k document retrieval—particularly how careful index compression and "
                "score bounding can dramatically reduce the number of documents that need "
                "to be scored at query time. That kind of principled performance engineering "
                "for large-scale retrieval systems connects directly to the data pipeline "
                "work I do, and I'd love to contribute to research in your lab.",
    ),
    dict(
        name="Qi Sun",
        email="qisun@nyu.edu",
        email_status="ready",
        profile_url="https://qisun.me/",
        focus_label="VR/AR, Computer Graphics & Computational Perception",
        focus="Directs the Immersive Computing Lab, working on VR/AR display optimization, "
              "computer graphics, and computational perception; recently collaborated with "
              "Meta on power efficiency for XR displays (SIGGRAPH 2024).",
        opening="I read about your SIGGRAPH 2024 collaboration with Meta evaluating display "
                "optimization techniques for XR headsets—finding that brightness rolloff "
                "is the most power-efficient approach while maintaining perceptual quality. "
                "Applying perceptual science to make real-time graphics systems more "
                "efficient is a great example of principled hardware-software co-design, "
                "and I'd love to learn more about the projects in your Immersive Computing Lab.",
    ),
    # ── T ──────────────────────────────────────────────────────────────────────
    dict(
        name="Joseph Tassarotti",
        email="jt4767@nyu.edu",
        email_status="ready",
        profile_url="https://cs.nyu.edu/~jt4767/",
        focus_label="Formal Verification of Concurrent & Probabilistic Programs",
        focus="Develops program logics and verification tools for concurrent, randomized, "
              "and probabilistic programs; recent work on formally verifying differential "
              "privacy in separation logic (2026 Sloan Fellow).",
        opening="I read about your work on modular verification of differential privacy "
                "in separation logic—giving a compositional framework to prove that a "
                "program's output distribution is appropriately indistinguishable. "
                "Formal proofs of privacy properties are increasingly important as "
                "ML systems handle sensitive data, and I'd love to understand more "
                "about how your verification methods apply to learned systems.",
    ),
    dict(
        name="Matus Telgarsky",
        email="mjt10041@nyu.edu",
        email_status="ready",
        profile_url="https://cims.nyu.edu/~matus/",
        focus_label="Deep Learning Theory: Margins, Expressivity & Optimization",
        focus="Studies deep learning theory including margin-based analysis, neural network "
              "expressivity, and optimization convergence; recent work on transformer layers "
              "as parallel computation rounds.",
        opening="I read your recent paper characterizing transformer layers as parallel "
                "computation rounds—showing that the architecture's depth translates into "
                "a specific kind of parallel logical depth. Understanding the computational "
                "expressivity of architectures from a formal perspective is foundational to "
                "knowing what transformers can and cannot learn, and I'd love to learn more "
                "about the theoretical tools your lab uses to approach those questions.",
    ),
    dict(
        name="Julian Togelius",
        email="julian.togelius@nyu.edu",
        email_status="ready",
        profile_url="https://engineering.nyu.edu/faculty/julian-togelius",
        focus_label="Game AI, LLMs for Puzzle Design & Evolutionary Computation",
        focus="Studies AI for games, including procedural content generation, player modeling, "
              "and game-playing AI; recent work on LLM-based puzzle generation for the NYT "
              "Connections puzzle and why AI fails at unfamiliar games.",
        opening="I read your work using LLMs to generate New York Times Connections puzzles "
                "that rival human-designed ones in quality. Building generative systems that "
                "produce creative artifacts with the right difficulty and semantic structure—"
                "not just valid outputs—is a hard evaluation challenge, and the method of "
                "using human game designers as a comparison point is exactly right. I'd love "
                "to contribute to research in your lab.",
    ),
    dict(
        name="Paul Torrens",
        email="torrens@nyu.edu",
        email_status="ready",
        profile_url="https://engineering.nyu.edu/faculty/paul-torrens",
        focus_label="Urban Simulation, VR & Autonomous Vehicle Safety",
        focus="Directs the Simspace motion capture lab, working on modeling, simulation, "
              "and VR for urban environments; recent work on AV systems that respond to "
              "pedestrian behavior and edge computing for streetscape analysis.",
        opening="I read about your work building autonomous vehicle systems that are "
                "more responsive to pedestrian behavior—using simulation environments "
                "to test how AV decision-making adapts to the full range of human "
                "street behavior. Simulating rare and dangerous pedestrian scenarios "
                "that real-world data collection can't easily capture is a great use "
                "of synthetic data generation, and I'd love to contribute to that research.",
    ),
    # ── V ──────────────────────────────────────────────────────────────────────
    dict(
        name="Erdem Varol",
        email="ev2240@nyu.edu",
        email_status="ready",
        profile_url="https://engineering.nyu.edu/faculty/erdem-varol",
        focus_label="NeuroAI: Brain Connectivity, Genomics & Computer Vision",
        focus="Develops computational tools bridging genomics and neuroimaging; recent work "
              "includes ConnectionMiner, which integrates gene expression with electron "
              "microscopy connectomes to infer neuronal identities and synaptic connectivity.",
        opening="I read about your ConnectionMiner tool, which integrates gene expression "
                "profiles with EM connectome data to infer how genes orchestrate synaptic "
                "wiring in the fruit fly motor system. Building a pipeline that aligns "
                "two fundamentally different data modalities—high-dimensional gene expression "
                "and spatial connectivity graphs—to make inferences about individual neurons "
                "is a fascinating data integration challenge, and I'd love to contribute to "
                "your lab's computational neuroscience work.",
    ),
    # ── W ──────────────────────────────────────────────────────────────────────
    dict(
        name="Michael Walfish",
        email="mwalfish@cs.nyu.edu",
        email_status="ready",
        profile_url="http://www.cs.nyu.edu/~mwalfish/",
        focus_label="Computer Systems, Security & Verified Computation",
        focus="Works on computer systems, security, and networks, including verifiable "
              "computation, secure systems design, and distributed storage.",
        opening="I've been reading about your work on verifiable computation—systems that "
                "allow an untrusted server to prove to a client that it computed a function "
                "correctly, without the client having to re-run the computation. As ML "
                "inference increasingly runs on untrusted cloud infrastructure, the ability "
                "to verify correctness without re-computation is becoming genuinely important, "
                "and I'd love to contribute to that research.",
    ),
    dict(
        name="Sam Westrick",
        email="",
        email_status="needs_lookup",
        profile_url="http://samwestrick.com",
        focus_label="Programming Languages, Parallel Algorithms & Compilers",
        focus="Studies programming languages, compilers, and parallel algorithms, with "
              "focus on parallel functional programming and efficient compilation strategies.",
        opening="I've been reading about your work on parallel functional programming—"
                "particularly how to compile functional programs to efficiently use "
                "multicore hardware without sacrificing correctness guarantees. Designing "
                "languages where parallelism is safe by construction, rather than a source "
                "of bugs, is a great framing, and I'd love to learn more about the "
                "problems your lab is working on.",
    ),
    dict(
        name="Thomas Wies",
        email="wies@cs.nyu.edu",
        email_status="ready",
        profile_url="http://cs.nyu.edu/wies/",
        focus_label="Program Verification: Raven, Concurrency & Separation Logic",
        focus="Works on program analysis and verification, automated deduction, and "
              "concurrent software; building Raven, a deductive verifier for concurrent "
              "programs based on concurrent separation logic.",
        opening="I read about your Raven verifier for concurrent programs—using concurrent "
                "separation logic to give modular, compositional proofs of correctness for "
                "multi-threaded code. Formally verifying concurrent programs, where races "
                "and deadlocks are notoriously hard to catch by testing, is a compelling "
                "challenge, and I'd love to learn more about the open problems your group "
                "is working on.",
    ),
    dict(
        name="Andrew Gordon Wilson",
        email="andrewgw@cims.nyu.edu",
        email_status="ready",
        profile_url="https://cims.nyu.edu/~andrewgw",
        focus_label="Bayesian ML, Uncertainty Quantification & Deep Learning Theory",
        focus="Pursues a prescriptive approach to building autonomous intelligent systems "
              "with principled uncertainty, studying Bayesian methods, scaling laws, "
              "distribution shift, and physics-informed ML.",
        opening="I've been reading your work on Bayesian deep learning and distribution "
                "shift—particularly how uncertainty-aware models that represent what they "
                "don't know can be more reliable under distribution shift than overconfident "
                "point-estimate models. Building ML systems that know their own limits is "
                "fundamental to safe deployment, and given my interest in model validation "
                "and data quality at Lea Technologies, I'd love to contribute to that research.",
    ),
    # ── X ──────────────────────────────────────────────────────────────────────
    dict(
        name="Saining Xie",
        email="saining.xie@nyu.edu",
        email_status="ready",
        profile_url="http://www.sainingxie.com/",
        focus_label="World Models & Multimodal AI (AMI Labs co-founder)",
        focus="Builds world models that learn from continuous real-world sensory data, "
              "including Solaris (multiplayer Minecraft world model) and Cambrian-S for "
              "spatial video understanding.",
        opening="I read about your Solaris project—a multiplayer video world model in "
                "Minecraft where AI agents interact collaboratively in a shared virtual "
                "environment. Building world models that support multi-agent interaction "
                "and shared physical constraints, rather than single-agent rollouts, is "
                "a significant step toward systems with genuine world understanding, and "
                "I'd love to contribute to the data collection and training pipeline work "
                "behind that.",
    ),
    # ── Y ──────────────────────────────────────────────────────────────────────
    dict(
        name="Sherry Yang",
        email="sherryyang@nyu.edu",
        email_status="ready",
        profile_url="https://sherryy.github.io/",
        focus_label="ML, World Models & RL for Robotics & Science",
        focus="Studies machine learning at the intersection of foundation models and "
              "decision making, including world models, reinforcement learning for "
              "robotics, and AI for scientific discovery (CrystalReasoner).",
        opening="I read about your CrystalReasoner system (2026), which combines language "
                "model reasoning with reinforcement learning for crystal structure "
                "generation—using RL to guide the generative process toward physically "
                "plausible and stable crystal configurations. Applying RL to scientific "
                "discovery problems, where reward comes from physical validity rather than "
                "human preference, is one of the most exciting applications of the field, "
                "and I'd love to contribute to that work.",
    ),
    dict(
        name="Chee Yap",
        email="",
        email_status="needs_lookup",
        profile_url="https://cs.nyu.edu/~yap/",
        focus_label="Computational Geometry & Exact Arithmetic",
        focus="Works on computational geometry, computer algebra, and algorithmic robotics, "
              "with focus on exact computation and subdivision methods for geometric problems.",
        opening="I've been reading about your Exact Computation Project and subdivision "
                "algorithms for geometric problems—particularly the challenge of getting "
                "provably correct answers for geometric queries without the numerical "
                "instability that plagues floating-point implementations. That gap between "
                "theoretical correctness and practical numerical robustness is something "
                "that shows up in data pipelines too, and I'd love to learn more about "
                "the problems your lab is focused on.",
    ),
    # ── Z ──────────────────────────────────────────────────────────────────────
    dict(
        name="Denis Zorin",
        email="dzorin@cs.nyu.edu",
        email_status="ready",
        profile_url="http://cs.nyu.edu/~dzorin/",
        focus_label="Computer Graphics, Geometric Modeling & AI Initiative",
        focus="Works on computer graphics and geometric modeling including subdivision "
              "surfaces, simulation, and rendering; also directs the NYU AI Initiative.",
        opening="I've been reading about your work on subdivision surfaces and physically "
                "accurate simulation for computer graphics—particularly how geometric "
                "modeling methods that respect physical constraints can produce more "
                "realistic results. As Director of the NYU AI Initiative, you're also "
                "at the intersection of AI research and institutional strategy, which "
                "I find compelling. I'd love to learn more about research opportunities "
                "in your group.",
    ),
    # ── CDS Joint Faculty ──────────────────────────────────────────────────────
    dict(
        name="Carlos Fernandez-Granda",
        email="cfgranda@cims.nyu.edu",
        email_status="ready",
        profile_url="https://math.nyu.edu/~cfgranda/",
        focus_label="ML for Medicine, Computational Biology & Climate Science (CDS)",
        focus="Designs and analyzes data-science methodology with focus on ML applied to "
              "medicine, computational biology, climate science, and scientific imaging.",
        opening="I've been reading about your group's work applying ML to medical imaging "
                "and computational biology—particularly building and validating models "
                "that are not just accurate but interpretable and reliable enough for "
                "clinical or scientific use. The challenge of making ML methods that "
                "domain experts can actually trust is something I find really compelling, "
                "and I'd love to contribute to your lab's research.",
    ),
    dict(
        name="Jonathan Niles-Weed",
        email="jnw@cims.nyu.edu",
        email_status="ready",
        profile_url="https://www.jonathannilesweed.com/",
        focus_label="High-Dimensional Statistics & Optimal Transport (CDS)",
        focus="Studies high-dimensional statistics, optimal transport theory, and information "
              "theory, developing statistical methods with provable guarantees for learning "
              "and estimation in complex settings.",
        opening="I've been reading your work on optimal transport for statistical estimation—"
                "particularly using Wasserstein distances to measure distributional "
                "differences in ways that classical metrics miss. That framework is "
                "increasingly important for ML tasks like distribution shift detection "
                "and generative model evaluation, and given my interest in data quality "
                "and validation, I'd love to learn more about the statistical foundations "
                "your lab is developing.",
    ),
    dict(
        name="Tal Linzen",
        email="linzen@nyu.edu",
        email_status="ready",
        profile_url="https://tallinzen.net/",
        focus_label="NLP: Language Models & Computational Cognitive Science (CDS)",
        focus="Studies natural language processing and language models from both an AI "
              "and cognitive science perspective, examining what structural and linguistic "
              "knowledge language models acquire and how they compare to human learners.",
        opening="I've been reading your work on evaluating structural linguistic knowledge "
                "in language models—particularly your research on whether LLMs learn "
                "grammatical dependencies like subject-verb agreement or just exploit "
                "surface statistical patterns. Drawing on cognitive science to design "
                "more rigorous behavioral evaluations of LLMs is exactly the kind of "
                "principled NLP research I'm most interested in, and I'd love to "
                "contribute to your lab's work.",
    ),
    # ── CDS Additional Faculty ─────────────────────────────────────────────────
    dict(
        name="Yanjun Han",
        email="",
        email_status="needs_lookup",
        profile_url="https://cds.nyu.edu/phdfaculty/yanjun-han/",
        focus_label="Statistical Estimation & Information Theory (CDS)",
        focus="Studies the fundamental limits of statistical estimation, learning, and inference "
              "through an information-theoretic lens, including minimax rates, bandits, and online "
              "learning.",
        opening="I've been reading your work on the information-theoretic limits of statistical "
                "estimation—particularly how lower bounds derived from mutual information and channel "
                "capacity arguments give tight minimax sample complexity rates for problems like "
                "distribution testing and density estimation. Proving that an estimator is optimal "
                "by showing no algorithm can do better information-theoretically is one of the most "
                "elegant results in statistics, and I'd love to learn more about the open problems "
                "your group is working on.",
    ),
    dict(
        name="Qi Lei",
        email="ql518@nyu.edu",
        email_status="ready",
        profile_url="https://cecilialeiqi.github.io/",
        focus_label="ML Theory: Generalization, Optimization & Weak-to-Strong Supervision (CDS)",
        focus="Studies machine learning theory including optimization convergence, generalization "
              "bounds, and learning under spurious correlations, with emphasis on overparameterized "
              "models and weak-to-strong generalization.",
        opening="I read your ICLR 2026 paper 'Does Weak-to-strong Generalization Happen under "
                "Spurious Correlations?'—showing that the promising weak-to-strong supervision "
                "paradigm breaks down when the weaker supervisor's errors are correlated with "
                "spurious features in the data. That failure mode is critical to understand before "
                "using weak-to-strong methods in safety-critical contexts, and given my work "
                "building data validation systems, I find the problem of understanding when "
                "generalization claims hold versus break really compelling. I'd love to contribute "
                "to your lab's research.",
    ),
    dict(
        name="Grace Lindsay",
        email="grace.lindsay@nyu.edu",
        email_status="ready",
        profile_url="https://gracewlindsay.com/",
        focus_label="Computational Neuroscience & Neural Networks as Cognitive Models (CDS)",
        focus="Develops and analyzes artificial neural network models as hypotheses about visual "
              "and cognitive processing in biological brains, asking when and why brain-like "
              "computation emerges from architecture.",
        opening="I read your book 'Models of the Mind' and your work on using convolutional and "
                "recurrent neural networks not just to perform tasks but to test hypotheses about "
                "how the brain computes. The distinction between a model that achieves the right "
                "answer and one that achieves it in a biologically meaningful way—and your "
                "framework for thinking about when a model is genuinely explanatory—is exactly the "
                "kind of rigorous thinking about AI and cognition I'd love to contribute to.",
    ),
    dict(
        name="Brian McFee",
        email="brian.mcfee@nyu.edu",
        email_status="ready",
        profile_url="https://brianmcfee.net/",
        focus_label="Music Information Retrieval & Audio ML (CDS / MARL)",
        focus="Develops machine learning methods for music information retrieval, audio analysis, "
              "and music structure analysis; created and maintains librosa, the canonical Python "
              "library for audio and music processing.",
        opening="I've been reading about your work on music structure analysis and your development "
                "of librosa—the Python library for audio analysis that has become the standard "
                "infrastructure for the open-source MIR community. Building reusable scientific "
                "software that lets researchers focus on the science rather than reimplementing "
                "signal processing from scratch is exactly the kind of data infrastructure work "
                "I find compelling, and I'd love to contribute to your research.",
    ),
    dict(
        name="Cristina Savin",
        email="csavin@nyu.edu",
        email_status="ready",
        profile_url="https://as.nyu.edu/faculty/cristina-savin.html",
        focus_label="Neural Circuit Computation & Probabilistic Models of Plasticity (CDS)",
        focus="Develops probabilistic and statistical models to understand how neural circuits "
              "implement learning and memory, combining theoretical neuroscience with neural data "
              "analysis.",
        opening="I read your ICLR 2025 paper 'Desiderata for Normative Models of Synaptic "
                "Plasticity'—laying out principled criteria for when a learning rule counts as "
                "a good model of biological plasticity, rather than just fitting neural data. "
                "That kind of theoretical grounding for what makes a computational model "
                "explanatory rather than merely descriptive is something I find really "
                "compelling, and I'd love to contribute to your lab's work at the intersection "
                "of probabilistic ML and neuroscience.",
    ),
    dict(
        name="Laure Zanna",
        email="laure.zanna@nyu.edu",
        email_status="ready",
        profile_url="https://laurezanna.github.io/",
        focus_label="ML for Climate Science & Ocean Modeling (CDS / M²LInES)",
        focus="Develops data-driven and ML approaches to improve climate models, particularly "
              "learned parameterizations of ocean and sea-ice processes, as co-director of the "
              "M²LInES consortium.",
        opening="I read about your M²LInES consortium's work building data-driven emulators for "
                "climate systems—including the FloeNet sea-ice emulator and SamudrACE coupled "
                "ocean-atmosphere models that replace costly physical simulations with learned "
                "surrogates. Building ML systems accurate and stable enough to be embedded inside "
                "a climate simulator, rather than run alongside it, is a hard constraint, and "
                "given my background in data pipelines and ML model validation, I'd love to "
                "contribute to that work.",
    ),
    # ── Incoming Faculty (Starting September 2026) ─────────────────────────────
    dict(
        name="Thibault Dardinier",
        email="",
        email_status="needs_lookup",
        profile_url="https://dardinier.me/",
        focus_label="Formal Verification: Hyperproperties & Separation Logic (Incoming)",
        focus="Develops program logics and mechanized verification tools for programs with "
              "complex memory and security properties, including extending separation logic to "
              "hyperproperties.",
        opening="I read your PLDI 2026 paper on Hyper Separation Logic—extending separation "
                "logic to hyperproperties, so that security properties like noninterference "
                "(which relate multiple execution traces rather than a single one) can be "
                "verified compositionally. Making formal proofs of security properties modular "
                "enough to scale to real programs is a hard challenge, and I'd love to "
                "contribute to the verification infrastructure work your lab will be building.",
    ),
    dict(
        name="Evan Johnson",
        email="",
        email_status="needs_lookup",
        profile_url="https://enjhnsn2.github.io/",
        focus_label="Systems Security & Verified Isolation in Production OSes (Incoming)",
        focus="Applies formal verification and security principles to real operating systems, "
              "including verified isolation in production embedded OS kernels.",
        opening="I read your SOSP 2025 paper '✓Tock: Verified Isolation in a Production "
                "Embedded OS'—showing that formal isolation guarantees can be achieved in "
                "a real, widely-deployed embedded OS rather than a toy system. Bringing "
                "verification into production infrastructure, rather than keeping it in "
                "academic case studies, is exactly the kind of practical systems security "
                "work I find compelling, and I'd love to learn more about the projects "
                "your lab will be working on.",
    ),
    dict(
        name="Gautam Kamath",
        email="",
        email_status="needs_lookup",
        profile_url="https://www.gautamkamath.com/",
        focus_label="Statistical Differential Privacy & Robust Estimation (Incoming)",
        focus="Studies the sample complexity and fundamental limits of statistical estimation "
              "under differential privacy and adversarial data corruption, establishing optimal "
              "algorithms and tight lower bounds.",
        opening="I've been reading your work on the statistical complexity of differentially "
                "private estimation—particularly your tight analysis of private mean and covariance "
                "estimation that precisely quantifies how much extra data privacy costs relative "
                "to non-private baselines. That fundamental understanding of the privacy-utility "
                "tradeoff is essential for deploying ML on sensitive data responsibly, and given "
                "my work in data pipelines and validation, I'd love to contribute to your lab's "
                "research.",
    ),
    dict(
        name="Zongyi Li",
        email="",
        email_status="needs_lookup",
        profile_url="https://zongyi-li.github.io/",
        focus_label="Neural Operators & Scientific ML—Fourier Neural Operator (Incoming CDS)",
        focus="Develops neural operator methods—particularly the Fourier Neural Operator (FNO)—"
              "for learning maps between function spaces, enabling fast and resolution-invariant "
              "surrogate models for PDEs in climate, fluid dynamics, and engineering simulation.",
        opening="I read your paper on the Fourier Neural Operator—using the Fourier transform to "
                "learn solution operators for PDEs directly in frequency space, producing surrogate "
                "models that are resolution-invariant and orders of magnitude faster than classical "
                "solvers. Shifting from learning finite-dimensional mappings to learning operators "
                "on function spaces is a powerful conceptual step, and given my background in ML "
                "data pipelines and model evaluation, I'd love to contribute to your lab's "
                "scientific ML work.",
    ),
    dict(
        name="Tony Metger",
        email="",
        email_status="needs_lookup",
        profile_url="https://tonymetger.com/",
        focus_label="Quantum Cryptography & Quantum Information Theory (Incoming)",
        focus="Studies quantum information theory and quantum cryptography, including single-round "
              "proofs of quantumness, quantum self-testing, and device-independent cryptography.",
        opening="I read your ITCS 2025 paper on single-round proofs of quantumness from knowledge "
                "assumptions—giving a way to cryptographically certify that a device is performing "
                "genuine quantum computation using only classical interaction. The idea that "
                "classical cryptographic assumptions can underwrite verification of quantum "
                "behavior is a remarkable bridge between the two fields, and I'd love to learn "
                "more about the open problems your lab is working on.",
    ),
    dict(
        name="Juan C. Perdomo",
        email="",
        email_status="needs_lookup",
        profile_url="https://jcperdomo.org/",
        focus_label="AI & Society: Performative Prediction & Algorithmic Impact (Incoming)",
        focus="Studies how deployed ML systems shape the social environments they predict, "
              "including performative prediction, feedback loops between algorithms and human "
              "behavior, and the impact of prediction on the most vulnerable populations.",
        opening="I read your ICML 2025 Outstanding Paper 'The Value of Prediction in Identifying "
                "the Worst-Off'—showing that ML predictions can be used not just to optimize "
                "average outcomes but to specifically identify and prioritize the most vulnerable "
                "individuals. That connection between algorithmic prediction and distributive "
                "justice is exactly the kind of ML research I'd love to contribute to, and it "
                "connects directly to your earlier work on performative prediction where model "
                "deployment changes the distribution being predicted.",
    ),
    dict(
        name="Pratyusha Sharma",
        email="",
        email_status="needs_lookup",
        profile_url="https://pratyushasharma.github.io/",
        focus_label="Deep Learning Theory, NLP & AI for Science (Incoming)",
        focus="Studies the theoretical and empirical properties of deep learning methods, "
              "including fine-tuning dynamics, language model behavior, and ML applied to "
              "scientific discovery.",
        opening="I read your NeurIPS 2025 paper 'LoRA vs Full Fine-tuning: An Illusion of "
                "Equivalence'—showing that despite matching performance metrics, LoRA and full "
                "fine-tuning produce models with fundamentally different internal representations. "
                "Understanding when two training procedures are genuinely equivalent versus just "
                "empirically similar is critical for reliable deployment, and given my background "
                "in ML model validation, I'd love to contribute to your research.",
    ),
    # ── Tandon Faculty ─────────────────────────────────────────────────────────
    dict(
        name="Siddharth Garg",
        email="sg175@nyu.edu",
        email_status="ready",
        profile_url="https://engineering.nyu.edu/faculty/siddharth-garg",
        focus_label="Hardware Security & ML Model Security (Tandon ECE)",
        focus="Studies hardware security and the security of ML systems, including neural "
              "trojan attacks (backdoors embedded in model weights), hardware IP protection, "
              "and security of ML accelerators.",
        opening="I read about your work on neural trojan attacks—showing that backdoors can be "
                "embedded into neural network weights during training so that the model behaves "
                "correctly on clean inputs but triggers on a specific pattern. Understanding "
                "how ML models can be compromised at the training stage, rather than at "
                "inference time, is a critical security problem as ML is deployed in more "
                "sensitive contexts, and given my experience building data validation pipelines, "
                "I'd love to contribute to that research.",
    ),
    dict(
        name="Sandra Siby",
        email="sandra.siby@nyu.edu",
        email_status="ready",
        profile_url="https://sandrasiby.github.io/",
        focus_label="Network Privacy & Privacy-Preserving ML on Edge Devices (Tandon / NYUAD)",
        focus="Studies network security and privacy, including traffic analysis attacks, "
              "website fingerprinting defenses, and privacy-preserving ML inference on "
              "edge devices.",
        opening="I've been reading about your work on network traffic analysis and privacy—"
                "particularly how metadata from encrypted traffic can be used to fingerprint "
                "websites and user behavior even without decrypting the payload. Building "
                "defenses that are practical enough to deploy while providing meaningful "
                "privacy guarantees is a hard challenge, and I'd love to learn more about "
                "the privacy-preserving ML work coming out of your group. I'm primarily "
                "looking for research opportunities in the NYC area, but I'd also welcome "
                "remote collaboration with your group.",
    ),
]


def slug(name):
    return "nyu-cs-" + re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


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
            "affiliation": "NYU",
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
    print(f"Generated {generated} NYU CS drafts in {DRAFTS_DIR}/")
    print(f"{needs_lookup} professors still need email lookup before drafts can be written.")
    print(f"Total professors: {len(PROFESSORS)}")


if __name__ == "__main__":
    main()
