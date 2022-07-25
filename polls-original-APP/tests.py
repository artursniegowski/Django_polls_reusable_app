import datetime
from urllib import response
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Question

###############################
## Testing Model  - Question ##
###############################

class QuestionModelTest(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future
         """
        time = timezone.now() + datetime.timedelta(days=30) 
        future_question = Question(pub_date = time)
        self.assertIs(future_question.was_published_recently() , False)


    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day
         """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1) 
        future_question = Question(pub_date = time)
        self.assertIs(future_question.was_published_recently() , False)


    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day
         """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=9) 
        future_question = Question(pub_date = time)
        self.assertIs(future_question.was_published_recently() , True)


###############################
## Testing IndexView  #########
###############################

def create_question(question_text, days, choice_text='Choice text'):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    Add choice_text as a random choice to each question. 
    """
    time = timezone.now() + datetime.timedelta(days=days)
    q = Question.objects.create(question_text=question_text, pub_date = time)
    if choice_text:
        q.choice_set.create(choice_text=choice_text, votes=0)
    return q


class QuestionIndexViewTests(TestCase):
    def test_no_question(self):
        """
        If no questions exists, an appropriate message is displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    
    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the index page
        """
        question = create_question(question_text='Past question', days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question],
        )

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on the index page.
        """
        create_question(question_text='Future question', days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [],)

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exists, onlly past questions
        are displayed
        """
        question = create_question(question_text='Past question', days=-30)
        create_question(question_text='Future question', days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question],
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        question1 = create_question(question_text='Past question 1', days=-29)
        question2 = create_question(question_text='Past question 2', days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question2, question1],
        )

    def test_question_without_any_choice(self):
        """
        The questions index page may display only questions if they have choices included.
        If there are no choices, the question wont be displayed
        """
        question = create_question(question_text='Past question 1', days=-29, choice_text=None)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [],
        )

    def test_question_with_at_least_one_choice(self):
        """
        The questions index page may display only questions if they have choices included.
        If there is one or more choices the question will be displayed.
        """
        question = create_question(question_text='Past question 1', days=-29, choice_text='Random choice')
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question],
        )

###############################
## Testing DetailView  #########
###############################

class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found
        """
        future_question = create_question(question_text="Future question.", days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
    

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past 
        displays the question's text
        """
        past_question = create_question(question_text="Past question.", days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)


###############################
## Testing ResultslView  ######
###############################
class QuestionResultsViewTests(TestCase):
    def test_future_question(self):
        """
        The results view of a question with a pub_date in the future
        returns a 404 not found
        """
        future_question = create_question(question_text="Future question.", days=5)
        url = reverse('polls:results', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
    

    def test_past_question(self):
        """
        The result view of a question with a pub_date in the past 
        displays the question's text
        """
        past_question = create_question(question_text="Past question.", days=-5)
        url = reverse('polls:results', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
