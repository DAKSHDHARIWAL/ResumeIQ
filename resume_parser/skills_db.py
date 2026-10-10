

SKILLS_DB = {
    "Programming Languages": [
        "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "C",
        "Go", "Golang", "Rust", "Kotlin", "Swift", "PHP", "Ruby", "Scala",
        "R", "MATLAB", "Dart", "Perl", "Objective-C", "Solidity",
    ],
    "Web Development": [
        "HTML", "HTML5", "CSS", "CSS3", "React", "React.js", "Angular",
        "Vue", "Vue.js", "Next.js", "Nuxt.js", "Node.js", "Express.js",
        "Django", "Flask", "FastAPI", "Spring Boot", "Ruby on Rails",
        "jQuery", "Bootstrap", "Tailwind CSS", "Sass", "Webpack", "Vite",
        "REST API", "RESTful API", "GraphQL", "WebSockets", "Redux",
    ],
    "Data, ML & AI": [
        "Machine Learning", "Deep Learning", "Artificial Intelligence",
        "Natural Language Processing", "NLP", "Computer Vision",
        "TensorFlow", "PyTorch", "Keras", "Scikit-learn", "Pandas",
        "NumPy", "OpenCV", "Data Analysis", "Data Science",
        "Data Visualization", "Power BI", "Tableau", "Matplotlib",
        "Seaborn", "Statistics", "A/B Testing", "Big Data", "Hadoop",
        "Spark", "PySpark", "ETL", "LLM", "Generative AI",
    ],
    "Cloud & DevOps": [
        "AWS", "Amazon Web Services", "Azure", "Google Cloud", "GCP",
        "Docker", "Kubernetes", "Jenkins", "CI/CD", "Terraform",
        "Ansible", "Linux", "Bash", "Shell Scripting", "Nginx",
        "Microservices", "Serverless", "DevOps", "GitHub Actions",
    ],
    "Databases": [
        "SQL", "MySQL", "PostgreSQL", "MongoDB", "SQLite", "Redis",
        "Oracle", "Firebase", "DynamoDB", "Cassandra", "NoSQL",
        "Database Design", "Data Modeling",
    ],
    "Tools & Practices": [
        "Git", "GitHub", "GitLab", "Bitbucket", "Jira", "Confluence",
        "Agile", "Scrum", "Kanban", "Postman", "VS Code", "Figma",
        "Unit Testing", "Test Driven Development", "TDD", "Selenium",
        "API Testing", "Design Patterns", "Object Oriented Programming",
        "OOP", "System Design", "Data Structures", "Algorithms",
    ],
    "Soft Skills": [
        "Communication", "Leadership", "Teamwork", "Problem Solving",
        "Critical Thinking", "Time Management", "Adaptability",
        "Collaboration", "Project Management", "Presentation",
        "Mentoring", "Public Speaking", "Analytical Skills",
        "Attention to Detail", "Creativity",
    ],
}

# Common section headers we look for to judge resume structure/completeness.
SECTION_PATTERNS = {
    "Contact Information": [r"email", r"phone", r"linkedin", r"github"],
    "Summary / Objective": [r"summary", r"objective", r"profile", r"about me"],
    "Education": [r"education", r"academic"],
    "Experience": [r"experience", r"employment", r"work history", r"internship"],
    "Skills": [r"skills", r"technical skills", r"competenc"],
    "Projects": [r"projects?"],
    "Certifications": [r"certificat", r"licen[cs]e"],
    "Achievements": [r"achievements?", r"awards?", r"honou?rs?"],
}

# Verbs that make bullet points read as accomplishments rather than duties.
ACTION_VERBS = [
    "achieved", "built", "created", "designed", "developed", "engineered",
    "improved", "increased", "reduced", "launched", "led", "managed",
    "optimized", "implemented", "automated", "delivered", "spearheaded",
    "streamlined", "architected", "deployed", "analyzed", "researched",
    "collaborated", "mentored", "solved", "boosted", "generated",
]

WEAK_PHRASES = [
    "responsible for", "worked on", "helped with", "duties included",
    "in charge of", "tasked with",
]