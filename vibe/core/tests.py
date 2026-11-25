from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Question, QuizAttempt, Topic

User = get_user_model()


class TopicModelTest(TestCase):
    def test_create_and_str(self):
        topic = Topic.objects.create(title="Тема 1", description="Описание")
        self.assertEqual(str(topic), "Тема 1")
        self.assertEqual(Topic.objects.count(), 1)


class QuestionModelTest(TestCase):
    def setUp(self):
        self.topic = Topic.objects.create(title="Тема 1")

    def test_create_question_with_options(self):
        question = Question.objects.create(
            topic=self.topic,
            text="Вопрос?",
            options=["А", "Б", "В", "Г"],
            correct_index=2,
        )
        self.assertEqual(question.correct_answer, "В")
        self.assertEqual(len(question.options), 4)

    def test_correct_answer_out_of_range(self):
        question = Question.objects.create(
            topic=self.topic,
            text="Вопрос?",
            options=["А", "Б"],
            correct_index=5,
        )
        self.assertEqual(question.correct_answer, "")


class QuizAttemptModelTest(TestCase):
    def test_create_attempt(self):
        user = User.objects.create_user("u1", password="pw")
        topic = Topic.objects.create(title="Тема 1")
        attempt = QuizAttempt.objects.create(
            user=user, topic=topic, question_ids=[1, 2], score=1, total=2
        )
        self.assertEqual(attempt.score, 1)
        self.assertEqual(QuizAttempt.objects.filter(user=user).count(), 1)

    def test_attempt_str(self):
        user = User.objects.create_user("u2", password="pw")
        topic = Topic.objects.create(title="Тема 1")
        attempt = QuizAttempt.objects.create(user=user, topic=topic)
        self.assertIn("u2", str(attempt))


class AuthViewsTest(TestCase):
    def test_register_get(self):
        response = self.client.get(reverse("core:register"))
        self.assertEqual(response.status_code, 200)

    def test_register_post_creates_user(self):
        response = self.client.post(
            reverse("core:register"),
            {"username": "newuser", "password1": "Secret123!", "password2": "Secret123!"},
        )
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username="newuser")
        self.assertTrue(user.check_password("Secret123!"))

    def test_login_requires_valid_credentials(self):
        User.objects.create_user("loginuser", password="pw")
        response = self.client.post(
            reverse("core:login"),
            {"username": "loginuser", "password": "wrong"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(self.client.session.get("_auth_user_id"))

    def test_login_and_logout(self):
        User.objects.create_user("loginuser", password="pw")
        response = self.client.post(
            reverse("core:login"),
            {"username": "loginuser", "password": "pw"},
        )
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse("core:topics"))
        self.assertEqual(response.status_code, 200)
        self.client.post(reverse("core:logout"))
        response = self.client.get(reverse("core:topics"))
        self.assertEqual(response.status_code, 302)


class QuizFlowTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("quizuser", password="pw")
        self.topic = Topic.objects.create(title="Тема: Python")
        for i in range(12):
            Question.objects.create(
                topic=self.topic,
                text=f"Вопрос {i + 1}?",
                options=["А", "Б", "В", "Г"],
                correct_index=i % 4,
            )
        self.client.login(username="quizuser", password="pw")

    def test_topics_page_lists_topics(self):
        response = self.client.get(reverse("core:topics"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["topics"].count(), 1)

    def test_quiz_shows_10_random_questions(self):
        response = self.client.get(reverse("core:quiz", args=[self.topic.pk]))
        self.assertEqual(response.status_code, 200)
        questions = response.context["questions"]
        self.assertEqual(len(questions), 10)
        self.assertTrue(
            all(q.topic_id == self.topic.pk for q in questions)
        )
        self.assertEqual(
            len({q.pk for q in questions}), 10
        )

    def test_quiz_shows_all_if_fewer_than_10(self):
        small_topic = Topic.objects.create(title="Маленькая тема")
        for i in range(3):
            Question.objects.create(
                topic=small_topic, text=f"Короткий вопрос {i + 1}?", options=["А", "Б"], correct_index=0
            )
        response = self.client.get(reverse("core:quiz", args=[small_topic.pk]))
        self.assertEqual(len(response.context["questions"]), 3)

    def test_quiz_post_creates_attempt_and_result(self):
        self.client.get(reverse("core:quiz", args=[self.topic.pk]))
        question_ids = self.client.session["quiz_question_ids"]
        data = {f"answer_{qid}": "1" for qid in question_ids}
        response = self.client.post(
            reverse("core:quiz", args=[self.topic.pk]), data, follow=True
        )
        self.assertEqual(response.status_code, 200)
        attempt = QuizAttempt.objects.filter(user=self.user).first()
        self.assertIsNotNone(attempt)
        self.assertEqual(attempt.topic, self.topic)
        self.assertEqual(attempt.total, 10)
        self.assertEqual(len(attempt.results), 10)
        for r in attempt.results:
            self.assertEqual(r["is_correct"], r["user_answer"] == r["correct_answer"])

    def test_result_page_shows_score_and_correct_answers(self):
        self.client.get(reverse("core:quiz", args=[self.topic.pk]))
        question_ids = self.client.session["quiz_question_ids"]
        questions = Question.objects.filter(pk__in=question_ids).in_bulk()
        data = {}
        for qid in question_ids:
            q = questions[qid]
            data[f"answer_{qid}"] = str((q.correct_index + 1) % 4)
        self.client.post(reverse("core:quiz", args=[self.topic.pk]), data)
        response = self.client.get(reverse("core:result"))
        self.assertEqual(response.status_code, 200)
        attempt = QuizAttempt.objects.filter(user=self.user).first()
        self.assertEqual(response.context["attempt"], attempt)
        self.assertEqual(response.context["attempt"].score, 0)

    def test_my_results_lists_attempts(self):
        self.client.get(reverse("core:quiz", args=[self.topic.pk]))
        self.client.post(reverse("core:quiz", args=[self.topic.pk]), {})
        response = self.client.get(reverse("core:my_results"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["attempts"].count(), 1)

    def test_quiz_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("core:quiz", args=[self.topic.pk]))
        self.assertEqual(response.status_code, 302)

    def test_result_without_attempts_redirects(self):
        QuizAttempt.objects.filter(user=self.user).delete()
        response = self.client.get(reverse("core:result"))
        self.assertEqual(response.status_code, 302)
