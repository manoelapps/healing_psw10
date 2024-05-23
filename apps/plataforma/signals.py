from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings
from django.core.mail import send_mail
from .models import Analise


@receiver(post_save, sender=Analise)
def envia_email(sender, instance, created, **kwargs):

    if created:
        assunto = 'HEALING - Análise cadastro'

        mensagem_email = f"""Prezado(a) {instance.pessoa.user.username.capitalize()},
        
        Informamos que seu cadastro em nosso sistema foi {instance.get_decisao_display().upper()}.

        {instance.mensagem}

        
        Equipe de Análise do HEALING
        """

        send_mail(
            assunto,
            mensagem_email,
            settings.EMAIL_HOST_USER,
            [instance.pessoa.user.email,]
        )
