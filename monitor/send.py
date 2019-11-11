# 简单邮件传输协议
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(html):
    HOST = 'smtp.qq.com' # 邮箱域名
    SUBJECT = '蛛蛛给您汇报爬虫运行情况' # 邮件主题
    FROM = '943870433@qq.com' # 发件人邮箱
    TO = 'zhangzhenxing527@163.com' # 收件人邮箱
    message = MIMEMultipart('related')

    # 发送邮件主体到对方的邮箱中
    message_html = MIMEText(html, 'html', 'utf-8')
    message.attach(message_html)

    # 设置邮件发件人
    message['From'] = ''
    # 设置邮件收件人
    message['To'] = TO
    # 设置邮件标题
    message['Subject'] = SUBJECT

    # 获取简单邮件传输协议的证书
    email_client = smtplib.SMTP_SSL()
    # 设置发件人邮箱的域名和端口，端口为465
    email_client.connect(HOST, '465')

    # ---------------------------邮箱授权码------------------------------
    result = email_client.login(FROM, 'mpdhogbjlgelbeef')
    print('登录结果', result)
    email_client.sendmail(from_addr=FROM, to_addrs=TO.split(','), msg=message.as_string())
    # 关闭邮件发送客户端
    email_client.close()

if __name__ == '__main__':
    html = ''
    send_email(html)