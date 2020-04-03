#!/usr/bin/python3
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import os
import datetime
import email.mime.application
import yaml


def mail(text, im_fle=False):
    date = datetime.date.today().strftime("%B %d, %Y")

    with open(r'mail.yaml') as file:
        server_list = yaml.load(file)

    server = server_list['server']
    username = server_list['user']
    password = server_list['password']
    port = server_list['port']
    mail_from = server_list['from']
    mail_to = server_list['to']

    smtp_server = server
    port = port  # For starttls
    sender_email = mail_from
    password = password

    # Create a secure SSL context
    context = ssl.create_default_context()

    # Try to log in to server and send email
    try:
        server = smtplib.SMTP_SSL(smtp_server, port)
        # server.starttls(context=context)  # Secure the connection
        server.login(username, password)

        msg = MIMEMultipart()
        msg['Subject'] = "Forecast - " + date
        msg['From'] = mail_from
        msg['To'] = mail_to

        txt = MIMEText(text, 'html')
        msg.attach(txt)
        # if True:
        #     img_data = open(im_fle, 'rb').read()
        #     im = MIMEImage(img_data, name=os.path.basename(im_fle))
        #     # image.add_header('Gunluk_Fotograf', 'attachment', filename=im)
        #     msg.attach(im)

        fp = open(im_fle, 'rb')
        msgImage = MIMEImage(fp.read())
        fp.close()
        msgImage.add_header('Content-ID', '<image1>')
        msg.attach(msgImage)
        server.send_message(msg, mail_from, [mail_to])
        # server.send_message(msg, "e154968@metu.edu.tr", ["cagrkaraman@gmail.com"])
        # TODO: Send email here
    except Exception as e:
        # Print any error messages to stdout
        print(e)
    finally:
        print("Mail sent")
        server.quit()


text = "Hello World"
image = '/mnt/e/Datasets/GFS/GIF/GFS_2020-04-02_temp.gif'
html = """\
<html>
  <head></head>
  <body>
    <img src="cid:image1" alt="Logo" style="width:800px;height:600px;"><br>
       <p><h4 style="font-size:15px;">Forecast.</h4></p>
    <table>
        <tbody>
            <tr>
                <td><img src="cid:image1" alt="Logo" style="width:800px;height:600px;"><br>
                    <p><h4 style="font-size:15px;">Forecast.</h4></p></td>
                <td><img src="cid:image1" alt="Logo" style="width:800px;height:600px;"><br>
                    <p><h4 style="font-size:15px;">Forecast.</h4></p></td>
            </tr>
        </tbody>
    </table>
  </body>
</html>
"""

mail(html, image)
