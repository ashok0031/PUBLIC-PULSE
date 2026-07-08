from flask import jsonify

def success(data, status=200):
    return jsonify({'success': True, 'data': data}), status

def error(message, status=400):
    return jsonify({'success': False, 'error': message}), status

def generate_otp_email_html(otp):
    return f"""
    <!DOCTYPE html>
    <html>
      <body style='font-family: Arial, sans-serif; background: #f4f4f4; margin: 0; padding: 0;'>
        <div style='max-width: 420px; margin: 40px auto; background: #fff; border-radius: 12px; box-shadow: 0 2px 8px #eee; padding: 32px;'>
          <div style='text-align: center; margin-bottom: 24px;'>
            <img src='cid:publicpulse_logo' alt='Public Pulse Logo' style='height: 64px; margin-bottom: 12px;' />
          </div>
          <h2 style='text-align: center; color: #1a237e; margin-bottom: 8px;'>Welcome to Public Pulse!</h2>
          <p style='text-align: center; color: #333; margin-bottom: 24px;'>We are thrilled to have you join our Public Pulse family.<br/>To complete your registration, please use the OTP below:</p>
          <div style='background: #f5f5f5; border-radius: 8px; padding: 24px 0; margin: 0 auto 24px auto; text-align: center;'>
            <span style='font-size: 2.2rem; font-weight: bold; color: #d4a017; letter-spacing: 6px;'>{otp}</span>
          </div>
          <p style='text-align: center; color: #555; margin-bottom: 0;'>If you did not request this, please ignore this email.<br/>Thank you for joining Public Pulse!</p>
        </div>
      </body>
    </html>
    """ 