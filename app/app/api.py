import json
from ninja import NinjaAPI
from webhook.models import TestWebhook

api = NinjaAPI()

@api.api_operation(["POST", "GET"], "/v1/webhook")
def webhook(request):
    try:
        obj = json.loads(request.body.decode('utf-8'))
        TestWebhook.objects.create(data=json.dumps(obj))
        return {"result": True}
    except Exception as err:
        return {"result": str(err)}