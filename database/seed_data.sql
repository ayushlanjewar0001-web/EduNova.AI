-- Seed data for EduNova.AI

-- 1. Insert Universities
INSERT INTO universities (id, name, location, is_autonomous) VALUES
(1, 'University of Mumbai', 'Mumbai', FALSE),
(2, 'Savitribai Phule Pune University', 'Pune', FALSE),
(3, 'Shivaji University, Kolhapur', 'Kolhapur', FALSE),
(4, 'Rashtrasant Tukadoji Maharaj Nagpur University', 'Nagpur', FALSE),
(5, 'Sant Gadge Baba Amravati University', 'Amravati', FALSE),
(6, 'Dr. Babasaheb Ambedkar Marathwada University', 'Aurangabad', FALSE),
(7, 'Dr. Babasaheb Ambedkar Technological University (Lonere)', 'Lonere', FALSE),
(8, 'G H Raisoni College of Engineering (Autonomous)', 'Nagpur', TRUE)
ON CONFLICT (name) DO NOTHING;

-- Reset serial sequences for universities (optional since we hardcode IDs here)

-- 2. Insert Colleges/Institutions (Samples)
INSERT INTO colleges (university_id, name, code) VALUES
(1, 'Veermata Jijabai Technological Institute (VJTI)', 'VJTI-M'),
(1, 'Thadomal Shahani Engineering College', 'TSEC-M'),
(2, 'College of Engineering Pune (COEP)', 'COEP-P'),
(2, 'Pune Institute of Computer Technology (PICT)', 'PICT-P'),
(7, 'Dr. Babasaheb Ambedkar Technological University Campus', 'DBATU-C'),
(8, 'G H Raisoni College of Engineering', 'GHRCE-N');

-- 3. Insert Courses
INSERT INTO courses (id, name, duration_semesters) VALUES
(1, 'Bachelor of Technology (B.Tech)', 8),
(2, 'Bachelor of Engineering (B.E.)', 8),
(3, 'Master of Computer Applications (MCA)', 4)
ON CONFLICT DO NOTHING;

-- 4. Insert Branches
INSERT INTO branches (id, course_id, name, code) VALUES
(1, 1, 'Computer Science and Engineering', 'CSE'),
(2, 1, 'Information Technology', 'IT'),
(3, 2, 'Computer Engineering', 'COMP'),
(4, 2, 'Mechanical Engineering', 'MECH')
ON CONFLICT DO NOTHING;

-- 5. Insert Subjects
INSERT INTO subjects (id, branch_id, semester, name, code) VALUES
(1, 1, 5, 'Database Management Systems', 'CS501'),
(2, 1, 5, 'Operating Systems', 'CS502'),
(3, 1, 5, 'Theory of Computation', 'CS503'),
(4, 3, 6, 'Software Engineering', 'CE601'),
(5, 3, 6, 'Computer Networks', 'CE602')
ON CONFLICT DO NOTHING;

-- 6. Insert Topics
INSERT INTO topics (id, subject_id, name, description) VALUES
(1, 1, 'Relational Algebra', 'Basic and Extended Relational Operations'),
(2, 1, 'Normalization', '1NF, 2NF, 3NF, BCNF, and Multi-valued dependencies'),
(3, 1, 'Transaction Management', 'ACID properties, Serializability, Concurrency Control'),
(4, 2, 'CPU Scheduling', 'FCFS, SJF, Round Robin, Priority scheduling algorithms'),
(5, 2, 'Memory Management', 'Paging, Segmentation, Virtual Memory, Page Replacement'),
(6, 2, 'Deadlocks', 'Prevention, Avoidance (Banker''s Algorithm), Detection, Recovery')
ON CONFLICT DO NOTHING;

-- 7. Insert Mock PYQs
INSERT INTO pyqs (subject_id, topic_id, question_text, answer_explanation, year, month, marks, frequency_count, difficulty_level) VALUES
(1, 2, 'Explain 3NF and BCNF with a suitable example. Why is BCNF stronger than 3NF?', 'BCNF (Boyce-Codd Normal Form) is a stronger version of 3NF. A relation is in 3NF if for every non-trivial functional dependency X -> A, either X is a superkey or A is a prime attribute. In BCNF, for every non-trivial functional dependency X -> A, X must be a superkey. BCNF eliminates anomalies that 3NF might allow when there are overlapping candidate keys.', 2023, 'May', 10, 4, 'Medium'),
(1, 3, 'What are the ACID properties of a transaction? Explain each in detail.', 'ACID stands for Atomicity (all or nothing), Consistency (preserves database integrity), Isolation (execution of transactions in parallel yields same result as serial execution), and Durability (once committed, changes survive failures).', 2022, 'Dec', 8, 5, 'Easy'),
(2, 4, 'Consider the following processes with burst times: P1: 6ms, P2: 8ms, P3: 7ms, P4: 3ms. Find average waiting time using Round Robin (quantum = 2ms).', 'Perform Round Robin scheduling: Gantt chart: P1(0-2) -> P2(2-4) -> P3(4-6) -> P4(6-8) -> P1(8-10) -> P2(10-12) -> P3(12-14) -> P4(14-15) -> P1(15-17) -> P2(17-19) -> P3(19-21) -> P2(21-23) -> P3(23-24). Waiting times: P1=11ms, P2=15ms, P3=17ms, P4=12ms. Average waiting time = (11+15+17+12)/4 = 13.75ms.', 2023, 'Dec', 10, 3, 'Hard'),
(2, 6, 'Explain Banker''s Algorithm for deadlock avoidance. Solve for given allocation and max matrices.', 'Banker''s algorithm is a resource allocation and deadlock avoidance algorithm that tests for safety by simulating the allocation for predetermined maximum possible amounts of all resources, then makes an ''s-state'' check to decide whether allocation should be allowed.', 2024, 'May', 12, 6, 'Hard'),
(2, 5, 'Differentiate between Paging and Segmentation.', 'Paging divides memory into fixed-size pages. It has no external fragmentation but suffers from internal fragmentation. Segmentation divides memory into variable-sized logical segments based on user views, avoiding internal fragmentation but potentially causing external fragmentation.', 2023, 'May', 6, 3, 'Easy');
