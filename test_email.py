#!/usr/bin/env python
"""
Test Email Configuration Script for NutriLogic
This script tests if the email configuration is working correctly.
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nutrilogic.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def test_email_connection():
    """Test the email configuration by sending a test email."""
    
    print("=" * 60)
    print("NutriLogic - Email Configuration Test")
    print("=" * 60)
    print()
    
    # Check if password is set
    if not settings.EMAIL_HOST_PASSWORD:
        print("[ERROR] EMAIL_HOST_PASSWORD is not set!")
        print()
        print("Please set the environment variable:")
        print("  Windows PowerShell: $env:EMAIL_HOST_PASSWORD=\"your-app-password\"")
        print("  Windows CMD: set EMAIL_HOST_PASSWORD=your-app-password")
        print("  macOS/Linux: export EMAIL_HOST_PASSWORD=\"your-app-password\"")
        print()
        print("Or create a .env file with:")
        print("  EMAIL_HOST_PASSWORD=your-app-password")
        print()
        return False
    
    # Display current configuration
    print("Current Email Configuration:")
    print(f"  Backend: {settings.EMAIL_BACKEND}")
    print(f"  Host: {settings.EMAIL_HOST}")
    print(f"  Port: {settings.EMAIL_PORT}")
    print(f"  Use TLS: {settings.EMAIL_USE_TLS}")
    print(f"  From Email: {settings.EMAIL_HOST_USER}")
    print(f"  Password: {'*' * len(settings.EMAIL_HOST_PASSWORD)} (hidden)")
    print()
    
    # Get recipient email
    recipient = input("Enter recipient email address (default: adithiyavinu.b@gmail.com): ").strip()
    if not recipient:
        recipient = "adithiyavinu.b@gmail.com"
    
    print()
    print(f"Sending test email to: {recipient}")
    print("Please wait...")
    print()
    
    try:
        # Send test email
        result = send_mail(
            subject='🔥 NutriLogic - Email Configuration Test',
            message=(
                'Hello!\n\n'
                'This is a test email from NutriLogic.\n\n'
                'If you received this email, the SMTP configuration is working correctly!\n\n'
                '✅ Email Backend: Configured\n'
                '✅ Gmail SMTP: Connected\n'
                '✅ Password Reset: Ready\n\n'
                'You can now use the password reset functionality on the NutriLogic website.\n\n'
                'Best regards,\n'
                'NutriLogic Team\n'
                '---\n'
                'This is an automated test email. Please do not reply.'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=False,
        )
        
        if result == 1:
            print("[SUCCESS] Test email sent successfully!")
            print()
            print(f"Check the inbox of: {recipient}")
            print("   (Don't forget to check spam/junk folder)")
            print()
            print("Email Configuration Status: WORKING")
            print()
            return True
        else:
            print("[FAILED] Email was not sent.")
            print("   Result code:", result)
            return False
            
    except Exception as e:
        print("[ERROR] Failed to send email.")
        print()
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        print()
        print("Common Solutions:")
        print("  1. Check that EMAIL_HOST_PASSWORD is the App Password from Google")
        print("  2. Verify 2-Factor Authentication is enabled on nutrilogic79@gmail.com")
        print("  3. Generate a new App Password at: https://myaccount.google.com/apppasswords")
        print("  4. Check your internet connection")
        print("  5. Verify firewall isn't blocking port 587")
        print()
        print("For detailed setup instructions, see: EMAIL_SETUP_GUIDE.md")
        print()
        return False

if __name__ == '__main__':
    try:
        test_email_connection()
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user.")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
    
    print()
    print("=" * 60)
    input("Press Enter to exit...")

