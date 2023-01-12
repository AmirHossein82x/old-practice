from django.shortcuts import render
from django.core.mail import send_mail, send_mass_mail, mail_admins, BadHeaderError, EmailMessage

# if you want to send more than one email you have to use send_mass_mail
from templated_mail.mail import BaseEmailMessage

def say_hello(request):
    try:
        # send_mail('football', 'you entered the team', 'amirhosseing983@gmail.com', ['amirmahdi@gmail.com'])

        # mail_admins('football', 'you entered the team', html_message='message')

        # message = EmailMessage('football', 'message', 'amirhosseing983@gmail.com', ['amirmahdi@gmail.com'])
        # message.attach_file('playground/static/images/download.png')
        # message.send()

        message = BaseEmailMessage(request, context={'name': 'amirhossein'}, template_name='emails/hello.html')
        message.send(['amirmahdi@gmail.com'])
    except BadHeaderError:
        pass
    return render(request, 'hello.html', {'name': 'Mosh'})
