from django.test import TestCase,client
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import datetime
from django.utils import timezone
import uuid
from .models import Blog, Category, Question, Purpose,Language,SubCategory,ContactRequest,Feedback
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils.text import slugify
from django.core.paginator import Paginator
from django.http import JsonResponse
from unittest.mock import patch


# Model unitest
class LanguageModelTest(TestCase):
    def test_create_language(self):
        # Test creating a Language object with the default language
        language = Language.objects.create(language='English')
        self.assertEqual(language.language, 'English')
        self.assertIsNotNone(language.uid)  # Check if uid is set
        self.assertEqual(str(language), 'English')  # Check the string representation

    def test_default_language(self):
        # Test that the default language is set to 'English'
        language = Language.objects.create(language='English')
        self.assertEqual(language.language, 'English')

    def test_language_choices(self):
        # Test if only valid choices are allowed
        valid_language = Language.objects.create(language='Hindi')
        self.assertEqual(valid_language.language, 'Hindi')

        # Check invalid language (this should raise a validation error)
        with self.assertRaises(ValidationError):
            invalid_language = Language(language='Invalid')
            invalid_language.full_clean()  # Manually trigger validation

    def test_language_str_method(self):
        # Test the __str__ method
        language = Language.objects.create(language='Hindi')
        self.assertEqual(str(language), 'Hindi')

class CategoryModelTest(TestCase):

    def test_category_creation_without_slug(self):
        # Create a category without providing a slug.
        category = Category.objects.create(name="Test Category")
        
        # Check if the category is saved and the slug is automatically generated.
        self.assertEqual(category.slug, slugify(category.name))
    
    def test_category_creation_with_slug(self):
        # Create a category with a provided slug.
        category = Category.objects.create(name="Test Category", slug="test-category")
        
        # Check if the slug is exactly as provided.
        self.assertEqual(category.slug, "test-category")
    
    def test_category_name_uniqueness(self):
        # Create a category with a specific name
        Category.objects.create(name="Unique Category")
        
        # Try creating another category with the same name, it should raise an IntegrityError
        with self.assertRaises(IntegrityError):
            Category.objects.create(name="Unique Category")
    
    def test_category_slug_uniqueness(self):
        # Create a category with a specific slug
        Category.objects.create(name="Category One", slug="unique-slug")
        
        # Try creating another category with the same slug, it should raise an IntegrityError
        with self.assertRaises(IntegrityError):
            Category.objects.create(name="Category Two", slug="unique-slug")
    
    def test_str_method(self):
        category = Category.objects.create(name="Test Category")
        
        # Check if the string representation of the category is the name
        self.assertEqual(str(category), "Test Category")

class SubCategoryModelTest(TestCase):

    def test_subcategory_creation_without_slug(self):
        # Create a subcategory without providing a slug
        subcategory = SubCategory.objects.create(name="Test SubCategory")
        
        # Check if the slug is automatically generated based on the name
        self.assertEqual(subcategory.slug, slugify(subcategory.name))
    
    def test_subcategory_creation_with_slug(self):
        # Create a subcategory with a predefined slug
        subcategory = SubCategory.objects.create(name="Test SubCategory", slug="test-subcategory")
        
        # Check if the slug is exactly as provided
        self.assertEqual(subcategory.slug, "test-subcategory")
    
    def test_subcategory_name_uniqueness(self):
        # Create a subcategory with a specific name
        SubCategory.objects.create(name="Unique SubCategory")
        
        # Try creating another subcategory with the same name; this should raise an IntegrityError
        with self.assertRaises(IntegrityError):
            SubCategory.objects.create(name="Unique SubCategory")
    
    def test_subcategory_slug_uniqueness(self):
        # Create a subcategory with a specific slug
        SubCategory.objects.create(name="SubCategory One", slug="unique-slug")
        
        # Try creating another subcategory with the same slug; this should raise an IntegrityError
        with self.assertRaises(IntegrityError):
            SubCategory.objects.create(name="SubCategory Two", slug="unique-slug")
    
    def test_str_method(self):
        subcategory = SubCategory.objects.create(name="Test SubCategory")
        
        # Check if the string representation of the subcategory is in the format "name | slug"
        self.assertEqual(str(subcategory), f"{subcategory.name} | {subcategory.slug}")

class PurposeModelTest(TestCase):

    def test_purpose_creation_without_slug(self):
        # Create a purpose without providing a slug
        purpose = Purpose.objects.create(title="Test Purpose", description="This is a test purpose.")
        
        # Check if the slug is automatically generated based on the title
        self.assertEqual(purpose.slug, slugify(purpose.title))
    
    def test_purpose_creation_with_slug(self):
        # Create a purpose with a predefined slug
        purpose = Purpose.objects.create(title="Test Purpose", description="This is a test purpose.", slug="test-purpose")
        
        # Check if the slug is exactly as provided
        self.assertEqual(purpose.slug, "test-purpose")
    
    def test_purpose_title_uniqueness(self):
        # Create a purpose with a specific title
        Purpose.objects.create(title="Unique Purpose", description="A unique purpose description.")
        
        # Try creating another purpose with the same title; this should raise an IntegrityError
        with self.assertRaises(IntegrityError):
            Purpose.objects.create(title="Unique Purpose", description="Another description.")
    
    def test_purpose_slug_uniqueness(self):
        # Create a purpose with a specific slug
        Purpose.objects.create(title="Purpose One", description="Description for Purpose One", slug="unique-slug")
        
        # Try creating another purpose with the same slug; this should raise an IntegrityError
        with self.assertRaises(IntegrityError):
            Purpose.objects.create(title="Purpose Two", description="Description for Purpose Two", slug="unique-slug")
    
    def test_str_method(self):
        purpose = Purpose.objects.create(title="Test Purpose", description="Description for test purpose")
        
        # Check if the string representation of the purpose is the title
        self.assertEqual(str(purpose), purpose.title)

class BlogTest(TestCase):
    def setUp(self):
        # Set up required objects for tests
        self.category = Category.objects.create(name="Test Category")
        self.language = Language.objects.create(language="English")
        self.user = User.objects.create_user(username="testuser", password="password")
        self.blog_data = {
            'title': "Test Blog",
            'category': self.category,
            'language': self.language,
            'author': self.user,
            'description': "<p>This is a test blog</p>",
            'blog_list_image': "path/to/list_image.jpg",
            'detail_image': "path/to/detail_image.jpg"
        }

    def test_blog_creation_without_slug(self):
        # Create a blog post without providing a slug
        blog = Blog.objects.create(**self.blog_data)
        
        # Check if the slug is automatically generated based on the title
        self.assertEqual(blog.slug, slugify(blog.title))

    def test_blog_creation_with_slug(self):
        # Create a blog post with a predefined slug
        blog_data_with_slug = self.blog_data.copy()
        blog_data_with_slug['slug'] = "custom-slug"
        blog = Blog.objects.create(**blog_data_with_slug)
        
        # Check if the slug is exactly as provided
        self.assertEqual(blog.slug, "custom-slug")

    def test_blog_slug_uniqueness(self):
        # Create a blog post with a specific slug
        blog_data_with_slug = self.blog_data.copy()
        blog_data_with_slug['slug'] = "unique-slug"
        Blog.objects.create(**blog_data_with_slug)
        
        # Try creating another blog with the same slug; this should raise an IntegrityError
        with self.assertRaises(IntegrityError):
            Blog.objects.create(**blog_data_with_slug)

    def test_blog_foreign_keys(self):
        # Create a blog post and check if it is correctly linked to the Category, Language, and User
        blog = Blog.objects.create(**self.blog_data)
        
        # Check the foreign key relations
        self.assertEqual(blog.category, self.category)
        self.assertEqual(blog.language, self.language)
        self.assertEqual(blog.author, self.user)

    def test_str_method(self):
        # Create a blog post
        blog = BlogsModel.objects.create(**self.blog_data)
        
        # Check if the string representation is in the format "title | published_date with timezone"
        expected_str = f"{blog.title} | {blog.published_date}"
        self.assertEqual(str(blog), expected_str)

    def test_blog_pdf_field(self):
        # Create a blog post with a PDF file
        blog_data_with_pdf = self.blog_data.copy()
        blog_data_with_pdf['pdf_file'] = "path/to/pdf_file.pdf"
        blog = BlogsModel.objects.create(**blog_data_with_pdf)
        
        # Check that the PDF file has been set correctly
        self.assertEqual(blog.pdf_file.name, "path/to/pdf_file.pdf")

    def test_blog_images_fields(self):
        # Create a blog post with images
        blog = BlogsModel.objects.create(**self.blog_data)
        
        # Check that the image file paths have been set correctly
        self.assertEqual(blog.blog_list_image.name, "path/to/list_image.jpg")
        self.assertEqual(blog.detail_image.name, "path/to/detail_image.jpg")

class QuestionTest(TestCase):
    def setUp(self):
        # Set up categories, subcategories, languages, purposes
        self.category = Category.objects.create(name="Maths")
        self.sub_category = SubCategory.objects.create(name="Algebra")
        
        # Adjusting the Language creation to use 'name' field (assuming 'name' exists in the model)
        self.language = Language.objects.create(language="English")
        
        self.purpose = Purpose.objects.create(title="Education", description="For learning purposes")

        # Create an MCQ_Question instance
        self.mcq = Question.objects.create(
            question="What is 2 + 2?",
            category=self.category,
            sub_category=self.sub_category,
            language=self.language,
            purpose=self.purpose,
            option1="3",
            option2="4",
            option3="5",
            option4="6",
            correct_ans="4",
            explanation="<p>The answer is 4</p>",
        )

    def test_uuid_field(self):
        # Assert that the UUID is set correctly
        self.assertTrue(isinstance(self.mcq.uid, uuid.UUID))
        self.assertIsNotNone(self.mcq.uid)

    def test_slug_generation(self):
        # Assert that the slug is generated correctly based on the question
        self.assertEqual(self.mcq.slug, slugify("What is 2 + 2?"))

    def test_str_method(self):
        # Assert the __str__ method output
        expected_str = f'{self.mcq.question} | {self.category.name}'
        self.assertEqual(str(self.mcq), expected_str)

    def test_foreign_key_relationships(self):
        # Assert that the foreign keys are correctly assigned
        self.assertEqual(self.mcq.category, self.category)
        self.assertEqual(self.mcq.sub_category, self.sub_category)
        self.assertEqual(self.mcq.language, self.language)
        self.assertEqual(self.mcq.purpose, self.purpose)

class ContactRequestTest(TestCase):
    def setUp(self):
        # Set up contact query data for testing
        self.contact_query_data = {
            'name': "John Doe",
            'phone': "1234567890",
            'email': "johndoe@example.com",
            'subject': "Test Subject",
            'query': "This is a test query."
        }
        # Create and save a ContactQuery instance
        self.contact_query = ContactRequest.objects.create(**self.contact_query_data)

    def test_uuid_field(self):
        # Test that the UUID is set correctly
        self.assertTrue(isinstance(self.contact_query.uid, uuid.UUID))
        self.assertIsNotNone(self.contact_query.uid)

    def test_slug_generation(self):
        # Assert that the slug is generated based on the name field
        self.assertEqual(self.contact_query.slug, slugify(self.contact_query.name))

    def test_unique_phone(self):
        # Assert that creating a contact query with a duplicate phone raises an IntegrityError
        contact_query_data_new_phone = self.contact_query_data.copy()
        contact_query_data_new_phone['phone'] = "1234567890"  # Duplicate phone number

        with self.assertRaises(IntegrityError):
            ContactQuery.objects.create(**contact_query_data_new_phone)

    def test_unique_email(self):
        # Assert that creating a contact query with a duplicate email raises an IntegrityError
        contact_query_data_new_email = self.contact_query_data.copy()
        contact_query_data_new_email['email'] = "johndoe@example.com"  # Duplicate email

        with self.assertRaises(IntegrityError):
            ContactQuery.objects.create(**contact_query_data_new_email)

    def test_str_method(self):
        # Ensure the object is saved and has a uuid before calling str()
        self.contact_query.save()  # Save explicitly to ensure the `uid` is assigned
        expected_str = f'{self.contact_query.uid} | {self.contact_query.name} | {self.contact_query.subject}'
        self.assertEqual(str(self.contact_query), expected_str)

class FeedbackModelTest(TestCase):
    def setUp(self):
        # Setup initial test data
        self.feedback = Feedback.objects.create(
            overall_experience='5',  # Excellent
            content_quality='4',  # Good
            design_usability='3',  # Average
            most_enjoyable_thing="The design is user-friendly.",
            suggestions="Add more features.",
            encountered_any_issues='2',  # Content Error
            description_of_issue="The text in the footer is incorrect.",
            additional_comment="Great work overall!",
        )

    def test_feedback_creation(self):
        # Test that the feedback instance is created properly
        feedback = self.feedback
        self.assertEqual(feedback.overall_experience, '5')
        self.assertEqual(feedback.content_quality, '4')
        self.assertEqual(feedback.design_usability, '3')
        self.assertEqual(feedback.most_enjoyable_thing, "The design is user-friendly.")
        self.assertEqual(feedback.suggestions, "Add more features.")
        self.assertEqual(feedback.encountered_any_issues, '2')
        self.assertEqual(feedback.description_of_issue, "The text in the footer is incorrect.")
        self.assertEqual(feedback.additional_comment, "Great work overall!")

    def test_slug_creation(self):
        # Test that the slug is created when description_of_issue is provided
        feedback = self.feedback
        feedback.save()  # Ensure the save method is triggered
        self.assertEqual(feedback.slug, "the-text-in-the-footer-is-incorrect")

    def test_string_representation(self):
        # Test the string representation of the model
        feedback = self.feedback
        expected_str = f'{feedback.uid} | {feedback.overall_experience} | {feedback.content_quality} | {feedback.encountered_any_issues}'
        self.assertEqual(str(feedback), expected_str)

    def test_default_values(self):
        # Test default values for feedback fields
        feedback = Feedback.objects.create(
            most_enjoyable_thing="The navigation is intuitive.",
            suggestions="Maybe improve speed.",
            description_of_issue="No issues.",
            additional_comment="Overall satisfied.",
        )
        self.assertEqual(feedback.overall_experience, '5')
        self.assertEqual(feedback.content_quality, '5')
        self.assertEqual(feedback.design_usability, '5')
        self.assertEqual(feedback.encountered_any_issues, '5')
        self.assertEqual(feedback.slug, "no-issues")

    def test_invalid_feedback(self):
        # Test creating invalid feedback (e.g. passing invalid choices)
        feedback = Feedback(
            overall_experience='6',  # Invalid choice, since the valid choices are '1' to '5'
            content_quality='4',
            design_usability='3',
            most_enjoyable_thing="Great experience.",
            suggestions="None.",
            encountered_any_issues='2',
            description_of_issue="Minor bug.",
            additional_comment="Fix soon.",
        )

        # Expecting ValidationError to be raised due to invalid choice in overall_experience
        with self.assertRaises(ValidationError):
            feedback.full_clean()  # This triggers the validation

class BlogsViewTestCase(TestCase):
    def setUp(self):
        # Create a user and a category
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.category = Category.objects.create(name="Tech")
        self.language = Language.objects.create(language="English")
        # Create some blog posts
        self.blog1 = Blog.objects.create(
            title="Blog Post 1",
            category=self.category,
            language=self.language,
            author=self.user,
            description="Description of Blog Post 1",
            published_date=timezone.now(),
            blog_list_image="image1.jpg",
            detail_image="detail1.jpg",
            slug="blog-post-1"
        )
        self.blog2 = Blog.objects.create(
            title="Blog Post 2",
            category=self.category,
            language=self.language,
            author=self.user,
            description="Description of Blog Post 2",
            published_date=timezone.now(),
            blog_list_image="image2.jpg",
            detail_image="detail2.jpg",
            slug="blog-post-2"
        )
        self.blog_today = Blog.objects.create(
            title="Blog Post Today",
            category=self.category,
            language=self.language,
            author=self.user,
            description="Description of Blog Post Today",
            published_date=timezone.now(),
            blog_list_image="image_today.jpg",
            detail_image="detail_today.jpg",
            slug="blog-post-today"
        )

    def test_blogs_view(self):
        # Make a GET request to the blogs view
        response = self.client.get(reverse('home'))  # Use the correct name 'blogs'
        # Check if the response is successful
        self.assertEqual(response.status_code, 200)
        # Check if the correct template is used
        self.assertTemplateUsed(response, 'blog/index.html')
           # Check if the context contains the correct data
        self.assertIn('cat_manu', response.context)
        self.assertIn('pages', response.context)
        self.assertIn('slides', response.context)
        
    def test_blogs_view_with_pagination(self):
        # Create more blog posts to test pagination
        for i in range(7):
            Blog.objects.create(
                title=f"Extra Blog Post {i+3}",
                category=self.category,
                language=self.language,
                author=self.user,
                description=f"Description of Extra Blog Post {i+3}",
                published_date=timezone.now() - timezone.timedelta(days=i+3),
                blog_list_image="extra_image.jpg",
                detail_image="extra_detail.jpg",
                slug=f"extra-blog-post-{i+3}"
            )

        # Test pagination with the new posts
        response = self.client.get(reverse('home') + '?page=2')  # Use the correct name 'blogs'
        self.assertEqual(response.status_code, 200)

class BlogDetailViewTestCase(TestCase):
    
    def setUp(self):
        # Create a user and category for blog posts
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.category = Category.objects.create(name="Tech")
        self.language = Language.objects.create(language='English')
        
        # Create a single blog post
        self.blog = Blog.objects.create(
            title="Blog Post 1",
            category=self.category,
            language=self.language,
            author=self.user,
            description="Description of Blog Post 1",
            published_date=timezone.now(),
            blog_list_image="image1.jpg",
            detail_image="detail1.jpg",
            slug="blog-post-1"
        )

    def test_blog_detail_view(self):
        # Test that the BlogDetail view works for the single blog post
        response = self.client.get(reverse('post_detail', kwargs={'slug': self.blog.slug}))
        # Check that the response is successful (status code 200)
        self.assertEqual(response.status_code, 200)
        # Check that the correct template is used
        self.assertTemplateUsed(response, 'blog/blog_detail.html')
        # Check that the correct context data is passed to the template
        self.assertIn('obj', response.context)  # The current blog post
        self.assertIn('obje', response.context)  # Other blog posts (should be empty since only one exists)
        self.assertIn('cat_manu', response.context)  # Categories
        self.assertIn('random_blogs', response.context)  # Random blogs (should be 1, since there's only one blog)
        # Ensure the blog post is correct in the context
        self.assertEqual(response.context['obj'], self.blog)
        # Ensure that 'obje' is empty because there are no other posts
        self.assertEqual(len(response.context['obje']), 0)
        # Ensure that the 'cat_manu' contains categories
        self.assertTrue(response.context['cat_manu'].exists())
        # Ensure that 'random_blogs' contains only the current blog post (since it's the only one)
        self.assertEqual(len(response.context['random_blogs']), 1)
        self.assertEqual(response.context['random_blogs'][0], self.blog)

    def test_blog_detail_no_blog_found(self):
        # Test the case where no blog is found for a given slug
        response = self.client.get(reverse('post_detail', kwargs={'slug': 'non-existent-slug'}))
        
        # Check if 404 error occurs when a blog post does not exist
        self.assertEqual(response.status_code, 404)

class TestSeriesListViewTestCase(TestCase):

    def setUp(self):
        # Set up test data for categories, sub-categories, and languages
        self.category = Category.objects.create(name='Science')
        self.sub_category = SubCategory.objects.create(name='Physics')
        self.language = Language.objects.create(language='English')
        
        # Set up test data for Purpose and MCQ_Question models
        self.purpose = Purpose.objects.create(title='Test Series 1', description='Sample Test Series 1')
        
        # Creating one MCQ question
        self.mcq1 = Question.objects.create(
            question='What is 2+2?',
            category=self.category,
            sub_category=self.sub_category,
            language=self.language,
            purpose=self.purpose,
            option1='3', option2='4', option3='5', option4='6',
            correct_ans='4',
            explanation='Simple addition.',
            slug='what-is-2-plus-2'
        )

    def test_test_series_list_view(self):
        # Test that the TestSeriesList view works correctly
        response = self.client.get(reverse('test-series'))  # Use the correct URL name here
        
        # Check if the response status is 200 (OK)
        self.assertEqual(response.status_code, 200)
        
        # Check if the correct template is used
        self.assertTemplateUsed(response, 'mcq/test-series-list.html')
        
        # Check if the context contains the correct data
        self.assertIn('test_series_list', response.context)
        self.assertIn('pages', response.context)
        self.assertIn('cat_manu', response.context)
        self.assertIn('random_question', response.context)
        self.assertIn('total_question', response.context)
        
        # Ensure that the random question is selected from MCQ_Question
        random_question = response.context['random_question']
        self.assertEqual(random_question, self.mcq1)
        
        # Check the total number of MCQs is correct
        self.assertEqual(response.context['total_question'], Question.objects.count())
        
    #    # Ensure pagination is working correctly
    #     test_series_list = Purpose.objects.all() # Order the queryset by uid
    #     pag = Paginator(test_series_list, 1)  # Set paginator to 1 item per page for this test
        self.assertEqual(len(response.context['pages'].object_list), 1)  # Should return 1 test series on the first page
         
        # Check the categories are correctly passed to the context
        self.assertTrue(response.context['cat_manu'].exists())

    def test_pagination(self):
        # Add more purposes to check pagination
        for i in range(25):  # Adding 25 test series to ensure pagination
            Purpose.objects.create(title=f'Test Series {i+2}', description=f'Sample Test Series {i+2}')
        
        # Test pagination by checking the second page
        response = self.client.get(reverse('test-series') + '?page=2')
        
        # Check pagination: should display 20 items per page (as set in the paginator)
        self.assertEqual(response.status_code, 200)
        
        # Check that the first item on the second page is correct
        self.assertEqual(response.context['pages'].object_list[0].title, 'Test Series 21')

class CategoriesWiseQuestionViewTestCase(TestCase):

    def setUp(self):
        # Create a test category
        self.category = Category.objects.create(name='Science', slug='science')
        self.sub_category = SubCategory.objects.create(name='Science tech', slug='science-tech')
        self.purpose = Purpose.objects.create(title='Practice')

        # Create a test MCQ question for the category
        self.mcq = Question.objects.create(
            question='What is the chemical symbol for water?',
            category=self.category,
            sub_category=self.sub_category,  # Corrected field name
            purpose=self.purpose,
            language=Language.objects.create(language='English'),
            option1='H2O', option2='O2', option3='CO2', option4='N2',
            correct_ans='H2O',
            explanation='The chemical symbol for water is H2O.',
            slug='water-chemical-symbol'
        )

    def test_categories_wise_question_view(self):
        # Simulate GET request to the view for the category
        response = self.client.get(reverse('category-wise-question', kwargs={'slug': self.category.slug}))

        # Check if the response is successful
        self.assertEqual(response.status_code, 200)

        # Check if the correct template is used
        self.assertTemplateUsed(response, 'mcq/categorywisequestion.html')

        # Check if the context contains the correct data
        self.assertIn('category', response.context)
        self.assertIn('cat_manu', response.context)  # Ensure 'cat_manu' is in context
        self.assertIn('next_question', response.context)
        self.assertIn('options', response.context)

        # Check if the next_question in context is the question we created
        self.assertEqual(response.context['next_question'], self.mcq)

        # Ensure the options are shuffled (Ensure they're not in the same order as before)
        options = response.context['options']
        self.assertNotEqual(options, ['H2O', 'O2', 'CO2', 'N2'])

    def test_answer_submission(self):
        # Simulate POST request with selected answer (correct answer)
        response = self.client.post(reverse('category-wise-question', kwargs={'slug': self.category.slug}),
                                    {'mcq_option': 'H2O'})  # Correct answer
        
        # Check if the response is successful
        self.assertEqual(response.status_code, 200)

        # Check if session variables are correctly set for the answer
        self.assertEqual(self.client.session.get('selected_answer'), 'H2O')
        self.assertEqual(self.client.session.get('is_answer_correct'), True)

    def test_answer_submission_incorrect_answer(self):
        # Simulate POST request with incorrect answer
        response = self.client.post(reverse('category-wise-question', kwargs={'slug': self.category.slug}),
                                    {'mcq_option': 'O2'})  # Incorrect answer
        
        # Check if the response is successful
        self.assertEqual(response.status_code, 200)

        # Check if session variables are correctly set for the answer
        self.assertEqual(self.client.session.get('selected_answer'), 'O2')
        self.assertEqual(self.client.session.get('is_answer_correct'), False)
    
    def test_redirect_when_no_questions_left(self):
        # Simulate a request to the view, assuming the category has 1 question and we're at current_question_id 1
        self.client.get(reverse('category-wise-question', kwargs={'slug': self.category.slug}) + '?current_question=1')

        # Since the current_question_id is equal to the number of available questions, we expect a redirect
        response = self.client.get(reverse('category-wise-question', kwargs={'slug': self.category.slug}) + '?current_question=1')
        
        # Check if the user is redirected to 'endpractice'
        self.assertRedirects(response, reverse('endpractice'))

        
    def test_invalid_category_slug(self):
        # Test that an invalid category slug returns a 404 error
        response = self.client.get(reverse('category-wise-question', kwargs={'slug': 'non-existent-category'}))
        
        # Check if a 404 is returned
        self.assertEqual(response.status_code, 404)

class SubCategoryListViewTestCase(TestCase):

    def setUp(self):
        # Set up test data for categories, sub-categories, and languages
        self.category = Category.objects.create(name='Science')
        self.sub_category = SubCategory.objects.create(name='Physics')
        self.language = Language.objects.create(language='English')
        
        # Set up test data for Purpose and MCQ_Question models
        self.purpose = Purpose.objects.create(title='Test Series 1', description='Sample Test Series 1')
        
        # Create only one MCQ question
        self.mcq1 = Question.objects.create(
            question='What is 2+2?',
            category=self.category,
            sub_category=self.sub_category,
            language=self.language,
            purpose=self.purpose,
            option1='3', option2='4', option3='5', option4='6',
            correct_ans='4',
            explanation='Simple addition.',
            slug='what-is-2-plus-2'
        )

    def test_subcategory_list_view(self):
        # Test that the SubCategoryList view works correctly
        response = self.client.get(reverse('sub-category-test'))  # Use the correct URL name here
        
        # Check if the response status is 200 (OK)
        self.assertEqual(response.status_code, 200)
        
        # Check if the correct template is used
        self.assertTemplateUsed(response, 'mcq/Subcategory-list.html')
        
        # Check if the context contains the correct data
        self.assertIn('subcategorylist', response.context)
        self.assertIn('pages', response.context)
        self.assertIn('cat_manu', response.context)
        self.assertIn('random_question', response.context)
        self.assertIn('total_question', response.context)
        
        # Ensure that the random question is selected from MCQ_Question
        random_question = response.context['random_question']
        self.assertEqual(random_question, self.mcq1)  # It should be the only question
        
        # Check the total number of MCQs is correct
        self.assertEqual(response.context['total_question'], Question.objects.count())
        
        # Ensure pagination is working correctly
        subcategory_list = SubCategory.objects.all()  # Get all subcategories
        pag = Paginator(subcategory_list, 20)  # Set paginator to 20 items per page for this test
        self.assertEqual(len(response.context['pages'].object_list), 1)  # Only 1 subcategory should be returned
        
        # Check the categories are correctly passed to the context
        self.assertTrue(response.context['cat_manu'].exists())

class SubCategoryWiseQuestionViewTestCase(TestCase):

    def setUp(self):
        # Set up test data for categories and languages
        self.category = Category.objects.create(name='Science')
        self.sub_category = SubCategory.objects.create(name='Physics', slug='physics')
        self.language = Language.objects.create(language='English')

        # Set up test data for Purpose and MCQ_Question models
        self.purpose = Purpose.objects.create(title='Test Series 1', description='Sample Test Series 1')

        # Create one MCQ question for the subcategory
        self.mcq1 = Question.objects.create(
            question='What is 2+2?',
            category=self.category,  # The question still has the category associated with it
            sub_category=self.sub_category,
            language=self.language,
            purpose=self.purpose,
            option1='3', option2='4', option3='5', option4='6',
            correct_ans='4',
            explanation='Simple addition.',
            slug='what-is-2-plus-2'
        )

    def test_subcategory_wise_question_view(self):
        # Test that the SubCategoryWiseQuestion view works correctly for the first question
        response = self.client.get(reverse('sub-category-wise-question', kwargs={'slug': 'physics'}))  # Make sure the URL pattern is correct
        
        # Check if the response status is 200 (OK)
        self.assertEqual(response.status_code, 200)
        
        # Check if the correct template is used
        self.assertTemplateUsed(response, 'mcq/subcategoryewisequestion.html')
        
        # Check if the context contains the correct data
        self.assertIn('subcategory', response.context)
        self.assertIn('next_question', response.context)
        self.assertIn('options', response.context)
        self.assertIn('next_question_id', response.context)
        
        # Ensure that the correct question (mcq1) is in the context
        next_question = response.context['next_question']
        self.assertEqual(next_question, self.mcq1)  # The first and only question should be passed to the context
        
        # Get the options from the context
        options = response.context['options']
        
        # Check that the options are shuffled by comparing the shuffled list with the original order
        original_order = [self.mcq1.option1, self.mcq1.option2, self.mcq1.option3, self.mcq1.option4]
        
        # Ensure that the options are shuffled (not in the original order)
        self.assertNotEqual(options, original_order)
        
        # Check that next_question_id is correct (it should be 1 after displaying the first question)
        self.assertEqual(response.context['next_question_id'], 1)


    def test_subcategory_wise_question_view_end_redirect(self):
        # Test that when the last question is shown, the user is redirected to 'endpractice'
        response = self.client.get(reverse('sub-category-wise-question', kwargs={'slug': 'physics'}) + '?current_question=1')  # Try to go beyond the last question
        
        # Check if the response redirects to 'endpractice'
        self.assertRedirects(response, reverse('endpractice'))

class ResultViewTest(TestCase):

    def setUp(self):
        # Create categories
        self.category = Category.objects.create(name="General Knowledge")
        
        # Create subcategories
        self.sub_category = SubCategory.objects.create(name="Science")
        
        # Create languages
        self.language = Language.objects.create(language="English")
        
        # Create purposes
        self.purpose = Purpose.objects.create(title="Test Purpose")
        
        # Create MCQ questions
        self.mcq_1 = Question.objects.create(
            question="What is the capital of France?",
            category=self.category,
            sub_category=self.sub_category,
            language=self.language,
            purpose=self.purpose,
            option1="London",
            option2="Berlin",
            option3="Paris",
            option4="Madrid",
            correct_ans="Paris",
            explanation="<p>Paris is the capital city of France.</p>",
            slug="what-is-the-capital-of-france"
        )
        
        self.mcq_2 = Question.objects.create(
            question="What is 2 + 2?",
            category=self.category,
            sub_category=self.sub_category,
            language=self.language,
            purpose=self.purpose,
            option1="3",
            option2="4",
            option3="5",
            option4="6",
            correct_ans="4",
            explanation="<p>2 + 2 equals 4.</p>",
            slug="what-is-2-plus-2"
        )

        # Set up session data (simulate user session with attempted, correct, incorrect answers)
        self.session_data = {
            'attempted_questions': 5,
            'correct_answers': 3,
            'incorrect_answers': 2,
        }
        
    def test_result_view(self):
        # Set the session data
        session = self.client.session
        session['attempted_questions'] = self.session_data['attempted_questions']
        session['correct_answers'] = self.session_data['correct_answers']
        session['incorrect_answers'] = self.session_data['incorrect_answers']
        session.save()

        # Send a GET request to the ResultView
        response = self.client.get(reverse('endpractice'))

        # Check that the response status is 200 OK
        self.assertEqual(response.status_code, 200)

        # Check that the correct data is passed into the context
        self.assertIn('attempted', response.context)
        self.assertIn('correct', response.context)
        self.assertIn('incorrect', response.context)
        self.assertIn('percentage', response.context)
        self.assertIn('next_question', response.context)
        self.assertIn('cat_manu', response.context)

        # Get the result data from the response context
        context_data = response.context

        # Validate session data
        self.assertEqual(context_data['attempted'], self.session_data['attempted_questions'])
        self.assertEqual(context_data['correct'], self.session_data['correct_answers'])
        self.assertEqual(context_data['incorrect'], self.session_data['incorrect_answers'])

        # Calculate expected percentage
        expected_percentage = (self.session_data['correct_answers'] / self.session_data['attempted_questions']) * 100
        self.assertEqual(context_data['percentage'], expected_percentage)

        # Validate next question (randomly chosen MCQ)
        self.assertIn(context_data['next_question'], [self.mcq_1, self.mcq_2])

        # Check that the categories are being passed in the context
        self.assertIn(self.category, context_data['cat_manu'])

        # Reset session after the result (simulate the actual view behavior)
        session.flush()

    def test_result_view_no_session_data(self):
        # Send a GET request to the ResultView without setting session data
        response = self.client.get(reverse('endpractice'))

        # Check that the response status is 200 OK
        self.assertEqual(response.status_code, 200)

        # Check if session data is missing, and default values are used
        self.assertIn('attempted', response.context)
        self.assertIn('correct', response.context)
        self.assertIn('incorrect', response.context)
        self.assertIn('percentage', response.context)

        # Default values should be 0, since no session data is set
        self.assertEqual(response.context['attempted'], 0)
        self.assertEqual(response.context['correct'], 0)
        self.assertEqual(response.context['incorrect'], 0)
        self.assertEqual(response.context['percentage'], 0)

class CategoriesViewTest(TestCase):
    
    def setUp(self):
        # Create a sample user (author of the blog posts)
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        
        # Create languages
        self.language_english = Language.objects.create(language="English")
        self.language_spanish = Language.objects.create(language="Spanish")
        
        # Create categories
        self.category_tech = Category.objects.create(name="Technology", slug="technology")
        self.category_science = Category.objects.create(name="Science", slug="science")
        
        # Create blog posts for the Technology category
        for i in range(15):  # 15 posts to test pagination
            Blog.objects.create(
                title=f"Technology Post {i}",
                category=self.category_tech,
                language=self.language_english,
                author=self.user,
                description=f"Description for Technology Post {i}",
                published_date=timezone.now(),
                blog_list_image="path_to_image",  # Add a path to an image
                detail_image="path_to_detail_image",  # Add a path to a detail image
                slug=f"tech-post-{i}"
            )

        # Create blog posts for the Science category
        for i in range(5):  # 5 posts for Science
            Blog.objects.create(
                title=f"Science Post {i}",
                category=self.category_science,
                language=self.language_spanish,
                author=self.user,
                description=f"Description for Science Post {i}",
                published_date=timezone.now(),
                blog_list_image="path_to_image",  # Add a path to an image
                detail_image="path_to_detail_image",  # Add a path to a detail image
                slug=f"science-post-{i}"
            )
    
    def test_categories_view_with_posts(self):
        # Test for category_tech (Technology)
        response = self.client.get(reverse('category', args=[self.category_tech.slug]))
        
        # Ensure the response status is 200
        self.assertEqual(response.status_code, 200)
        
        # Check that the category passed is the correct one
        self.assertEqual(response.context['category'], self.category_tech)
        
        # Ensure only 6 posts are shown on the first page due to pagination
        self.assertEqual(len(response.context['pages']), 6)
        
        # Check if pagination works (Test page 2 should have 6 more posts)
        response_page_2 = self.client.get(reverse('category', args=[self.category_tech.slug]) + '?page=2')
        self.assertEqual(len(response_page_2.context['pages']), 6)
        
        # Check if the list of categories is passed correctly to the template
        self.assertIn(self.category_tech, response.context['cat_manu'])
        self.assertIn(self.category_science, response.context['cat_manu'])
        
        # Check if the correct template is used
        self.assertTemplateUsed(response, 'blog/category.html')
    
    def test_categories_view_empty_category(self):
        # Delete all posts associated with the Science category
        Blog.objects.filter(category=self.category_science).delete()
        
        # Test for category_science (Science), which now has no posts
        response = self.client.get(reverse('category', args=[self.category_science.slug]))
        
        # Ensure the response status is 200
        self.assertEqual(response.status_code, 200)
        
        # Ensure there are no posts in the context for this category
        self.assertEqual(len(response.context['pages']), 0)  # No posts in category_science
        
        # Check that the list of categories is passed correctly
        self.assertIn(self.category_tech, response.context['cat_manu'])
        self.assertIn(self.category_science, response.context['cat_manu'])
        
        # Ensure the correct template is used
        self.assertTemplateUsed(response, 'blog/category.html')

    def test_categories_view_with_invalid_slug(self):
        # Test for an invalid category slug
        response = self.client.get(reverse('category', args=["invalid_slug"]))
        
        # Ensure a 404 error is returned since the category doesn't exist
        self.assertEqual(response.status_code, 404)

class RandomQuestionViewTest(TestCase):
    def setUp(self):
        # Create a sample category
        self.category = Category.objects.create(name="Test Category", slug="test-category")
        
        # Create sample MCQ questions
        self.question1 = Question.objects.create(
            question="What is 2 + 2?",  # Use 'question' instead of 'question_text'
            option1="3",
            option2="4",
            option3="5",
            option4="6",
            correct_ans="4",
            category=self.category,
            uid=uuid.uuid4()
        )
        self.question2 = Question.objects.create(
            question="What is the capital of France?",  # Use 'question' instead of 'question_text'
            option1="Berlin",
            option2="Madrid",
            option3="Paris",
            option4="Rome",
            correct_ans="Paris",
            category=self.category,
            uid=uuid.uuid4()
        )
        
        # Set up the request factory
        self.factory = RequestFactory()

    def add_session_to_request(self, request):
        """Helper function to add session to the request."""
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()

    def test_random_question_view(self):
        # Create a request for the first question
        request = self.factory.get(reverse('random_question', args=[self.question1.uid]))
        self.add_session_to_request(request)
        
        # Call the view
        response = RandomQuestion(request, uid=self.question1.uid)
        
        # Check that the response status is 200
        self.assertEqual(response.status_code, 200)
        
        # Check that the correct question is in the context
        self.assertEqual(response.context['question'], self.question1)
        
        # Check that the options are shuffled and the correct answer position is set
        self.assertIn(response.context['correct_answer_position'], [0, 1, 2, 3])
        
        # Check that the next question is set
        self.assertEqual(response.context['next_question'], self.question2)
        
        # Check that random questions are in the context
        self.assertEqual(len(response.context['random_questions']), 1)  # Only 1 other question exists
        
        # Check that session variables are initialized
        self.assertEqual(request.session['attempted_questions'], 0)
        self.assertEqual(request.session['correct_answers'], 0)
        self.assertEqual(request.session['incorrect_answers'], 0)

    def test_random_question_view_no_more_questions(self):
        # Delete all questions except the current one
        Question.objects.exclude(uid=self.question1.uid).delete()
        
        # Create a request for the first question
        request = self.factory.get(reverse('random_question', args=[self.question1.uid]))
        self.add_session_to_request(request)
        
        # Call the view
        response = RandomQuestion(request, uid=self.question1.uid)
        
        # Check that the response is a redirect to the end practice page
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('endpractice'))