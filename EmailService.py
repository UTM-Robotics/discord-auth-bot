import smtplib as smt
from email.message import EmailMessage
from email.mime.text import MIMEText
import ssl

class EmailService():
    """
    A email_bot to send emails. Configured to use Gmail account.

    Attributes:

    sender : Email-id to send the email from
    password : Password of the sender email
    
    Add comment for email setup process to use the bot.
    Add support for other account types.
    Add exception handling.
    """
    sender : str
    password : str


    def __init__(self, sender:str, password:str) -> None:
        """
        Initiates the bot with proper email account.
        :param sender: 
        :param password: 
        """
        self.sender = sender
        self.password = password

    def sendmail(self, receiver:str, subject:str, body:str) -> bool:
        """
        Send a email to the receiver with given subject and body text.
        :param receiver: email id of the receiver.
        :param subject: subject of the email.
        :param body: body of the email.
        :return: returns true if the email was sent successfully and 
                false otherwise.
        """
        sender = self.sender
        password = self.password
        message = 'Subject: {}\n\n{}'.format(subject, body)
        context = ssl.create_default_context()
        try:
            server = smt.SMTP('smtp.gmail.com', 587)
            server.ehlo()
            server.starttls()
            server.ehlo()

            text_type = 'plain' # or 'html'
            mime = MIMEText(body, text_type, 'utf-8')
            mime['Subject'] = subject
            mime['From'] = sender
            mime['To'] = receiver
            server.login(sender, password)
            server.sendmail(sender, receiver, mime.as_string())
            return True
        except Exception as e:
            print(e)
            print(self.sender)
            print(self.password)
            return False
