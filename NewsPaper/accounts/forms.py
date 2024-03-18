from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group


class CustomSignupForm(SignupForm):
    def save(self, request):
        user = super().save(request) #переопределить только метод save(), который выполняется при успешном заполнении формы регистрации
        common_users = Group.objects.get(name="authors")
        user.groups.add(common_users)
        return user #Обязательным требованием метода save() является возвращение объекта модели User по итогу выполнения функции.


