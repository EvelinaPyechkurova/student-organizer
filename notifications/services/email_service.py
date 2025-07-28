from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from utils.constants import EVENT_TYPE_SPECIFIC_EMAIL_MESSAGES

TEXT_TEMPLATE_PATH = 'notifications/email.txt'
HTML_TEMPLATE_PATH = 'notifications/email.html'

def build_email_context(base_context):
    context = base_context.copy()
    print(context)
    context['event_type_specific_message'] = EVENT_TYPE_SPECIFIC_EMAIL_MESSAGES[context['event_type']]
    return context

def render_email_templates(context):
    text_content = render_to_string(TEXT_TEMPLATE_PATH, context)
    html_content = render_to_string(HTML_TEMPLATE_PATH, context)
    return text_content, html_content    

def build_email_message(context, text_content, html_content):
    msg = EmailMultiAlternatives(
        f'{context['title']} Reminder',
        text_content,
        'address@gmail.com',
        ['address.com'],
    )
    msg.attach_alternative(html_content, "text/html")
    return msg

def send_email(context):
    context = build_email_context(context)
    text_content, html_content = render_email_templates(context)
    msg = build_email_message(context, text_content, html_content)
    msg.send()
    print(f'Sending email: {text_content}')