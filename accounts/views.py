"""
Thông tin các view cơ bản
index: view này để import thông tin từ file datatest vào trong database
AccountsListView: hiển thị danh sách các account

"""

from django.shortcuts import render
from django.views.generic import (CreateView, UpdateView, DetailView, ListView, DeleteView, TemplateView)
from django.shortcuts import render
from django.template import loader
from django.contrib.auth.models import User
import openpyxl

from .models import Account
from common.models import Address, Team
from common.utils import INDCHOICES
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

def index(request):
    if "GET" ==  request.method: 
        return render(request, 'accounts/index_account.html', {})
    else:
        excel_file = request.FILES["excel_file"]

        wb = openpyxl.load_workbook(excel_file)

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
        queryset = self.model.objects.all().select_related("billing_address")
        request_post = self.request.POST
        if request_post:
            if request_post.get('name'):
                queryset = queryset.filter(name__icontains=request_post.get('name'))
            if request_post.get('city'):
                queryset = queryset.filter(
                    billing_address__in=[i.id for i in Address.objects.filter(
                        city__contains=request_post.get('city'))])
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