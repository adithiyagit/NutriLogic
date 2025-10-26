# 📧 Email Configuration Guide for NutriLogic Password Reset

This guide will help you set up Gmail SMTP for password reset functionality in NutriLogic.

## 🎯 Overview

- **Sender Email**: `nutrilogic79@gmail.com`
- **Recipient**: Users requesting password reset (e.g., `adithiyavinu.b@gmail.com`)
- **SMTP Service**: Gmail SMTP Server
- **Purpose**: Send password reset emails to users

---

## 📋 Prerequisites

1. Access to the Gmail account: `nutrilogic79@gmail.com`
2. Two-Factor Authentication (2FA) enabled on the Gmail account
3. Python environment with Django installed

---

## 🔐 Step 1: Generate Gmail App Password

Since Google requires App Passwords for third-party applications, you need to create one:

### Instructions:

1. **Sign in to Gmail**: Go to [Google Account](https://myaccount.google.com/) and sign in with `nutrilogic79@gmail.com`

2. **Enable 2-Step Verification** (if not already enabled):
   - Go to: https://myaccount.google.com/security
   - Under "How you sign in to Google", click on "2-Step Verification"
   - Follow the prompts to set it up

3. **Generate App Password**:
   - Go to: https://myaccount.google.com/apppasswords
   - Or navigate: Google Account → Security → 2-Step Verification → App passwords
   - Select app: **Mail**
   - Select device: **Other (Custom name)** → Type "NutriLogic Django"
   - Click **Generate**
   - Copy the 16-character password (format: `xxxx xxxx xxxx xxxx`)
   - **IMPORTANT**: Save this password securely - you won't be able to see it again!

---

## 💻 Step 2: Set Up Environment Variable

### Option A: Using Command Line (Temporary - Current Session Only)

#### For Windows (PowerShell):
```powershell
$env:EMAIL_HOST_PASSWORD="your-16-char-app-password"
```

#### For Windows (Command Prompt):
```cmd
set EMAIL_HOST_PASSWORD=your-16-char-app-password
```

#### For macOS/Linux (Terminal):
```bash
export EMAIL_HOST_PASSWORD="your-16-char-app-password"
```

### Option B: Using .env File (Recommended for Development)

1. **Install python-decouple** (if not already installed):
   ```bash
   pip install python-decouple
   ```

2. **Create a `.env` file** in your project root:
   ```
   EMAIL_HOST_PASSWORD=your-16-char-app-password
   ```

3. **Update settings.py** to use decouple:
   ```python
   from decouple import config
   
   EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
   ```

### Option C: Direct Configuration (NOT Recommended - Security Risk)

**⚠️ WARNING**: Never commit passwords to version control!

For testing only, you can temporarily add directly to `settings.py`:
```python
EMAIL_HOST_PASSWORD = 'your-16-char-app-password'
```

**Remember to remove this before committing!**

---

## 🧪 Step 3: Test the Email Configuration

### Method 1: Using Django Shell

```python
python manage.py shell
```

Then in the shell:
```python
from django.core.mail import send_mail

send_mail(
    'Test Email from NutriLogic',
    'This is a test email to verify SMTP configuration.',
    'nutrilogic79@gmail.com',
    ['adithiyavinu.b@gmail.com'],
    fail_silently=False,
)
```

If successful, you should see output like: `1`

### Method 2: Test Password Reset Flow

1. Run the development server:
   ```bash
   python manage.py runserver
   ```

2. Navigate to: http://127.0.0.1:8000/password-reset/

3. Enter a registered user's email (e.g., `adithiyavinu.b@gmail.com`)

4. Click "Send Reset Instructions"

5. Check the recipient's inbox for the password reset email

---

## 📝 Current Configuration in `settings.py`

```python
# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'nutrilogic79@gmail.com'
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = 'NutriLogic <nutrilogic79@gmail.com>'
SERVER_EMAIL = 'nutrilogic79@gmail.com'
EMAIL_TIMEOUT = 10
```

---

## 🐛 Troubleshooting

### Issue 1: SMTPAuthenticationError
**Error**: `535-5.7.8 Username and Password not accepted`

**Solutions**:
- Verify you're using the App Password, not your regular Gmail password
- Check that 2-Step Verification is enabled
- Regenerate a new App Password
- Ensure there are no extra spaces in the password

### Issue 2: Connection Timeout
**Error**: `[Errno 10060] A connection attempt failed`

**Solutions**:
- Check your internet connection
- Verify firewall isn't blocking port 587
- Try using port 465 with `EMAIL_USE_SSL = True` instead of `EMAIL_USE_TLS`

### Issue 3: Environment Variable Not Found
**Error**: Email password is empty or not working

**Solutions**:
- Verify the environment variable is set: `echo %EMAIL_HOST_PASSWORD%` (Windows) or `echo $EMAIL_HOST_PASSWORD` (macOS/Linux)
- Restart your terminal/command prompt after setting the variable
- Restart the Django development server after setting the variable

### Issue 4: Email Goes to Spam
**Solutions**:
- Mark the email as "Not Spam" in the recipient's inbox
- Set up SPF and DKIM records (for production domains)
- Use a custom domain email instead of Gmail (for production)

---

## 🔒 Security Best Practices

1. **Never commit passwords to Git**:
   - Add `.env` to your `.gitignore` file
   - Use environment variables or secret management tools

2. **Rotate App Passwords regularly**:
   - Generate new App Passwords every 3-6 months
   - Revoke old App Passwords

3. **Monitor Gmail Account Activity**:
   - Check for suspicious activity at: https://myaccount.google.com/notifications

4. **For Production**:
   - Use environment variables from your hosting platform
   - Consider using dedicated email services (SendGrid, AWS SES, Mailgun)
   - Implement rate limiting for password reset requests

---

## 🚀 Production Deployment

For production environments (Heroku, AWS, Azure, etc.):

### Heroku:
```bash
heroku config:set EMAIL_HOST_PASSWORD=your-app-password
```

### AWS/Environment Variables:
Add `EMAIL_HOST_PASSWORD` to your environment configuration in your hosting platform's dashboard.

---

## 📞 Support

If you encounter issues:

1. Check Django logs for detailed error messages
2. Review Gmail's security settings: https://myaccount.google.com/security
3. Verify the email quota (Gmail has daily sending limits)
4. Contact: `adithiyavinu.b@gmail.com` for assistance

---

## ✅ Quick Checklist

- [ ] 2FA enabled on `nutrilogic79@gmail.com`
- [ ] App Password generated
- [ ] Environment variable `EMAIL_HOST_PASSWORD` set
- [ ] Test email sent successfully
- [ ] Password reset flow tested
- [ ] `.env` file added to `.gitignore` (if using .env)

---

**Last Updated**: October 2025  
**Email Account**: nutrilogic79@gmail.com  
**Project**: NutriLogic - Meal Recommendation & Health Prediction System

