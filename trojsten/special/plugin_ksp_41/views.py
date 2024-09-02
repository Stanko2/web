import copy
import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt

from .levels import levels, test_program

# from .interpreter import
from .models import UserLevel

# from .interpreter import unpack_blockly
from .update_points import update_points


@login_required()
def main(request):
    return redirect("/specialne/ksp/41/1/index.html")


@login_required()
def state(request):
    data = UserLevel.objects.filter(user=request.user)
    levels2 = copy.deepcopy(levels)
    for level in levels2:
        level["solved"] = False
        for d in data:
            if d.level == level["id"]:
                level["solved"] = d.solved
                level["workspace"] = json.loads(d.data)
                break

    return JsonResponse(levels2, safe=False)


@login_required()
@csrf_exempt
def save(request):
    data = json.loads(request.body)
    is_prask = "prask" in request.get_host()
    userLevel = UserLevel.objects.get_or_create(user=request.user, level=data["level"])[
        0
    ]
    userLevel.data = json.dumps(data["data"])
    level = levels[data["level"] - 2]
    status = test_program(data["data"], level)
    if status == "OK":
        userLevel.solved = True
        userLevel.save()
        update_points(request.user, is_prask)
    userLevel.save()
    return JsonResponse({"status": status})


@login_required()
def run(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Only POST requests are allowed")

    data = json.loads(request.body)
    level = data["level"]
    # unpack_blockly(data["block"])

    return JsonResponse({})
