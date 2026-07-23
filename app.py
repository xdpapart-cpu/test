from flask import send_from_directory
import os
from flask import Flask
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, url_for
from flask import session, redirect, url_for, request, render_template
from flask import Flask, render_template, request, redirect, url_for
from flask_mail import Mail, Message





app = Flask(__name__)
app.secret_key = 'your_secret_key_dito'
# Dito ise-save ang database file
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['uploads'] = 'uploads'
db = SQLAlchemy(app)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'students.db')


if not os.path.exists('uploads'):
    os.makedirs('uploads')



# Dito natin ilalagay ang lahat ng fields
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(50), nullable=False)
    middlename = db.Column(db.String(50))
    lastname = db.Column(db.String(50), nullable=False)
    Address = db.Column(db.String(50), nullable=False)
    sex = db.Column(db.String(10), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(100))
    year = db.Column(db.String(10), nullable=False)
    strand = db.Column(db.String(20), nullable=False)
    father_name = db.Column(db.String(100), nullable=False)
    mother_name = db.Column(db.String(100), nullable=False)
    father_phone = db.Column(db.String(20), nullable=True)
    mother_phone = db.Column(db.String(20), nullable=True)
    status = db.Column(db.String(20), default='Pending')

# I-create ang table (run this once)
with app.app_context():
    db.create_all()



@app.route('/uploads/<filename>')
def view_file(filename):
    # Dito mo tinutukoy kung saan folder naka-save ang mga files
    return send_from_directory('uploads', filename)

@app.route('/submit', methods=['POST'])
def submit():
    # 1. I-save ang data sa Database
    new_student = Student (
        firstname=request.form.get('firstname'),
        middlename=request.form.get('middlename'),
        lastname=request.form.get('lastname'),
        Address=request.form.get('Address'),
        sex=request.form.get('sex'),
        age=request.form.get('age'),
        year=request.form.get('year'),
        strand=request.form.get('strand'),
        father_name=request.form.get('father_name'),
        mother_name=request.form.get('mother_name'),
        father_phone=request.form.get('father_phone'),
        mother_phone=request.form.get('mother_phone'),
       email=request.form['email']
    )
    db.session.add(new_student)
    db.session.commit()
    
    # 2. Dito isama ang File Saving Logic (yung code natin kanina)
    requirements = ['good_moral', 'form137', 'psa', 'cert_grad']
    for req in requirements:
        file = request.files.get(req)
        if file and file.filename != '':
            ext = os.path.splitext(file.filename)[1]
            filename = f"{new_student.id}_{new_student.lastname}_{new_student.firstname}_{req}{ext}"
            file.save(os.path.join(app.config['uploads'], filename))
            




            
    # 3. Pagkatapos ng lahat, i-redirect sa success page
    return redirect(url_for('succes'))

# Route para sa success page
@app.route('/succes')
def succes():
    return render_template('succes.html')




@app.route('/admindashboard')
def admindashboard():
    all_students = Student.query.all() 
    return render_template('admindashboard.html', students=all_students)



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/enroll') 
def enroll():
    return render_template('enroll.html')





@app.route('/adminlogin', methods=['GET', 'POST'])
def adminlogin():
    error = None
    if request.method == 'POST':
        # Dito mo ilalagay ang password na gusto mo
        if request.form['password'] == 'NZC2026': 
            session['admin_logged_in'] = True
            return redirect(url_for('admindashboard'))
        else:
            error = "Wrong Password! Try again."
    return render_template('adminlogin.html',error=error)

@app.route('/admindashboard')
def dashboard():
    # Proteksyon: Kung hindi naka-login, pabalikin sa login page
    if not session.get('admin_logged_in'):
        return redirect(url_for('adminlogin'))
        
    all_students = Student.query.all()
    return render_template('admindashboard.html', students=all_students)

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))
  
@app.route('/disapprove/<int:id>')
def disapprove_student(id):
    student = Student.query.get_or_404(id)
    student.status = 'Pending' # Ibabalik sa Pending
    db.session.commit()
    return redirect(url_for('admindashboard'))




app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = 'xdpapart@gmail.com'
app.config['MAIL_PASSWORD'] = 'xdftjoivdifqzouo'
app.config['MAIL_DEFAULT_SENDER'] = 'xdpapart@gmail.com'

mail = Mail(app)

@app.route('/set-date/<int:id>')
def set_date(id):
    student = Student.query.get_or_404(id)
    return render_template('setdate.html', student=student)

@app.route('/approve/<int:id>', methods=['GET', 'POST'])
def approve_student(id):
    print("DEBUG: Pumasok sa approve route!")
    
    # Kunin ang petsa na pinili ng admin mula sa form
    submission_date = request.form.get('sched_date', 'July 30, 2026') # Fallback kung sakaling wala

    student = Student.query.get_or_404(id)
    student.status = 'Approved'
    db.session.commit()

    try:
        msg = Message(
            subject="Admission Status - Northern Zambales College",
            recipients=[student.email]
        )
        
        # Naka-dynamic na ngayon ang petsa batay sa tinype ng admin
        msg.body = f"""Hello {student.firstname},

Congratulations! You have been admitted to Northern Zambales College.

Please proceed to the registrar's office to submit your physical documents on {submission_date}. 

Bring the following requirements:
- Form 137
- Good Moral Certificate
- PSA Birth Certificate

Please bring this email or notification with you. Thank you!

Best regards,
Northern Zambales College Admin
"""

        with app.app_context():
            mail.send(msg)
        print("EMAIL SENT SUCCESSFULLY WITH DATE:", submission_date)
    except Exception as e:
        print(f"ERROR SA PAG-SEND NG EMAIL: {e}")

    return redirect(url_for('admindashboard'))


































if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


