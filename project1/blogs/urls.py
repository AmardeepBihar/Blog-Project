from django.urls import path
from . import views
from django.contrib import admin
admin.site.site_header = 'Rams Administration'
admin.site.site_title = "Ram's Blog Login"
admin.site.index_title = 'Welcome to this Portal'
urlpatterns = [
    path('', views.Blogs, name='home'),
    path('category/<slug:slug>/', views.Categories, name='category'),
    path('post/<slug:slug>/', views.BlogDetail, name='post_detail'),
    path('search-result', views.UniversalSearch, name='searched_universaly'),
    path('contact/', views.Contact, name='contact'),
    path('about/', views.About, name='about'),
    path('declaration/', views.DeclarationPage, name='declaration'),
    path('privacy-policy/', views.PrivacyPolicy, name='privacyandpolicy'),
    path('feedback/', views.Feedback, name='feedback'),
    path('author-detail/', views.AuthorDetail, name='author-detail'),
    path('all-test-series/', views.TestSeriesList, name='test-series'),
    path('category-wise-question/<slug:slug>/', views.CategoriesWiseQuestion, name='category-wise-question'),
    path('all-sub-category-test/', views.SubCategoryList, name='sub-category-test'),
    path('endpractice/', views.ResultView, name='endpractice'),
    path('update-session-results/', views.UpdateSessionResults, name='update-session-results'),
    path('question/<uuid:uid>/', views.RandomQuestion, name='ansthequestion'),
    path('sub-category-wise-question/<slug:slug>/', views.SubCategoryWiseQuestion, name='sub-category-wise-question'),
    path('purpose-wise-question/<slug:slug>/', views.PurposeWiseQuestion, name='purpose-wise-question'),
    
]   