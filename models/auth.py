import hashlib
from models.user import User

class Auth:
    
    @staticmethod
    def hash_password(password):
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def register(name, email, password, phone='', role='customer'):
        try:
            print(f"Registering: {name}, {email}, {role}")
            
            # Check if email exists
            existing_user = User.find_by_email(email)
            if existing_user:
                return {'success': False, 'message': 'Email already registered!'}
            
            # Hash the password before saving
            hashed_password = Auth.hash_password(password)
            
            # Create new user with hashed password
            new_user = User(
                name=name,
                email=email,
                password=hashed_password,
                phone=phone,
                role=role
            )
            
            if new_user.save():
                return {
                    'success': True, 
                    'message': 'Registration successful!',
                    'user': new_user.to_dict()
                }
            else:
                return {'success': False, 'message': 'Failed to save user to database'}
                
        except Exception as e:
            print(f"Register error: {e}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def login(email, password):
        """Authenticate user login (WITH HASHING)"""
        user = User.find_by_email(email)
        
        if user:
            # Hash the entered password and compare
            hashed_password = Auth.hash_password(password)
            if user.password == hashed_password:
                return {
                    'success': True, 
                    'message': 'Login successful!', 
                    'user': user.to_dict()
                }
        
        return {'success': False, 'message': 'Invalid email or password!'}