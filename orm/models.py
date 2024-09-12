from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from ckeditor.fields import RichTextField
from datetime import datetime, timedelta
from tinymce.models import HTMLField

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50)
    portfolios = models.ManyToManyField('Portfolio', related_name='user_profiles')

    def __str__(self):
        return self.user.username

# class UserProfile2(models.Model):


class Portfolio(models.Model):
    name = models.CharField(max_length=100)
    description = HTMLField()

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = HTMLField()

    def __str__(self):
        return self.name

class Mitigation(models.Model):
    title = models.CharField(max_length=100)
    description = HTMLField()
    owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='owned_mitigations')
    portfolio = models.ForeignKey(Portfolio, on_delete=models.SET_NULL, null=True, blank=True)
    effectiveness = models.CharField(max_length=50, choices=[
        ('not_tested', 'Not Tested'),
        ('ineffective', 'Ineffective'),
        ('partially_effective', 'Partially Effective'),
        ('effective', 'Effective')
    ], default='not_tested')

    def __str__(self):
        return self.title




class Action(models.Model):
    title = models.CharField(max_length=100)
    description = HTMLField()
    owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='owned_actions')
    portfolio = models.ForeignKey(Portfolio, on_delete=models.SET_NULL, null=True, blank=True)
    performer = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='performed_actions')
    deadline = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.title

class Indicator(models.Model):
    FREQUENCY_CHOICES = [
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semiannual', 'Semi-Annual'),
        ('annual', 'Annual'),
    ]

    title = models.CharField(max_length=100)
    description = HTMLField()
    field = models.CharField(max_length=100)
    repetition_frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    current_value = models.FloatField()
    reporting_date = models.DateField()
    next_reporting_date = models.DateField(blank=True, null=True)
    owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='owned_indicators')
    portfolio = models.ForeignKey(Portfolio, on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.next_reporting_date:
            self.next_reporting_date = self.calculate_next_reporting_date()
        super().save(*args, **kwargs)
        self.create_value_history()

    def calculate_next_reporting_date(self):
        if self.repetition_frequency == 'weekly':
            return self.reporting_date + timedelta(weeks=1)
        elif self.repetition_frequency == 'monthly':
            return self.reporting_date + timedelta(days=30)
        elif self.repetition_frequency == 'quarterly':
            return self.reporting_date + timedelta(days=90)
        elif self.repetition_frequency == 'semiannual':
            return self.reporting_date + timedelta(days=182)
        elif self.repetition_frequency == 'annual':
            return self.reporting_date + timedelta(days=365)
        return self.reporting_date

    def create_value_history(self):
        IndicatorValueHistory.objects.create(
            indicator=self,
            value=self.current_value,
            timestamp=self.reporting_date
        )

    def __str__(self):
        return self.title

class IndicatorValueHistory(models.Model):
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE, related_name='value_history')
    value = models.FloatField()
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.indicator.title} - {self.value} at {self.timestamp}"

class Event(models.Model):
    title = models.CharField(max_length=100)
    description = HTMLField()
    date = models.DateField()
    owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='owned_events')
    portfolio = models.ForeignKey(Portfolio, on_delete=models.SET_NULL, null=True, blank=True)
    reporter = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='reported_events')

    def save(self, *args, **kwargs):
        if isinstance(self.date, datetime):
            self.date = self.date.date()
        elif isinstance(self.date, str):
            self.date = datetime.fromisoformat(self.date).date()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title



        

class Risk(models.Model):
    last_assessed_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='last_assessed_risks')
    last_assessed_date = models.DateTimeField(blank=True, null=True)

    # existing fields...

    def update_last_assessed(self, user_profile):
        self.last_assessed_by = user_profile
        self.last_assessed_date = timezone.now()
        self.save()


    SCORE_CHOICES = [(i, str(i)) for i in range(1, 6)]
    TREATMENT_CHOICES = [
        ('acceptance', 'Acceptance'),
        ('mitigation', 'Mitigation'),
        ('transfer', 'Transfer'),
        ('avoidance', 'Avoidance')
    ]

    title = models.CharField(max_length=100)
    description = HTMLField()
    owners = models.ManyToManyField(UserProfile, related_name='owned_risks')
    mitigations = models.ManyToManyField(Mitigation, related_name='risks', blank=True)
    actions = models.ManyToManyField(Action, related_name='risks', blank=True)
    indicators = models.ManyToManyField(Indicator, related_name='risks', blank=True)
    events = models.ManyToManyField(Event, related_name='risks', blank=True)
    procedures = models.ManyToManyField('Procedure', related_name='risks', blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.SET_NULL, null=True, blank=True)
    inherent_likelihood = models.IntegerField(choices=SCORE_CHOICES, null=True, blank=True,default=5)
    inherent_impact = models.IntegerField(choices=SCORE_CHOICES, null=True, blank=True,default=5)
    residual_likelihood = models.IntegerField(choices=SCORE_CHOICES, null=True, blank=True,default=3)
    residual_impact = models.IntegerField(choices=SCORE_CHOICES, null=True, blank=True,default=3)
    targeted_likelihood = models.IntegerField(choices=SCORE_CHOICES, null=True, blank=True,default=1)
    targeted_impact = models.IntegerField(choices=SCORE_CHOICES, null=True, blank=True,default=1)
    treatment_type = models.CharField(max_length=50, choices=TREATMENT_CHOICES, null=True, blank=True,default='mitigation')

    def inherent_score(self):
        if self.inherent_likelihood is not None and self.inherent_impact is not None:
            return self.inherent_likelihood * self.inherent_impact
        return None

    def residual_score(self):
        if self.residual_likelihood is not None and self.residual_impact is not None:
            return self.residual_likelihood * self.residual_impact
        return None

    def targeted_score(self):
        if self.targeted_likelihood is not None and self.targeted_impact is not None:
            return self.targeted_likelihood * self.targeted_impact
        return None

    def get_traffic_light(self, score):
        if score is None:
            return 'N/A', '#FFFFFF'  # White for not applicable
        if score > 12:
            return 'HIGH', '#FF0000'
        elif score > 6:
            return 'MEDIUM', '#FFA500'
        else:
            return 'LOW', '#00FF00'

    def inherent_traffic_light(self):
        return self.get_traffic_light(self.inherent_score())

    def residual_traffic_light(self):
        return self.get_traffic_light(self.residual_score())

    def targeted_traffic_light(self):
        return self.get_traffic_light(self.targeted_score())

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.create_score_history()

    def create_score_history(self):
        if self.inherent_score() is not None:
            RiskScoreHistory.objects.create(risk=self, score_type='inherent', score=self.inherent_score(), timestamp=timezone.now())
        if self.residual_score() is not None:
            RiskScoreHistory.objects.create(risk=self, score_type='residual', score=self.residual_score(), timestamp=timezone.now())
        if self.targeted_score() is not None:
            RiskScoreHistory.objects.create(risk=self, score_type='targeted', score=self.targeted_score(), timestamp=timezone.now())

    def __str__(self):
        return self.title

    def inherent_score_display(self):
        score = self.inherent_score()
        traffic_light, color = self.inherent_traffic_light()
        return format_html("<span style='color:{};'>{} x {} = {} ({})</span>", color, self.inherent_likelihood, self.inherent_impact, score, traffic_light) if score else "N/A"
    inherent_score_display.short_description = 'Inherent Score'
    inherent_score_display.allow_tags = True

    def residual_score_display(self):
        score = self.residual_score()
        traffic_light, color = self.residual_traffic_light()
        return format_html("<span style='color:{};'>{} x {} = {} ({})</span>", color, self.residual_likelihood, self.residual_impact, score, traffic_light) if score else "N/A"
    residual_score_display.short_description = 'Residual Score'
    residual_score_display.allow_tags = True

    def targeted_score_display(self):
        score = self.targeted_score()
        traffic_light, color = self.targeted_traffic_light()
        return format_html("<span style='color:{};'>{} x {} = {} ({})</span>", color, self.targeted_likelihood, self.targeted_impact, score, traffic_light) if score else "N/A"
    targeted_score_display.short_description = 'Targeted Score'
    targeted_score_display.allow_tags = True

    def mitigations_list(self):
        return ", ".join(mitigation.title for mitigation in self.mitigations.all())
    mitigations_list.short_description = 'Mitigations'

    def last_approval_info(self):
        latest_approval = self.approval_requests.filter(status='approved').order_by('-response_date').first()
        if latest_approval:
            return f"{latest_approval.user.user.username} on {latest_approval.response_date.strftime('%Y-%m-%d')}"
        return "No approvals"
    last_approval_info.short_description = 'Last Approval Info'

    def approval_flag_color(self):
        latest_approval = self.approval_requests.filter(status='approved').order_by('-response_date').first()
        if latest_approval:
            if latest_approval.response_date >= timezone.now() - timedelta(days=180):
                return '#00FF00'  # Green if within six months
            else:
                return '#FF0000'  # Red if older than six months
        return '#FFFFFF'  # White if no approvals

    class Meta:
        permissions = [
            ("view_risk_report", "Can view the risk report"),
        ]
class RiskScoreHistory(models.Model):
    risk = models.ForeignKey(Risk, on_delete=models.CASCADE, related_name='score_history')
    score_type = models.CharField(max_length=50)
    score = models.IntegerField()
    timestamp = models.DateTimeField(default=timezone.now)
    # saved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='risk_score_histories')
    def __str__(self):
        return f"{self.risk.title} - {self.score_type} - {self.score} at {self.timestamp}"

class ApprovalRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    risk = models.ForeignKey(Risk, on_delete=models.CASCADE, related_name='approval_requests')
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    response_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"ApprovalRequest for {self.risk.title} by {self.user.user.username}"

    def approve(self):
        self.status = 'approved'
        self.response_date = timezone.now()
        self.save()

    def reject(self):
        self.status = 'rejected'
        self.response_date = timezone.now()
        self.save()

class Procedure(models.Model):
    title = models.CharField(max_length=100)
    description = HTMLField()
    url = models.URLField(max_length=200, blank=True, null=True)
    owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='owned_procedures')
    department = models.CharField(max_length=100)

    def __str__(self):
        return self.title

# models.py

from django.utils import timezone

class RiskAssessment(models.Model):
    # existing fields...
    title = models.CharField(max_length=255)
    description = HTMLField()
    risks = models.ManyToManyField(Risk, related_name='assessments')
    assessor = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='assessments')
    created_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='created_assessments')
    created_at = models.DateTimeField(auto_now_add=True)
    assessed_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('completed', 'Completed')], default='pending')

    def __str__(self):
        return f"Assessment by {self.assessor} on {self.created_at}"

    def mark_assessed(self):
        self.status = 'completed'
        self.assessed_at = timezone.now()
        self.save()

        # Create the history entry
        history = AssessmentHistory.objects.create(
            risk_assessment=self,
            assessor=self.assessor,
            date=timezone.now()
        )

        # Create snapshots of each risk at this time
        for risk in self.risks.all():
            RiskSnapshot.objects.create(
                title=risk.title,
                description=risk.description,
                inherent_score=risk.inherent_score(),
                residual_score=risk.residual_score(),
                targeted_score=risk.targeted_score(),
                assessment_history=history
            )
class RiskSnapshot(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    inherent_score = models.IntegerField()
    residual_score = models.IntegerField()
    targeted_score = models.IntegerField()
    assessment_history = models.ForeignKey('AssessmentHistory', related_name='risk_snapshots', on_delete=models.CASCADE)

    def __str__(self):
        return f"Snapshot of {self.title} during assessment"

class AssessmentHistory(models.Model):
    risk_assessment = models.ForeignKey('RiskAssessment', on_delete=models.CASCADE, related_name='assessment_history')
    date = models.DateTimeField(default=timezone.now)
    assessor = models.ForeignKey('UserProfile', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Assessment on {self.date.strftime('%Y-%m-%d')} by {self.assessor.user.username}"