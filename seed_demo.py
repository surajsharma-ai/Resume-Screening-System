import sqlite3
import bcrypt

db = sqlite3.connect('data/resume.db')
c = db.cursor()
pw = bcrypt.hashpw(b'password', bcrypt.gensalt()).decode()
c.execute('INSERT OR IGNORE INTO users (username, password, email, fullname, role, company) VALUES (?, ?, ?, ?, ?, ?)', ('demo_recruiter', pw, 'demo@example.com', 'Demo Recruiter', 'recruiter', 'Tech Corp'))
db.commit()
user_id = c.execute('SELECT id FROM users WHERE username="demo_recruiter"').fetchone()[0]

# check if job exists for this recruiter
has_job = c.execute('SELECT COUNT(*) FROM jobs WHERE recruiter_id=?', (user_id,)).fetchone()[0]
if not has_job:
    c.execute("INSERT INTO jobs (recruiter_id, title, company, location, status) VALUES (?, ?, ?, ?, ?)", (user_id, 'Software Engineer', 'Tech Corp', 'Remote', 'active'))
    job_id = c.execute('SELECT last_insert_rowid()').fetchone()[0]
    
    # insert 10 dummy applications in different stages
    for i in range(10):
        # 3 hired, 2 interviewed, 1 selected, 4 pending
        status = 'pending'
        if i < 3: status = 'hired'
        elif i < 5: status = 'interviewed'
        elif i == 5: status = 'selected'
        
        # some dummy applicants
        c.execute("INSERT OR IGNORE INTO users (username, password, fullname, role) VALUES (?, ?, ?, ?)", (f'applicant_{i}', pw, f'Test Applicant {i}', 'applicant'))
        app_id = c.execute(f'SELECT id FROM users WHERE username="applicant_{i}"').fetchone()[0]
        
        c.execute("""
            INSERT OR IGNORE INTO applications (job_id, applicant_id, status)
            VALUES (?, ?, ?)
        """, (job_id, app_id, status))
    db.commit()

print(f'Recruiter created with username "demo_recruiter" and password "password". Details set up.')
db.close()
