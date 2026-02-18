🎓 CA Final Tracker
A Neon-Powered, Data-Driven Command Center for CA Aspirants

Not just a study tracker.
A performance analytics cockpit for CA Final domination.

🚀 Overview

CA Final Tracker is a high-performance, visually immersive dashboard built using Streamlit, Plotly, Supabase, and advanced custom CSS glassmorphism UI.

It transforms traditional study tracking into a real-time strategic performance system — helping CA Final students measure, analyze, and optimize preparation with precision.

Designed for serious aspirants targeting AIR-level performance.

🔥 Core Highlights
⚡ Neon Cyberpunk UI

Glassmorphism cards

Animated KPI metrics

Fully custom top navigation

Dark immersive blue gradient background

Custom Plotly dark theme

Zero Streamlit branding

Professional dashboard aesthetics

This is not default Streamlit.
This is a controlled UI architecture layer.

📊 Advanced Study Analytics

📈 Subject-wise progress tracking

⏱ Target hours vs actual hours

📆 Exam countdown engine

📉 Daily/weekly performance insights

🏆 Leaderboard style performance sections

🎯 Topic-level granular tracking

🔄 Revision monitoring

Every hour logged becomes measurable intelligence.

🗂 Complete Subject Coverage

The system includes all CA Final subjects:

Code	Subject
FR	Financial Reporting
AFM	Advanced FM & Economics
AA	Advanced Auditing
DT	Direct Tax & International Tax
IDT	Indirect Tax

Each subject contains structured topic-level segmentation aligned with ICAI syllabus logic.

🧠 Built For Strategic Preparation
Target Hour Architecture

Pre-configured optimal hour targets:

Subject	Target Hours
FR	200
AFM	160
AA	150
DT	200
IDT	180

These are embedded into the performance engine to calculate:

Completion %

Remaining hours

Velocity analysis

Risk scoring (based on exam date proximity)

🛠 Tech Stack
Layer	Technology
Frontend	Streamlit
Styling	Custom CSS (Neon Glass UI)
Database	Supabase
Charts	Plotly (Dark Themed Engine)
Backend Logic	Python
Caching	st.cache_resource
Auth	Supabase Auth
🔐 Authentication System

Secure user signup/login

Username validation

Supabase backend profile storage

Session state management

Personalized dashboards

Each student gets their own performance database.

🎨 UI System Architecture

The app injects a fully custom CSS layer including:

Root neon variables

Animated scanlines

Glass card containers

Custom metric hover effects

Custom tabs navigation

Styled form elements

Styled select boxes

Custom progress bars

Neon badges (green/red performance tags)

Sticky top navbar

Custom scrollbar

Even Plotly charts follow the same dark-neon theme via a reusable apply_theme() function.

📦 Installation
1️⃣ Clone Repository
git clone https://github.com/yourusername/ca-final-tracker.git
cd ca-final-tracker

2️⃣ Install Dependencies
pip install -r requirements.txt


Core packages required:

streamlit

pandas

plotly

supabase

3️⃣ Configure Supabase

Create .streamlit/secrets.toml

SUPABASE_URL = "your-supabase-url"
SUPABASE_KEY = "your-anon-key"


Ensure your Supabase project contains:

profiles table

Auth enabled

4️⃣ Run Application
streamlit run streamlit_app.py

🧮 Key Functional Modules
🔹 Exam Countdown Engine

Calculates days remaining dynamically from:

exam_date - current_date


Displayed with animated neon countdown block.

🔹 Subject Performance Engine

For each subject:

Total hours logged

Target comparison

% completion

Visual progress bar

Color-coded indicators

🔹 Plotly Dark Theme Wrapper

Reusable function:

apply_theme(fig, title="", height=None)


Ensures:

Consistent dark backgrounds

Neon gridlines

Styled legend

Controlled margins

Typography consistency

🏗 Architecture Design Philosophy

This project follows:

Modular layout segmentation

UI/Logic separation

Centralized constants

Themed visualization pipeline

State-managed authentication

Database abstraction layer

🎯 Who Is This For?

CA Final aspirants

Rank-focused candidates

Structured learners

Performance-obsessed students

Dashboard lovers

Productivity hackers

🌟 Why This Is Different

Most trackers:

Log hours.

This tracker:

Measures velocity.

Calculates pressure.

Visualizes weakness.

Forces accountability.

Looks elite.

📸 Suggested Enhancements (Future Scope)

AIR probability prediction model

Mock test analytics engine

AI-driven weak topic detection

Peer leaderboard (multi-user comparison)

Printable A4 performance sheet

Export to Excel/PDF

Mobile optimized UI mode

Pomodoro timer integration

🏁 Final Note

This is not a beginner project.
This is a performance engineering system disguised as a study app.

If you are preparing for CA Final —
You don’t need motivation.

You need metrics.

📄 License

MIT License (or customize as needed)

👨‍💻 Author

Built with precision for serious CA aspirants.
