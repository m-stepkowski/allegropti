from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Post
from .production import Allegro

# Create your views here.

def post_list(request):
	posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')[:3]
	return render(request, 'search_mode/index.html', {'posts': posts, 'hp': 1})
	
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'search_mode/post_detail.html', {'post': post})
	
def search_item(request):
	# Search item
	si = request.POST['search_item']
	# Search result
	Polaczenie = Allegro()
	sr = Polaczenie.wyszukaj(si)
	return render(request, 'search_mode/search_result.html', {'results': sr})