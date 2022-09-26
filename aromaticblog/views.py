from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views import generic, View
from django.contrib import messages
from .models import Post, Comment
from .forms import CommentForm, PostForm
from django.views.generic.edit import DeleteView


class ListOfPosts(View):
    """ Displaying posts on a landing page """
    def get(self, request, *args, **kwargs):
        post_list = Post.objects.all().filter(status=1).order_by('-created')
        return render(request, 'index.html', {'post_list': post_list})


class UsersDraftPost(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            post_author = get_object_or_404(User, username=kwargs['username'])
            drafts_list = Post.objects.all().filter(
                status=0, author=post_author
            ).order_by('-created')
            print(drafts_list)
            return render(request, 'drafts.html', {'drafts_list': drafts_list})


class DraftDetail(View):
    def get(self, request, *args, **kwargs):
        current_user = get_object_or_404(User, username=kwargs['username'])
        draft_post = get_object_or_404(Post, slug=kwargs['slug'])
        if draft_post.author == current_user            
            return render(request, 'draft_detail.html', {'draft_post': draft_post})

class Detail(View):
    """ For rendering details of the blog post """
    def get(self, request, slug, *args, **kwargs):
        """ A method to get posts and render filtering by status """
        queryset = Post.objects.filter(status=1)
        post = get_object_or_404(queryset, slug=slug)
        # Comments are filtered in order by most recent and published
        comments = post.comments.filter(approved=True).order_by("-created")
        liked = False
        # Only users who are logged in can like
        if post.likes.filter(id=self.request.user.id).exists():
            liked = True

        return render(
            request,
            "detail_view.html",
            {
                "post": post,
                "comments": comments,
                "commented": False,
                "liked": liked,
                "comment_form": CommentForm()
            },
        )

    def post(self, request, slug, *args, **kwargs):
        """ A method for getting the comments and request approval """
        queryset = Post.objects.filter(status=1)
        post = get_object_or_404(queryset, slug=slug)
        comments = post.comments.filter(approved=True).order_by("-created")
        liked = False  # Originally comments are not 'liked'
        if post.likes.filter(id=self.request.user.id).exists():
            liked = True  # Users that have a profile can like

        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            comment_form.instance.name = request.user.username
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.save()
            # Alert user with django messages
            messages.add_message(request, messages.SUCCESS, 'Thank you, your comment matters!')
        else:
            comment_form = CommentForm()

        return render(
            request,
            "detail_view.html",
            {
                "post": post,
                "comments": comments,
                "commented": True,
                "comment_form": comment_form,
                "liked": liked
            },
        )

class PostAdding(View):
    """ Creating view class """
    def get(self, request, *args, **kwargs):
        """ A function to create posts """
        form = PostForm()
        context = {
            'form': form
        }
        return render(request, 'add_post.html', context)

    def post(self, request, *args, **kwargs):
        """ Handling post request """
        form = PostForm(request.POST)
        user = get_object_or_404(User, username=request.user.username)
        if form.is_valid:
            form.save()
            return HttpResponseRedirect('/drafts/{}'.format(user.username))
        else:
            form = PostForm()
        context = {
            'form': form,
        }
        return render(request, 'add_post.html', context)
        


class PostUpdate(View):
    """ Updating view class """
    def get(self, request, *args, **kwargs):
        """ A function to get the data of existing post from an author, add into form """
        post = get_object_or_404(Post, slug=kwargs['slug'])
        current_user = get_object_or_404(User, username=kwargs['username'])
        if post.status == 0 or post.author == current_user:
            form = PostForm(instance=post)
            print('this is printing post')
            context = {
                'post': post,
                'form': form
            }
            return render(request, 'edit_post.html', context)

    def post(self, request, *args, **kwargs):
        post = get_object_or_404(Post, slug=kwargs['slug'])
        form = PostForm(request.POST, request.FILES, instance=post)
        current_user = get_object_or_404(User, username=kwargs['username'])
        if post.status == 0 or post.author == current_user:
            if form.is_valid:
                form.save()
                return HttpResponseRedirect('/drafts_detail/{}'.format(post.slug))
            else:
                form = PostForm(request.POST, request.FILES, instance=post)
            context = {
                'post': post,
                'form': form,
            }
            return render(request, 'edit_post.html', context)
        
        # if request.user.is_superuser or request.user.id == post.author.id:

class PostDelete(DeleteView):
    """ A class to delete posts that are in draft """
    def get(self, request, *args, **kwargs):
        """ A function to get the data of existing post from an author and put it into form """
        post = get_object_or_404(Post, slug=kwargs['slug'])
        current_user = get_object_or_404(User, username=kwargs['username'])
        if post.status == 0 or post.author == current_user:
            print('this is deleting printing post')
            context = {
                'post': post,
            }
            return render(request, 'post_confirm_delete.html', context)
    def post(self, request, *args, **kwargs):
        """ Getting the post data and prefilled form to be deleting them"""
        post = get_object_or_404(Post, slug=kwargs['slug'])
        user = get_object_or_404(User, username=request.user.username)
        post.delete()
        messages.success(request, 'Post deleted successfully')
        return HttpResponseRedirect('/drafts/{}'.format(user.username))  



# @login_required
# def update_comment(request, slug, id):
#     """ A view to update comments by users who created them/admin """
#     post = get_object_or_404(Post, slug=slug)
#     comment = get_object_or_404(Comment, id=id)
#     comment_form = CommentForm()
#     if request.method == 'POST':
#         comment_form = CommentForm(instance=comment.comment_author)
#         if comment_form.is_valid():
#             comment_form.save()
#             return HttpResponseRedirect('post_detail', slug=slug)  
#         context = {
#             'comment_form': comment_form,
#         }      
#     return render(request, 'edit_comment.html', context)


class TheLikes(View):
    """ The view for the users to Like the posts or comment """
    def post(self, request, slug, *args, **kwargs):
        """ Connecting to a particular post by slug """
        post = get_object_or_404(Post, slug=slug)
        # If there is likes already, clicking deletes it
        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
        else:
            # If user did not like yet, add like
            post.likes.add(request.user)
        # Redirecting to the post detail page
        return HttpResponseRedirect(reverse('post_detail', args=[slug]))


