from django.shortcuts import render,redirect
# from .models import *
from . forms import *
from django.contrib import messages
from django.views import generic
from youtubesearchpython import VideosSearch
import requests
import wikipedia
from django.contrib.auth.decorators import login_required

# Create your views here.
# def index(request):
#     return render(request,'index.html')

def home(request):
    return render(request,'home.html')

@login_required
def notes(request):
    if request.method =="POST":
        form = Notesform(request.POST)
        if form.is_valid():
            notes = Notes(user=request.user,title=request.POST['title'],description=request.POST['description'])
            notes.save()
            return redirect("notes")
        messages.success(request,f"Notes Added From {request.user.username} Successfully")
    else:        
        form=Notesform()
    notes=Notes.objects.filter(user=request.user)
    context={'notes':notes,'form':form}
    return render(request,'notes.html',context)  

@login_required
def delete_note(request,pk=None):
    Notes.objects.get(id=pk).delete()
    return redirect("notes")

class NotesDetailView(generic.DetailView):
    model = Notes


@login_required
def homework(request):
    if request.method =="POST":
        form = HomeworkForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST['is_finished']
                if finished == 'on':
                    finished = True
                else:
                    finished = False
            except:
                finished = False            
            homeworks = Homework(
                user=request.user,
                subject=request.POST["subject"],
                title=request.POST['title'],
                description=request.POST['description'],
                due=request.POST['due'],
                is_finished=finished,
            )
            homeworks.save()
            return redirect("homework")
        messages.success(request,f"homework Added From {request.user.username} Successfully")
    else:        
        form=HomeworkForm()

    homework=Homework.objects.filter(user=request.user)

    if len(homework) ==0:
        homework_done =True
    else:
        homework_done = False        
    context={'homework':homework,'homework_done':homework_done,'form':form,}
    return render(request,'homework.html',context)



@login_required
def update_homework(request,pk=None):
    homework = Homework.objects.get(id=pk)
    if homework.is_finished == True:
        homework.is_finished = False
    else:
        homework.is_finished  = True
    homework.save()
    return redirect('homework')
        
@login_required
def delete_homework(request,pk=None):
    Homework.objects.get(id=pk).delete()
    return redirect("homework")


def youtube(request):
    if request.method =="POST":
        form=DashboardForm(request.POST)
        text = request.POST['text'] 
        video= VideosSearch(text,limit=10)
        result_list =[]
        for i in video.result()['result']:
            result_dict ={
                'input':text,
                'title':i['title'],
                'duration':i['duration'],
                'thumbnail':i['thumbnails'][0]['url'],
                'channel':i['channel']['name'],
                'link':i['link'],
                'views':i['viewCount']['short'],
                'published':i['publishedTime'],
            }
            desc = ''
            if i['descriptionSnippet']:
                for j in i['descriptionSnippet']:
                    desc +=j['text']
            result_dict['description'] = desc 
            result_list.append(result_dict)
            context={
                'form':form,
                'results':result_list,
            }
        return render(request,'youtube.html',context)          
    else:
        form = DashboardForm()
    context ={'form' :form}
    return render(request,'youtube.html',context)


@login_required
def todo(request):
    if request.method =="POST":
        form = ToDoForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST['is_finished']
                if finished == 'on':
                    finished = True
                else:
                    finished = False
            except:
                finished = False            
            todos = ToDo(
                user=request.user,
                title=request.POST['title'],
                is_finished=finished,
            )
            todos.save()
            # return redirect("todo")
        messages.success(request,f"ToDo Added From {request.user.username} Successfully")
        # return redirect("todo")
    else:        
        form=ToDoForm()
    todo=ToDo.objects.filter(user=request.user)
    if len(todo) ==0:
        todo_done =True
    else:
        todo_done = False
    context ={'todo' :todo,'form' :form,'todo_done':todo_done}
    return render(request,"todo.html",context)

@login_required
def update_todo(request,pk=None):
    todo = ToDo.objects.get(id=pk)
    if todo.is_finished == True:
        todo.is_finished = False
    else:
        todo.is_finished  = True
    todo.save()
    return redirect('todo')        

@login_required
def delete_todo(request,pk=None):
    ToDo.objects.get(id=pk).delete()
    return redirect("todo")


@login_required
def book(request):
    if request.method =="POST":
        form=DashboardForm(request.POST)
        text = request.POST['text']
        url = "https://www.googleapis.com/books/v1/volumes?q=" +text
        r = requests.get(url)
        answer = r.json()
        result_list =[]
        for i in range(10):
            result_dict ={
                'title':answer['items'][i]['volumeInfo']['title'],
                'subtitle':answer['items'][i]['volumeInfo'].get('subtitle'),
                'description':answer['items'][i]['volumeInfo'].get('description'),
                'count':answer['items'][i]['volumeInfo'].get('pageCount'),
                'categories':answer['items'][i]['volumeInfo'].get('categories'),
                'rating':answer['items'][i]['volumeInfo'].get('pageRating'),
                'thumbnail':answer['items'][i]['volumeInfo'].get('imageLinks').get('thumbnail'),
                'preview':answer['items'][i]['volumeInfo'].get('previewLink'),
            }
            result_list.append(result_dict)
            context={
                'form':form,
                'results':result_list,
            }
        return render(request,'books.html',context)          
    else:
        form = DashboardForm()
    context ={'form' :form}
    return render(request,'books.html',context)


def dictionary(request):
    if request.method =="POST":
        form=DashboardForm(request.POST)
        text = request.POST['text']
        url = "https://api.dictionaryapi.dev/api/v2/entries/en_US/"+text
        r = requests.get(url)
        answer = r.json()
        try:
            phonetics = answer[0]['phonetics'][0]['text']
            audio = answer[0]['phonetics'][0]['audio']
            definition = answer[0]['meanings'][0]['definitions'][0]['definition']
            example = answer[0]['meanings'][0]['definitions'][0]['example']
            synonyms = answer[0]['meanings'][0]['definitions'][0]['synonyms']
            context={
                'form':form,
                'input':text,
                'phonetics':phonetics,
                'audio':audio,
                'definition':definition,
                'example':example,
                'synonyms':synonyms,
            }
        except:
            context={
                'form':form,
                'input':''
            }    
        return render(request,'dictionary.html',context)
    else:
        form = DashboardForm()
    context ={'form' :form}
    return render(request,'dictionary.html',context)



def wiki(request):
    if request.method =="POST":
        text = request.POST['text']
        form=DashboardForm(request.POST)
        search= wikipedia.page(text)
        context={
            'form':form,
            'title':search.title,
            'link':search.url,
            'details':search.summary,

        }    
        return render(request,'wiki.html',context)
    else:
        form = DashboardForm()
        context ={'form' :form}
    return render(request,'wiki.html',context)



def conversion(request):
    if request.method =="POST":
        form = ConversionForm(request.POST)
        if request.POST['measurement'] == 'length':
            measurment_form = ConversionLengthForm()
            context ={
                'form':form,
                'm_form':measurment_form,
                'input':True    
            }
            if 'input' in request.POST:
                first = request.POST['measure1']
                second = request.POST['measure2']
                input = request.POST['input']
                answer =''
                if input and int(input) >=0:
                    if first == 'yard' and second == 'foot':
                        answer = f'{input} yard = {int(input)*3} foot'
                    if first == 'foot' and second == 'yard':
                        answer = f'{input} foot = {int(input)/3} yard'
                context={
                    'form':form,
                    'm_form':measurment_form,
                    'input':True,
                    'answer':answer,
                }
        if request.POST['measurement'] == 'mass':
            measurment_form = ConversionMassForm()
            context ={
                'form':form,
                'm_form':measurment_form,
                'input':True    
            }
            if 'input' in request.POST:
                first = request.POST['measure1']
                second = request.POST['measure2']
                input = request.POST['input']
                answer =''
                if input  and int(input) >=0:
                    if first == 'pound' and second == 'kilogram':
                        answer = f'{input} pound = {int(input)*0.453592} kilogram'
                    if first == 'kilogram' and second == 'pound':
                        answer = f'{input} kilogram = {int(input)*2.20462} pound'
                context={
                    'form':form,
                    'm_form':measurment_form,
                    'input':True,
                    'answer':answer,
                }
    else:    
        form = ConversionForm()
        context={
            'form':form,
            'input':False,
        }
    return render(request,'conversion.html',context)



def register(request):
    if request.method =="POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request,f"Account Created for {username} Successfully")
            return redirect ("login")
    else:        
        form = UserCreationForm()
    context ={
        'form':form
    }
    return render(request,'register.html',context)


@login_required
def profile(request):
    homework=Homework.objects.filter(user=request.user,is_finished=False)
    todo=ToDo.objects.filter(user=request.user,is_finished=False)
    if len(homework) == 0:
        homework_done = True
    else:
        homework_done = False

    if len(todo) == 0:
        todo_done = True
    else:
        todo_done = False
    context ={
        'homework':homework,
        'todo':todo,
        'todo_done':todo_done,
        'homework_done':homework_done,
    }
    return render(request,'profile.html',context)

