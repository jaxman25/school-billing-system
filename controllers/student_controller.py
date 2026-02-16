from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.database import db
from models.student import Student
from models.bill import Bill
from datetime import datetime

from controllers.auth_controller import login_required

from controllers.auth_controller import login_required

student_bp = Blueprint('student', __name__)

@login_required
@login_required
@student_bp.route('/')
def list_students():
    students = Student.query.all()
    return render_template('students/list.html', students=students)

@login_required
@login_required
@student_bp.route('/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        try:
            student = Student(
                name=request.form['name'],
                grade=request.form['grade'],
                guardian_name=request.form.get('guardian_name', ''),
                phone=request.form.get('phone', ''),
                email=request.form.get('email', '')
            )
            db.session.add(student)
            db.session.commit()
            flash('Student added successfully!', 'success')
            return redirect(url_for('student.list_students'))
        except Exception as e:
            flash(f'Error adding student: {str(e)}', 'danger')
    
    return render_template('students/add.html')

@login_required
@login_required
@student_bp.route('/<int:student_id>')
def view_student(student_id):
    student = Student.query.get_or_404(student_id)
    return render_template('students/view.html', student=student)

@login_required
@login_required
@student_bp.route('/delete/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    try:
        student = Student.query.get_or_404(student_id)
        db.session.delete(student)
        db.session.commit()
        flash('Student deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting student: {str(e)}', 'danger')
    
    return redirect(url_for('student.list_students'))

@login_required
@login_required
@student_bp.route('/search', methods=['GET'])
def search_students():
    query = request.args.get('query', '').strip()
    grade = request.args.get('grade', '')
    
    students_query = Student.query
    
    if query:
        students_query = students_query.filter(
            (Student.name.ilike(f'%{query}%')) | 
            (Student.guardian_name.ilike(f'%{query}%')) |
            (Student.phone.ilike(f'%{query}%'))
        )
    
    if grade:
        students_query = students_query.filter(Student.grade == grade)
    
    students = students_query.all()
    
    return render_template('students/search.html', 
                         students=students,
                         query=query,
                         grade=grade)


