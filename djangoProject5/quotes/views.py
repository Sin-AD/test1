from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import F
from django.http import JsonResponse, HttpResponseBadRequest
from .models import Quote, Source
from .forms import QuoteForm
import random

def weighted_random_quote():
    qs = Quote.objects.all()
    if not qs.exists():
        return None
    choices = []
    weights = []
    for q in qs:
        w = max(0, int(q.weight))
        if w > 0:
            choices.append(q.pk)
            weights.append(w)
    if not choices:
        return qs.order_by("?").first()
    selected_pk = random.choices(choices, weights=weights, k=1)[0]
    return Quote.objects.get(pk=selected_pk)

def index(request):
    quote = weighted_random_quote()
    if quote:
        quote.increment_views()
    return render(request, "quotes/index.html", {"quote": quote})


def add_quote(request):
    if request.method == "POST":
        form = QuoteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("quotes:index")
    else:
        form = QuoteForm()
    return render(request, "quotes/add_quote.html", {"form": form})


def top10(request):
    top = Quote.objects.order_by("-likes", "-views")[:10]
    return render(request, "quotes/top10.html", {"top": top})

def vote(request, pk):
    if request.method != "POST":
        return HttpResponseBadRequest("Только POST")

    quote = get_object_or_404(Quote, pk=pk)
    kind = request.POST.get("vote")

    if kind not in ("like", "dislike"):
        return HttpResponseBadRequest("Некорректный тип голоса")

    if "quote_votes" not in request.session:
        request.session["quote_votes"] = {}

    votes = request.session["quote_votes"]
    previous_vote = votes.get(str(pk))  

    if previous_vote == kind:
        return JsonResponse({"likes": quote.likes, "dislikes": quote.dislikes})

    if previous_vote == "like":
        Quote.objects.filter(pk=pk).update(likes=F("likes") - 1)
    elif previous_vote == "dislike":
        Quote.objects.filter(pk=pk).update(dislikes=F("dislikes") - 1)

    if kind == "like":
        Quote.objects.filter(pk=pk).update(likes=F("likes") + 1)
    elif kind == "dislike":
        Quote.objects.filter(pk=pk).update(dislikes=F("dislikes") + 1)

    votes[str(pk)] = kind
    request.session["quote_votes"] = votes
    request.session.modified = True

    quote.refresh_from_db()
    return JsonResponse({"likes": quote.likes, "dislikes": quote.dislikes})

def popular_quotes(request):
    filter_by = request.GET.get('filter', 'likes')  
    if filter_by not in ['likes', 'dislikes', 'views']:
        filter_by = 'likes'

    quotes = Quote.objects.order_by(f'-{filter_by}')[:10]
    return render(request, 'quotes/popular.html', {
        'quotes': quotes,
        'filter_by': filter_by

    })
