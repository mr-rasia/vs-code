import smtplib
from email.message import EmailMessage
msg = EmailMessage()


server = smtplib.SMTP('smtp.gmail.com',587)
server.serttls()
server.login("anurag.chaurasia@cloudkeeper.com", "epzj hmgs dmsb kbna")

msg['From'] = "anurag.chaurasia@cloudkeeper.com"
msg["To"] = "receiver_email"
msg["Subject"] = "subject"