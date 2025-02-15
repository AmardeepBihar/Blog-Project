from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils.html import strip_tags
from tinymce.models import HTMLField
from django.utils.text import slugify

# --- Base Abstract Model ---
class BaseClass(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']

# --- Language Model ---
class Language(BaseClass):
    LANGUAGE_CHOICES = (
        ('EN', 'English'),
        ('HI', 'Hindi'),
    )
    code = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, unique=True)
    name = models.CharField(max_length=20, unique=True)

    class Meta:
        verbose_name = "Language"
        verbose_name_plural = "Languages"

    def __str__(self):
        return self.name

# --- Category Models ---
class Category(BaseClass):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, max_length=60)
    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @staticmethod
    def generate_unique_slug(base):
        slug = slugify(base)[:50]
        counter = 1
        while Category.objects.filter(slug=slug).exists():
            slug = f"{slug[:46]}-{counter}"
            counter += 1
        return slug

class SubCategory(BaseClass):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=100)
    slug = models.SlugField(max_length=70, unique=True)

    class Meta:
        verbose_name = "Subcategory"
        verbose_name_plural = "Subcategories"
        unique_together = ('category', 'name')

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.category.name} {self.name}")
            self.slug = self.generate_unique_slug(base_slug)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.category.name} - {self.name}"

# --- Purpose Model ---
class Purpose(BaseClass):
    title = models.CharField(max_length=50, unique=True)
    description = models.TextField(max_length=100)
    slug = models.SlugField(max_length=60, unique=True)

    class Meta:
        verbose_name = "Purpose"
        verbose_name_plural = "Purposes"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

# --- Blog Model ---
class Blog(BaseClass):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    )
    title = models.CharField(max_length=100)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='authorby')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='categoryby')
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, related_name='languageby')
    content = HTMLField()
    status = models.CharField(max_length=9, choices=STATUS_CHOICES, default='draft')
    featured_image = models.ImageField(upload_to='blogs/images/%Y/%m/')
    pdf_file = models.FileField(upload_to='blogs/pdfs/%Y/%m/', blank=True, null=True)
    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    slug = models.SlugField(unique=True, max_length=110)

    class Meta:
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"
        indexes = [
            models.Index(fields=['slug', 'status']),
            models.Index(fields=['created_at', 'status']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

class Question(BaseClass):
    DIFFICULTY_CHOICES = (
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    )
    # Question Text
    question = models.TextField(max_length=300)
    # Slug for URL structure
    slug = models.SlugField(unique=True, max_length=200)
    # Foreign Keys to categorize the question
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='category_wise_questions')
    sub_category = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, related_name='sub_catetory_wise_questions')
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True)
    purpose = models.ForeignKey(Purpose, on_delete=models.SET_NULL, null=True, related_name='purpose_wise_questions')

    # Options for the multiple-choice question
    option1 = models.CharField(max_length=50, null=True)
    option2 = models.CharField(max_length=50, null=True)
    option3 = models.CharField(max_length=50, null=True)
    option4 = models.CharField(max_length=50, null=True)


    # The correct option (This stores the option number as a string, e.g., 'option1', 'option2')
    correct_answer = models.CharField(max_length=50)

    # Explanation for the correct answer
    explanation = HTMLField()

    # Difficulty level of the question
    difficulty = models.CharField(max_length=6, choices=DIFFICULTY_CHOICES, default='medium')

    # SEO Meta fields
    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)

    class Meta:
        verbose_name = "MCQ Question"
        verbose_name_plural = "MCQ Questions"
        indexes = [
            models.Index(fields=['slug', 'difficulty']),
            models.Index(fields=['category', 'sub_category']),
        ]

    def save(self, *args, **kwargs):
        # Generate slug if not provided
        if not self.slug:
            base_slug = slugify(f"{self.category.name if self.category else 'question'} {self.question}")[:180]
            self.slug = self.generate_unique_slug(base_slug)

        # Set meta_title if not provided
        if not self.meta_title:
            self.meta_title = self.question[:60]
        if not self.meta_description:
            self.meta_description = self.question[:200]
        
        # Clean the explanation by removing HTML tags if any
        self.explanation = strip_tags(self.explanation)
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.question[:50]}... ({self.difficulty})"

# --- Contact & Feedback Models ---
class ContactRequest(BaseClass):
    STATUS_CHOICES = (
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    )
    
    name = models.CharField(max_length=80)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    subject = models.CharField(max_length=100)
    message = models.TextField(max_length=500)
    status = models.CharField(max_length=11, choices=STATUS_CHOICES, default='new')

    class Meta:
        verbose_name = "Contact Request"
        verbose_name_plural = "Contact Requests"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.subject} - {self.get_status_display()}"

class Feedback(BaseClass):
    RATING_CHOICES = (
        (5, 'Excellent'),
        (4, 'Good'),
        (3, 'Average'),
        (2, 'Poor'),
        (1, 'Very Poor'),
    )
    
    ISSUE_CHOICES = (
        ('design', 'Design Problem'),
        ('content', 'Content Error'),
        ('technical', 'Technical Issue'),
        ('other', 'Other'),
        ('None','None')
    )
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    blog_title_or_question = models.CharField(null=True, blank=True, max_length=300)
    overall_experience = models.IntegerField(default=5, choices=RATING_CHOICES)
    content_quality = models.IntegerField(default=5, choices=RATING_CHOICES)
    design_quality = models.IntegerField(default=5, choices=RATING_CHOICES)
    issue_type = models.CharField(choices=ISSUE_CHOICES, default='None', max_length=15)
    description_of_issue = models.TextField(max_length=300, blank=True)
    additional_comment = models.TextField(max_length=300, blank=True)

    class Meta:
        verbose_name = "User Feedback"
        verbose_name_plural = "User Feedback"
        ordering = ['-created_at']

    def __str__(self):
        return f"Feedback #{self.uid} ({self.get_overall_experience_display()})"
