"""
EduNova.AI General Knowledge Base (Non-CS)
===========================================
Contains comprehensive academic content for Non-CS subjects like Mechanical, Physics, Math, Chemistry, MBA, and Pharmacy.
"""

GENERAL_KNOWLEDGE = {
    'thermodynamics': {
        'title': 'Laws of Thermodynamics',
        'definition': 'Thermodynamics is the branch of physics that deals with the relationships between heat, work, temperature, and energy. The laws of thermodynamics describe how these quantities behave under various circumstances.',
        'key_concepts': [
            'Zeroth Law - Thermal Equilibrium and Temperature measurement',
            'First Law - Conservation of Energy ($dU = dQ - dW$)',
            'Second Law - Entropy increase and Heat Engine efficiency limits',
            'Third Law - Absolute zero entropy ($S \\rightarrow 0$ as $T \\rightarrow 0$)',
            'Carnot Cycle and Heat Engines'
        ],
        'detailed_notes': """
Thermodynamics is governed by four fundamental laws:

### 1. Zeroth Law of Thermodynamics:
If two thermodynamic systems are each in thermal equilibrium with a third system, then they are in thermal equilibrium with each other. This law defines temperature and justifies the use of thermometers.

### 2. First Law of Thermodynamics:
Energy can neither be created nor destroyed, but only transformed from one form to another. Mathematically:
$$dQ = dU + dW$$
where $dQ$ is heat added, $dU$ is change in internal energy, and $dW$ is work done by the system.

### 3. Second Law of Thermodynamics:
Heat cannot spontaneously flow from a colder body to a warmer body (Clausius statement), and it is impossible to construct a heat engine operating in a cycle that converts all heat absorbed from a reservoir into work (Kelvin-Planck statement). This law introduces the concept of **Entropy (S)**, stating that the total entropy of an isolated system always increases over time:
$$dS \\ge \\frac{dQ}{T}$$

### 4. Third Law of Thermodynamics:
As the temperature of a system approaches absolute zero ($0\\text{ K}$), the entropy of a pure crystalline substance approaches a constant minimum value (usually zero).
""",
        'exam_tips': 'For Maharashtra university exams, always state both the Kelvin-Planck and Clausius statements when explaining the Second Law, and show that they are equivalent through a heat pump and engine combination diagram.',
        'formulas': [
            'First Law: dQ = dU + dW',
            'Entropy: dS = dQ_rev / T',
            'Carnot Efficiency: \\eta = 1 - T_C / T_H'
        ],
        'questions': [
            {
                'q': 'State and explain the First and Second Laws of Thermodynamics.',
                'a': 'The First Law is the conservation of energy (dQ = dU + dW). The Second Law states that entropy increases (dS >= 0) and establishes limits on efficiency, meaning heat cannot be converted fully into work.',
                'marks': 10,
                'type': 'descriptive'
            },
            {
                'q': 'What is the maximum theoretical efficiency of a heat engine operating between 600K and 300K?',
                'a': '50%. Using Carnot formula: Efficiency = 1 - (TC / TH) = 1 - (300 / 600) = 1 - 0.5 = 50%.',
                'options': ['25%', '50%', '75%', '100%'],
                'type': 'mcq'
            }
        ]
    },
    'applied mathematics': {
        'title': 'Applied Calculus & Matrices',
        'definition': 'Applied mathematics involves the application of mathematical methods by different fields such as engineering, science, and business. Major pillars include differential calculus, linear algebra, and transforms.',
        'key_concepts': [
            'Eigenvalues and Eigenvectors of Matrices',
            'Cayley-Hamilton Theorem and applications',
            'Laplace and Fourier Transforms',
            'Taylor and Maclaurin Series expansion',
            'Multiple Integrals (Double and Triple integrals)'
        ],
        'detailed_notes': """
### 1. Eigenvalues and Eigenvectors:
For a square matrix $A$ of order $n$, a non-zero vector $X$ is called an eigenvector if there exists a scalar $\\lambda$ such that:
$$AX = \\lambda X$$
The scalar $\\lambda$ is called an eigenvalue. They are found by solving the characteristic equation:
$$\\det(A - \\lambda I) = 0$$

### 2. Cayley-Hamilton Theorem:
Every square matrix satisfies its own characteristic equation. If the characteristic equation is $\\lambda^n + a_1\\lambda^{n-1} + ... + a_n = 0$, then:
$$A^n + a_1 A^{n-1} + ... + a_n I = O$$
This theorem is extremely useful for calculating the inverse ($A^{-1}$) and higher powers of a matrix.

### 3. Laplace Transform:
The Laplace transform of a function $f(t)$ is defined as:
$$\\mathcal{L}\\{f(t)\\} = F(s) = \\int_{0}^{\\infty} e^{-st} f(t) dt$$
It converts differential equations in the time domain into algebraic equations in the $s$-domain, simplifying solving process.
""",
        'exam_tips': 'When proving Cayley-Hamilton theorem, write out the characteristic polynomial clearly, substitute matrix A, compute matrix multiplications step-by-step, and always state how A^-1 is computed using the expression.',
        'formulas': [
            'Characteristic Equation: |A - \\lambda I| = 0',
            'Laplace: L{e^(at)} = 1 / (s - a)',
            'Inverse Matrix: A^-1 = -1/a_n (A^(n-1) + a_1 A^(n-2) + ... + a_(n-1) I)'
        ],
        'questions': [
            {
                'q': 'State the Cayley-Hamilton Theorem and explain how it can be used to find the inverse of a matrix.',
                'a': 'Cayley-Hamilton theorem states that a matrix satisfies its characteristic equation. By replacing lambda with A, we get a polynomial equation. Multiplying the entire polynomial by A^-1 allows isolating A^-1 on one side, yielding an expression in terms of powers of A.',
                'marks': 8,
                'type': 'descriptive'
            },
            {
                'q': 'What is the Laplace transform of the function f(t) = e^(3t)?',
                'a': '1 / (s - 3). By definition, L{e^(at)} = 1 / (s - a). Here a = 3, so L{e^(3t)} = 1 / (s - 3).',
                'options': ['1/s', '1/(s+3)', '1/(s-3)', '3/s'],
                'type': 'mcq'
            }
        ]
    },
    'semiconductors': {
        'title': 'Semiconductor Physics',
        'definition': 'Semiconductors are materials with electrical conductivity values between that of a conductor, like copper, and an insulator, like glass. Their conductivity can be altered by temperature or doping.',
        'key_concepts': [
            'Energy Band Theory (Valence, Conduction, Band Gap)',
            'Intrinsic vs Extrinsic Semiconductors',
            'Doping (N-type vs P-type)',
            'PN Junction Diode operation and V-I characteristics',
            'Hall Effect and its applications'
        ],
        'detailed_notes': """
Semiconductors form the backbone of modern solid-state electronics.

### 1. Energy Band Structure:
* **Valence Band (VB)**: Lower energy level, containing valence electrons.
* **Conduction Band (CB)**: Higher energy level, where electrons can move freely.
* **Forbidden Band Gap (Eg)**: Energy difference between VB and CB. In semiconductors, $E_g \\approx 1\\text{ eV}$ (e.g., $1.1\\text{ eV}$ for Silicon, $0.7\\text{ eV}$ for Germanium).

### 2. Doping:
Adding impurity atoms to intrinsic (pure) semiconductors to increase carrier concentration:
* **N-type (Pentavalent impurities)**: Doped with elements like Phosphorus (P) or Arsenic (As). Introduces extra free electrons. Fermi level shifts towards the Conduction Band.
* **P-type (Trivalent impurities)**: Doped with elements like Boron (B) or Indium (In). Introduces "holes" (absence of electrons). Fermi level shifts towards the Valence Band.

### 3. PN Junction Diode:
When a P-type and N-type semiconductor are joined, a **depletion region** is formed due to carrier diffusion.
* **Forward Bias**: P-terminal to positive, N-terminal to negative. Depletion region narrows, leading to current flow.
* **Reverse Bias**: P-terminal to negative, N-terminal to positive. Depletion region widens, stopping current flow.
""",
        'exam_tips': 'Always draw the band diagram showing Valence Band, Conduction Band, and Fermi Energy Level ($E_f$) for Intrinsic, N-type, and P-type semiconductors. Label the bandgap energy clearly.',
        'formulas': [
            'Diode Current Equation: I = I_0 * (e^(V / (\\eta V_T)) - 1)',
            'Hall Coefficient: R_H = 1 / (n * e)'
        ],
        'questions': [
            {
                'q': 'Explain the formation and working of a PN junction diode under forward and reverse bias.',
                'a': 'Under forward bias, the external field opposes the internal barrier potential, reducing the depletion width, allowing majority carriers to cross the junction (exponential current). Under reverse bias, the field strengthens the barrier, widening the depletion region, blocking majority carriers (only tiny leakage current flows).',
                'marks': 10,
                'type': 'descriptive'
            },
            {
                'q': 'What is the value of the energy band gap for pure Silicon at room temperature?',
                'a': '1.1 eV. Germanium is 0.7 eV, while insulators are typically greater than 5 eV.',
                'options': ['0.1 eV', '0.7 eV', '1.1 eV', '5.0 eV'],
                'type': 'mcq'
            }
        ]
    },
    'organic chemistry': {
        'title': 'Organic Reactions and Mechanisms',
        'definition': 'Organic chemistry is the scientific study of the structure, properties, composition, reactions, and preparation of carbon-containing compounds. Reaction mechanisms trace the step-by-step movement of electrons.',
        'key_concepts': [
            'Nucleophilic Substitution reactions (SN1 vs SN2)',
            'Electrophilic Aromatic Substitution (nitration, sulfonation)',
            'Inductive and Resonance effects',
            'Markovnikov and Anti-Markovnikov addition rules',
            'Common Named Reactions (Aldol, Cannizzaro, Grignard)'
        ],
        'detailed_notes': """
### 1. SN1 vs SN2 Mechanisms:
These are the two primary mechanisms for nucleophilic substitution at a saturated carbon:

* **SN1 (Substitution Nucleophilic Unimolecular)**:
  * Two-step mechanism. First step is the slow, rate-determining loss of leaving group to form a **carbocation intermediate**. Second step is the fast attack of nucleophile.
  * Kinetics: $\\text{Rate} = k[\\text{Substrate}]$.
  * Favored by tertiary substrates, polar protic solvents, and weak nucleophiles. Leads to **racemization** (mixture of enantiomers).

* **SN2 (Substitution Nucleophilic Bimolecular)**:
  * One-step, concerted mechanism. Nucleophile attacks from the backside while the leaving group leaves simultaneously, passing through a **pentacoordinate transition state**.
  * Kinetics: $\\text{Rate} = k[\\text{Substrate}][\\text{Nucleophile}]$.
  * Favored by primary substrates, polar aprotic solvents, and strong nucleophiles. Leads to **inversion of configuration** (Walden inversion).
""",
        'exam_tips': 'In university chemistry exams, SN1 vs SN2 comparison is highly recurring. Draw the step-by-step transition states showing partial bonds, and clearly explain why tertiary carbocations are stable (hyperconjugation and +I effect).',
        'formulas': [
            'SN1 Rate = k[Substrate]',
            'SN2 Rate = k[Substrate][Nucleophile]'
        ],
        'questions': [
            {
                'q': 'Compare SN1 and SN2 reaction mechanisms with energy profile diagrams.',
                'a': 'SN1 is a two-step mechanism with a carbocation intermediate (two transition states in energy profile). SN2 is a one-step concerted mechanism with no intermediate (single transition state barrier). SN1 rate depends on substrate only; SN2 depends on both substrate and nucleophile. SN1 results in racemization; SN2 results in Walden inversion.',
                'marks': 10,
                'type': 'descriptive'
            },
            {
                'q': 'Which reaction mechanism involves Walden inversion?',
                'a': 'SN2. Because the nucleophile attacks from the exact opposite side of the leaving group, the spatial configuration of the molecule is inverted.',
                'options': ['SN1', 'SN2', 'E1', 'E2'],
                'type': 'mcq'
            }
        ]
    },
    'marketing management': {
        'title': 'The 4 Ps of Marketing',
        'definition': 'Marketing management is the practical application, design, and execution of marketing techniques and resources within businesses. The 4 Ps represent the fundamental mix variables controlled by marketing managers.',
        'key_concepts': [
            'Marketing Mix: Product, Price, Place, Promotion',
            'STP Framework (Segmentation, Targeting, Positioning)',
            'Product Life Cycle (Introduction, Growth, Maturity, Decline)',
            'Brand Equity and Consumer Behavior',
            'Digital Marketing channels and SEO'
        ],
        'detailed_notes': """
The **Marketing Mix** is a foundational model used to formulate marketing strategies, consisting of the **4 Ps**:

1. **Product**:
   * The good or service being offered to satisfy consumer needs.
   * Decisions include branding, design, quality, packaging, features, and product lines.

2. **Price**:
   * The amount a customer pays for the product.
   * Strategies include penetration pricing (low initial price), skimming (high initial price), value-based pricing, and psychological pricing.

3. **Place**:
   * The channels and locations through which the product is distributed.
   * Decides inventory levels, transport modes, retail outlets, and distribution intermediaries (wholesalers, agents).

4. **Promotion**:
   * The communication activities used to make product benefits known to customers.
   * Elements include advertising, sales promotion, public relations, personal selling, and digital/direct marketing.

### STP Framework:
* **Segmentation**: Dividing the heterogeneous market into distinct, homogeneous groups of consumers.
* **Targeting**: Selecting which segments are the most attractive to pursue.
* **Positioning**: Designing the brand image and value proposition to occupy a clear, distinct place in target minds.
""",
        'exam_tips': 'For business management answers, always include a diagram of the Product Life Cycle (PLC) showing Sales and Profits curves across the four stages, and explain marketing mix adjustments for each stage.',
        'formulas': [
            'Value = Perceived Benefits / Cost',
            'ROI = (Sales Growth - Marketing Investment) / Marketing Investment'
        ],
        'questions': [
            {
                'q': 'Explain the 4 Ps of the Marketing Mix in detail with real-world examples.',
                'a': 'The 4 Ps are: Product (e.g., Apple iPhone, emphasizing premium design), Price (skimming strategy for iPhones), Place (Apple stores and authorized retailers), and Promotion (premium TV advertisements and keynotes). Adjusting these four elements allows companies to meet consumer demand and align with their corporate strategy.',
                'marks': 10,
                'type': 'descriptive'
            },
            {
                'q': 'Which stage of the Product Life Cycle is typically characterized by maximum competition and profit stabilization?',
                'a': 'Maturity stage. Sales peak, competition is highest as market saturation is reached, and price wars often lead to profit stabilization and eventual decline.',
                'options': ['Introduction', 'Growth', 'Maturity', 'Decline'],
                'type': 'mcq'
            }
        ]
    }
}


def find_relevant_content(query: str, subject_name: str = '') -> dict:
    """Fuzzy keyword matching function to locate the best knowledge base entry."""
    from app.services.smart_engine import get_best_match
    return get_best_match(query, subject_name)
