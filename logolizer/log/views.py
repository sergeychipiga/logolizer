import re
from django.shortcuts import *
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from logolizer.log.forms import UploadForm
from logolizer.log.models import Log

@login_required
def upload(request):
  if request.method == "POST":
    form = UploadForm(request.POST, request.FILES)
# TODO: simplify it, move custom checking to model and form
    if form.is_valid():
      file = form.cleaned_data['file']
      if file.content_type.split('/')[0] == 'text':
        if file.size < 209715200:
          try:
            check_parsable(file)
            log = Log(title=form.cleaned_data['title'],
                      file=file,
                      user=request.user)
            log.save()
            messages.info(request, "File was upload successfully")
          except:
            messages.info(request, "Unparsable file")
        else:
          messages.error(request, "Too large file")
      else:
        messages.error(request, "Invalid file format")
    else:
      messages.error(request, "Invalid title or file")
  else:
    messages.error(request, "Use POST request")
  return redirect(reverse('profile'))

def check_parsable(log):
  line = log.readline()
  ip = line.split(" ")[0]
  time = re.search('\[(.+)\]', line).group(1)
  elems = re.findall('"([^"]+)"', line)
  reqwest = elems[0]
  host = elems[1]
  agent = elems[2]
  code = re.search('" (\d+) ', line).group(1)
  duration = re.search('" (\d+\.\d+)', line).group(1)
