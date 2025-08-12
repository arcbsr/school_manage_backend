from rolepermissions.roles import AbstractUserRole


class Admin(AbstractUserRole):
    available_permissions = {
        'manage_users': True,
        'manage_school': True,
        'view_reports': True,
    }


class Staff(AbstractUserRole):
    available_permissions = {
        'manage_school': True,
        'view_reports': True,
    }


class Teacher(AbstractUserRole):
    available_permissions = {
        'manage_classes': True,
        'grade_students': True,
        'view_reports': True,
    }


class Student(AbstractUserRole):
    available_permissions = {
        'view_grades': True,
        'view_schedule': True,
    }


class Parent(AbstractUserRole):
    available_permissions = {
        'view_student_progress': True,
        'view_reports': True,
    }


