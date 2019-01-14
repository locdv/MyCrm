"""
Thông tin các view cơ bản
index: view này để import thông tin từ file datatest vào trong database
LeadsListView: hiển thị danh sách các lead
CreateLeadView: cho phép tạo một lead mới
UpdateLeadView: cho phép cập nhật thông tin cho lead
UpdateLeadView: hiển thị thông tin chi tiết cho một lead
DeleteLeadView: xóa một lead
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

from .models import Lead
from accounts.forms import AccountForm
from common.models import Address, Team
from common.utils import  INDCHOICES, COUNTRIES, CURRENCY_CODES, CASE_TYPE, PRIORITY_CHOICE, STATUS_CHOICE
from opportunity.models import Opportunity, STAGES, SOURCES
from common.forms import BillingAddressForm, ShippingAddressForm
from contacts.models import Contact
from cases.models import Case
from opportunity.models import Opportunity
# Create your views here.


def FindLeadByTenKhachHang(tenKhachHang):
    """ Tìm kiếm account bởi tên khách hàng
    return None nếu không tìm thấy
    Ngược lại trả về một object
    """
    khachHangs = Lead.objects.filter(first_name=tenKhachHang)
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


def AddLead(row_data):
    """
    create Lead từ một row data trong file
    """
    stt = row_data[0]
    FirstName = row_data[1]
    lastName = row_data[2]
    email = row_data[3]
    dienthoai = row_data[4]
    status = row_data[5]
    source = row_data[6]
    diachi = row_data[7]
    website = row_data[8]
    description = row_data[9]
    assigned_to = row_data[10]
    teamName = row_data[11]
    print(FirstName)
    lead = FindLeadByTenKhachHang(FirstName)
    if lead is None:
        lead = Lead()
    
    address = AddAddress(diachi)
    team = AddTeam(teamName)
    #update thông tin lead
    lead.first_name = FirstName
    lead.last_name = lastName
    lead.email = email
    lead.status = status
    lead.phone = dienthoai
    lead.address = address
    lead.website = website
    lead.created_by = User.objects.get(pk=1)
    lead.save()
def index(request):
    if "GET" ==  request.method: 
        return render(request, 'leads/index_lead.html', {})
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
                AddLead(row_data)

            index = index + 1
            excel_data.append(row_data)
        return render(request, 'leads/index_lead.html', {"excel_data":excel_data})


class LeadsListView(TemplateView):
    model = Lead
    context_object_name = "leads_list"
    template_name = "leads/list_leads.html"

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
        context = super(LeadsListView, self).get_context_data(**kwargs)
        context["leads_list"] = self.get_queryset()
        context["industries"] = INDCHOICES
        context["per_page"] = self.request.POST.get('per_page')
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

class CreateLeadView(CreateView):
    model = Lead
    form_class = AccountForm
    template_name  = "accounts/create_account.html"
    def dispatch(self, request, *args, **kwargs):
        self.users = User.objects.filter(is_active=True).order_by('email')
        return super(CreateLeadView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(CreateLeadView, self).get_form_kwargs()
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
        context = super(CreateLeadView, self).get_context_data(**kwargs)
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

class DetailLeadView(DetailView):
    model = Lead
    context_object_name = "account_record"
    template_name = "accounts/view_account.html"

    def get_context_data(self, **kwargs):
        context = super(DetailLeadView, self).get_context_data(**kwargs)
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
class UpdateLeadView(UpdateView):
    model = Lead
    form_class = AccountForm
    template_name = "accounts/update_account.html"

    def dispatch(self, request, *args, **kwargs):
        self.users = User.objects.filter(is_active=True).order_by('email')
        return super(UpdateLeadView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(UpdateLeadView, self).get_form_kwargs()
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
        context = super(UpdateLeadView, self).get_context_data(**kwargs)
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


class DeleteLeadView(DeleteView):
    model = Lead
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