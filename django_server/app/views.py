from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import os
from .singleton import ProjectList

CURRENT_PORT = os.environ['DJANGO_SERVER_PORT']

def health(request):
    return JsonResponse({'status': 'ok'})

@require_http_methods(["GET"])
def get_projects(request):
    project_list = ProjectList()
    return JsonResponse({
        'projects': project_list.projects,
        'port': CURRENT_PORT
    })

@require_http_methods(["GET"])
def get_project(request, project_id):
    project_list = ProjectList()
    project = project_list.get_project(project_id)
    if project:
        return JsonResponse({'project': project, 'port': CURRENT_PORT})
    return JsonResponse({'error': 'Project not found'}, status=404)

@csrf_exempt
@require_http_methods(["POST"])
def update_project_info(request, project_id):
    try:
        import json
        data = json.loads(request.body)
        description = data.get('description')
        
        project_list = ProjectList()
        project = project_list.get_project(project_id)
        
        if project:
            project['description'] = description
            return JsonResponse({
                'status': 'ok',
                'project': project,
                'port': CURRENT_PORT
            })
        return JsonResponse({'error': 'Project not found'}, status=404)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)