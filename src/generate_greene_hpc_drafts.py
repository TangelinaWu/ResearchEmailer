"""Generate Greene HPC sponsorship request drafts for NYU faculty.

Unlike the research-internship scripts, these emails ask a faculty member
to sponsor Prof. Babak Ardekani's team for access to NYU's Greene GPU
cluster. Babak is affiliated with NYU Grossman School of Medicine / NKI,
which does not automatically receive Greene access, so a main-campus
NYU faculty sponsor is required.

Team: Prof. Babak Ardekani (PI, Grossman/NKI), Angelina Wu (research
engineer), Amir (PhD, HKUST), Nathan (Northeastern). Project: 3D CNN
pipeline for MRI brain age prediction and neurodegenerative disease
detection (BrainAge).

Usage (from src/):
  python generate_greene_hpc_drafts.py
Then review and send via the existing pipeline:
  python review_drafts.py
  python gmail_client.py
"""
import os
import re

from contacts_store import load_contacts, save_contacts, upsert
from draft_generator import first_name, safe_filename

DRAFTS_DIR = os.path.join(os.path.dirname(__file__), "..", "drafts")

SENDER = {
    "email": "angelina@getlea.io",
}

SUBJECT = "Request for Greene HPC Sponsorship — CNN/MRI Brain Aging Research"

BODY_TEMPLATE = """Dear Professor {last_name},

I hope this message finds you well. {opening}

I am writing to ask if you would be willing to sponsor our research team for access to NYU's \
Greene GPU cluster. Our PI, Prof. Babak Ardekani, is affiliated with NYU Grossman School of \
Medicine rather than the main campus, so his lab does not automatically receive Greene access — \
a sponsoring NYU faculty member is all that is needed to bridge that gap.

**Our Team**

- Prof. Babak Ardekani, PhD (PI) — Nathan S. Kline Institute / NYU Grossman School of Medicine. \
Over 25 years in computational neuroimaging, author of the ART (Automatic Registration Toolbox) \
used by labs worldwide, with 100+ peer-reviewed publications on MRI brain registration and \
Alzheimer's detection.
- Angelina Wu — research engineer, NYU CS & Economics '28. Pipeline architecture, preprocessing, \
and model training.
- Amir — PhD student, HKUST. Deep learning architecture and longitudinal analysis.
- Nathan — undergraduate researcher, Northeastern University. Data processing and evaluation.

**The Project**

We are training 3D CNNs on structural MRI to predict brain age and compute the Brain Age Gap \
(BAG) — a biomarker for accelerated neurodegeneration linked to Alzheimer's disease and \
frontotemporal dementia. Our data comes from ADNI and OASIS-3 (several thousand scans). \
Training a single model takes 12–24 hours on an A100; across experiments we estimate \
500–800 GPU hours and ~2 TB of storage — well within a typical faculty allocation, and we \
would stay within any sub-limits you set.

Sponsoring us would mean a one-time administrative step to add Prof. Ardekani's account to \
your allocation. We would handle everything else independently and are happy to share results, \
include acknowledgments, or explore collaboration if there is interest.

I would love to get on a short call with you to discuss the specifics — 15 to 20 minutes at \
your convenience. Feel free to suggest a time, or just reply and I will send a calendar invite.

Thank you so much for considering this.

Warmly,
Angelina Wu
NYU, CS & Economics '28
{email}
"""


def slug(name):
    return "greene-hpc-" + re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


# Each dict: name, email, email_status, profile_url, focus_label, focus, opening.
# opening = one sentence connecting their research to our project — keeps the
# email personal and shows we did our homework.
PROFESSORS = [
    # ── Courant / CS ──────────────────────────────────────────────────────────
    dict(
        name="Yann LeCun",
        email="yann@nyu.edu",
        email_status="ready",
        profile_url="http://yann.lecun.com",
        focus_label="Deep learning, convolutional networks, computer vision",
        focus="Pioneered convolutional neural networks; currently developing Joint Embedding "
              "Predictive Architectures as a path toward human-level AI.",
        opening="Your foundational work on convolutional neural networks is precisely the "
                "architecture class we are applying to volumetric brain MRI for age prediction.",
    ),
    dict(
        name="Joan Bruna",
        email="bruna@nyu.edu",
        email_status="ready",
        profile_url="http://cims.nyu.edu/~bruna",
        focus_label="Geometric deep learning, graph neural networks, ML theory",
        focus="Studies mathematical foundations of ML covering optimization, representation "
              "theory, and statistical aspects.",
        opening="Your work on geometric deep learning and equivariant architectures directly "
                "informs how we handle the 3D spatial structure of MRI volumes.",
    ),
    dict(
        name="Andrew Gordon Wilson",
        email="andrewgw@nyu.edu",
        email_status="ready",
        profile_url="https://cims.nyu.edu/~andrewgw",
        focus_label="Bayesian deep learning, uncertainty quantification",
        focus="Pursues principled uncertainty-aware ML, Bayesian methods, scaling laws, "
              "and physics-informed ML.",
        opening="Your research on uncertainty in neural networks is directly relevant to the "
                "confidence estimation we build on top of our brain age gap predictions.",
    ),
    dict(
        name="He He",
        email="hhe@nyu.edu",
        email_status="ready",
        profile_url="https://hhexiy.ai/",
        focus_label="LLMs, robustness, human-AI collaboration",
        focus="Studies how large language models generalize, how to evaluate complex model "
              "behavior, and how humans remain valuable in automated pipelines.",
        opening="Your work on model robustness and rigorous evaluation methodology shapes how "
                "we think about bias correction in our brain age prediction pipeline.",
    ),
    dict(
        name="Kyunghyun Cho",
        email="kyunghyun.cho@nyu.edu",
        email_status="ready",
        profile_url="http://kyunghyuncho.me/",
        focus_label="Machine learning, sequence models, biomedical AI",
        focus="Works on ML and NLP with recent focus on drug discovery and biomedical AI.",
        opening="Your interdisciplinary AI-for-health research is a strong match for our "
                "MRI-based neurodegenerative disease prediction work.",
    ),
    dict(
        name="Lerrel Pinto",
        email="lerrel@nyu.edu",
        email_status="ready",
        profile_url="https://www.lerrelpinto.com/",
        focus_label="Robot learning, self-supervised learning, representation learning",
        focus="Directs the GRAIL Lab, building frontier robotics models including Robot "
              "Utility Models and AnySkin tactile sensors.",
        opening="Your work on self-supervised visual representations is directly applicable "
                "to our limited-labeled-data challenge in neuroimaging.",
    ),
    dict(
        name="Mehryar Mohri",
        email="mohri@nyu.edu",
        email_status="ready",
        profile_url="http://cs.nyu.edu/cs/faculty/mohri/",
        focus_label="ML theory, LLMs, game theory",
        focus="Studies ML theory with recent work on LLM ranking algorithms and swap regret "
              "(Best Paper EC 2025).",
        opening="Your theoretical framework for learning guarantees helps us reason about "
                "generalization on small neuroimaging datasets.",
    ),
    dict(
        name="Rajesh Ranganath",
        email="rajeshr@nyu.edu",
        email_status="ready",
        profile_url="https://cims.nyu.edu/~rajeshr/",
        focus_label="Probabilistic ML, deep learning for healthcare, clinical AI",
        focus="Develops causal, statistical, and probabilistic inference methods for healthcare.",
        opening="Your work on deep learning for health and clinical inference is a near-perfect "
                "match for our brain aging and neurodegeneration prediction project.",
    ),
    dict(
        name="Subhash Khot",
        email="khot@nyu.edu",
        email_status="ready",
        profile_url="http://cs.nyu.edu/~khot/",
        focus_label="Computational complexity, approximation algorithms",
        focus="Studies algorithms, computational complexity, and hardness of approximation; "
              "author of the Unique Games Conjecture.",
        opening="Your faculty position in Courant CS makes you well-placed to facilitate HPC "
                "resource access for interdisciplinary neuroscience-ML work.",
    ),
    dict(
        name="Dennis Shasha",
        email="shasha@nyu.edu",
        email_status="ready",
        profile_url="http://cs.nyu.edu/cs/faculty/shasha/",
        focus_label="Database systems, time series, bioinformatics",
        focus="Studies database systems, time series pattern recognition, and biological "
              "network inference.",
        opening="Your bioinformatics and database systems experience and long-standing Courant "
                "affiliation make you a strong potential sponsor for our project.",
    ),
    dict(
        name="Denis Zorin",
        email="dzorin@nyu.edu",
        email_status="ready",
        profile_url="http://cs.nyu.edu/~dzorin/",
        focus_label="Computer graphics, geometric modeling, NYU AI Initiative director",
        focus="Works on computer graphics and geometric modeling; directs the NYU AI Initiative.",
        opening="As Director of the NYU AI Initiative, your position at the intersection of AI "
                "research and institutional strategy makes you an ideal potential sponsor.",
    ),
    dict(
        name="Lakshminarayanan Subramanian",
        email="lakshmi@nyu.edu",
        email_status="ready",
        profile_url="http://cs.nyu.edu/~lakshmi/",
        focus_label="Networked systems, AI for health, computing for development",
        focus="Works on networks, distributed systems, and computing for global health in "
              "low-resource settings.",
        opening="Your AI-for-health work and Courant CS affiliation make you a natural potential "
                "bridge between our interdisciplinary team and NYU HPC resources.",
    ),
    # ── Center for Data Science ───────────────────────────────────────────────
    dict(
        name="Carlos Fernandez-Granda",
        email="cfgranda@nyu.edu",
        email_status="ready",
        profile_url="https://math.nyu.edu/~cfgranda/",
        focus_label="ML for medicine, MRI reconstruction, computational biology",
        focus="Designs data-science methodology applied to medicine, computational biology, "
              "climate science, and scientific imaging.",
        opening="Your research on ML-accelerated MRI reconstruction and medical imaging is "
                "foundational to the preprocessing stage of our brain age pipeline.",
    ),
    dict(
        name="Rumi Chunara",
        email="rumi.chunara@nyu.edu",
        email_status="ready",
        profile_url="https://engineering.nyu.edu/faculty/rumi-chunara",
        focus_label="ML for public health, health equity, clinical data science",
        focus="Directs the Center for Health Data Science, applying ML to public health equity "
              "and social determinants of health.",
        opening="Your work on population-level health prediction with ML connects directly to "
                "our goal of scalable brain health screening.",
    ),
    dict(
        name="Jonathan Niles-Weed",
        email="jnw@nyu.edu",
        email_status="ready",
        profile_url="https://www.jonathannilesweed.com/",
        focus_label="High-dimensional statistics, optimal transport",
        focus="Studies high-dimensional statistics, optimal transport theory, and information "
              "theory with provable guarantees.",
        opening="Your optimal transport work informs our approach to distribution shift between "
                "brain age training and test populations.",
    ),
    dict(
        name="Cristina Savin",
        email="csavin@nyu.edu",
        email_status="ready",
        profile_url="https://as.nyu.edu/faculty/cristina-savin.html",
        focus_label="Computational neuroscience, probabilistic models of plasticity",
        focus="Develops probabilistic and statistical models to understand how neural circuits "
              "implement learning and memory.",
        opening="Your computational neuroscience background and CDS affiliation make you an "
                "ideal bridge between our ML methodology and neuroscience goals.",
    ),
    dict(
        name="Julia Kempe",
        email="kempe@nyu.edu",
        email_status="ready",
        profile_url="https://cims.nyu.edu/~kempe/",
        focus_label="ML theory, LLM reasoning, model collapse",
        focus="Investigates foundations of reasoning in large AI models, including model "
              "collapse on synthetic data and mechanistic interpretability.",
        opening="Your computational expertise and position at CDS are well-suited to support "
                "our GPU-intensive 3D MRI training pipeline.",
    ),
    dict(
        name="Tal Linzen",
        email="linzen@nyu.edu",
        email_status="ready",
        profile_url="https://tallinzen.net/",
        focus_label="NLP, language models, computational cognitive science",
        focus="Studies NLP and language models from both an AI and cognitive science perspective.",
        opening="Your CDS affiliation and experience with large-scale GPU training workloads "
                "make you a potential sponsor for our Greene access request.",
    ),
    dict(
        name="Grace Lindsay",
        email="grace.lindsay@nyu.edu",
        email_status="ready",
        profile_url="https://gracewlindsay.com/",
        focus_label="Computational neuroscience, neural networks as cognitive models",
        focus="Develops and analyzes artificial neural network models as hypotheses about "
              "visual and cognitive processing in biological brains.",
        opening="Your work using CNNs as models of brain computation is directly adjacent to "
                "our CNN-based brain age prediction pipeline.",
    ),
    dict(
        name="Qi Lei",
        email="ql518@nyu.edu",
        email_status="ready",
        profile_url="https://cecilialeiqi.github.io/",
        focus_label="ML theory, generalization, optimization",
        focus="Studies machine learning theory including optimization convergence, "
              "generalization bounds, and learning under spurious correlations.",
        opening="Your ML theory work on generalization and your CDS affiliation make you a "
                "potential supporter of our GPU-based neuroimaging research.",
    ),
    dict(
        name="Laure Zanna",
        email="laure.zanna@nyu.edu",
        email_status="ready",
        profile_url="https://laurezanna.github.io/",
        focus_label="ML for climate science, ocean modeling",
        focus="Develops data-driven and ML approaches to improve climate models as "
              "co-director of the M²LInES consortium.",
        opening="Your experience running GPU-intensive scientific ML workloads and your CDS "
                "position make you a strong potential Greene access sponsor.",
    ),
    # ── Neural Science ────────────────────────────────────────────────────────
    dict(
        name="David Heeger",
        email="david.heeger@nyu.edu",
        email_status="ready",
        profile_url="https://www.cns.nyu.edu/heegerlab/",
        focus_label="Computational vision, fMRI, brain imaging",
        focus="Studies the computational basis of visual perception and fMRI signals.",
        opening="Your pioneering fMRI and computational brain imaging work is the scientific "
                "foundation our brain age prediction project builds upon.",
    ),
    dict(
        name="Eero Simoncelli",
        email="eero.simoncelli@nyu.edu",
        email_status="ready",
        profile_url="https://www.cns.nyu.edu/~eero/",
        focus_label="Computational neuroscience, visual processing, statistical models",
        focus="Studies statistical models of neural data and image processing at the "
              "intersection of vision science and computation.",
        opening="Your foundational work on statistical models of neural data and image "
                "processing is deeply relevant to our MRI-based brain aging pipeline.",
    ),
    dict(
        name="Xiao-Jing Wang",
        email="xjwang@nyu.edu",
        email_status="ready",
        profile_url="https://www.cns.nyu.edu/wanglab/",
        focus_label="Computational psychiatry, large-scale brain modeling",
        focus="Works on computational psychiatry, working memory, and large-scale brain "
              "circuit modeling.",
        opening="Your computational psychiatry work and expertise in modeling brain states "
                "maps closely to our neural disease prediction objective.",
    ),
    dict(
        name="Roozbeh Kiani",
        email="roozbeh@nyu.edu",
        email_status="ready",
        profile_url="https://www.cns.nyu.edu/kianilab/Home.html",
        focus_label="Neural computation, decision-making, neural population dynamics",
        focus="Studies how the brain integrates sensory evidence to form decisions, using "
              "Neuropixels recording and neural perturbation.",
        opening="Your neural population analysis methods and quantitative neuroscience "
                "background position you as a strong scientific sponsor for our project.",
    ),
    dict(
        name="Wei Ji Ma",
        email="weijima@nyu.edu",
        email_status="ready",
        profile_url="https://www.cns.nyu.edu/malab/",
        focus_label="Bayesian brain, uncertainty, computational cognitive neuroscience",
        focus="Works on Bayesian models of brain function and how the brain handles "
              "uncertainty in perception and decision-making.",
        opening="Your work on Bayesian models of brain function connects to our uncertainty-"
                "aware brain age distribution prediction framework.",
    ),
    dict(
        name="Dmitri Chklovskii",
        email="dm@nyu.edu",
        email_status="ready",
        profile_url="https://www.simonsfoundation.org/team/dmitri-chklovskii/",
        focus_label="Connectomics, neural circuit analysis, computational neuroscience",
        focus="Works on connectomics and neural circuit analysis with the Simons Foundation "
              "and NYU.",
        opening="Your experience analyzing large-scale neural datasets with computational "
                "methods aligns well with our volumetric brain analysis pipeline.",
    ),
    # ── NYU Tandon Engineering ────────────────────────────────────────────────
    dict(
        name="Yao Wang",
        email="yw1@nyu.edu",
        email_status="ready",
        profile_url="https://engineering.nyu.edu/faculty/yao-wang",
        focus_label="Medical image processing, deep learning for imaging",
        focus="Works on medical image processing and CNN-based imaging analysis at NYU Tandon.",
        opening="Your work on medical image processing and CNN-based imaging is the closest "
                "methodological match to our brain MRI aging pipeline in the entire university.",
    ),
    dict(
        name="Anna Choromanska",
        email="ac4245@nyu.edu",
        email_status="ready",
        profile_url="https://engineering.nyu.edu/faculty/anna-choromanska",
        focus_label="Deep learning optimization, ML theory, neural networks",
        focus="Studies the optimization landscape of deep neural networks and ML theory.",
        opening="Your research on the optimization landscape of deep neural networks is "
                "directly relevant to our 3D CNN training on volumetric MRI.",
    ),
    dict(
        name="Chinmay Hegde",
        email="chinmay.h@nyu.edu",
        email_status="ready",
        profile_url="https://chinmayhegde.github.io/",
        focus_label="ML, signal processing, compressed sensing",
        focus="Runs the DICE Lab working on ML, algorithms, compressed sensing, and "
              "adversarial robustness.",
        opening="Your compressed sensing and inverse problems expertise is directly relevant "
                "to our MRI reconstruction and preprocessing work.",
    ),
    dict(
        name="Siddharth Garg",
        email="sg175@nyu.edu",
        email_status="ready",
        profile_url="https://engineering.nyu.edu/faculty/siddharth-garg",
        focus_label="Hardware-software co-design, ML acceleration, efficient inference",
        focus="Studies hardware security and the security/efficiency of ML systems, including "
              "neural trojan attacks and ML accelerators.",
        opening="Your ML hardware and efficient inference work is highly relevant to our need "
                "for GPU-accelerated 3D convolution workloads on the Greene cluster.",
    ),
    dict(
        name="Guido Gerig",
        email="guido.gerig@nyu.edu",
        email_status="ready",
        profile_url="https://engineering.nyu.edu/faculty/guido-gerig",
        focus_label="Medical image analysis, brain development, shape statistics, neuroimaging",
        focus="Develops computational tools for medical image analysis and neuroimaging, "
              "including shape statistics and longitudinal brain development studies.",
        opening="Your medical image analysis and neuroimaging work is the most direct "
                "methodological overlap with our project — you analyze the same data modalities.",
    ),
    dict(
        name="Claudio Silva",
        email="csilva@nyu.edu",
        email_status="ready",
        profile_url="https://engineering.nyu.edu/faculty/claudio-silva",
        focus_label="Scientific visualization, urban computing, biomedical data",
        focus="Co-directs the VIDA Center, working on visualization, geometric computing, "
              "and urban analytics.",
        opening="Your work on visualizing large scientific datasets intersects directly with "
                "our pipeline for visualizing saliency maps over brain volumes.",
    ),
    dict(
        name="Elza Erkip",
        email="elza.erkip@nyu.edu",
        email_status="ready",
        profile_url="https://engineering.nyu.edu/faculty/elza-erkip",
        focus_label="Information theory, coding theory",
        focus="Studies information theory and coding theory at NYU Tandon.",
        opening="Your information theory background and senior Tandon faculty position make "
                "you a strong potential sponsor for our computational research infrastructure needs.",
    ),
    dict(
        name="Sundeep Rangan",
        email="srangan@nyu.edu",
        email_status="ready",
        profile_url="https://engineering.nyu.edu/faculty/sundeep-rangan",
        focus_label="Estimation theory, compressed sensing, signal processing",
        focus="Studies estimation theory, compressed sensing, and signal processing.",
        opening="Your estimation and signal processing expertise is relevant to our MRI "
                "reconstruction and preprocessing pipeline.",
    ),
    dict(
        name="Ludovic Righetti",
        email="righetti@nyu.edu",
        email_status="ready",
        profile_url="https://engineering.nyu.edu/faculty/ludovic-righetti",
        focus_label="Robotics, optimization, CDS joint faculty",
        focus="Works on robotics and optimization methods at Tandon and CDS.",
        opening="Your optimization methods and joint Tandon-CDS affiliation make you a "
                "potential bridge to NYU HPC resources for our project.",
    ),
    dict(
        name="Nasir Memon",
        email="memon@nyu.edu",
        email_status="ready",
        profile_url="https://engineering.nyu.edu/faculty/nasir-memon",
        focus_label="Digital forensics, biometrics, deepfake detection",
        focus="Studies media forensics, biometrics, and authentication including deepfake "
              "detection and co-founding NYU's Center for Cyber Security.",
        opening="Your biometrics and large-scale data processing experience and senior Tandon "
                "position make you a strong candidate to support our Greene access request.",
    ),
    dict(
        name="Torsten Suel",
        email="torsten.suel@nyu.edu",
        email_status="ready",
        profile_url="https://engineering.nyu.edu/faculty/torsten-suel",
        focus_label="Search engines, information retrieval, large-scale systems",
        focus="Studies search engines, scalable information retrieval, data compression, "
              "and web mining.",
        opening="Your large-scale systems expertise and Tandon faculty standing make you a "
                "potential sponsor for our HPC access needs.",
    ),
    dict(
        name="Erdem Varol",
        email="ev2240@nyu.edu",
        email_status="ready",
        profile_url="https://engineering.nyu.edu/faculty/erdem-varol",
        focus_label="NeuroAI, brain connectivity, genomics and computer vision",
        focus="Develops computational tools bridging genomics and neuroimaging; recent work "
              "integrates gene expression with EM connectomes.",
        opening="Your NeuroAI work combining neuroimaging and computation is highly aligned "
                "with our CNN-based brain MRI analysis — you are a natural potential co-sponsor.",
    ),
    dict(
        name="Viviana Acquaviva",
        email="va694@nyu.edu",
        email_status="ready",
        profile_url="https://engineering.nyu.edu/faculty/viviana-acquaviva",
        focus_label="ML for astrophysics, probabilistic ML, scientific ML",
        focus="Works on ML for astrophysics and scientific data at NYU Tandon.",
        opening="Your experience running GPU-heavy scientific ML workloads and your Tandon "
                "affiliation make you a candidate sponsor for our Greene access request.",
    ),
    dict(
        name="Zhong-Ping Jiang",
        email="zpjiang@nyu.edu",
        email_status="ready",
        profile_url="https://engineering.nyu.edu/faculty/zhong-ping-jiang",
        focus_label="Nonlinear control, learning-based control, dynamic systems",
        focus="Studies nonlinear control, learning-based control, and dynamic systems.",
        opening="Your control theory and learning methods work and senior faculty position "
                "at Tandon make you a strong candidate to support our project.",
    ),
    dict(
        name="Quanyan Zhu",
        email="qz494@nyu.edu",
        email_status="ready",
        profile_url="https://engineering.nyu.edu/faculty/quanyan-zhu",
        focus_label="Game theory, control, network security",
        focus="Studies game theory, control theory, and network security.",
        opening="Your interdisciplinary research and Tandon faculty position make you a "
                "potential supporter of our cross-institutional research team.",
    ),
    # ── Courant Math ──────────────────────────────────────────────────────────
    dict(
        name="Georg Stadler",
        email="stadler@nyu.edu",
        email_status="ready",
        profile_url="https://cims.nyu.edu/~stadler/",
        focus_label="Scientific computing, inverse problems, PDE-constrained optimization",
        focus="Develops scientific computing methods for inverse problems and "
              "PDE-constrained optimization.",
        opening="Your inverse problems and scientific computing work maps directly to our "
                "MRI registration and deformable brain atlas pipeline.",
    ),
    dict(
        name="Benjamin Peherstorfer",
        email="pehersto@nyu.edu",
        email_status="ready",
        profile_url="https://cims.nyu.edu/~pehersto/",
        focus_label="Scientific computing, model reduction, neural Galerkin schemes",
        focus="Develops nonlinear model reduction and data-driven methods for scientific "
              "simulation, including neural Galerkin schemes for PDEs.",
        opening="Your experience with large-scale GPU-accelerated scientific ML and your "
                "Courant affiliation make you a potential Greene access sponsor.",
    ),
    dict(
        name="Esteban Tabak",
        email="tabak@nyu.edu",
        email_status="ready",
        profile_url="https://cims.nyu.edu/~tabak/",
        focus_label="Fluid dynamics, probability, transport phenomena",
        focus="Studies fluid dynamics, probability flows, and statistical modeling.",
        opening="Your work on probability flows and statistical modeling is methodologically "
                "relevant to our probabilistic brain age distribution prediction.",
    ),
    dict(
        name="Robert Kohn",
        email="kohn@nyu.edu",
        email_status="ready",
        profile_url="https://cims.nyu.edu/~kohn/",
        focus_label="Applied mathematics, variational methods",
        focus="Studies applied mathematics including variational methods and materials science.",
        opening="Your applied mathematics work and long-standing Courant affiliation make you "
                "a potential bridge to NYU HPC resources for our interdisciplinary project.",
    ),
    dict(
        name="Jonathan Goodman",
        email="goodman@nyu.edu",
        email_status="ready",
        profile_url="https://cims.nyu.edu/~goodman/",
        focus_label="Numerical methods, Monte Carlo, computational science",
        focus="Studies numerical methods, Monte Carlo methods, and computational science.",
        opening="Your numerical methods and scientific computing work and senior Courant "
                "affiliation position you as a strong potential HPC sponsor.",
    ),
    dict(
        name="Gérard Ben Arous",
        email="gba1@nyu.edu",
        email_status="ready",
        profile_url="https://cims.nyu.edu/~benarous/",
        focus_label="Probability, stochastic processes, statistical physics of learning",
        focus="Works on probability, stochastic processes, and the statistical physics of "
              "learning.",
        opening="Your statistical physics of learning work is foundational to understanding "
                "the training dynamics of our deep brain age CNN.",
    ),
    dict(
        name="Fanghua Lin",
        email="linf@nyu.edu",
        email_status="ready",
        profile_url="https://cims.nyu.edu/~linf/",
        focus_label="Partial differential equations, geometric analysis",
        focus="Studies partial differential equations and geometric analysis.",
        opening="Your applied mathematics expertise and Courant affiliation make you well-"
                "positioned to support computation-intensive research at NYU.",
    ),
    # ── Additional CDS / Tandon faculty ───────────────────────────────────────
    dict(
        name="Samuel Bowman",
        email="bowman@nyu.edu",
        email_status="ready",
        profile_url="https://sleepinyourhat.github.io/",
        focus_label="AI safety, LLM evaluation, NLP",
        focus="Studies AI safety, LLM alignment, and evaluation methods.",
        opening="Your ML evaluation methodology work and CDS affiliation make you a potential "
                "sponsor bridging our project to NYU's HPC infrastructure.",
    ),
    dict(
        name="Mengye Ren",
        email="mengye@nyu.edu",
        email_status="ready",
        profile_url="https://mengyeren.com/",
        focus_label="Continual learning, world models, agentic AI",
        focus="Directs the Agentic Learning AI Lab, developing ML systems that continuously "
              "learn and adapt.",
        opening="Your GPU-intensive continual learning workloads and NYU faculty position "
                "make you a potential sponsor for our Greene HPC access request.",
    ),
    dict(
        name="Sumit Chopra",
        email="sumit@nyu.edu",
        email_status="ready",
        profile_url="https://www.spchopra.net/",
        focus_label="ML for medical imaging, MRI triaging, multi-modal learning",
        focus="Develops ML models for healthcare with focus on MRI triaging and "
              "multi-modal medical data.",
        opening="Your work on end-to-end ML pipelines for MRI analysis is a direct "
                "methodological match for our brain age prediction project.",
    ),
    dict(
        name="Matus Telgarsky",
        email="mjt10041@nyu.edu",
        email_status="ready",
        profile_url="https://cims.nyu.edu/~matus/",
        focus_label="Deep learning theory, margins, expressivity, optimization",
        focus="Studies deep learning theory including margin-based analysis, neural network "
              "expressivity, and optimization convergence.",
        opening="Your deep learning theory work on optimization and expressivity and your "
                "Courant/CDS affiliation make you a potential Greene access sponsor.",
    ),
    dict(
        name="Rob Fergus",
        email="fergus@nyu.edu",
        email_status="ready",
        profile_url="http://cs.nyu.edu/~fergus/",
        focus_label="Computer vision, self-supervised learning, deep learning",
        focus="Works on computer vision and self-supervised representation learning.",
        opening="Your self-supervised visual representation learning and your Courant CS "
                "affiliation make you a strong potential sponsor for our GPU cluster access.",
    ),
    dict(
        name="Saining Xie",
        email="saining.xie@nyu.edu",
        email_status="ready",
        profile_url="http://www.sainingxie.com/",
        focus_label="World models, multimodal AI, large-scale vision",
        focus="Builds world models learning from continuous sensory data, including "
              "Solaris and Cambrian-S.",
        opening="Your large-scale vision and world model training experience and NYU "
                "affiliation make you a natural potential Greene access sponsor.",
    ),
    dict(
        name="David Fouhey",
        email="david.fouhey@nyu.edu",
        email_status="ready",
        profile_url="https://cs.nyu.edu/~fouhey/",
        focus_label="3D reconstruction, physical estimation, learning-based CV",
        focus="Develops learning-based CV systems for estimating physical properties from "
              "images in 3D.",
        opening="Your 3D physical estimation from images and Courant CS affiliation make you "
                "a potential sponsor for our GPU-based 3D MRI analysis work.",
    ),
    dict(
        name="Christopher Musco",
        email="cmusco@nyu.edu",
        email_status="ready",
        profile_url="https://www.chrismusco.com/",
        focus_label="Randomized algorithms, scalable ML, numerical linear algebra",
        focus="Studies algorithmic foundations of data science and ML, including randomized "
              "sketching and streaming algorithms.",
        opening="Your scalable ML methods and Tandon/CDS affiliation make you a potential "
                "sponsor for our Greene HPC access request.",
    ),
    dict(
        name="Daniel Neill",
        email="daniel.neill@nyu.edu",
        email_status="ready",
        profile_url="http://www.cs.nyu.edu/~neill",
        focus_label="ML for public health, disease surveillance, algorithmic fairness",
        focus="Develops ML methods for disease surveillance and healthcare analytics.",
        opening="Your ML-for-health focus and Tandon faculty position make you a natural "
                "potential sponsor for our brain health prediction research.",
    ),
]


def main():
    os.makedirs(DRAFTS_DIR, exist_ok=True)
    contacts = load_contacts()

    generated = 0
    needs_lookup = 0

    for prof in PROFESSORS:
        arxiv_id = slug(prof["name"])
        last = prof["name"].split()[-1]

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
            body = BODY_TEMPLATE.format(
                last_name=last,
                opening=prof["opening"],
                email=SENDER["email"],
            )
            fname = safe_filename(prof["name"], arxiv_id)
            path = os.path.join(DRAFTS_DIR, fname)
            with open(path, "w", encoding="utf-8") as f:
                f.write(f"TO: {prof['email']}\nSUBJECT: {SUBJECT}\n\n{body}")
            contact["draft_path"] = os.path.join("drafts", fname)
            contact["status"] = "drafted"
            generated += 1
        else:
            needs_lookup += 1

        contacts = upsert(contacts, contact)

    save_contacts(contacts)
    print(f"Generated {generated} Greene HPC sponsorship drafts in {DRAFTS_DIR}/")
    if needs_lookup:
        print(f"{needs_lookup} professors still need email lookup.")
    print(f"Total professors: {len(PROFESSORS)}")
    print(f"\nNext steps:")
    print(f"  python review_drafts.py   # approve / skip each draft interactively")
    print(f"  python gmail_client.py    # send approved drafts")


if __name__ == "__main__":
    main()
