from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.api import auth, curriculum, study, tests_engine
from app.models import University, College, Course, Branch, Subject, Topic, PYQ

# Create Database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set CORS origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Auth"])
app.include_router(curriculum.router, prefix=f"{settings.API_V1_STR}/curriculum", tags=["Curriculum"])
app.include_router(study.router, prefix=f"{settings.API_V1_STR}/ai", tags=["AI Study System"])
app.include_router(tests_engine.router, prefix=f"{settings.API_V1_STR}/tests", tags=["Test Engine"])

@app.on_event("startup")
def startup_event():
    """
    On startup, verify database seeding of Maharashtra Universities curriculum.
    """
    db = SessionLocal()
    try:
        # Check if universities already exist
        if db.query(University).count() == 0:
            print("Seeding database with Maharashtra curriculum...")
            
            # 1. Seeding Universities (supported list)
            mumbai = University(id=1, name="University of Mumbai", location="Mumbai", is_autonomous=False)
            pune = University(id=2, name="Savitribai Phule Pune University", location="Pune", is_autonomous=False)
            kolhapur = University(id=3, name="Shivaji University", location="Kolhapur", is_autonomous=False)
            nagpur = University(id=4, name="Rashtrasant Tukadoji Maharaj Nagpur University", location="Nagpur", is_autonomous=False)
            amravati = University(id=5, name="Sant Gadge Baba Amravati University", location="Amravati", is_autonomous=False)
            marathwada = University(id=6, name="Dr. Babasaheb Ambedkar Marathwada University", location="Aurangabad", is_autonomous=False)
            dbatu = University(id=7, name="Dr. Babasaheb Ambedkar Technological University (DBATU)", location="Lonere", is_autonomous=False)
            
            universities = [mumbai, pune, kolhapur, nagpur, amravati, marathwada, dbatu]
            db.add_all(universities)
            db.commit()
            
            # 2. Seeding Colleges (Optional)
            db.add_all([
                College(university_id=1, name="Veermata Jijabai Technological Institute (VJTI)", code="VJTI-M"),
                College(university_id=1, name="Thadomal Shahani Engineering College", code="TSEC-M"),
                College(university_id=2, name="College of Engineering Pune (COEP)", code="COEP-P"),
                College(university_id=2, name="Pune Institute of Computer Technology (PICT)", code="PICT-P"),
                College(university_id=7, name="DBATU Campus Lonere", code="DBATU-C")
            ])
            db.commit()
            
            # 3. Seeding Courses (Programs)
            btech = Course(id=1, name="Bachelor of Technology (B.Tech)", duration_semesters=8)
            bpharm = Course(id=2, name="Bachelor of Pharmacy (B.Pharm)", duration_semesters=8)
            barch = Course(id=3, name="Bachelor of Architecture (B.Arch)", duration_semesters=10)
            mca = Course(id=4, name="Master of Computer Applications (MCA)", duration_semesters=4)
            mba = Course(id=5, name="Master of Business Administration (MBA)", duration_semesters=4)
            bsc = Course(id=6, name="Bachelor of Science (B.Sc)", duration_semesters=6)
            bcom = Course(id=7, name="Bachelor of Commerce (B.Com)", duration_semesters=6)
            
            db.add_all([btech, bpharm, barch, mca, mba, bsc, bcom])
            db.commit()
            
            # 4. Seeding Branches dynamic per Course
            b_cse = Branch(id=1, course_id=1, name="Computer Science and Engineering", code="CSE")
            b_mech = Branch(id=2, course_id=1, name="Mechanical Engineering", code="MECH")
            b_pharmacy = Branch(id=3, course_id=2, name="Pharmacology", code="PHARM")
            b_pharmaceutics = Branch(id=4, course_id=2, name="Pharmaceutics", code="PHCEUT")
            b_arch_design = Branch(id=5, course_id=3, name="Architectural Design", code="ARCHDES")
            b_mca_dev = Branch(id=6, course_id=4, name="Software Development", code="DEV")
            b_mba_marketing = Branch(id=7, course_id=5, name="Marketing Management", code="MKT")
            b_mba_finance = Branch(id=8, course_id=5, name="Financial Management", code="FIN")
            b_bsc_physics = Branch(id=9, course_id=6, name="Physics", code="PHYS")
            b_bsc_chem = Branch(id=10, course_id=6, name="Chemistry", code="CHEM")
            b_bcom_acc = Branch(id=11, course_id=7, name="Accountancy", code="ACC")
            
            db.add_all([
                b_cse, b_mech, b_pharmacy, b_pharmaceutics, b_arch_design,
                b_mca_dev, b_mba_marketing, b_mba_finance, b_bsc_physics,
                b_bsc_chem, b_bcom_acc
            ])
            db.commit()
            
            # 5. Map subjects list per branch and semester
            subjects_by_branch_and_sem = {
                # B.Tech CSE
                (1, 1): ["Applied Mathematics I", "Engineering Physics I", "Engineering Chemistry I", "Basic Electrical Engineering", "Engineering Mechanics"],
                (1, 2): ["Applied Mathematics II", "Engineering Physics II", "Engineering Chemistry II", "Structured Programming Approach", "Engineering Drawing"],
                (1, 3): ["Applied Mathematics III", "Discrete Structures", "Data Structures", "Digital Logic Design", "Database Management Systems"],
                (1, 4): ["Applied Mathematics IV", "Analysis of Algorithms", "Computer Org & Architecture", "Operating Systems", "Theory of Computer Science"],
                (1, 5): ["Microprocessors", "Database Management Systems", "Operating Systems", "Theory of Computation", "Software Engineering"],
                (1, 6): ["Compiler Construction", "Cryptography & Network Security", "Mobile Computing", "Software Engineering", "System Programming"],
                (1, 7): ["Digital Signal Processing", "Artificial Intelligence", "Cloud Computing", "Elective I"],
                (1, 8): ["Natural Language Processing", "Big Data Analytics", "Deep Learning", "Internet of Things"],
                # B.Tech Mech
                (2, 1): ["Applied Mathematics I", "Engineering Physics I", "Engineering Chemistry I", "Basic Electrical Engineering", "Engineering Mechanics"],
                (2, 2): ["Applied Mathematics II", "Engineering Physics II", "Engineering Chemistry II", "Structured Programming Approach", "Engineering Drawing"],
                (2, 3): ["Strength of Materials", "Thermodynamics", "Production Process I", "Material Technology"],
                (2, 4): ["Theory of Machines I", "Fluid Mechanics", "Production Process II", "Mechanical Measurements"],
                (2, 5): ["Theory of Machines II", "Heat Transfer", "Dynamics of Machinery", "Machine Design I"],
                (2, 6): ["Machine Design II", "Internal Combustion Engines", "Metrology & Quality Control", "Computer Aided Engineering"],
                (2, 7): ["CAD/CAM/CAE", "Automobile Engineering", "Refrigeration & Air Conditioning", "Elective II"],
                (2, 8): ["Design of Mechanical Systems", "Energy Engineering", "Industrial Engineering", "Elective III"],
                # B.Pharm Pharmacology
                (3, 1): ["Human Anatomy & Physiology I", "Pharmaceutical Analysis I", "Pharmaceutics I", "Inorganic Chemistry"],
                (3, 2): ["Human Anatomy & Physiology II", "Organic Chemistry I", "Biochemistry", "Pathophysiology"],
                (3, 3): ["Organic Chemistry II", "Physical Pharmaceutics I", "Pharmaceutical Microbiology", "Pharmaceutical Engineering"],
                (3, 4): ["Organic Chemistry III", "Medicinal Chemistry I", "Physical Pharmaceutics II", "Pharmacology I", "Pharmacognosy I"],
                (3, 5): ["Medicinal Chemistry II", "Industrial Pharmacy I", "Pharmacology II", "Pharmacognosy II", "Jurisprudence"],
                (3, 6): ["Medicinal Chemistry III", "Pharmacology III", "Herbal Drug Technology", "Biopharmaceutics", "Biotechnology", "Quality Assurance"],
                (3, 7): ["Instrumental Analysis", "Industrial Pharmacy II", "Pharmacy Practice", "Novel Drug Delivery"],
                (3, 8): ["Biostatistics", "Social and Preventive Pharmacy", "Elective Subject"],
                # B.Pharm Pharmaceutics
                (4, 1): ["Human Anatomy & Physiology I", "Pharmaceutical Analysis I", "Pharmaceutics I", "Inorganic Chemistry"],
                (4, 2): ["Human Anatomy & Physiology II", "Organic Chemistry I", "Biochemistry", "Pathophysiology"],
                (4, 3): ["Organic Chemistry II", "Physical Pharmaceutics I", "Pharmaceutical Microbiology", "Pharmaceutical Engineering"],
                (4, 4): ["Organic Chemistry III", "Medicinal Chemistry I", "Physical Pharmaceutics II", "Pharmacology I", "Pharmacognosy I"],
                (4, 5): ["Medicinal Chemistry II", "Industrial Pharmacy I", "Pharmacology II", "Pharmacognosy II", "Jurisprudence"],
                (4, 6): ["Medicinal Chemistry III", "Pharmacology III", "Herbal Drug Technology", "Biopharmaceutics", "Biotechnology", "Quality Assurance"],
                (4, 7): ["Instrumental Analysis", "Industrial Pharmacy II", "Pharmacy Practice", "Novel Drug Delivery"],
                (4, 8): ["Biostatistics", "Social and Preventive Pharmacy", "Elective Subject"],
                # B.Arch Design
                (5, 1): ["Architectural Design I", "Allied Design I", "Theory of Structures I", "Humanities I"],
                (5, 2): ["Architectural Design II", "Allied Design II", "Theory of Structures II", "Humanities II"],
                (5, 3): ["Architectural Design III", "History of Architecture I", "Structural Design III", "Environmental Studies I"],
                (5, 4): ["Architectural Design IV", "History of Architecture II", "Structural Design IV", "Environmental Studies II"],
                (5, 5): ["Architectural Design V", "History of Architecture III", "Structural Design V", "Building Services I"],
                (5, 6): ["Architectural Design VI", "History of Architecture IV", "Structural Design VI", "Building Services II"],
                (5, 7): ["Architectural Design VII", "Professional Practice I", "Specifications", "Building Services III"],
                (5, 8): ["Architectural Design VIII", "Professional Practice II", "Urban Planning Introduction", "Building Services IV"],
                (5, 9): ["Architectural Design IX", "Thesis Project Phase I", "Advanced Structures"],
                (5, 10): ["Professional Training (Internship)", "Thesis Project Phase II", "Professional Elective"],
                # MCA
                (6, 1): ["Mathematical Foundations", "Object Oriented Programming", "Computer Architecture", "Software Engineering", "Web Technologies"],
                (6, 2): ["Data Structures & Algorithms", "DBMS", "Operating Systems", "Project Management", "Advanced Java"],
                (6, 3): ["Machine Learning", "Artificial Intelligence", "Data Mining", "Cloud Computing", "Cyber Security"],
                (6, 4): ["Big Data Analytics", "IoT", "Mobile Computing", "Thesis Project"],
                # MBA Marketing
                (7, 1): ["Managerial Economics", "Financial Accounting", "Organizational Behavior", "Marketing Management"],
                (7, 2): ["HR Management", "Financial Management", "Operations Research", "Strategic Management"],
                (7, 3): ["Consumer Behavior", "Product & Brand Management", "Digital Marketing", "Retail Management"],
                (7, 4): ["International Business", "Project Management", "Entrepreneurship Development", "Viva-Voce"],
                # MBA Finance
                (8, 1): ["Managerial Economics", "Financial Accounting", "Organizational Behavior", "Marketing Management"],
                (8, 2): ["HR Management", "Financial Management", "Operations Research", "Strategic Management"],
                (8, 3): ["Corporate Finance", "Investment Analysis", "Financial Derivatives", "International Finance"],
                (8, 4): ["Portfolio Management", "Project Management", "Entrepreneurship Development", "Viva-Voce"],
                # B.Sc Physics
                (9, 1): ["Classical Mechanics", "Calculus and ODEs", "Inorganic Chemistry", "Basic Electronics"],
                (9, 2): ["Waves and Oscillations", "Linear Algebra", "Organic Chemistry", "Digital Electronics"],
                (9, 3): ["Thermodynamics", "Probability and Stats", "Physical Chemistry", "Thermal Physics"],
                (9, 4): ["Optics", "Numerical Methods", "Analytical Chemistry", "Solid State Physics"],
                (9, 5): ["Quantum Mechanics", "Abstract Algebra", "Physical Chemistry II", "Atomic Physics"],
                (9, 6): ["Nuclear Physics", "Complex Analysis", "Organic Chemistry II", "Analytical Chemistry II"],
                # B.Sc Chemistry
                (10, 1): ["Classical Mechanics", "Calculus and ODEs", "Inorganic Chemistry", "Basic Electronics"],
                (10, 2): ["Waves and Oscillations", "Linear Algebra", "Organic Chemistry", "Digital Electronics"],
                (10, 3): ["Thermodynamics", "Probability and Stats", "Physical Chemistry", "Thermal Physics"],
                (10, 4): ["Optics", "Numerical Methods", "Analytical Chemistry", "Solid State Physics"],
                (10, 5): ["Quantum Mechanics", "Abstract Algebra", "Physical Chemistry II", "Atomic Physics"],
                (10, 6): ["Nuclear Physics", "Complex Analysis", "Organic Chemistry II", "Analytical Chemistry II"],
                # B.Com Accountancy
                (11, 1): ["Financial Accounting I", "Business Communication", "Business Economics", "Environmental Studies"],
                (11, 2): ["Financial Accounting II", "Business Mathematics", "Commerce II", "Business Law"],
                (11, 3): ["Corporate Accounting", "Business Regulatory Framework", "Banking and Finance", "HR Management"],
                (11, 4): ["Advanced Cost Accounting", "Auditing", "Modern Business Practices", "Business Management"],
                (11, 5): ["Cost Accounting I", "Direct and Indirect Taxes I", "Financial Management I", "Commerce V"],
                (11, 6): ["Cost Accounting II", "Direct and Indirect Taxes II", "Financial Management II", "Commerce VI"]
            }
            
            # Loop and seed subjects for all 7 universities dynamically
            subject_id_counter = 1
            seeded_subjects = []
            
            for univ in universities:
                for (branch_id, semester), subject_names in subjects_by_branch_and_sem.items():
                    for name in subject_names:
                        # Create unique code
                        code = f"UN{univ.id}-B{branch_id}-S{semester}-{name[:3].upper()}"
                        sub = Subject(
                            id=subject_id_counter,
                            university_id=univ.id,
                            branch_id=branch_id,
                            semester=semester,
                            name=name,
                            code=code
                        )
                        seeded_subjects.append(sub)
                        subject_id_counter += 1
            
            db.add_all(seeded_subjects)
            db.commit()
            print(f"Seeded {len(seeded_subjects)} subjects dynamically!")
            
            # 6. Seeding core topics dynamically for all Database Management Systems / DBMS subjects
            dbms_subjects = db.query(Subject).filter(
                (Subject.name == "Database Management Systems") | (Subject.name == "DBMS")
            ).all()
            
            print(f"Found {len(dbms_subjects)} DBMS subjects to seed topics/PYQs for.")
            
            for sub in dbms_subjects:
                # Seed topics for each matching subject
                t1 = Topic(subject_id=sub.id, name="Relational Algebra", description="Basic and Extended Operations")
                t2 = Topic(subject_id=sub.id, name="Database Normalization", description="1NF, 2NF, 3NF, BCNF")
                t3 = Topic(subject_id=sub.id, name="Normalization Structures", description="Decomposition into normal forms")
                t4 = Topic(subject_id=sub.id, name="Transaction Management", description="ACID properties concurrency control")
                
                db.add_all([t1, t2, t3, t4])
                db.commit() # commit to get IDs for topics
                
                # Seed Mock PYQs for this subject mapping back to the created topics
                db.add_all([
                    PYQ(
                        subject_id=sub.id,
                        topic_id=t2.id,
                        question_text="Explain 3NF and BCNF with a suitable example. Why is BCNF stronger than 3NF?",
                        answer_explanation="BCNF (Boyce-Codd Normal Form) is a stronger version of 3NF. A relation is in 3NF if for every non-trivial functional dependency X -> A, either X is a superkey or A is a prime attribute. In BCNF, for every functional dependency, the LHS must be a superkey.",
                        year=2023,
                        month="May",
                        marks=10,
                        frequency_count=4,
                        difficulty_level="Medium"
                    ),
                    PYQ(
                        subject_id=sub.id,
                        topic_id=t3.id,
                        question_text="Explain database normalization steps for 1NF, 2NF and 3NF.",
                        answer_explanation="1NF: Remove multi-valued attributes. 2NF: Remove partial dependencies. 3NF: Remove transitive dependencies.",
                        year=2023,
                        month="Dec",
                        marks=10,
                        frequency_count=3,
                        difficulty_level="Medium"
                    ),
                    PYQ(
                        subject_id=sub.id,
                        topic_id=t4.id,
                        question_text="What are the ACID properties of a transaction? Explain each in detail.",
                        answer_explanation="ACID stands for Atomicity (all or nothing), Consistency (preserves database integrity), Isolation (concurrency control), and Durability (committed results survive database failures).",
                        year=2022,
                        month="Dec",
                        marks=8,
                        frequency_count=5,
                        difficulty_level="Easy"
                    )
                ])
                db.commit()
            print("Database fully seeded with all subjects for all courses!")
    finally:
        db.close()

@app.get("/api")
@app.get("/api/")
def api_status():
    return {"status": "ok", "message": "EduNova.AI API is running"}

@app.get("/")
def read_root():
    return {"message": "Welcome to EduNova.AI Backend API"}
