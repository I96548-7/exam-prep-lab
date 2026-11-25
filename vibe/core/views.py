import random

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import RegisterForm
from .models import Question, QuizAttempt, Topic

QUESTIONS_PER_TEST = 10


def index(request):
    return redirect("core:topics")


@login_required
def topics(request):
    return render(request, "core/topics.html", {"topics": Topic.objects.all()})


@login_required
def quiz(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)

    if request.method == "POST":
        question_ids = request.session.get("quiz_question_ids", [])
        if not question_ids:
            return redirect("core:topics")

        answers = {}
        for key, value in request.POST.items():
            if key.startswith("answer_"):
                answers[key[len("answer_"):]] = value

        questions = Question.objects.in_bulk(question_ids)
        results = []
        score = 0
        for qid in question_ids:
            question = questions.get(qid)
            if question is None:
                continue
            raw = answers.get(str(qid))
            user_answer = int(raw) if raw not in (None, "") else None
            is_correct = (
                user_answer is not None and user_answer == question.correct_index
            )
            if is_correct:
                score += 1
            results.append(
                {
                    "question_id": question.pk,
                    "question": question.text,
                    "options": question.options,
                    "user_answer": user_answer,
                    "correct_answer": question.correct_index,
                    "is_correct": is_correct,
                }
            )

        attempt = QuizAttempt.objects.create(
            user=request.user,
            topic=topic,
            question_ids=question_ids,
            answers={
                k: v for k, v in answers.items() if v not in (None, "")
            },
            results=results,
            score=score,
            total=len(results),
        )
        request.session.pop("quiz_question_ids", None)
        request.session.pop("quiz_topic_id", None)
        request.session["last_attempt_id"] = attempt.pk
        return redirect("core:result")

    if request.session.get("quiz_topic_id") != topic.pk:
        ids = list(
            Question.objects.filter(topic=topic, is_active=True).values_list(
                "pk", flat=True
            )
        )
        random.shuffle(ids)
        request.session["quiz_question_ids"] = ids[:QUESTIONS_PER_TEST]
        request.session["quiz_topic_id"] = topic.pk

    question_ids = request.session.get("quiz_question_ids", [])
    questions = Question.objects.in_bulk(question_ids)
    ordered = [questions[qid] for qid in question_ids if qid in questions]
    return render(request, "core/quiz.html", {"topic": topic, "questions": ordered})


@login_required
def result(request):
    attempt = None
    attempt_id = request.session.get("last_attempt_id")
    if attempt_id:
        attempt = QuizAttempt.objects.filter(pk=attempt_id, user=request.user).first()
    if attempt is None:
        attempt = QuizAttempt.objects.filter(user=request.user).first()
    if attempt is None:
        return redirect("core:topics")
    return render(request, "core/result.html", {"attempt": attempt})


@login_required
def my_results(request):
    attempts = QuizAttempt.objects.filter(user=request.user).select_related("topic")
    return render(request, "core/my_results.html", {"attempts": attempts})


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "core/register.html"
    success_url = reverse_lazy("core:login")

    def form_valid(self, form):
        messages.success(self.request, "Регистрация успешна. Войдите в систему.")
        return super().form_valid(form)
