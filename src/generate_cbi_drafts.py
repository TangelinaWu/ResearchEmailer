"""One-off: generate custom outreach drafts for NYU Center for Brain Imaging PIs.

Unlike build_contacts.py/draft_generator.py (arXiv-sourced, templated hook), these
contacts come from https://as.nyu.edu/research-centers/cbi/about/PI.html and each
opening paragraph was individually researched and hand-written, not templated.
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

Thank you for your time and for the work you're doing. I really enjoyed learning about your research.

Best,
Angelina Wu
{linkedin} | {github}
"""

PIS = [
    dict(
        name="Babak Ardekani",
        email="Babak.Ardekani@nyulangone.org",
        email_status="ready",
        profile_url="https://med.nyu.edu/faculty/babak-a-ardekani",
        focus_label="MRI registration methods & Alzheimer's detection (Ardekani Lab, NKI/NYU Langone)",
        focus="Develops computational methods for MRI/tomographic brain image analysis, including image "
        "registration algorithms and machine-learning approaches to brain morphometry, applied to early "
        "detection of Alzheimer's disease.",
        opening="I've been reading about your work on longitudinal MRI registration methods at the Center "
        "for Biomedical Imaging and Neuromodulation. Designing registration algorithms specifically to "
        "reduce bias when tracking brain changes over time, in service of catching Alzheimer's disease "
        "earlier, struck me as a really elegant application of computational methods to a hard clinical problem.",
    ),
    dict(
        name="Esti Blanco-Elorrieta",
        email="eb134@nyu.edu",
        email_status="ready",
        profile_url="https://estiblancoelorrieta.github.io/",
        focus_label="Neurobiology of bilingualism (Blanco-Elorrieta Lab)",
        focus="Studies the neurobiology of bilingualism/multilingualism using MEG, computational modeling, "
        "and behavioral methods, with a focus on understudied multilingual populations including signers.",
        opening="I recently read about your MEG study showing that Spanish-English bilinguals rely on a "
        "single shared neural \"grammar engine\" to conjugate and transform words in both languages, rather "
        "than separate circuits per language. That's a compelling challenge to the more intuitive assumption "
        "that bilingual brains keep languages neurally separate, and it's exactly the kind of question about "
        "language and cognition that drew me to your lab's work.",
    ),
    dict(
        name="Adam Buchwald",
        email="buchwald@nyu.edu",
        email_status="ready",
        profile_url="https://wp.nyu.edu/buchwaldlab/",
        focus_label="Aphasia, speech rehabilitation & neuromodulation (Buchwald Lab)",
        focus="Studies the cognitive/neural mechanisms of speech and language production and how they break "
        "down after stroke, pairing transcranial direct current stimulation (tDCS) with speech-language "
        "therapy to improve rehabilitation outcomes.",
        opening="I came across your lab's NIH-funded clinical trial pairing transcranial direct current "
        "stimulation with speech-language therapy for post-stroke apraxia and aphasia, including the finding "
        "that treatment gains paired with tDCS appear more durable months after therapy ends than therapy "
        "alone. That's a great example of neuromodulation research translating into something that could "
        "meaningfully change rehabilitation outcomes.",
    ),
    dict(
        name="Marisa Carrasco",
        email="marisa.carrasco@nyu.edu",
        email_status="ready",
        profile_url="https://wp.nyu.edu/carrascolab/",
        focus_label="Visual attention & perception (Carrasco Lab)",
        focus="Studies how covert visual attention alters perception and appearance, using psychophysics, "
        "fMRI, EEG, MEG, TMS, and computational modeling, including how perception varies around the visual field.",
        opening="I've been reading your lab's recent work (with Hsing-Hao Lee) showing that covert spatial "
        "attention boosts performance uniformly across the cardinal meridians, even though visual adaptation "
        "itself is stronger along the horizontal than the vertical meridian. That's a clean dissociation between "
        "what attention does and what adaptation does. It made me want to learn more about how your lab "
        "designs psychophysics experiments to tease apart effects like these.",
    ),
    dict(
        name="Clayton Curtis",
        email="cc99@nyu.edu",
        email_status="ready",
        profile_url="https://www.clayspacelab.com/",
        focus_label="Spatial cognition & visual working memory (ClaySpace Lab)",
        focus="Studies the neural mechanisms of spatial cognition, visual working memory, attention, and "
        "motor planning, combining fMRI, TMS, MEG, iEEG, and computational modeling.",
        opening="I read your lab's recent paper using TMS to disrupt a specific lateral prefrontal region "
        "and show that this impairs the brain's ability to prioritize which item in working memory gets "
        "protected. That moves beyond correlational fMRI to actual causal evidence for a working-memory control "
        "mechanism. That's exactly the kind of question about spatial cognition and memory I'd love to help investigate.",
    ),
    dict(
        name="Adriana Di Martino",
        email="",
        email_status="needs_lookup",
        profile_url="https://childmind.org/bio/adriana-di-martino-md/",
        focus_label="Autism neuroimaging & ABIDE consortium (Di Martino, NYU Langone Child Study Center)",
        focus="Studies the neurobiology of autism spectrum disorder using brain imaging combined with "
        "clinical and cognitive measures; founded and directs ABIDE (Autism Brain Imaging Data Exchange), a "
        "large multi-site data-sharing consortium.",
        opening="I came across your October paper in Molecular Psychiatry showing that in children with "
        "autism and/or ADHD, more severe autism symptoms, regardless of diagnostic category, tracked with "
        "increased frontoparietal-default-mode network connectivity, overlapping with specific "
        "gene-expression patterns. I found that dimensional, symptom-based approach really compelling, and "
        "I'd love to learn more about the work your lab and the ABIDE consortium are doing.",
    ),
    dict(
        name="Paul Glimcher",
        email="paul.glimcher@nyu.edu",
        email_status="ready",
        profile_url="https://www.neuroeconomicslab.org/",
        focus_label="Neuroeconomics & computational psychiatry (Glimcher Lab / Institute for the Study of Decision Making)",
        focus="Models human and animal choice by combining experimental economics, brain imaging, "
        "single-neuron recording, and computational/neural random utility theory, with growing focus on "
        "decision-making dysfunction in psychiatric disorders.",
        opening="I've been reading about your lab's recent work identifying \"decisional reference point "
        "pathology\" as a specific cognitive mechanism linked to major depressive disorder. That's a great example "
        "of extending neuroeconomic choice theory into computational psychiatry, and exactly the kind of "
        "quantitative modeling of decision-making that drew me to your work.",
    ),
    dict(
        name="Catherine Hartley",
        email="cate@nyu.edu",
        email_status="ready",
        profile_url="https://www.hartleylab.org/",
        focus_label="Developmental cognitive neuroscience of learning & memory (Hartley Lab)",
        focus="Studies how learning, memory, and decision-making develop from childhood through adulthood, "
        "using behavioral, computational, and neuroimaging methods.",
        opening="I read your recent Nature Communications paper with Nussenbaum showing that reinforcement "
        "learning becomes increasingly tied to episodic memory specificity as children develop into adults. "
        "That's a great example of two separate learning systems becoming more tightly coupled over development, "
        "and the kind of developmental question about learning and memory I'd love to help study.",
    ),
    dict(
        name="Danique Jeurissen",
        email="d.jeurissen@nyu.edu",
        email_status="ready",
        profile_url="https://www.jeurissenlab.com/",
        focus_label="Recovery of decision-making circuits after cortical inactivation (Jeurissen Lab)",
        focus="Combines causal cortical inactivation with electrophysiology and behavioral tasks to trace "
        "how decision-making circuits reroute information after a cortical area is disrupted, aiming to "
        "explain recovery after damage like stroke.",
        opening="I came across your lab's work building on the Neuron paper on neural mechanisms for "
        "terminating decisions, and understand your new lab is now using causal cortical inactivation "
        "alongside electrophysiology to trace how decision-making circuits reroute after a cortical area is "
        "disrupted. Congratulations on the Sloan Research Fellowship. I'd love to learn more about a "
        "project this early-stage and hands-on.",
    ),
    dict(
        name="Roozbeh Kiani",
        email="roozbeh@nyu.edu",
        email_status="ready",
        profile_url="https://www.cns.nyu.edu/kianilab/Home.html",
        focus_label="Perceptual & mnemonic decision-making (Kiani Lab)",
        focus="Studies how the brain integrates sensory evidence to form decisions and generate confidence "
        "estimates, using multi-electrode/Neuropixels recording, fMRI, and neural perturbation.",
        opening="I read about your lab's recent work using Neuropixels recordings in area LIP to show that "
        "population activity encodes a confidence signal predicting choice accuracy before a decision is even "
        "made. That's a compelling look at how the brain represents its own uncertainty, and exactly the kind of "
        "large-scale neural recording and analysis work I'd love to contribute to.",
    ),
    dict(
        name="Eric Knowles",
        email="eric.knowles@nyu.edu",
        email_status="ready",
        profile_url="https://wp.nyu.edu/knowleslab/",
        focus_label="Political psychology of race, class & inequality (Politics and Intergroup Relations Lab)",
        focus="Studies how race, gender, and social class shape political judgment, including how advantaged "
        "groups manage threats to their status and beliefs about economic inequality.",
        opening="I came across your 2025 paper in Communications Psychology using latent profile analysis on "
        "a large representative sample to identify five distinct strategies (defend, deny, distance, "
        "dismantle, and flexible) that advantaged-group members use to manage threats to their racial "
        "identity. That's a rigorous, data-driven way to study something usually discussed only "
        "qualitatively, and it's the kind of quantitative social psychology work I'd love to learn more about.",
    ),
    dict(
        name="Michael Landy",
        email="landy@nyu.edu",
        email_status="ready",
        profile_url="https://wp.nyu.edu/landylab/",
        focus_label="Multisensory perception & sensorimotor integration (Landy Lab)",
        focus="Studies human visual and multisensory perception and the visual guidance of action, combining "
        "psychophysics with fMRI to understand how the brain integrates cues across sensory modalities.",
        opening="I read about your lab's recent work on \"sensory-motor confidence,\" showing that people are "
        "systematically overconfident about the precision of their own sensory estimates during multisensory "
        "cue combination. That's a great example of psychophysics revealing biases we're not aware we have, and "
        "I'd love to learn more about how your lab studies perception and the visual guidance of action.",
    ),
    dict(
        name="Marcelo Mattar",
        email="marcelo.mattar@nyu.edu",
        email_status="ready",
        profile_url="https://www.mattarlab.com/about",
        focus_label="Computational cognition: planning, memory & RL (Mattar Lab)",
        focus="Studies the computations underlying learning, memory, and planning, spanning model-based "
        "reinforcement learning, hippocampal replay, and recurrent neural networks as interpretable models "
        "of decision strategies.",
        opening="I've been reading your lab's recent papers using small recurrent neural networks trained on "
        "decision-making tasks to reverse-engineer the actual algorithms animals and humans use for planning, "
        "including the Nature Neuroscience paper linking this to hippocampal replay. As someone who's spent "
        "a lot of time building and evaluating ML models, I found the idea of using RNNs as interpretable "
        "models of cognition, rather than just black boxes, really compelling.",
    ),
    dict(
        name="Sebastian Michelmann",
        email="s.michelmann@nyu.edu",
        email_status="ready",
        profile_url="https://as.nyu.edu/faculty/sebastian-michelmann.html",
        focus_label="Naturalistic memory & neural data analysis (Michelmann Lab)",
        focus="Studies how continuous, real-world experience is neurally encoded and retrieved as episodic "
        "memory, using EEG/MEG/intracranial recordings combined with computational modeling.",
        opening="I read your recent Trends in Cognitive Sciences paper proposing to give large language "
        "models human-like, event-segmented episodic memory, building on your earlier finding that event "
        "boundaries act as \"access points\" for memory retrieval. Given my own background working with LLMs "
        "and data pipelines, I found the bridge you're drawing between naturalistic memory research and LLM "
        "architecture especially compelling.",
    ),
    dict(
        name="Tony Movshon",
        email="movshon@nyu.edu",
        email_status="ready",
        profile_url="https://www.cns.nyu.edu/~vnl/",
        focus_label="Visual cortex neurophysiology (Movshon Lab / Center for Neural Science)",
        focus="Studies how primate visual cortex processes motion, form, texture, and color, using "
        "single-neuron electrophysiology, psychophysics, and computational modeling in behaving macaques.",
        opening="I came across your lab's 2024 Journal of Neuroscience paper showing that V2 neurons' "
        "sensitivity to naturalistic texture statistics tracks behavioral discrimination performance more "
        "closely than V1 does. That's a great example of linking single-neuron population responses directly to "
        "perceptual judgments, and exactly the kind of visual neuroscience question that drew me to your work.",
    ),
    dict(
        name="Candace Raio",
        email="candace.raio@nyulangone.org",
        email_status="ready",
        profile_url="https://www.raiolab.org/",
        focus_label="Stress & affective neuroscience of decision-making (Raio Lab, NYU Grossman)",
        focus="Studies how stress reshapes the cognitive, neural, and computational mechanisms underlying "
        "decision-making, using neuroimaging, psychophysiology, and computational modeling.",
        opening="I read your work linking cumulative lifetime stress exposure (measured with the STRAIN) to "
        "a specific economic decision-making bias, ambiguity aversion, and thought it was a really clean "
        "example of connecting a validated stress-exposure measure to a concrete computational account of "
        "choice under uncertainty. It's the kind of quantitative approach to stress and decision-making I'd "
        "love to help with.",
    ),
    dict(
        name="Pablo Ripollés",
        email="pripolles@nyu.edu",
        email_status="ready",
        profile_url="https://www.ripolleslab.com/",
        focus_label="Music, reward & learning (Ripollés Lab)",
        focus="Studies how music-related reward and dopaminergic signaling shape learning, memory, and "
        "emotion, spanning language learning, auditory-motor synchronization, and music-based stroke rehabilitation.",
        opening="I came across your lab's finding that vocal music listening can enhance language network "
        "reorganization during stroke recovery, tying your broader work on music-related reward and "
        "dopaminergic signaling directly to a clinical rehabilitation outcome. That's a striking bridge "
        "between reward/learning neuroscience and applied recovery, and I'd love to learn more about the "
        "work happening in your lab.",
    ),
    dict(
        name="Bas Rokers",
        email="rokers@nyu.edu",
        email_status="ready",
        profile_url="https://sites.nyuad.nyu.edu/rokersvisionlaboratory/",
        focus_label="3D vision & motion perception (Rokers Vision Lab)",
        focus="Studies the neural basis of motion and depth perception — how the brain transforms 2D "
        "retinal motion signals into 3D representations of object motion — using psychophysics, fMRI, and "
        "Bayesian computational modeling.",
        opening="I read about your lab's work showing that human visual area MT+ encodes two distinct "
        "binocular cues to 3D motion through separate computational mechanisms, with eye-of-origin "
        "information preserved into later stages of motion processing. That's a compelling look at how the "
        "brain reconstructs 3D structure from 2D retinal signals, and exactly the kind of computational "
        "vision question I'd love to help investigate.",
    ),
    dict(
        name="Jonathan Winawer",
        email="jonathan.winawer@nyu.edu",
        email_status="ready",
        profile_url="https://wp.nyu.edu/winawerlab/",
        focus_label="Visual neuroscience & fMRI/ECoG methods (Winawer Lab)",
        focus="Studies the neural computations underlying human visual perception, linking activity in "
        "visual cortex to fMRI, EEG, MEG, and intracranial EEG signals.",
        opening="I came across your lab's 2025 Scientific Data paper releasing an open, multi-center "
        "intracranial EEG dataset, built with NYU Langone epilepsy patients, for studying conscious visual "
        "perception. That's a great example of building shared infrastructure for a whole research "
        "community, and given my own background in data pipelines, it's exactly the kind of large-scale "
        "neuroimaging dataset work I'd love to contribute to.",
    ),
]


def slug(name):
    return "cbi-" + re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def main():
    os.makedirs(DRAFTS_DIR, exist_ok=True)
    contacts = load_contacts()

    generated = 0
    for pi in PIS:
        arxiv_id = slug(pi["name"])
        contact = {
            "name": pi["name"],
            "email": pi["email"],
            "email_source": "faculty_page" if pi["email"] else "",
            "affiliation": "NYU (Center for Brain Imaging)",
            "region": "nyc_tristate",
            "us_verified": "yes",
            "paper_title": pi["focus_label"],
            "arxiv_id": arxiv_id,
            "paper_url": pi["profile_url"],
            "abstract": pi["focus"],
            "status": pi["email_status"],
            "draft_path": "",
        }

        if pi["email_status"] == "ready" and pi["email"]:
            subject = "Undergrad Researcher Interested in Your Work"
            body = BODY_TEMPLATE.format(
                first_name=first_name(pi["name"]),
                opening=pi["opening"],
                position_ask=position_ask_for_region(contact["region"]),
                linkedin=SENDER["linkedin"],
                github=SENDER["github"],
            )
            fname = safe_filename(pi["name"], arxiv_id)
            path = os.path.join(DRAFTS_DIR, fname)
            with open(path, "w", encoding="utf-8") as f:
                f.write(f"TO: {pi['email']}\nSUBJECT: {subject}\n\n{body}")
            contact["draft_path"] = os.path.join("drafts", fname)
            contact["status"] = "drafted"
            generated += 1

        contacts = upsert(contacts, contact)

    save_contacts(contacts)
    print(f"Generated {generated} custom CBI drafts in {DRAFTS_DIR}/")
    print(f"{len(PIS) - generated} still need manual email verification before a draft can be written.")


if __name__ == "__main__":
    main()
