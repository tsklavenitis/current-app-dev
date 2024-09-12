from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from orm.admin import admin_site
from orm import views

from django.http import HttpResponse


urlpatterns = [

    path("risk_detail_report/",views.RiskDetailReport.as_view(),name="risk_detail_report"),    
    path('risk-category-charts/', views.RiskCategoryChartView.as_view(), name='risk_category_charts'),
    path('risk-by-portfolio/', views.RiskByPortfolioView.as_view(), name='risk_by_portfolio'),
    # path('portfolio-heatmap/', views.portfolio_heatmap_view, name='portfolio_heatmap'),
    path('interactive-heatmaps/', views.interactive_heatmap_view, name='interactive_heatmap'),
    path('', admin_site.urls),  # Root URL now points to the custom admin site
    path('admin/', admin.site.urls),  # Default Django admin (fallback)
    path('orm/', admin_site.urls),  # Custom admin site at a different path
    path('ckeditor/', include('ckeditor_uploader.urls')),  # CKEditor URL configuration
    path('accounts/', include('django.contrib.auth.urls')),  # Includes the default login and logout URLs
    
    # Place specific URLs before any catch-all patterns
    # Other specific URL patterns...
    
    # Place the catch-all pattern last

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
