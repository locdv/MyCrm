"""
Thông tin các view cơ bản
index: view này để import thông tin từ file datatest vào trong database
AccountsListView: hiển thị danh sách các account
CreateAccountView: cho phép tạo một account mới
UpdateAccoutView: cho phép cập nhật thông tin cho account
UpdateAccountView: hiển thị thông tin chi tiết cho một account
DeleteAccountView: xóa một account
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
import openpyxl

from .models import Account
from .forms import AccountForm
from common.models import Address, Team
from common.utils import  INDCHOICES, COUNTRIES, CURRENCY_CODES, CASE_TYPE, PRIORITY_CHOICE, STATUS_CHOICE
from opportunity.models import Opportunity, STAGES, SOURCES
from common.forms import BillingAddressForm, ShippingAddressForm
from contacts.models import Contact
from cases.models import Case
from opportunity.models import Opportunity
# Create your views here.


def FindAccountByTenKhachHang(tenKhachHang):
    """ Tìm kiếm account bởi tên khách hàng
    return None nếu không tìm thấy
    Ngược lại trả về một object
    """
    khachHangs = Account.objects.filter(name=tenKhachHang)
    if khachHangs.count() == 0:
        return None
    return khachHangs[0]

def AddAddress(diachi):
    """ tạo một địa chỉ mới
    Thêm địa chỉ mới vào trong database
    trả về địa chỉ được tạo

    """
    address = Address(address_line = diachi)
    address.save()
    return address

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


def AddAccount(row_data):
    """
    create Account từ một row data trong file
    """
    stt = row_data[0]
    tenkhachhang = row_data[1]
    email = row_data[2]
    dienthoai = row_data[3]
    industry = row_data[4]
    bill_diachi = row_data[5]
    ship_diachi = row_data[6]
    assigned_to = row_data[7]
    teamName = row_data[8]
    website = row_data[9]
    account = FindAccountByTenKhachHang(tenkhachhang)
    if account is None:
        account = Account()
    
    bill_address = AddAddress(bill_diachi)
    ship_address = AddAddress(ship_diachi)
    team = AddTeam(teamName)
    #update thông tin acccount
    account.name = tenkhachhang
    account.email = email
    account.phone = dienthoai
    account.industry = industry
    account.billing_address = bill_address
    account.ship_address = ship_address
    account.website = website
    account.created_by = User.objects.get(pk=1)
    account.save()
    account.teams.add(team)

def index(request):
    if "GET" ==  request.method: 
        return render(request, 'accounts/index_account.html', {})
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
                AddAccount(row_data)

            index = index + 1
            excel_data.append(row_data)
        return render(request, 'accounts/index_account.html', {"excel_data":excel_data})


class AccountsListView(TemplateView):
    model = Account
    context_object_name = "accounts_list"
    template_name = "accounts/list_accounts.html"

    def get_queryset(self):
        queryset = self.model.objects.all().select_related("billing_address").order_by('id')

        request_post = self.request.POST
        if request_post:
            #loc dữ liệu theo name
            if request_post.get('name'):
                queryset = queryset.filter(name__icontains=request_post.get('name'))
            # lọc dữ liệu theo city
            if request_post.get('city'):
                queryset = queryset.filter(
                    billing_address__in=[i.id for i in Address.objects.filter(
                        city__contains=request_post.get('city'))])
            # lọc dữ liệu theo industry
            if request_post.get('industry'):
                queryset = queryset.filter(industry__icontains=request_post.get('industry'))
        return queryset

    def get_context_data(self, **kwargs):
        context = super(AccountsListView, self).get_context_data(**kwargs)
        context["accounts_list"] = self.get_queryset()
        context["industries"] = INDCHOICES
        context["per_page"] = self.request.POST.get('per_page')
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

class CreateAccountView(CreateView):
    model = Account
    form_class = AccountForm
    template_name  = "accounts/create_account.html"
    def dispatch(self, request, *args, **kwargs):
        self.users = User.objects.filter(is_active=True).order_by('email')
        return super(CreateAccountView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        # set giá trị cho 'assigned_to' của kwargs
        kwargs = super(CreateAccountView, self).get_form_kwargs()
        kwargs.update({'assigned_to': self.users})
        return kwargs

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        billing_form = BillingAddressForm(request.POST)
        shipping_form = ShippingAddressForm(request.POST, prefix='ship')
        if form.is_valid(): #and billing_form.is_valid() and shipping_form.is_valid():
            print("form valid")
            
            return self.form_valid(form, billing_form, shipping_form)
        else:
            print("form invalid")
            print(form.errors)
            # for field, errors in form.errors.items:
            #     for error in errors:
            #         print(field, error)


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
        context = super(CreateAccountView, self).get_context_data(**kwargs)
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

class DetailAccountView(DetailView):
    model = Account
    context_object_name = "account_record"
    template_name = "accounts/view_account.html"

    def get_context_data(self, **kwargs):
        context = super(DetailAccountView, self).get_context_data(**kwargs)
        account_record = context["account_record"]
        if (
            self.request.user in account_record.assigned_to.all() or
            self.request.user == account_record.created_by
        ):
            comment_permission = True
        else:
            comment_permission = False
        context.update({
            "comments": account_record.accounts_comments.all(),
            "attachments": account_record.account_attachment.all(),
            "opportunity_list": Opportunity.objects.filter(account=account_record),
            "contacts": Contact.objects.filter(account=account_record),
            "users": User.objects.filter(is_active=True).order_by('email'),
            "cases": Case.objects.filter(account=account_record),
            "teams": Team.objects.all(),
            "stages": STAGES,
            "sources": SOURCES,
            "countries": COUNTRIES,
            "currencies": CURRENCY_CODES,
            "case_types": CASE_TYPE,
            "case_priority": PRIORITY_CHOICE,
            "case_status": STATUS_CHOICE,
            'comment_permission': comment_permission,
        })
        return context
class UpdateAccountView(UpdateView):
    model = Account
    form_class = AccountForm
    template_name = "accounts/update_account.html"

    def dispatch(self, request, *args, **kwargs):
        self.users = User.objects.filter(is_active=True).order_by('email')
        return super(UpdateAccountView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(UpdateAccountView, self).get_form_kwargs()
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
        context = super(UpdateAccountView, self).get_context_data(**kwargs)
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


class DeleteAccountView(DeleteView):
    model = Account
    form_class = AccountForm
    template_name = "accounts/remove_account.html"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.billing_address:
            self.object.billing_address.delete()
        if self.object.shipping_address:
            self.object.shipping_address.delete()
        self.object.delete()
        return redirect("accounts:list")