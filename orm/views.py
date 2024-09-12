import logging
from django.contrib.auth.mixins import PermissionRequiredMixin
from slick_reporting.views import ListReportView
from orm.models import UserProfile, Portfolio
from django.core.exceptions import PermissionDenied
from . import models

# Set up logging
logger = logging.getLogger(__name__)

class RiskDetailReport(PermissionRequiredMixin, ListReportView):
    permission_required = 'orm.view_risk_report'
    report_model = models.Risk
    report_title = "Risk Detail Report"
    filters = [
        "owners", 
        "portfolio", 
        # Αν χρειάζεται, προσθέστε περισσότερα φίλτρα εδώ
    ]
    export_formats = []  # Disables the export button
    
    columns = [
        "title",
        "description",
        "category__name",  # Εμφανίζουμε και την κατηγορία του κινδύνου στις λεπτομέρειες

        "inherent_likelihood",
        "inherent_impact",
        "residual_likelihood",
        "residual_impact",
        "targeted_likelihood",
        "targeted_impact",
    ]
    
    csv_export_class = False
    
    def get_queryset(self):
        user_profile = UserProfile.objects.get(user=self.request.user)
        user_portfolios = Portfolio.objects.filter(user_profiles=user_profile)

        queryset = self.report_model.objects.filter(portfolio__in=user_portfolios).order_by('-id')
        return queryset

    def handle_no_permission(self):
        logger.warning(f"Permission denied for user {self.request.user} attempting to access RiskDetailReport.")
        raise PermissionDenied("You do not have permission to view this report.")



from slick_reporting.views import ReportView
from slick_reporting.fields import ComputationField
from slick_reporting.views import Chart
from django.db.models import Count
from orm.models import UserProfile, Portfolio, Risk
from django.contrib.auth.mixins import PermissionRequiredMixin

from slick_reporting.views import ReportView
from slick_reporting.fields import ComputationField
from slick_reporting.views import Chart
from django.db.models import Count
from orm.models import UserProfile, Portfolio

class RiskCategoryChartView(PermissionRequiredMixin, ReportView):
    permission_required = 'orm.view_risk_report'
    report_title = "Risks per Category"

    report_model = models.Risk
    group_by = "category__name"  # Ομαδοποίηση ανά κατηγορία κινδύνου
    csv_export_class = False

    # Οι στήλες περιλαμβάνουν τώρα τα πεδία υπολογισμού
    columns = [
        "category__name",  # Όνομα κατηγορίας
        ComputationField.create(
            method=Count,
            field="id",
            name="number_of_risks",
            verbose_name="Total Number of Risks per Category",
        ),
        
    ]

    chart_settings = [
        Chart(
            "Total Number of Risks per Category",
            Chart.BAR,  # Αλλαγή σε ραβδόγραμμα (Bar Chart)
            data_source=["number_of_risks"],
            title_source="category__name",
            plot_total=True,
        ),
        Chart(
            "Total Number of Risks per Category",
            Chart.PIE,  # Διάγραμμα πίτας
            data_source=["number_of_risks"],
            title_source="category__name",
        ),
        
    ]

    def get_queryset(self):
        user_profile = UserProfile.objects.get(user=self.request.user)
        user_portfolios = Portfolio.objects.filter(user_profiles=user_profile)

        queryset = self.report_model.objects.filter(portfolio__in=user_portfolios)
        return queryset


from slick_reporting.views import ReportView
from slick_reporting.fields import ComputationField
from slick_reporting.views import Chart
from django.db.models import Count
from orm.models import UserProfile, Portfolio, Risk
from django.contrib.auth.mixins import PermissionRequiredMixin

class RiskByPortfolioView(PermissionRequiredMixin, ReportView):
    permission_required = 'orm.view_risk_report'
    report_title = "Risks per Portfolio"

    report_model = Risk
    group_by = "portfolio__name"  # Ομαδοποίηση ανά χαρτοφυλάκιο
    csv_export_class = False

    columns = [
        "portfolio__name",  # Όνομα χαρτοφυλακίου
        ComputationField.create(
            method=Count,
            field="title",  # Χρησιμοποιούμε το "title" για να μετρήσουμε τους κινδύνους
            name="number_of_risks_per_portfolio",
            verbose_name="Total Number of Risks per Portfolio",
        ),
    ]

    chart_settings = [
        Chart(
            "Total Number of Risks per Portfolio",
            Chart.BAR,  # Ραβδόγραμμα
            data_source=["number_of_risks_per_portfolio"],
            title_source="portfolio__name",
            plot_total=True,
        ),
        Chart(
            "Risk Distribution by Portfolio",
            Chart.PIE,  # Διάγραμμα πίτας
            data_source=["number_of_risks_per_portfolio"],
            title_source="portfolio__name",
        ),
    ]

    def get_queryset(self):
        user_profile = UserProfile.objects.get(user=self.request.user)
        user_portfolios = Portfolio.objects.filter(user_profiles=user_profile)
        queryset = self.report_model.objects.filter(portfolio__in=user_portfolios)
        return queryset






import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from matplotlib.colors import ListedColormap, BoundaryNorm
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import UserProfile, Portfolio, Risk
from datetime import datetime
from django.urls import reverse

@login_required
def interactive_heatmap_view(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        raise PermissionDenied("You do not have a profile associated with your account.")

    # Get all portfolios associated with the user
    all_portfolios = Portfolio.objects.filter(user_profiles=user_profile)

    # Extract portfolio IDs from query parameters
    portfolio_ids = request.GET.getlist('portfolios')
    
    # Filter portfolios based on the user's selection or show all available portfolios
    if portfolio_ids:
        user_portfolios = Portfolio.objects.filter(id__in=portfolio_ids, user_profiles=user_profile)
    else:
        user_portfolios = all_portfolios

    if not user_portfolios.exists():
        raise PermissionDenied("You do not have access to any portfolios.")

    # Handle AJAX request for risk details
    if request.GET.get('risk_type'):
        return get_risk_details(
            request, 
            request.GET['risk_type'], 
            int(request.GET['likelihood']), 
            int(request.GET['impact']),
            user_portfolios  # Pass the filtered portfolios queryset
        )

    # Get the names of all portfolios the user has access to
    portfolio_names = ", ".join([portfolio.name for portfolio in user_portfolios])

    # Get the current date
    current_date = datetime.now().strftime("%Y-%m-%d")

    # Initialize the 5x5 matrices for counting risks
    inherent_data = [[[] for _ in range(5)] for _ in range(5)]
    residual_data = [[[] for _ in range(5)] for _ in range(5)]
    targeted_data = [[[] for _ in range(5)] for _ in range(5)]

    inherent_scores = np.array([[1, 2, 3, 4, 5], [2, 4, 6, 8, 10], [3, 6, 9, 12, 15], [4, 8, 12, 16, 20], [5, 10, 15, 20, 25]])
    residual_scores = inherent_scores
    targeted_scores = inherent_scores

    risks = Risk.objects.filter(portfolio__in=user_portfolios)

    # Populate the heatmap data
    for risk in risks:
        inherent_data[risk.inherent_likelihood - 1][risk.inherent_impact - 1].append(risk)
        residual_data[risk.residual_likelihood - 1][risk.residual_impact - 1].append(risk)
        targeted_data[risk.targeted_likelihood - 1][risk.targeted_impact - 1].append(risk)

    # Generate a single set of heatmaps for all portfolios combined
    inherent_html = generate_interactive_heatmap(f"Inherent Risk Heatmap for Portfolios: {portfolio_names} (as of {current_date})", inherent_data, inherent_scores, 'inherent', request)
    residual_html = generate_interactive_heatmap(f"Residual Risk Heatmap for Portfolios: {portfolio_names} (as of {current_date})", residual_data, residual_scores, 'residual', request)
    targeted_html = generate_interactive_heatmap(f"Targeted Risk Heatmap for Portfolios: {portfolio_names} (as of {current_date})", targeted_data, targeted_scores, 'targeted', request)

    # Embedding JavaScript directly within the HTML
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Portfolio Risk Heatmaps</title>
        <style>
            #riskDetails {{
                position: fixed;
                top: 100px;
                right: 20px;
                width: 300px;
                height: 80%;
                overflow-y: auto;
                background-color: #f9f9f9;
                padding: 10px;
                border: 1px solid #ccc;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }}
            h2 {{
                word-wrap: break-word;
                max-width: 100%;
            }}
            .report-date {{
                font-size: 14px;
                font-style: italic;
                margin-bottom: 10px;
            }}
        </style>
        <script>
            function showRiskDetails(riskType, likelihood, impact) {{
                var selectedPortfolios = [];
                var options = document.getElementById('portfolios').options;
                for (var i = 0; i < options.length; i++) {{
                    if (options[i].selected) {{
                        selectedPortfolios.push(options[i].value);
                    }}
                }}

                var xhr = new XMLHttpRequest();
                xhr.open('GET', window.location.pathname + '?risk_type=' + riskType + '&likelihood=' + likelihood + '&impact=' + impact + '&portfolios=' + selectedPortfolios.join('&portfolios='), true);
                xhr.onload = function() {{
                    if (xhr.status >= 200 && xhr.status < 400) {{
                        var data = JSON.parse(xhr.responseText);
                        var html = "<ul>";
                        data.forEach(function(risk) {{
                            html += '<li><a href="' + risk.link + '" target="_blank"><strong>' + risk.title + '</strong></a><br>Portfolio: ' + risk.portfolio + '</li>';
                        }});
                        html += "</ul>";
                        document.getElementById('riskDetails').innerHTML = html;
                    }} else {{
                        document.getElementById('riskDetails').innerHTML = '<p>An error occurred while fetching risk details.</p>';
                    }}
                }};
                xhr.onerror = function() {{
                    document.getElementById('riskDetails').innerHTML = '<p>An error occurred while fetching risk details.</p>';
                }};
                xhr.send();
            }}
        </script>
    </head>
    <body>
        <h1>Portfolio Risk Heatmaps</h1>
        <div class="report-date">Report generated on: {current_date}</div>
        
        <form id="portfolioForm" action="" method="get">
            <label for="portfolios">Select Portfolios:</label><br>
            <select name="portfolios" id="portfolios" multiple>
                {"".join([f'<option value="{portfolio.id}" {"selected" if str(portfolio.id) in portfolio_ids else ""}>{portfolio.name}</option>' for portfolio in all_portfolios])}
            </select><br><br>
            <input type="submit" value="Update Heatmap">
        </form>

        <div>
            <h2>Inherent Risk Heatmap</h2>
            {inherent_html}
        </div>
        <div>
            <h2>Residual Risk Heatmap</h2>
            {residual_html}
        </div>
        <div>
            <h2>Targeted Risk Heatmap</h2>
            {targeted_html}
        </div>
        <div id="riskDetails">
            <h2>Risk Details</h2>
            <p>Click on a heatmap cell to see details.</p>
        </div>
    </body>
    </html>
    """

    return HttpResponse(full_html)


from django.urls import reverse

def get_risk_details(request, risk_type, likelihood, impact, user_portfolios):
    risks = Risk.objects.filter(
        portfolio__in=user_portfolios,
        **{f'{risk_type}_likelihood': likelihood, f'{risk_type}_impact': impact}
    )

    risk_details = [
        {
            'title': risk.title,
            'portfolio': risk.portfolio.name,
            'link': f'/orm/risk/{risk.id}/change/'  # Manually construct the link
        }
        for risk in risks
    ]

    return JsonResponse(risk_details, safe=False)




def generate_interactive_heatmap(title, data, score_data, risk_type, request):
    def risk_color(score):
        if score >= 1 and score <= 6:
            return 'green'
        elif score >= 8 and score <= 12:
            return 'yellow'
        elif score >= 15 and score <= 25:
            return 'red'
        else:
            return 'white'

    bounds = [0, 6, 12, 25]
    colors = ['green', 'yellow', 'red']
    cmap = ListedColormap(colors)
    norm = BoundaryNorm(bounds, cmap.N)

    plt.figure(figsize=(6, 4))

    ax = sns.heatmap(
        score_data[::-1],  # Reverse the y-axis data
        annot=False, 
        cmap=cmap, 
        norm=norm, 
        fmt="d", 
        linewidths=.5, 
        cbar=False
    )

    ax.set_title(title, fontsize=7, weight='normal', wrap=True)
    ax.set_xlabel('Impact', fontsize=10)
    ax.set_ylabel('Likelihood', fontsize=10)
    ax.set_xticklabels(['1', '2', '3', '4', '5'], fontsize=8)
    ax.set_yticklabels(['5', '4', '3', '2', '1'], rotation=0, fontsize=8)  # Reverse the labels

    for i in range(5):
        for j in range(5):
            score = score_data[::-1][i][j]  # Use reversed score_data
            count = len(data[::-1][i][j])  # Use reversed data for counting risks
            if count > 0:
                ax.text(j + 0.5, i + 0.5, f'{score}\n({count})', 
                        ha='center', va='center', color='black', fontsize=10, weight='bold')

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    buffer.seek(0)

    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    image_html = f"<img src='data:image/png;base64,{image_base64}' alt='{title}' usemap='#{risk_type}_map'>"

    width, height = 600, 400  # Assuming 600x400 is the figure size in pixels
    cell_width = width / 5
    cell_height = height / 5

    map_html = f"<map name='{risk_type}_map'>"
    for i in range(5):
        for j in range(5):
            if len(data[::-1][i][j]) > 0:  # Use reversed data for map areas
                x1, y1 = j * cell_width, i * cell_height
                x2, y2 = (j + 1) * cell_width, (i + 1) * cell_height
                map_html += f"<area shape='rect' coords='{x1},{y1},{x2},{y2}' " \
                            f"href='#' onclick='showRiskDetails(\"{risk_type}\", {5-i}, {j+1});'>"
    map_html += "</map>"

    return image_html + map_html
