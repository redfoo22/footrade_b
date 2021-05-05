

foo_email = "3102796480@tmomail.net"
alex_email = "3235594184@vtext.com"

def email_Text(whom,sub,msg):
    import config
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    email = "redfoo@partyrock.com" # the email where you sent the email
    password = config.GMP
    send_to_email = whom # for whom
    subject = sub
    message = msg

    msg = MIMEMultipart()
    msg["From"] = email
    msg["To"] = send_to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(message, 'plain'))

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(email, password)
    text = msg.as_string()
    server.sendmail(email, send_to_email, text)
    print("email server called")
    server.quit()

email_Text(foo_email,"test","TO THE MOON")
email_Text(alex_email,"test","TO THE MOON")


