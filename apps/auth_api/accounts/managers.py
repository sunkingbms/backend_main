from django.contrib.auth.base_user import BaseUserManager

class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifier
    for authentication instead of usernames.
    """
    #Overwritten create_user method, to adapt it to our custom user
    def create_user(self, email: str, password: str , **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError("Email must be provided")
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        
        return user 
    
    def create_superuser(self, email: str, password: str, **extra_fields):
        """ Method used to create a super user with given email and password """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser should have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser should have is_superuser=True')
        
        return self.create_user(email, password, **extra_fields)