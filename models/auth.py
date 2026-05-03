from models.user import User

class Auth:
    
    @staticmethod
    def register(name, email, password, phone='', role='customer'):
        try:
            print(f"Registering: {name}, {email}, {role}")
            
            # Check if email exists
            existing_user = User.find_by_email(email)
            if existing_user:
                return {'success': False, 'message': 'Email already registered!'}
            
            # Create new user
            new_user = User(
                name=name,
                email=email,
                password=password,
                phone=phone,
                role=role
            )
            
            if new_user.save():
                return {
                    'success': True, 
                    'message': 'Registration successful!',
                    'user': new_user.to_dict()  # ← CONVERT TO DICTIONARY!
                }
            else:
                return {'success': False, 'message': 'Failed to save user to database'}
                
        except Exception as e:
            print(f"Register error: {e}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def login(email, password):
        """Authenticate user login (DIRECT COMPARE)"""
        user = User.find_by_email(email)
        
        if user and user.password == password:
            return {
                'success': True, 
                'message': 'Login successful!', 
                'user': user.to_dict()  # ← CONVERT TO DICTIONARY!
            }
        return {'success': False, 'message': 'Invalid email or password!'}