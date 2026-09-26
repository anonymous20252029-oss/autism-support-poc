# An Integrated Digital Platform for Autism Spectrum Disorder Inclusion in Mainstream Schools (Digital Inclusion Platform for ASD)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://autism-support-poc-brorrc4ear763c2wwdsqid.streamlit.app/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Live Web Application:** [https://autism-support-poc-brorrc4ear763c2wwdsqid.streamlit.app/](https://autism-support-poc-brorrc4ear763c2wwdsqid.streamlit.app/)

A Proof-of-Concept (PoC) research software system designed to operationalize early identification, collaborative individualized education plan (IEP) management, and longitudinal intervention tracking for students with Autism Spectrum Disorder (ASD) within inclusive mainstream school settings.

---

## 🌟 Key Features & Visualizations

The demo platform provides comprehensive visualization of the intervention workflow and institutional role governance:

* **Role-Based Access Control (RBAC System):** Simulates four distinct authenticated user roles aligned with Circular 11/2024/TT-BGDĐT and Circular 21/2023/TT-BGDĐT (Homeroom Teacher, School Counselor/Case Coordinator, Special Education Support Personnel, and Parent).
* **Integration Triangle & RACI Responsibility Matrix:** Visualizes the closed-loop collaborative process among stakeholders with the neurodivergent student at the center.
* **Visual Student Profile Card:** Clearly separates individual strengths, special interests, and sensory triggers for targeted classroom accommodations.
* **Classroom Visual Support Toolbox:** Provides interactive simulations of visual schedules, transition countdown timers, and token economy behavioral reward boards.
* **Time-Series Behavioral Autonomy Tracking:** Renders multi-target weekly progress curves evaluating student independence levels against an autonomy benchmark threshold ($s \ge 4.0$).
* **Transition Readiness Radar Chart:** Assesses five core developmental competencies (Sensory Regulation, Communication, Peer Social Reciprocity, Task Independence, and Rule Compliance) across pre- and post-intervention phases.
* **Digital Inclusion Passport:** Generates an actionable transition dossier for incoming educators, specifying essential pedagogical *DOs* and environmental *DON'Ts* to prevent transition anxiety and behavioral regressions.

---

## 👥 Research Team & Scientific Credits

* **Technical Design & Implementation:**
  * **Lead Technical Investigator:** MSc. Vo Thi Kim Anh
  * Lecturer, Faculty of Information Technology, Ton Duc Thang University (TDTU), Ho Chi Minh City, Vietnam.
  * Ph.D. Candidate, Faculty of Electrical Engineering and Computer Science (FEI), VSB – Technical University of Ostrava, Czech Republic.
* **Theoretical Framework Foundation:**
  * Grounded in the integrated educational inclusion framework conceptualized by **Assoc. Prof. Dr. Nguyen Van Tuong** (University of Social Sciences and Humanities, VNU-HCM) and **Dr. Le Thi Thanh Huyen** (Ho Chi Minh City University of Education).

---

## 📌 Theoretical Grounding & Regulatory Framework

The digital architecture operationalizes an integrated school inclusion model aligned with national statutory regulations and international clinical standards:
* **Circular No. 11/2024/TT-BGDĐT (MOET Vietnam):** Defines the professional position and responsibilities of School Counselors (Case Coordination & Intake Management).
* **Circular No. 21/2023/TT-BGDĐT (MOET Vietnam):** Defines the professional position and duties of Special Education Support Personnel (Classroom Technical Support & Specialized Accommodations).
* **NICE Guidelines (CG128 & CG170) & NHS England:** Establishes non-diagnostic screening boundaries, continuous multidisciplinary assessment, and evidence-based school interventions.

---

## 🔄 The Continuous 6-Step Workflow Pipeline

1. **Step 1: Intake & Structured Risk Screening:** Systematic recording of observable classroom behavioral red flags (strictly non-diagnostic; does not replace clinical evaluations).
2. **Step 2: Multisource Collaborative Assessment:** Synthesizes observations from school, home, and clinical reports to determine functional barriers and student strengths.
3. **Step 3: Digital IEP Formulation:** Formulates measurable SMART objectives, assigns institutional responsibilities, and specifies classroom adaptations.
4. **Step 4: Classroom Support & Visual Aids:** Deploys structured visual schedules, countdown visual timers, and augmentative and alternative communication (AAC/PECS) aids.
5. **Step 5: Longitudinal Progress Tracking:** Systematically logs behavioral autonomy trajectories across academic terms via time-series interactive analytics.
6. **Step 6: Review & Transition Passport:** Preserves cumulative accommodation histories and issues a transition passport ensuring continuity across academic years and school transfers.

---

## 📊 Benchmark Synthetic Cohorts

The database comes pre-seeded with six standardized pediatric personas ($HS-01$ to $HS-06$) modeling common elementary-level challenges, including auditory hypersensitivity, unstructured recess isolation, and secondary school transition anxiety.

---

## 🛠 Technical Architecture & Stack

* **Frontend / User Interface:** `Streamlit` (Python reactive web framework).
* **Data Visualization:** `Plotly Express` & `Plotly Graph Objects` (Interactive time-series and polar radar charts).
* **Data Persistence:** Relational `SQLite` (ACID-compliant relational schema structured for seamless migration to `PostgreSQL / Supabase`).
* **Data Processing:** `Pandas` and `NumPy`.
* **Decision-Support Validation:** Supervised machine learning models evaluated on the real-world UCI Pediatric ASD Screening benchmark dataset (ID: 419).

---

## 🚀 Installation & Local Deployment Guide

```bash
# 1. Clone the repository
git clone [https://github.com/anonymous20252029-oss/autism-support-poc.git](https://github.com/anonymous20252029-oss/autism-support-poc.git)
cd autism-support-poc

# 2. Install required dependencies
pip install -r requirements.txt

# 3. Launch the Streamlit application
streamlit run app.py
