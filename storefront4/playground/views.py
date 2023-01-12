from django.shortcuts import render
from django.core.mail import send_mail, send_mass_mail, EmailMessage, BadHeaderError

def say_hello(request):
    try:
        # send_mail('good', 'this is food', 'amirhosseing983@gmail.com', ['amirmahdi@gmail.com'])
        message = EmailMessage("good", "this is good", 'amirhosseing983@gmail.com', ['amirmahdi@gmail.com'])
        message.attach_file('playground/media/images/new_fire.jfif')
        message.send()
    except BadHeaderError:
        pass

    return render(request, 'hello.html', {'name': 'Mosh'})
