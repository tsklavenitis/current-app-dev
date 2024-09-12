import matplotlib
matplotlib.use('Agg')  # Use 'Agg' backend for non-interactive plots

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin, GroupAdmin
from django.contrib.auth.models import User, Group
from django import forms
from django.core.exceptions import ValidationError
from django.utils.html import format_html, mark_safe, strip_tags
from django.http import HttpResponse, HttpResponseForbidden
from django.urls import path, reverse
from django.template.loader import render_to_string
import io
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import UserProfile, Risk, Portfolio, Category, Mitigation, Action, Indicator, Event, ApprovalRequest, RiskScoreHistory, IndicatorValueHistory, Procedure,AssessmentHistory,RiskAssessment,RiskSnapshot
from django.utils import timezone
import logging
from django.contrib import messages

class AssessmentHistoryInline(admin.TabularInline):
    model = AssessmentHistory
    extra = 0
    readonly_fields = ('date', 'assessor',)



# Define resources for import-export
class UserProfileResource(resources.ModelResource):
    class Meta:
        model = UserProfile
        encoding = 'utf-8'

class PortfolioResource(resources.ModelResource):
    class Meta:
        model = Portfolio
        export_order = ('id', 'name', 'description')
        encoding = 'utf-8'

class CategoryResource(resources.ModelResource):
    class Meta:
        model = Category
        export_order = ('id', 'name', 'description')
        encoding = 'utf-8'

class MitigationResource(resources.ModelResource):
    owner = fields.Field(column_name='owner', attribute='owner', widget=ForeignKeyWidget(UserProfile, 'user__username'))

    class Meta:
        model = Mitigation
        export_order = ('id', 'title', 'description', 'owner', 'portfolio', 'effectiveness')
        encoding = 'utf-8'

class ActionResource(resources.ModelResource):
    owner = fields.Field(column_name='owner', attribute='owner', widget=ForeignKeyWidget(UserProfile, 'user__username'))
    performer = fields.Field(column_name='performer', attribute='performer', widget=ForeignKeyWidget(UserProfile, 'user__username'))

    class Meta:
        model = Action
        export_order = ('id', 'title', 'description', 'owner', 'performer', 'deadline', 'portfolio')
        encoding = 'utf-8'

class IndicatorResource(resources.ModelResource):
    class Meta:
        model = Indicator
        encoding = 'utf-8'

class EventResource(resources.ModelResource):
    class Meta:
        model = Event
        encoding = 'utf-8'

class RiskResource(resources.ModelResource):
    class Meta:
        model = Risk
        encoding = 'utf-8'

class IndicatorValueHistoryResource(resources.ModelResource):
    class Meta:
        model = IndicatorValueHistory
        encoding = 'utf-8'

class RiskScoreHistoryResource(resources.ModelResource):
    class Meta:
        model = RiskScoreHistory
        encoding = 'utf-8'

class ApprovalRequestResource(resources.ModelResource):
    class Meta:
        model = ApprovalRequest
        encoding = 'utf-8'

class ProcedureResource(resources.ModelResource):
    class Meta:
        model = Procedure
        encoding = 'utf-8'

# Custom admin site
class CustomAdminSite(admin.AdminSite):
    site_header = ''
    site_title = ''
    index_title = 'Welcome'
    
    class Media:
        css = {
            'all': (
                #  'orm/css/custom_admin.css',  # Load custom CSS first
            ),
        }
    
    def each_context(self, request):
            # Get the default context
            context = super().each_context(request)
            # Add the CSS files to the context
            context['custom_css'] = '/static/css/custom_admin.css'
            return context

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('approvalrequest/<int:pk>/change/', self.admin_view(self.change_approval_request), name='approvalrequest_change'),
        ]
        return custom_urls + urls

    # def download_risk_score_graph(self, request, risk_id):
    #     try:
    #         risk = Risk.objects.get(pk=risk_id)
    #     except Risk.DoesNotExist:
    #         return HttpResponse("Risk not found", content_type='text/plain')

    #     inherent_scores = risk.score_history.filter(score_type='inherent').order_by('timestamp')
    #     residual_scores = risk.score_history.filter(score_type='residual').order_by('timestamp')
    #     targeted_scores = risk.score_history.filter(score_type='targeted').order_by('timestamp')

    #     dates = [score.timestamp for score in inherent_scores]
    #     inherent_values = [score.score for score in inherent_scores]
    #     residual_values = [score.score for score in residual_scores]
    #     targeted_values = [score.score for score in targeted_scores]

    #     if dates and (inherent_values or residual_values or targeted_values):
    #         fig, ax = plt.subplots()
    #         if inherent_values:
    #             ax.plot(dates, inherent_values, marker='o', label='Inherent Score', color='blue')
    #         if residual_values:
    #             ax.plot(dates, residual_values, marker='o', label='Residual Score', color='lightblue')
    #         if targeted_values:
    #             ax.plot(dates, targeted_values, marker='o', label='Targeted Score', color='darkblue')
    #         ax.set_title(f'Score Trends for {risk.title}')
    #         ax.set_xlabel('Date')
    #         ax.set_ylabel('Score')
    #         ax.legend()

    #         buffer = io.BytesIO()
    #         plt.savefig(buffer, format='png')
    #         plt.close(fig)
    #         buffer.seek(0)

    #         response = HttpResponse(buffer.read(), content_type='image/png')
    #         response['Content-Disposition'] = f'attachment; filename="risk_score_graph_{risk_id}.png"'
    #         return response

    #     return HttpResponse("No data available", content_type='text/plain')

    def change_approval_request(self, request, pk):
        return self.admin_view(self.approval_request_change_view)(request, pk)

    def approval_request_change_view(self, request, pk):
        approval_request = ApprovalRequest.objects.get(pk=pk)
        return self.change_view(request, object_id=str(pk), model=ApprovalRequest, extra_context={'approval_request': approval_request})

admin_site = CustomAdminSite(name='orm_admin')


class MitigationInlineForm(forms.ModelForm):
    class Meta:
        model = Risk.mitigations.through  # Adjust this to your actual model connection
        fields = ['mitigation']  # Only include the mitigation field (dropdown)

class MitigationInline(admin.TabularInline):
    model = Risk.mitigations.through  # Adjust to your actual model connection
    form = MitigationInlineForm
    extra = 0
    fields = ('mitigation', 'formatted_description')  # Include dropdown and formatted description
    readonly_fields = ('formatted_description',)  # Make description read-only

    def formatted_description(self, obj):
        if obj and obj.mitigation and obj.mitigation.description:
            return format_html(obj.mitigation.description)  # Render HTML as is without sanitization
        return ""

    formatted_description.short_description = 'Mitigation Description'

class ActionInlineForm(forms.ModelForm):
    class Meta:
        model = Risk.actions.through  # Adjust to your actual model connection
        fields = ['action']  # Only include the action field (dropdown)

class ActionInline(admin.TabularInline):
    model = Risk.actions.through
    form = ActionInlineForm
    extra = 0
    fields = ('action', 'formatted_description')
    readonly_fields = ('formatted_description',)

    def formatted_description(self, obj):
        if obj and obj.action and obj.action.description:
            return format_html(obj.action.description)
        return ""

    formatted_description.short_description = 'Action Description'

class IndicatorInlineForm(forms.ModelForm):
    class Meta:
        model = Risk.indicators.through  # Adjust this to your actual model connection
        fields = ['indicator']  # Only include the indicator field (dropdown)

class IndicatorInline(admin.TabularInline):
    model = Risk.indicators.through
    form = IndicatorInlineForm
    extra = 0
    fields = ('indicator', 'formatted_description')
    readonly_fields = ('formatted_description',)

    def formatted_description(self, obj):
        if obj and obj.indicator and obj.indicator.description:
            return format_html(obj.indicator.description)
        return ""

    formatted_description.short_description = 'Indicator Description'

class EventInlineForm(forms.ModelForm):
    class Meta:
        model = Risk.events.through  # Adjust this to your actual model connection
        fields = ['event']  # Only include the event field (dropdown)

class EventInline(admin.TabularInline):
    model = Risk.events.through
    form = EventInlineForm
    extra = 0
    fields = ('event', 'formatted_description')
    readonly_fields = ('formatted_description',)

    def formatted_description(self, obj):
        if obj and obj.event and obj.event.description:
            return format_html(obj.event.description)
        return ""

    formatted_description.short_description = 'Event Description'

class ProcedureInlineForm(forms.ModelForm):
    class Meta:
        model = Risk.procedures.through  # Adjust this to your actual model connection
        fields = ['procedure']  # Only include the procedure field (dropdown)

class ProcedureInline(admin.TabularInline):
    model = Risk.procedures.through
    form = ProcedureInlineForm
    extra = 0
    fields = ('procedure', 'formatted_description')
    readonly_fields = ('formatted_description',)

    def formatted_description(self, obj):
        if obj and obj.procedure and obj.procedure.description:
            return format_html(obj.procedure.description)
        return ""

    formatted_description.short_description = 'Procedure Description'

class UserProfileInlineForm(forms.ModelForm):
    class Meta:
        model = Risk.owners.through  # Adjust this to your actual model connection
        fields = ['userprofile']  # Only include the userprofile field (dropdown)

class UserProfileInline(admin.TabularInline):
    model = Risk.owners.through
    form = UserProfileInlineForm
    extra = 0
    fields = ('userprofile', 'formatted_role')
    readonly_fields = ('formatted_role',)

    def formatted_role(self, obj):
        if obj and obj.userprofile:
            role = obj.userprofile.role  # Assuming 'role' is a field in the UserProfile model
            return format_html("<strong>{}</strong>", role) if role else "No role assigned"
        return ""

    formatted_role.short_description = 'Role'


class RiskInline(admin.TabularInline):
    model = Procedure.risks.through
    extra = 0

class MitigationRiskInline(admin.TabularInline):
    model = Mitigation.risks.through
    extra = 0

class ActionRiskInline(admin.TabularInline):
    model = Action.risks.through
    extra = 0
    class Media:
        css = {
            'all': (
                 'orm/css/custom_admin.css',  # Load custom CSS first
            ),
        }

class IndicatorRiskInline(admin.TabularInline):
    model = Indicator.risks.through
    extra = 0
    class Media:
        css = {
            'all': (
                 'orm/css/custom_admin.css',  # Load custom CSS first
            ),
        }

class EventRiskInline(admin.TabularInline):
    model = Event.risks.through
    extra = 0

class IndicatorValueHistoryInline(admin.TabularInline):
    model = IndicatorValueHistory
    extra = 0

class RiskScoreHistoryInline(admin.TabularInline):
    model = RiskScoreHistory
    extra = 0

class ApprovalRequestInline(admin.TabularInline):
    model = ApprovalRequest
    extra = 0
    

class UserProfileInline(admin.TabularInline):
    model = Risk.owners.through
    extra = 0


class RiskAdminForm(forms.ModelForm):
    class Meta:
        model = Risk
        fields = ['title', 'description', 'category', 'portfolio', 'inherent_likelihood', 'inherent_impact', 'residual_likelihood', 'residual_impact', 'targeted_likelihood', 'targeted_impact', 'treatment_type']

    def clean(self):
        cleaned_data = super().clean()
        inherent_score = cleaned_data.get('inherent_likelihood') * cleaned_data.get('inherent_impact')
        residual_score = cleaned_data.get('residual_likelihood') * cleaned_data.get('residual_impact')
        targeted_score = cleaned_data.get('targeted_likelihood') * cleaned_data.get('targeted_impact')

        if not (targeted_score <= residual_score <= inherent_score):
            raise ValidationError("Targeted score must be less than or equal to residual score, and residual score must be less than or equal to inherent score.")

        return cleaned_data

class OwnershipAdminMixin:
    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is not None and hasattr(obj, 'owners') and request.user.userprofile not in obj.owners.all():
            return False
        elif obj is not None and hasattr(obj, 'owner') and request.user.userprofile != obj.owner:
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is not None and hasattr(obj, 'owners') and request.user.userprofile not in obj.owners.all():
            return False
        elif obj is not None and hasattr(obj, 'owner') and request.user.userprofile != obj.owner:
            return False
        return True

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            if hasattr(self.model, 'portfolio'):
                return qs.filter(portfolio__in=user_profile.portfolios.all())
            elif hasattr(self.model, 'owners'):
                return qs.filter(owners=user_profile)
            elif hasattr(self.model, 'owner'):
                return qs.filter(owner=user_profile)
            else:
                return qs.none()
        except UserProfile.DoesNotExist:
            return qs.none()

@admin.register(Risk, site=admin_site)
class RiskAdmin(OwnershipAdminMixin, admin.ModelAdmin):
    
    resource_class = RiskResource
    form = RiskAdminForm

    fieldsets = (
    ('Description', {
        'fields': ('title', 'description'),
    }),
     ('Profile', {
        'fields': ( 'category', 'portfolio'),
    }),
    ('Approval/Assesment', {
        'fields': (
            'last_assessed_by',
            'last_assessed_date',
            'last_approval_info',
            'approval_flag_color_display',
        ),
         # Προσθήκη κλάσης για επέκταση του πεδίου

    }),
     ('Scores', {
        'fields': (
            ('inherent_likelihood', 'inherent_impact', 'inherent_score_display'),
            ('residual_likelihood', 'residual_impact', 'residual_score_display'),
            ('targeted_likelihood', 'targeted_impact', 'targeted_score_display'),
        ),
        # 'classes': ('wide',),  # Προσθήκη κλάσης για επέκταση του πεδίου
    }),
    ('Visuals', {
        'fields': ('stacked_visualization',),
         # Προσθήκη κλάσης για επέκταση του πεδίου

    }), 

)
    class Media:
        css = {
            'all': (
                 'orm/css/custom_admin.css',  # Load custom CSS first
            ),
        }
               

    inlines = [
        UserProfileInline,
        MitigationInline,
        ActionInline,
        IndicatorInline,
        EventInline,
        ProcedureInline,
        RiskScoreHistoryInline,
        ApprovalRequestInline,
    ]

    readonly_fields = (
        'stacked_visualization', 'inherent_score_display', 'residual_score_display', 'targeted_score_display' ,'last_assessed_by',  # Make this field read-only
        'last_assessed_date',  # Make this field read-only
        'last_approval_info',  # Make this field read-only
        'approval_flag_color_display',  # Make this field read-only
        )

    actions = ['create_approval_requests']

    list_display = (
        'title', 'category','portfolio', 'inherent_score_display', 'residual_score_display', 'targeted_score_display',
        'last_approval_info',
        'approval_flag_color_display',  'last_assessed_by',
        'last_assessed_date',
        'get_short_description',
    )

    list_filter = ('title','category', 'owners','portfolio','inherent_likelihood', 'inherent_impact', 'residual_likelihood', 
                   'residual_impact', 'targeted_likelihood', 'targeted_impact')

    
    # def save_model(self, request, obj, form, change):
    #     # Set the created_by field to the current user's UserProfile (if applicable)
    #     obj.created_by = UserProfile.objects.get(user=request.user)
        
    #     # Save the Risk object
    #     super().save_model(request, obj, form, change)
        
    #     # Update the existing RiskScoreHistory records with the user who saved the risk
    #     score_histories = RiskScoreHistory.objects.filter(risk=obj)
    #     for history in score_histories:
    #         # history.saved_by = request.user
    #         history.save()        
        
    def create_approval_requests(self, request, queryset):
        for risk in queryset:
            for owner in risk.owners.all():
                approval_request = ApprovalRequest.objects.create(
                    risk=risk,
                    user=owner,
                    status='pending'
                )
                self.send_approval_request_email(request, approval_request)
        self.message_user(request, "Approval requests created and emails sent successfully.")

    create_approval_requests.short_description = "APPROVALS"

    def send_approval_request_email(self, request, approval_request):
        subject = f"Approval Request for Risk: {approval_request.risk.title}"
        message = render_to_string('emails/approval_request_email.html', {
            'user': approval_request.user.user,
            'risk': approval_request.risk,
            'requesting_user': request.user,
            'approval_link': request.build_absolute_uri(reverse('orm_admin:approvalrequest_change', args=[approval_request.id])),
        })
        try:
            self.send_email(subject, message, [approval_request.user.user.email])
        except Exception as e:
            logging.error(f"Failed to send email to {approval_request.user.user.email}: {e}")

    def send_email(self, subject, message, recipient_list):
        msg = MIMEMultipart()
        msg['From'] = 'riskmanagement@avax.gr'
        msg['To'] = ', '.join(recipient_list)
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'html'))

        try:
            with smtplib.SMTP('smtp.example.com', 587) as server:
                server.starttls()
                server.login('riskmanagement@avax.gr', 'your_password')
                server.send_message(msg)
        except smtplib.SMTPException as e:
            logging.error(f"Failed to send email: {e}")

    def inherent_score_display(self, obj):
        score = obj.inherent_score()
        traffic_light, color = obj.inherent_traffic_light()
        return format_html("<span style='color:{};'>{} x {} = {} ({})</span>", color, obj.inherent_likelihood, obj.inherent_impact, score, traffic_light) if score else "N/A"
    inherent_score_display.short_description = 'Inherent Score'

    def residual_score_display(self, obj):
        score = obj.residual_score()
        traffic_light, color = obj.residual_traffic_light()
        return format_html("<span style='color:{};'>{} x {} = {} ({})</span>", color, obj.residual_likelihood, obj.residual_impact, score, traffic_light) if score else "N/A"
    residual_score_display.short_description = 'Residual Score'

    def targeted_score_display(self, obj):
        score = obj.targeted_score()
        traffic_light, color = obj.targeted_traffic_light()
        return format_html("<span style='color:{};'>{} x {} = {} ({})</span>", color, obj.targeted_likelihood, obj.targeted_impact, score, traffic_light) if score else "N/A"
    targeted_score_display.short_description = 'Targeted Score'

    def approval_flag_color_display(self, obj):
        color = obj.approval_flag_color()
        return format_html("<span style='color:{};'>●</span>", color)
    approval_flag_color_display.short_description = 'Approval Flag'

    def score_trend_graph(self, obj):
        inherent_scores = obj.score_history.filter(score_type='inherent').order_by('timestamp')
        residual_scores = obj.score_history.filter(score_type='residual').order_by('timestamp')
        targeted_scores = obj.score_history.filter(score_type='targeted').order_by('timestamp')

        dates = [score.timestamp for score in inherent_scores]
        inherent_values = [score.score for score in inherent_scores]
        residual_values = [score.score for score in residual_scores]
        targeted_values = [score.score for score in targeted_scores]

        if dates and (inherent_values or residual_values or targeted_values):
            plt.figure(figsize=(5, 5))  # Consistent size with heatmap
            sns.set_style("darkgrid")

            if inherent_values:
                sns.lineplot(x=dates, y=inherent_values, marker='o', label='Inherent Score', color=self.SCORE_COLORS['inherent'])
            if residual_values:
                sns.lineplot(x=dates, y=residual_values, marker='o', label='Residual Score', color=self.SCORE_COLORS['residual'])
            if targeted_values:
                sns.lineplot(x=dates, y=targeted_values, marker='o', label='Targeted Score', color=self.SCORE_COLORS['targeted'])

            plt.title(f'Score Trends for {obj.title}', fontsize=12, weight='normal')  # Consistent title weight
            plt.xlabel('Date', fontsize=10)
            plt.ylabel('Score', fontsize=10)
            plt.xticks(fontsize=8)
            plt.yticks(fontsize=8)
            plt.legend(loc='best', fontsize=8)
            plt.grid(True)

            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            plt.close()
            buffer.seek(0)

            image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            image_html = f"<img src='data:image/png;base64,{image_base64}' alt='Score Trends for {obj.title}'>"

            return format_html(image_html)

        return 'No data available'

    score_trend_graph.short_description = 'Score Graph'



    # Define consistent colors for score types
    # Centralized color scheme
    SCORE_COLORS = {
        'inherent': '#1f77b4',  # Same blue across both graphs
        'residual': '#9467bd',  # Same purple across both graphs
        'targeted': '#8c564b'   # Same brown across both graphs
    }

    def generate_heatmap(self, obj):
        def risk_color(score):
            if score >= 1 and score <= 6:
                return 'green'
            elif score >= 8 and score <= 12:
                return 'yellow'
            elif score >= 15 and score <= 25:
                return 'red'
            else:
                return 'white'

        heatmap_data = np.array([
                        [5, 10, 15, 20, 25],

                        [4, 8, 12, 16, 20],
                        [3, 6, 9, 12, 15],

                        [2, 4, 6, 8, 10],

                        [1, 2, 3, 4, 5],

        ])

        plt.figure(figsize=(5, 5))  # Consistent size
        cmap = sns.color_palette([risk_color(i) for i in range(1, 26)])

        ax = sns.heatmap(heatmap_data, annot=True, cmap=cmap, fmt="d", linewidths=.5, cbar=False)
        ax.set_title(f'Risk Heatmap for {obj.title}', fontsize=12, weight='normal')  # Consistent title weight
        ax.set_xlabel('Impact', fontsize=10)
        ax.set_ylabel('Likelihood', fontsize=10)
        ax.set_xticklabels(['1', '2', '3', '4', '5'], fontsize=8)
        ax.set_yticklabels(['5', '4', '3', '2', '1'], rotation=0, fontsize=8)  # Ensure 1 is at the bottom and 5 at the top

        positions = {}
        for score_type in ['inherent', 'residual', 'targeted']:
            color = self.SCORE_COLORS[score_type]
            likelihood = getattr(obj, f"{score_type}_likelihood")
            impact = getattr(obj, f"{score_type}_impact")

            if likelihood is None:
                likelihood = 1
            if impact is None:
                impact = 1

            position = (5 - likelihood, impact - 1)  # Adjusted for the correct plotting scale
            
            if position not in positions:
                positions[position] = []
            positions[position].append((score_type.capitalize(), color))

        for (y, x), labels in positions.items():
            for i, (label, color) in enumerate(labels):
                ax.text(x + 0.5, y + 0.5 + 0.15 * i, label, ha='center', va='center', color=color, fontsize=10, weight='bold')

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        plt.close()
        buffer.seek(0)

        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        image_html = f"<img src='data:image/png;base64,{image_base64}' alt='Heatmap for {obj.title}'>"

        return format_html(image_html)

    generate_heatmap.short_description = 'Heatmap'



    def stacked_visualization(self, obj):
        heatmap_html = self.generate_heatmap(obj)
        score_trend_html = self.score_trend_graph(obj)

        return format_html(
            """
            <div class='graph-container' style='margin-bottom: 20px;'>{}</div>
            <div class='graph-container'>{}</div>
            """,
            heatmap_html,
            score_trend_html,
        )

    stacked_visualization.short_description = 'Risk Overview'

    def get_short_description(self, obj):
        return mark_safe(strip_tags(obj.description)[:200] + ('...' if len(strip_tags(obj.description)) > 20 else ''))
    get_short_description.short_description = 'Description'


        # Custom action to create a risk assessment
    def create_risk_assessment(self, request, queryset):
        if queryset:
            # Assuming the assessor is the current logged-in user
            title = f"Risk Assessment - {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"
            assessor = UserProfile.objects.get(user=request.user)
            # Create a new risk assessment with selected risks
            risk_assessment = RiskAssessment.objects.create(assessor=assessor, created_by=assessor,title=title)
            risk_assessment.risks.set(queryset)
            risk_assessment.save()
            # Display a success message
            self.message_user(request, f"New Risk Assessment was created with {queryset.count()} risks.", messages.SUCCESS)
        else:
            self.message_user(request, "No risks selected.", messages.WARNING)

    create_risk_assessment.short_description = "ASSESMENT"

    # Register the action
    actions = ['create_risk_assessment','create_approval_requests']





class ApprovalRequestAdminForm(forms.ModelForm):
    class Meta:
        model = ApprovalRequest
        fields = '__all__'
@admin.register(ApprovalRequest, site=admin_site)
class ApprovalRequestAdmin(admin.ModelAdmin):
    resource_class = ApprovalRequestResource
    form = ApprovalRequestAdminForm
    list_display = ('risk', 'user', 'status', 'response_date')
    actions = ['send_approval_email', 'approve_requests', 'reject_requests']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            return qs.filter(user=user_profile)
        except UserProfile.DoesNotExist:
            return qs.none()

    def send_approval_email(self, request, queryset):
        for approval_request in queryset:
            self.send_approval_request_email(request, approval_request)
        self.message_user(request, "Approval request emails sent successfully.")
    
    send_approval_email.short_description = "Request Emails"

    def send_approval_request_email(self, request, approval_request):
        subject = f"Approval Request for Risk: {approval_request.risk.title}"
        message = render_to_string('emails/approval_request_email.html', {
            'user': approval_request.user.user,
            'risk': approval_request.risk,
            'requesting_user': request.user,
            'approval_link': request.build_absolute_uri(reverse('orm_admin:approvalrequest_change', args=[approval_request.id])),
        })
        try:
            self.send_email(subject, message, [approval_request.user.user.email])
        except Exception as e:
            logging.error(f"Failed to send email to {approval_request.user.user.email}: {e}")

    def send_email(self, subject, message, recipient_list):
        msg = MIMEMultipart()
        msg['From'] = 'riskmanagement@avax.gr'
        msg['To'] = ', '.join(recipient_list)
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'html'))

        try:
            with smtplib.SMTP('smtp.example.com', 587) as server:
                server.starttls()
                server.login('riskmanagement@avax.gr', 'your_password')
                server.send_message(msg)
        except smtplib.SMTPException as e:
            logging.error(f"Failed to send email: {e}")

    def approve_requests(self, request, queryset):
        current_user_profile = UserProfile.objects.get(user=request.user)
        for approval_request in queryset:
            if approval_request.user != current_user_profile and not request.user.is_superuser:
                return HttpResponseForbidden("<h1>403 Forbidden</h1><p>You are not allowed to approve this request.</p>")
            approval_request.status = 'approved'
            approval_request.response_date = timezone.now()
            approval_request.save()
            self.send_approval_confirmation_email(approval_request)
        self.message_user(request, "Selected requests approved successfully.")
    
    approve_requests.short_description = "Approve Selected"

    def send_approval_confirmation_email(self, approval_request):
        subject = f"Approval Request Approved: {approval_request.risk.title}"
        message = render_to_string('emails/approval_confirmation_email.html', {
            'user': approval_request.user.user,
            'risk': approval_request.risk,
            'approving_user': approval_request.user.user,
        })
        try:
            self.send_email(subject, message, [approval_request.user.user.email])
        except Exception as e:
            logging.error(f"Failed to send email to {approval_request.user.user.email}: {e}")

    def reject_requests(self, request, queryset):
        current_user_profile = UserProfile.objects.get(user=request.user)
        for approval_request in queryset:
            if approval_request.user != current_user_profile and not request.user.is_superuser:
                return HttpResponseForbidden("<h1>403 Forbidden</h1><p>You are not allowed to reject this request.</p>")
            approval_request.status = 'rejected'
            approval_request.response_date = timezone.now()
            approval_request.save()
            self.send_rejection_notification_email(approval_request)
        self.message_user(request, "Selected requests rejected successfully.")
    
    reject_requests.short_description = "Reject Selected "

    def send_rejection_notification_email(self, approval_request):
        subject = f"Approval Request Rejected: {approval_request.risk.title}"
        message = render_to_string('emails/rejection_notification_email.html', {
            'user': approval_request.user.user,
            'risk': approval_request.risk,
            'rejecting_user': approval_request.user.user,
        })
        try:
            self.send_email(subject, message, [approval_request.user.user.email])
        except Exception as e:
            logging.error(f"Failed to send email: {e}")

class CustomUserAdmin(BaseUserAdmin):
    readonly_fields = ('password',)
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')

class CustomGroupAdmin(GroupAdmin):
    list_filter = ('name',)

# Register User and Group with the custom admin site
admin_site.register(User, CustomUserAdmin)
admin_site.register(Group, CustomGroupAdmin)

# Register the remaining models with the custom admin site
@admin.register(UserProfile, site=admin_site)
class UserProfileAdmin(admin.ModelAdmin):
    resource_class = UserProfileResource

@admin.register(Portfolio, site=admin_site)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    resource_class = PortfolioResource

@admin.register(Category, site=admin_site)
class CategoryAdmin(admin.ModelAdmin):
    resource_class = CategoryResource

@admin.register(IndicatorValueHistory, site=admin_site)
class IndicatorValueHistoryAdmin(admin.ModelAdmin):
    resource_class = IndicatorValueHistoryResource

@admin.register(RiskScoreHistory, site=admin_site)
class RiskScoreHistoryAdmin(admin.ModelAdmin):
            
    resource_class = RiskScoreHistoryResource

@admin.register(Procedure, site=admin_site)
class ProcedureAdmin(OwnershipAdminMixin, admin.ModelAdmin):
    resource_class = ProcedureResource
    search_fields = ('title', 'description', 'department', 'owner__user__username')
    
    # Matching list_display more closely with MitigationAdmin
    list_display = ('title', 'get_short_description', 'department', 'owner')
    
    # Adding list_filter similar to MitigationAdmin
    list_filter = ('title', 'owner','department', 'owner')

    # Inline models if applicable, similar to MitigationAdmin
    inlines = [RiskInline]

    class Media:
        css = {
            'all': ('orm/css/custom_admin.css',)
        }

    def get_short_description(self, obj):
        return format_html('<div>{}</div>', mark_safe(strip_tags(obj.description)[:200] + ('...' if len(strip_tags(obj.description)) > 20 else '')))
    get_short_description.short_description = 'Description'

@admin.register(Mitigation, site=admin_site)
class MitigationAdmin(OwnershipAdminMixin, admin.ModelAdmin):
    resource_class = MitigationResource
    list_display = ('title', 'owner','portfolio','related_risks', 'effectiveness', 'get_short_description')
    class Media:
                css = {
                    'all': ('orm/css/custom_admin.css',)
                }
    
    def get_short_description(self, obj):
        return format_html('<div>{}</div>', mark_safe(strip_tags(obj.description)[:200] + ('...' if len(strip_tags(obj.description)) > 20 else '')))
    get_short_description.short_description = 'Description'

    def related_risks(self, obj):
        return ", ".join([risk.title for risk in obj.risks.all()])
    related_risks.short_description = 'Related Risks'

    list_filter = ('title' ,'owner','portfolio','risks', 'effectiveness')
    inlines = [MitigationRiskInline]

from django.contrib import admin
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from django.utils.html import format_html
from datetime import timedelta  # Ensure this import is present
from .models import Indicator, IndicatorValueHistory
import os  # Add this import at the beginning of your file
import matplotlib.pyplot as plt
import io
import base64
from django.utils.html import format_html
from datetime import timedelta
@admin.register(Indicator, site=admin_site)
class IndicatorAdmin(OwnershipAdminMixin, admin.ModelAdmin):
    resource_class = IndicatorResource
    list_display = ('title', 'related_risks', 'owner', 'repetition_frequency', 'get_short_description')

    def get_short_description(self, obj):
        return format_html('<div>{}</div>', mark_safe(strip_tags(obj.description)[:200] + ('...' if len(strip_tags(obj.description)) > 20 else '')))
    get_short_description.short_description = 'Description'

    def related_risks(self, obj):
        return ", ".join([risk.title for risk in obj.risks.all()])
    related_risks.short_description = 'Related Risks'

    inlines = [IndicatorValueHistoryInline, IndicatorRiskInline]
    list_filter = ('title', 'owner','portfolio','field', 'repetition_frequency' )
    readonly_fields = ('indicator_value_graph',)  # Add the graph method here
    
    def indicator_value_graph(self, obj):
        value_history = IndicatorValueHistory.objects.filter(indicator=obj).order_by('timestamp')
        timestamps = [vh.timestamp for vh in value_history]
        values = [vh.value for vh in value_history]

        # Adjust timestamps to avoid identical values
        for i in range(1, len(timestamps)):
            if timestamps[i] == timestamps[i - 1]:
                timestamps[i] += timedelta(seconds=i)  # Add seconds to differentiate

        if len(timestamps) > 0 and len(values) > 0:
            try:
                print("Both lists are non-empty, proceeding to create the graph.")
                plt.figure()
                plt.plot(timestamps, values, marker='o')
                plt.title(f'Indicator Value Trends for {obj.title}')  # Replace 'name' with 'title' or the correct field
                plt.xlabel('Timestamp')
                plt.ylabel('Value')

                # Save the image to a known directory (e.g., Desktop)
                image_path = '/Users/sixela/Desktop/test_graph.png'  # Update this path
                plt.savefig(image_path)
                plt.close()

                if os.path.exists(image_path):
                    print(f"Graph saved to {image_path}")
                else:
                    print(f"Failed to save the graph to {image_path}")

                # Optionally, render the image in the admin if you want to test it
                with open(image_path, "rb") as image_file:
                    image_data = image_file.read()
                    image_base64 = base64.b64encode(image_data).decode('utf-8')
                    image_html = f"<img src='data:image/png;base64,{image_base64}' alt='Indicator Value Trends for {obj.title}'>"

                return format_html(image_html)

            except Exception as e:
                print(f"An error occurred: {e}")

        else:
            print("Graph will not be created because one or both lists are empty.")

        return format_html('<strong>No data available to display the graph.</strong>')

    chart_settings = {
        'default': {
            'title': 'Current Value Over Time',
            'chart_type': 'line',  # Choose from 'line', 'bar', 'pie', etc.
            'series': [
                {
                    'name': 'Current Value',
                    'field': 'current_value',
                    'aggregate': 'sum',  # Options: 'sum', 'count', 'avg', etc.
                }
            ],
            'group_by': 'reporting_date',  # Field to group data points by
            'filter': None,  # Optional filtering
        },
    }






# Register the IndicatorAdmin class with the Indicator model
admin.site.register(Indicator, IndicatorAdmin)
@admin.register(Event, site=admin_site)
class EventAdmin(OwnershipAdminMixin, admin.ModelAdmin):
    resource_class = EventResource
    list_display = ('title', 'get_short_description', 'related_risks', 'owner', 'reporter','portfolio')

    def get_short_description(self, obj):
        return format_html('<div>{}</div>', mark_safe(strip_tags(obj.description)[:200] + ('...' if len(strip_tags(obj.description)) > 20 else '')))
    get_short_description.short_description = 'Description'

    def related_risks(self, obj):
        return ", ".join([risk.title for risk in obj.risks.all()])
    related_risks.short_description = 'Related Risks'

    list_filter = ('title', 'owner', 'reporter','portfolio', 'date')
    inlines = [EventRiskInline]

@admin.register(Action, site=admin_site)
class ActionAdmin(OwnershipAdminMixin, admin.ModelAdmin):
    resource_class = ActionResource
    list_display = ('title', 'related_risks', 'owner', 'performer', 'deadline', 'get_short_description','portfolio')

    def get_short_description(self, obj):
        return format_html('<div>{}</div>', mark_safe(strip_tags(obj.description)[:200] + ('...' if len(strip_tags(obj.description)) > 20 else '')))
    get_short_description.short_description = 'Description'

    def related_risks(self, obj):
        return ", ".join([risk.title for risk in obj.risks.all()])
    related_risks.short_description = 'Related Risks'

    list_filter = ('title', 'risks', 'performer', 'deadline', 'owner','portfolio')
    inlines = [ActionRiskInline]

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail

def send_email(subject, body, to_email):
    try:
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,  # Using the default from email in settings
            [to_email],
            fail_silently=False,
        )
        print(f"Email sent successfully to {to_email}!")
    except Exception as e:
        print(f"Failed to send email: {e}")

def send_approval_request_email(requester, approver_email, request_details):
    subject = "New Approval Request"
    body = render_to_string('emails/approval_request.html', {'requester': requester, 'request_details': request_details})
    print(f"Triggering approval request email to {approver_email}")
    send_email(subject, body, approver_email)

def send_approval_accepted_email(approver, requester_email, approval_details):
    subject = "Approval Request Accepted"
    body = render_to_string('emails/approval_accepted.html', {'approver': approver, 'approval_details': approval_details})
    print(f"Triggering approval accepted email to {requester_email}")
    send_email(subject, body, requester_email)

def send_approval_rejected_email(approver, requester_email, rejection_details):
    subject = "Approval Request Rejected"
    body = render_to_string('emails/approval_rejected.html', {'approver': approver, 'rejection_details': rejection_details})
    print(f"Triggering approval rejected email to {requester_email}")
    send_email(subject, body, requester_email)

# Example usage in your workflow, ensure these functions are correctly triggered:
def create_approval_request(request, *args, **kwargs):
    print("Function create_approval_request called")
    approval_request = ApprovalRequest.objects.create(...)
    
    # Send the email
    send_approval_request_email(request.user, approval_request.approver.email, approval_request.details)

def approve_request(request, approval_request_id):
    print(f"Function approve_request called with ID: {approval_request_id}")
    approval_request = ApprovalRequest.objects.get(id=approval_request_id)
    approval_request.status = 'accepted'
    approval_request.save()
    
    # Send the email
    send_approval_accepted_email(request.user, approval_request.requester.email, approval_request.details)

def reject_request(request, approval_request_id):
    print(f"Function reject_request called with ID: {approval_request_id}")
    approval_request = ApprovalRequest.objects.get(id=approval_request_id)
    approval_request.status = 'rejected'
    approval_request.save()
    
    # Send the email
    send_approval_rejected_email(request.user, approval_request.requester.email, approval_request.details)


from django.utils.html import format_html
from django.contrib import admin
from .models import Risk, RiskAssessment
from django import forms
from .models import RiskAssessment

class RiskInlineForm(forms.ModelForm):
    class Meta:
        model = RiskAssessment.risks.through  # Assuming a ManyToMany relationship
        fields = ['risk']  # Include only the risk field (dropdown)

class RiskInline(admin.TabularInline):
    model = RiskAssessment.risks.through
    form = RiskInlineForm
    extra = 0
    fields = ('risk', 'formatted_description')  # Include dropdown and formatted description
    readonly_fields = ('formatted_description',)  # Make description read-only

    def formatted_description(self, obj):
        if obj and obj.risk and obj.risk.description:
            return format_html(obj.risk.description)  # Render HTML as is without sanitization
        return ""

    formatted_description.short_description = 'Risk Description'

class RiskSnapshotInline(admin.TabularInline):
    model = RiskSnapshot
    extra = 0
    readonly_fields = ('title', 'description', 'inherent_score', 'residual_score', 'targeted_score')

class AssessmentHistoryInline(admin.TabularInline):
    model = AssessmentHistory
    extra = 0
    readonly_fields = ('date', 'assessor')
    can_delete = False
    show_change_link = True


from .models import RiskAssessment, UserProfile
@admin.register(RiskAssessment, site=admin_site)

class RiskAssessmentAdmin(admin.ModelAdmin):
    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is not None and hasattr(obj, 'assessor'):
            user_profile = UserProfile.objects.get(user=request.user)
            return obj.assessor == user_profile
        return False

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            user_profile = UserProfile.objects.get(user=request.user)
            return qs.filter(assessor=user_profile)
    
    def mark_as_completed(self, request, queryset):
        user_profile = UserProfile.objects.get(user=request.user)
        
        for assessment in queryset:
            if assessment.assessor == user_profile:
                assessment.mark_assessed()
                self.message_user(request, f"Assessment '{assessment.title}' marked as completed.", messages.SUCCESS)
                
                # Update last assessed information for the risks
                for risk in assessment.risks.all():
                    risk.update_last_assessed(assessment.assessor)
            else:
                self.message_user(request, f"You do not have permission to complete the assessment '{assessment.title}'.", messages.ERROR)
        
    mark_as_completed.short_description = "Mark selected assessments as completed"
    actions = [mark_as_completed]        

    icon = 'fas fa-cogs'
    
    list_display = ('title', 'assessor', 'created_by', 'created_at', 'assessed_at', 'status')
    filter_horizontal = ('risks',)
    search_fields = ('assessor__user__username', 'created_by__user__username', 'status')
    list_filter = ('status', 'created_at', 'assessed_at')
    
    inlines = [RiskInline]
    
    class Media:
        css = {
            'all': (
                 'orm/css/custom_admin.css',  # Load custom CSS first
            ),
        }

    def save_model(self, request, obj, form, change):
        # Set the created_by field to the current user's UserProfile (if applicable)
        obj.created_by = UserProfile.objects.get(user=request.user)
        
        # Save the RiskAssessment object
        super().save_model(request, obj, form, change)
        
        # Update the RiskScoreHistory with the user who completed the assessment
        # score_histories = RiskScoreHistory.objects.filter(risk=obj.risk)  # Assuming `obj.risk` links to the Risk
        # for history in score_histories:
        #     if not history.saved_by:  # Only update if the saved_by field is not already set
        #         history.saved_by = request.user
        #         history.save()

    def assessment_history_display(self, obj):
        histories = obj.assessment_history.all()
        if not histories:
            return "No history available"
        display_html = ""
        for history in histories:
            display_html += f"<h3>Assessment on {history.date.strftime('%Y-%m-%d')} by {history.assessor.user.username}</h3>"
            for snapshot in history.risk_snapshots.all():
                display_html += f"<p>Risk: {snapshot.title} | Inherent Score: {snapshot.inherent_score} | Residual Score: {snapshot.residual_score} | Targeted Score: {snapshot.targeted_score}</p>"
        return format_html(display_html)

    assessment_history_display.short_description = "Assessment History"
    readonly_fields = ('assessment_history_display',)

admin.site.register(RiskAssessment, RiskAssessmentAdmin)