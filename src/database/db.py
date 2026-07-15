from src.database.config import supabase
import bcrypt

def hash_pass(pwd):
    return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()


def check_teacher_exist(username):
    response = supabase.table("teachers").select("username").eq("username",username).execute()
    return len(response.data) > 0

def create_teacher(username, password, name):
    data = {"username":username, "password":hash_pass(password), "name":name}
    response = supabase.table("teachers").insert(data).execute()
    return response.data

def check_pass(pwd, hashed):
    return bcrypt.checkpw(pwd.encode(), hashed.encode())

def teacher_login(username, password):
    response = supabase.table("teachers").select("*").eq("username",username).execute()

    print(response.data)

    if response.data:

        teacher = response.data[0]

        print("Stored hash",teacher['password'])
        
        if check_pass(password, teacher['password']):
            return teacher
        
    return None

def get_all_students():
    response = supabase.table("students").select("*").execute()
    return response.data

def create_students(new_name, face_emb=None, voice_emb=None):
    data = {'name':new_name, 'face_embedding':face_emb, 'voice_embedding':voice_emb}
    response = supabase.table('students').insert(data).execute()
    return response.data


def create_subject(sub_id, sub_name, sub_section, teacher_id):
    data = {"subject_code":sub_id, "name":sub_name, "section":sub_section,"teacher_id":teacher_id}
    response = supabase.table("subjects").insert(data).execute()


def get_teacher_subjects(teacher_id):
    response = supabase.table('subjects').select("*,subject_students(count), attendence_logs(time_stamp)").eq("teacher_id", teacher_id).execute()
    subjects = response.data

    for sub in subjects:
        sub['total_students'] = sub.get("subject_students", [{}])[0].get('count',0) if sub.get('subject_students') else 0
        attendence = sub.get('attendence_logs', [])
        unique_sessions = len(set(log['time_stamp'] for log in attendence))
        sub['total_classes'] = unique_sessions

        sub.pop('subject_students', None)
        sub.pop('attendence_logs', None)

    return subjects

def enroll_student_to_subject(student_id, subject_id):
    data = {'student_id': student_id, "subject_id":subject_id}
    response = supabase.table("subject_students").insert(data).execute()
    return response.data

def unenroll_student_to_subject(student_id, subeject_id):
    response = supabase.table('subject_students').delete().eq('student_id', student_id).eq('subject_id', subeject_id).execute()
    return response.data

def get_student_subjects(student_id):
    res = supabase.table('subject_students').select('*, subjects(*)').eq('student_id', student_id).execute()
    return res.data

def get_student_attendence(student_id):
    res = supabase.table('attendence_logs').select('*, subjects(*)').eq('student_id', student_id).execute()
    return res.data

def create_attendence(logs):
    res = supabase.table('attendence_logs').insert(logs).execute()
    return res.data

def get_attendence_for_teacher(teacher_id):
    res = supabase.table('attendence_logs').select("*,subjects!inner(*)").eq('subjects.teacher_id', teacher_id).execute()
    print(res.data)
    return res.data