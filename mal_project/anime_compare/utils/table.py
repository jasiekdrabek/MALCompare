from django.core.paginator import Paginator

def paginate(request,list_data, param):
    param = "page_" + param
    paginator = Paginator(list_data, 10)
    page = request.GET.get(param)
    return paginator.get_page(page)