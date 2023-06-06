#!/usr/bin/env python3

from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_mail():
    try:

        mail = SMTP("smtp.gmail.com",587)
        mail.ehlo()
        mail.starttls()
        MailAdress = "hsnzfdn@gmail.com"
        password = "psutgsmeqrmmclci"
        mail.login(MailAdress, password)

        mesaj = MIMEMultipart()
        mesaj["From"] = "hsnzfdn@gmail.com"           # Gönderen
        mesaj["To"] = " Eriskaan@outlook.com"          # Alıcı
        mesaj["Subject"] = "ADAS Alarm"    # Konusu

        body = """
        Sürücü uyuyor ve yolda trafiği tehlikeye atacak düzeyde sürüs gerceklestiriliyor. Arac durduruldu, hayati durum olabilir!!!.

        """

        body_text = MIMEText(body, "plain")  #
        mesaj.attach(body_text)

        mail.sendmail(mesaj["From"], mesaj["To"], mesaj.as_string())
        print("Mail başarılı bir şekilde gönderildi.")
        mail.close()

    except Exception as e:
        print('HATA')

send_mail()