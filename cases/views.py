"""
Thông tin các view cơ bản
index: view này để import thông tin từ file datatest vào trong database
CasesListView: hiển thị danh sách các case
CreateCaseView: cho phép tạo một case mới
UpdateCaseView: cho phép cập nhật thông tin cho case
DetailCaseView: hiển thị thông tin chi tiết cho một case
DeleteCaseView: xóa một case
"""
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.shortcuts import render
from django.views.generic import (CreateView, UpdateView, DetailView, ListView, DeleteView, TemplateView)
from django.template import loader
from django.contrib.auth.models import User
from django.db.models import Q
import openpyxl
from phonenumber_field.modelfields import PhoneNumberField

from .models import Case
from accounts.forms import AccountForm
from .forms import CaseForm
from common.models import Address, Team, Comment, Attachments
from common.utils import  INDCHOICES, COUNTRIES, CURRENCY_CODES, CASE_TYPE, PRIORITY_CHOICE, STATUS_CHOICE, LEAD_STATUS
from opportunity.models import Opportunity, STAGES, SOURCES
from common.forms import BillingAddressForm, ShippingAddressForm
from contacts.models import Contact
from cases.models import Case
from opportunity.models import Opportunity
from accounts.models import Account
from planner.models import Event
# Create your views here.


def FindCaseByName(tenCongViec):
    """ Tìm kiếm case bởi tên ten
    return None nếu không tìm thấy
    Ngược lại trả về một object
    """
    cases = Case.objects.filter(name=tenCongViec)
    if cases.count() == 0:
        return None
    return cases[0]

def AddTeam(ten):
    """ taọ một team mới
    Nếu team đã tồn tại thì return team
    ngược lại thì tạo mới và return team đó
    """
    teams = Team.objects.filter(name = ten)
    if teams.count() == 0:
        team = Team(name=ten)
        team.save()
        return team
    
    else:
        return teams[0]

def AddAccount(name):
    """
    tạo mot accout
    """
    account = Account(name = name)
    return account


def AddContact(ten):
    """ taọ một contact mới
    Nếu contact đã tồn tại thì return contact
    ngược lại thì tạo mới và return contact đó
    """
    contacts = Contact.objects.filter(first_name = ten)
    if contacts.count() == 0:
        contact = Contact(first_name=ten)
        contact.save()
        return contact
    
    else:
        return contacts[0]

def AddCase(row_data):
    """
    create Case từ một row data trong file
    """
    stt = row_data[0]
    name = row_data[1]
    status = row_data[2]
    priority = row_data[3]
    case_type = row_data[4]
    accountName = row_data[5]
    contact = row_data[6]
    description = row_data[7]
    assigned_to = row_data[8]
    teamName = row_data[9]
   
    case = FindCaseByName(name)
    if case is None:
        case = Case()
    
    team = AddTeam(teamName)
    account = AddAccount(accountName)
    contact = AddContact(contact)
    #update thông tin case
    case.name = name
    case.status = status
    case.priority = priority
    case.case_type = case_type
    case.description = description
    case.account = account
    case.created_by = User.objects.get(pk=1)
    case.save()
    case.teams.add(team)
    case.contacts.add(contact)
def index(request):
    if "GET" ==  request.method: 
        return render(request, 'cases/index_case.html', {})
    else:
        excel_file = request.FILES["excel_file"]

        wb = openpyxl.load_workbook(excel_file, data_only=True)

        worksheet = wb["Sheet1"]
        excel_data = list()

        #loop over all row in file
        index = 0
        for row in worksheet.iter_rows():
            row_data = list()
            for cell in row:

                row_data.append(str(cell.value))
            if index > 0:
                AddCase(row_data)

            index = index + 1
            excel_data.append(row_data)
        return render(request, 'cases/index_case.html', {"excel_data":excel_data})


class CasesListView(TemplateView):
    model = Case
    context_object_name = "cases_list"
    template_name = "cases/list_cases.html"

    def get_queryset(self):
        queryset = self.model.objects.all().select_related("address").order_by('id')

        request_post = self.request.POST
        if request_post:
            #loc dữ liệu theo name
            if request_post.get('first_name'):
                queryset = queryset.filter(name__icontains=request_post.get('first_name'))
            # lọc dữ liệu theo city
            if request_post.get('city'):
                queryset = queryset.filter(
                    billing_address__in=[i.id for i in Address.objects.filter(
                        city__contains=request_post.get('city'))])
            # lọc dữ liệu theo industry
            if request_post.get('status'):
                queryset = queryset.filter(industry__icontains=request_post.get('status'))
        return queryset

    def get_context_data(self, **kwargs):
        context = super(CasesListView, self).get_context_data(**kwargs)
        context["cases_list"] = self.get_queryset()
        context["industries"] = INDCHOICES
        context["per_page"] = self.request.POST.get('per_page')
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

class CreateCaseView(CreateView):
    model = Case
    form_class = AccountForm
    template_name  = "accounts/create_account.html"
    def dispatch(self, request, *args, **kwargs):
        self.users = User.objects.filter(is_active=True).order_by('email')
        return super(CreateCaseView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(CreateCaseView, self).get_form_kwargs()
        kwargs.update({'assigned_to': self.users})
        return kwargs

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        billing_form = BillingAddressForm(request.POST)
        shipping_form = ShippingAddressForm(request.POST, prefix='ship')
        if form.is_valid() and billing_form.is_valid() and shipping_form.is_valid():
            return self.form_valid(form, billing_form, shipping_form)
        else:
            return self.form_invalid(form, billing_form, shipping_form)

    def form_valid(self, form, billing_form, shipping_form):
        # Save Billing & Shipping Address
        billing_address_object = billing_form.save()
        shipping_address_object = shipping_form.save()
        # Save Account
        account_object = form.save(commit=False)
        account_object.billing_address = billing_address_object
        account_object.shipping_address = shipping_address_object
        account_object.created_by = self.request.user
        account_object.save()
        if self.request.POST.getlist('assigned_to', []):
            account_object.assigned_to.add(*self.request.POST.getlist('assigned_to'))
            assigned_to_list = self.request.POST.getlist('assigned_to')
            current_site = get_current_site(self.request)
            for assigned_to_user in assigned_to_list:
                user = get_object_or_404(User, pk=assigned_to_user)
                mail_subject = 'Assigned to account.'
                message = render_to_string('assigned_to/account_assigned.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'protocol': self.request.scheme,
                    'account': account_object
                })
                email = EmailMessage(mail_subject, message, to=[user.email])
                email.send()
        if self.request.POST.getlist('teams', []):
            account_object.teams.add(*self.request.POST.getlist('teams'))
        if self.request.POST.get("savenewform"):
            return redirect("accounts:new_account")
        else:
            return redirect("accounts:list")

    def form_invalid(self, form, billing_form, shipping_form):
        return self.render_to_response(
            self.get_context_data(
                form=form, billing_form=billing_form, shipping_form=shipping_form)
        )

    def get_context_data(self, **kwargs):
        context = super(CreateCaseView, self).get_context_data(**kwargs)
        context["account_form"] = context["form"]
        context["users"] = self.users
        context["industries"] = INDCHOICES
        context["countries"] = COUNTRIES
        context["teams"] = Team.objects.all()
        if "billing_form" in kwargs and "shipping_form" in kwargs:
            context["billing_form"] = kwargs["billing_form"]
            context["shipping_form"] = kwargs["shipping_form"]
        else:
            if self.request.POST:
                context["billing_form"] = BillingAddressForm(self.request.POST)
                context["shipping_form"] = ShippingAddressForm(self.request.POST, prefix='ship')
            else:
                context["billing_form"] = BillingAddressForm()
                context["shipping_form"] = ShippingAddressForm(prefix='ship')
        context["assignedto_list"] = [
            int(i) for i in self.request.POST.getlist('assigned_to', []) if i]
        context["teams_list"] = [
            int(i) for i in self.request.POST.getlist('teams', []) if i]
        return context

class DetailCaseView(DetailView):
    model = Case
    context_object_name = "case_record"
    template_name = "cases/view_case.html"

    def get_context_data(self, **kwargs):
        context = super(DetailCaseView, self).get_context_data(**kwargs)
        comments = Comment.objects.filter(case_id=self.object.id).order_by('-id')
        attachments = Attachments.objects.filter(case_id=self.object.id).order_by('-id')
        events = Event.objects.filter(
            Q(created_by=self.request.user) | Q(updated_by=self.request.user)).filter(attendees_cases=context["case_record"])
        meetings = events.filter(event_type='Meeting').order_by('-id')
        calls = events.filter(event_type='Call').order_by('-id')
        
        context.update({
            "comments": comments,
            "attachments": attachments,
            "status": LEAD_STATUS,
            "meetings": meetings,
            "calls": calls,
            "countries": COUNTRIES,
        })
        return context
class UpdateCaseView(UpdateView):
    model = Case
    form_class = AccountForm
    template_name = "accounts/update_account.html"

    def dispatch(self, request, *args, **kwargs):
        self.users = User.objects.filter(is_active=True).order_by('email')
        return super(UpdateCaseView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(UpdateCaseView, self).get_form_kwargs()
        kwargs.update({'assigned_to': self.users})
        return kwargs

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        billing_form = BillingAddressForm(request.POST, instance=self.object.billing_address)
        shipping_form = ShippingAddressForm(
            request.POST, instance=self.object.shipping_address, prefix='ship')
        if form.is_valid() and billing_form.is_valid() and shipping_form.is_valid():
            return self.form_valid(form, billing_form, shipping_form)
        else:
            return self.form_invalid(form, billing_form, shipping_form)

    def form_valid(self, form, billing_form, shipping_form):
        # Save Billing & Shipping Address
        billing_address_object = billing_form.save()
        shipping_address_object = shipping_form.save()
        # Save Account
        account_object = form.save(commit=False)
        account_object.billing_address = billing_address_object
        account_object.shipping_address = shipping_address_object
        account_object.save()
        account_object.assigned_to.clear()
        account_object.teams.clear()
        if self.request.POST.getlist('assigned_to', []):
            account_object.assigned_to.add(*self.request.POST.getlist('assigned_to'))
            assigned_to_list = self.request.POST.getlist('assigned_to')
            current_site = get_current_site(self.request)
            for assigned_to_user in assigned_to_list:
                user = get_object_or_404(User, pk=assigned_to_user)
                mail_subject = 'Assigned to account.'
                message = render_to_string('assigned_to/account_assigned.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'protocol': self.request.scheme,
                    'account': account_object
                })
                email = EmailMessage(mail_subject, message, to=[user.email])
                email.send()
        if self.request.POST.getlist('teams', []):
            account_object.teams.add(*self.request.POST.getlist('teams'))
        return redirect("accounts:list")

    def form_invalid(self, form, billing_form, shipping_form):
        return self.render_to_response(
            self.get_context_data(
                form=form, billing_form=billing_form, shipping_form=shipping_form)
        )

    def get_context_data(self, **kwargs):
        context = super(UpdateCaseView, self).get_context_data(**kwargs)
        context["account_obj"] = self.object
        context["billing_obj"] = self.object.billing_address
        context["shipping_obj"] = self.object.shipping_address
        context["account_form"] = context["form"]
        context["users"] = self.users
        context["industries"] = INDCHOICES
        context["countries"] = COUNTRIES
        context["teams"] = Team.objects.all()
        if "billing_form" in kwargs and "shipping_form" in kwargs:
            context["billing_form"] = kwargs["billing_form"]
            context["shipping_form"] = kwargs["shipping_form"]
        else:
            if self.request.POST:
                context["billing_form"] = BillingAddressForm(
                    self.request.POST, instance=self.object.billing_address)
                context["shipping_form"] = ShippingAddressForm(
                    self.request.POST, instance=self.object.shipping_address, prefix='ship')
            else:
                context["billing_form"] = BillingAddressForm(
                    instance=self.object.billing_address)
                context["shipping_form"] = ShippingAddressForm(
                    instance=self.object.shipping_address, prefix='ship')
        context["assignedto_list"] = [
            int(i) for i in self.request.POST.getlist('assigned_to', []) if i]
        context["teams_list"] = [
            int(i) for i in self.request.POST.getlist('teams', []) if i]
        return context


class DeleteCaseView(DeleteView):
    model = Case
    form_class = CaseForm
    template_name = "cases/remove_case.html"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.address:
            self.object.address.delete()
       
        return redirect("cases:list")
